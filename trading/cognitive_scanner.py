#!/usr/bin/env python3
import argparse
import json
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timedelta

import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import screener, transcript_fetcher

from db_schema import ensure_scanner_picks_schema


DB_PATH = "/home/cowork/cowork/trading/trading.db"
ENV_PATH = "/home/cowork/cowork/config/api_keys.env"
TRANSCRIPTS_DIR = "/home/cowork/cowork/trading/transcripts"
DISCORD_API_BASE = "https://discord.com/api/v10"
DEFAULT_SECTOR_ETF = "GRID"
DEFAULT_POSITION_NOTIONAL = 5000.0
SINGLE_SYMBOL_LIMIT = 150000.0
SECTOR_LIMIT = 600000.0


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def build_prompt(symbol, news_content, historical_signal_block=""):
    return """你是一个结构化信息提取器。只能根据下面提供的原始文本得出结论，禁止使用外部知识。

公司：{symbol}
最近新闻（按时间倒序，最多15条）：
{news_content}

{historical_signal_block}

请严格按JSON格式输出，每个判断必须附上原文依据（直接引用原文句子，没有原文依据的填null）：

{{
  "old_label": "市场现在用什么旧框架定义这家公司（1句话）",
  "new_signal": "原文中出现了什么新的变化信号（1-2句话）",
  "new_signal_quote": "支持new_signal的原文引用",
  "signal_continuity": "这个信号是第一次出现还是连续出现（one-time/recurring）",
  "score_narrative": 管理层语言变化分数0-3（整数，0=无变化/1=轻微/2=明显/3=显著且连续，无原文支撑给0）,
  "score_market_lag": 市场认知滞后分数0-3（整数，基于分析师覆盖少+评级保守+旧标签还在用）,
  "score_tailwind": 行业尾风分数0-2（整数，0=无/1=有迹象/2=明确外部数据支撑）,
  "score_catalyst": 催化剂清晰度0-2（整数，0=无/1=模糊/2=有明确时间点和可验证事件）,
  "score_tradability": 可交易性0-1（整数，1=日均成交额>M，0=低流动性）,
  "score_disconfirmation": 否定风险0-1（整数，0=高风险是一次性噪音/1=信号可持续）,
  "total_score": 以上6项之和（最高12分）,
  "invalidation_conditions": "什么信号说明这个thesis失效（1-2条具体可观测条件）",
  "explosion_catalyst": "什么事件会触发市场重新定价（1条）"
}}""".format(
        symbol=symbol,
        news_content=news_content,
        historical_signal_block=historical_signal_block.strip() or "近90天历史信号：无",
    )


def strip_code_fences(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def parse_claude_json(output_text):
    cleaned = strip_code_fences(output_text)
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return json.loads(cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in claude output")
    return json.loads(cleaned[start : end + 1])


def build_news_content(news_rows, max_items=15):
    parts = []
    for i, item in enumerate(news_rows[:max_items], 1):
        if isinstance(item, dict):
            title = item.get("title", "").strip()
            text = (item.get("text", "") or item.get("description", "") or "").strip()
            text_excerpt = text[:500] if text else ""
        else:
            title = str(item).strip()
            text_excerpt = ""
        if not title:
            continue
        block = f"--- 新闻 {i} ---\n标题: {title}"
        if text_excerpt:
            block += f"\n内容: {text_excerpt}"
        parts.append(block)
    return "\n\n".join(parts) or "无相关新闻"


def build_historical_signal_block(headlines):
    if not headlines:
        return ""
    lines = ["[近90天关键信号]"]
    for headline in headlines[:15]:
        lines.append(f"- {headline}")
    return "\n".join(lines)


def fetch_recent_signal_headlines(conn, symbol):
    since = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    rows = conn.execute(
        """
        SELECT headline
        FROM signals
        WHERE symbol = ?
          AND signal_quality IN ('HIGH', 'MEDIUM')
          AND date >= ?
          AND headline IS NOT NULL
          AND TRIM(headline) != ''
        ORDER BY date DESC, id DESC
        LIMIT 15
        """,
        (symbol, since),
    ).fetchall()
    return [row[0] for row in rows if row[0]]


def run_claude_analysis(symbol, news_rows, historical_headlines=None):
    news_content = build_news_content(news_rows)
    historical_signal_block = build_historical_signal_block(historical_headlines or [])
    prompt_text = build_prompt(symbol=symbol, news_content=news_content, historical_signal_block=historical_signal_block)
    try:
        proc = subprocess.run(
            ["claude", "--print", prompt_text],
            capture_output=True,
            text=True,
            cwd="/tmp",
            timeout=120,
            check=False,
        )
    except Exception as e:
        print(f"[ERROR] claude CLI 调用失败 ({symbol}): {e}", flush=True)
        return None

    if proc.returncode != 0 or not proc.stdout.strip():
        print(f"[ERROR] claude CLI 返回异常 ({symbol}): rc={proc.returncode} stderr={proc.stderr[:200]}", flush=True)
        return None

    try:
        parsed = parse_claude_json(proc.stdout)
    except Exception as e:
        print(f"[ERROR] JSON 解析失败 ({symbol}): {e} | 输出片段: {proc.stdout[:200]}", flush=True)
        return None

    if not isinstance(parsed, dict):
        return None

    for key in (
        "score_narrative",
        "score_market_lag",
        "score_tailwind",
        "score_catalyst",
        "score_tradability",
        "score_disconfirmation",
        "total_score",
    ):
        value = parsed.get(key, 0)
        try:
            parsed[key] = int(value)
        except Exception:
            parsed[key] = 0

    parsed["symbol"] = symbol
    return parsed


def send_discord_report(env, results, scan_date, scanned_count):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id or not results:
        return False

    lines = [
        f"📊 P9认知滞后扫描 - {scan_date}",
        f"共扫描{scanned_count}家公司，Top {len(results)}家入围",
        "",
    ]
    for item in results:
        lines.extend(
            [
                f"🔍 {item['symbol']} | 评分：{item.get('total_score', 0)}/12",
                f"旧标签：{item.get('old_label', '')}",
                f"新信号：{item.get('new_signal', '')}",
                f"爆发条件：{item.get('explosion_catalyst', '')}",
                f"失效条件：{item.get('invalidation_conditions', '')}",
                "",
                "---",
                "",
            ]
        )

    message = "\n".join(lines).strip()
    chunks = []
    while message:
        if len(message) <= 1900:
            chunks.append(message)
            break
        split_at = message.rfind("\n\n", 0, 1900)
        if split_at == -1:
            split_at = 1900
        chunks.append(message[:split_at].strip())
        message = message[split_at:].strip()

    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    for chunk in chunks:
        try:
            response = requests.post(
                f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
                headers=headers,
                json={"content": chunk},
                timeout=15,
            )
            response.raise_for_status()
        except Exception:
            return False
    return True


def send_position_limit_alert(env, symbol, sector_etf, symbol_exposure, sector_exposure):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        return
    message = (
        f"⚠️ 仓位限制跳过 {symbol}\n"
        f"单股敞口约 ${symbol_exposure:,.0f} / 上限 ${SINGLE_SYMBOL_LIMIT:,.0f}\n"
        f"{sector_etf} 板块敞口约 ${sector_exposure:,.0f} / 上限 ${SECTOR_LIMIT:,.0f}"
    )
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    try:
        requests.post(
            f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
            headers=headers,
            json={"content": message},
            timeout=15,
        ).raise_for_status()
    except Exception:
        pass


def ensure_watchlist_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            score INTEGER,
            old_label TEXT,
            new_signal TEXT,
            invalidation TEXT,
            explosion_catalyst TEXT,
            scan_date TEXT
        )
        """
    )
    conn.commit()


def fetch_current_price(symbol):
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return None


def get_position_notional(row, has_qty_column):
    entry_price = row["entry_price"] or 0
    if has_qty_column:
        qty = row["qty"]
        if qty and entry_price:
            try:
                return float(qty) * float(entry_price)
            except Exception:
                pass
    return DEFAULT_POSITION_NOTIONAL


def check_position_limits(conn, symbol, sector_etf, new_position_notional):
    columns = {row[1] for row in conn.execute("PRAGMA table_info(scanner_picks)").fetchall()}
    has_qty_column = "qty" in columns
    select_qty = ", qty" if has_qty_column else ""
    rows = conn.execute(
        f"""
        SELECT symbol, entry_price, sector_etf{select_qty}
        FROM scanner_picks
        WHERE status = 'open'
        """
    ).fetchall()

    symbol_exposure = new_position_notional
    sector_exposure = new_position_notional

    for row in rows:
        row_data = {"symbol": row[0], "entry_price": row[1], "sector_etf": row[2]}
        if has_qty_column:
            row_data["qty"] = row[3]
        notional = get_position_notional(row_data, has_qty_column)
        if row_data["symbol"] == symbol:
            symbol_exposure += notional
        if row_data["sector_etf"] == sector_etf:
            sector_exposure += notional

    return {
        "allowed": symbol_exposure <= SINGLE_SYMBOL_LIMIT and sector_exposure <= SECTOR_LIMIT,
        "symbol_exposure": symbol_exposure,
        "sector_exposure": sector_exposure,
    }


def write_scanner_picks(results, scan_date, env):
    conn = sqlite3.connect(DB_PATH)
    try:
        ensure_scanner_picks_schema(conn)
        inserted = 0
        for item in results:
            symbol = item.get("symbol")
            price = fetch_current_price(symbol)
            sector_etf = DEFAULT_SECTOR_ETF
            limit_check = check_position_limits(conn, symbol, sector_etf, DEFAULT_POSITION_NOTIONAL)
            if not limit_check["allowed"]:
                print(f"跳过 {symbol}: 仓位限制触发", flush=True)
                send_position_limit_alert(
                    env,
                    symbol,
                    sector_etf,
                    limit_check["symbol_exposure"],
                    limit_check["sector_exposure"],
                )
                continue

            existing = conn.execute(
                "SELECT id FROM scanner_picks WHERE symbol=? AND status='open' LIMIT 1",
                (symbol,),
            ).fetchone()
            if existing:
                print(f"跳过 {symbol}: 已有 open 持仓 (id={existing[0]})", flush=True)
                continue

            spy_entry = fetch_current_price("SPY")
            sector_etf_entry = fetch_current_price(sector_etf)
            conn.execute(
                """
                INSERT OR IGNORE INTO scanner_picks
                (symbol, entry_price, scan_date, score, old_label, new_signal,
                 invalidation, explosion_catalyst, status, spy_entry, sector_etf, sector_etf_entry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
                """,
                (
                    symbol,
                    price,
                    scan_date,
                    item.get("total_score", 0),
                    item.get("old_label"),
                    item.get("new_signal"),
                    item.get("invalidation_conditions"),
                    item.get("explosion_catalyst"),
                    spy_entry,
                    sector_etf,
                    sector_etf_entry,
                ),
            )
            inserted += 1
        conn.commit()
        print(f"scanner_picks 写入 {inserted} 条", flush=True)
    finally:
        conn.close()


def write_watchlist(results, scan_date):
    conn = sqlite3.connect(DB_PATH)
    try:
        ensure_watchlist_table(conn)
        for item in results:
            conn.execute(
                """
                INSERT INTO watchlist
                (symbol, score, old_label, new_signal, invalidation, explosion_catalyst, scan_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.get("symbol"),
                    item.get("total_score", 0),
                    item.get("old_label"),
                    item.get("new_signal"),
                    item.get("invalidation_conditions"),
                    item.get("explosion_catalyst"),
                    scan_date,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def analyze_symbols(symbols):
    results = []
    total = len(symbols)
    print(f"开始 LLM 分析，共 {total} 家公司...", flush=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        for i, symbol in enumerate(symbols, 1):
            print(f"  [{i}/{total}] 分析 {symbol}...", end=" ", flush=True)
            payload = load_symbol_payload(symbol)
            if not payload:
                print("⚠️ 无 transcript，跳过", flush=True)
                continue
            news_rows = payload.get("news") or []
            historical_headlines = fetch_recent_signal_headlines(conn, symbol)
            analysis = run_claude_analysis(symbol, news_rows, historical_headlines)
            if analysis:
                score = analysis.get("total_score", 0)
                print(f"✅ 分数 {score}/12", flush=True)
                results.append(analysis)
            else:
                print("❌ LLM 无有效输出", flush=True)
    finally:
        conn.close()
    print(f"分析完成，{len(results)}/{total} 家有效结果", flush=True)
    return results


def load_symbol_payload(symbol, transcripts_dir=TRANSCRIPTS_DIR):
    path = os.path.join(transcripts_dir, f"{symbol}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as e:
        print(f"[ERROR] transcript 加载失败 ({symbol}): {e}", flush=True)
        return None
    return payload if isinstance(payload, dict) else None


def run_full_pipeline(test_symbol=None):
    if test_symbol:
        transcript_fetcher.fetch_for_symbols([test_symbol])
        payload = load_symbol_payload(test_symbol)
        if not payload:
            return None
        conn = sqlite3.connect(DB_PATH)
        try:
            historical_headlines = fetch_recent_signal_headlines(conn, test_symbol)
        finally:
            conn.close()
        return run_claude_analysis(test_symbol, payload.get("news") or [], historical_headlines)

    screener_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screener_output.json")
    if not os.path.exists(screener_path):
        print("screener_output.json不存在，请先运行screener.py")
        return {"scanned_count": 0, "top_results": []}
    with open(screener_path, encoding="utf-8") as f:
        candidates = json.load(f)
    symbols = [row["symbol"] for row in candidates if row.get("symbol")]
    transcript_fetcher.fetch_for_symbols(symbols)
    analyses = analyze_symbols(symbols)
    analyses.sort(key=lambda item: item.get("total_score", 0), reverse=True)
    return {
        "scanned_count": len(symbols),
        "analyzed_count": len(analyses),
        "top_results": [item for item in analyses if item.get("total_score", 0) >= 5][:10],
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", metavar="SYMBOL")
    return parser.parse_args()


def main():
    args = parse_args()
    result = run_full_pipeline(test_symbol=args.test)

    if args.test:
        print(json.dumps(result or {}, ensure_ascii=False, indent=2))
        return

    scanned_count = (result or {}).get("scanned_count", 0)
    analyzed_count = (result or {}).get("analyzed_count", 0)
    top_results = (result or {}).get("top_results", [])

    if scanned_count > 0 and analyzed_count == 0:
        print(f"[FATAL] 扫描了 {scanned_count} 家公司但 0 家成功分析，pipeline 全跪", flush=True)
        sys.exit(1)

    if not top_results:
        print(f"[INFO] 扫描 {scanned_count} 家，分析 {analyzed_count} 家，无标的达到入选阈值（≥5分）", flush=True)
        return

    scan_date = datetime.now().strftime("%Y-%m-%d")
    env = load_env()
    send_discord_report(env, top_results, scan_date, scanned_count)
    write_watchlist(top_results, scan_date)
    write_scanner_picks(top_results, scan_date, env)


if __name__ == "__main__":
    main()
