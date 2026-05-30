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
sys.path.insert(0, "/home/cowork/cowork/scripts")
import screener, transcript_fetcher

from db_schema import ensure_scanner_picks_schema
from config import BENCHMARK_SYMBOL, DEFAULT_SECTOR_ETF
from tide_utils import load_env


DB_PATH = "/home/cowork/cowork/trading/trading.db"
TRANSCRIPTS_DIR = "/home/cowork/cowork/trading/transcripts"
SYSTEM_LOG_PATH = "/home/cowork/cowork/trading/system_log.md"
DISCORD_API_BASE = "https://discord.com/api/v10"
ALPACA_BASE = "https://paper-api.alpaca.markets/v2"
DEFAULT_POSITION_NOTIONAL = 5000.0
SINGLE_SYMBOL_LIMIT = 150000.0
SECTOR_LIMIT = 600000.0

# 2026-05-18 ghost positions 事件后：研究阶段允许自动下单
# 见 memory/feedback_p9_auto_execute.md
AUTO_EXECUTE_NOTIONAL_TARGET = 3000.0   # 每只目标 notional
AUTO_EXECUTE_NOTIONAL_MAX = 5000.0      # 单只 hard cap（防 qty 计算错误）
AUTO_EXECUTE_BATCH_MAX = 15             # 单次扫描下单数量上限


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
  "explosion_catalyst": "Bull Thesis：什么事件会触发市场重新定价（1条具体可验证）",
  "invalidation_conditions": "Invalidation：什么信号说明这个thesis失效（1-2条具体可观测条件）",
  "bear_thesis": "Bear Thesis：为什么市场可能永远不买账（强制写满，不许 null；不是 invalidation 的反面，而是独立的反方逻辑——例如旧框架其实合理/竞争对手抢先/估值已 fully priced in/管理层 track record 差/类似 thesis 历史上都失败）",
  "hidden_risk": "Hidden Risk：3 个最危险变量（用 ; 分隔），每个含'变量+监测信号'，例如：地热补贴政策回撤 - 监测 IRA 修订/储能竞争加剧 - 监测 Tesla/Fluence 季报/利率反弹 - 监测 10Y > 4.5%",
  "theme": "主题标签（5选1，必填）：AI电力 / AI软件 / 公用事业现代化 / 分析师重定价 / 行业重分类",
  "secondary_themes": "次要主题（0-2 个，用 ; 分隔，可为 null）"
}}

⚠️ 重要规则（thesis 写作纪律）：
1. **Bear_thesis 必须独立思考**，不许只是 invalidation 的反面表述；hidden_risk 必须输出 3 个具体监测变量
2. **Hypothesis 语气强制**：bear_thesis 和 explosion_catalyst 的散文部分必须用 may / could / potentially / historically / suggests / appears / market skepticism / durability concerns / structurally 等假设性词汇；**禁止** declarative 断言（如"是 contra-indicator" / "反映 terminal value"），因为这类断言隐含统计支持但实际没有
3. **精确数字不许出现在 thesis 散文部分**（如"forward P/S >30x" / "PE <7x"），未经实时验证的数字会因时间漂移失效。具体数字**只能放在 hidden_risk 的"监测信号"里**作为研究者主观设定的监测阈值
4. **保留可证伪性**：每条 thesis 必须 specific 到能被 invalidation 触发，但 hypothetical 到 6 个月后被打脸不会摧毁可信度
5. 不许偷懒；不许"看起来聪明但缺 falsification 结构"的装饰性表达""".format(
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
          AND signal_quality IN ('high', 'medium')
          AND date >= ?
          AND headline IS NOT NULL
          AND TRIM(headline) != ''
        ORDER BY date DESC, id DESC
        LIMIT 15
        """,
        (symbol, since),
    ).fetchall()
    return [row[0] for row in rows if row[0]]


def run_claude_analysis(symbol, news_rows, historical_headlines=None, max_retries=1):
    """2026-05-18 加 retry once: 38% JSON 解析失败率太高，偶发 LLM 输出格式错误，retry 一次预期降到 15-20%。
    任一步失败 → sleep 2 秒 → 重调 claude --print 一次。
    """
    import time
    news_content = build_news_content(news_rows)
    historical_signal_block = build_historical_signal_block(historical_headlines or [])
    prompt_text = build_prompt(symbol=symbol, news_content=news_content, historical_signal_block=historical_signal_block)

    for attempt in range(max_retries + 1):  # attempt 0 = 第一次，attempt 1 = retry
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
            print(f"[ERROR] claude CLI 调用失败 ({symbol}) attempt {attempt+1}: {e}", flush=True)
            if attempt < max_retries:
                time.sleep(2); continue
            return None

        if proc.returncode != 0 or not proc.stdout.strip():
            print(f"[ERROR] claude CLI 返回异常 ({symbol}) attempt {attempt+1}: rc={proc.returncode} stderr={proc.stderr[:200]}", flush=True)
            if attempt < max_retries:
                time.sleep(2); continue
            return None

        try:
            parsed = parse_claude_json(proc.stdout)
        except Exception as e:
            print(f"[ERROR] JSON 解析失败 ({symbol}) attempt {attempt+1}: {e} | 输出片段: {proc.stdout[:200]}", flush=True)
            if attempt < max_retries:
                time.sleep(2); continue
            return None

        if not isinstance(parsed, dict):
            if attempt < max_retries:
                time.sleep(2); continue
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
        if attempt > 0:
            print(f"[INFO] {symbol} retry 成功（attempt {attempt+1}）", flush=True)
        return parsed

    return None


def send_discord_report(env, results, scan_date, scanned_count, executed_summary=None):
    """results: scanner top picks; executed_summary: 来自 write_scanner_picks 的下单回执"""
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id or not results:
        return False

    executed_summary = executed_summary or []
    filled = [s for s in executed_summary if s.get("status") in ("accepted","submitted","filled","pending_new","new")]
    rejected = [s for s in executed_summary if s.get("status") == "rejected"]
    total_notional = sum(s.get("notional", 0) for s in filled)

    lines = [
        f"📋 P9 认知滞后扫描 已自动下单 - {scan_date}",
        f"扫描 {scanned_count} 家公司，Top {len(results)} 家入围 → 自动下单 {len(filled)} 只 / 拒绝 {len(rejected)} 只",
        f"预计 notional ${total_notional:,.0f}（opg 单，下个交易日开盘成交）",
        "",
    ]
    if rejected:
        lines.append("⚠️ 被 sanity check 拒绝：")
        for r in rejected:
            lines.append(f"  {r['symbol']}: {r.get('note', '')}")
        lines.append("")
    for item in results:
        sym = item["symbol"]
        exe = next((s for s in executed_summary if s["symbol"] == sym), None)
        if exe and exe.get("status") in ("accepted","submitted","filled","pending_new","new"):
            exe_tag = f"✅ 已下单 {exe['qty']}股"
        elif exe and exe.get("status") == "rejected":
            exe_tag = f"❌ 拒绝 ({exe.get('note','')})"
        else:
            exe_tag = "⏸️ 无 executed 记录"
        lines.extend(
            [
                f"🔍 {sym} | 评分：{item.get('total_score', 0)}/12 | {exe_tag}",
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
        WHERE status IN ('filled', 'filled_late')
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


def fetch_buying_power(env):
    """拉 Alpaca swing 账户 buying_power（buying_power = cash + margin available）。
    返回 float，失败返回 0（保守拒所有新单）。"""
    url = f"{ALPACA_BASE}/account"
    headers = {
        "APCA-API-KEY-ID": env.get("ALPACA_SWING_KEY", ""),
        "APCA-API-SECRET-KEY": env.get("ALPACA_SWING_SECRET", ""),
    }
    import urllib.request as _urllib_req
    req = _urllib_req.Request(url, headers=headers)
    try:
        resp = _urllib_req.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        return float(data.get("buying_power", 0))
    except Exception as e:
        print(f"[WARN] fetch_buying_power 失败: {e}", flush=True)
        return 0.0


def auto_place_order(env, symbol, qty, time_in_force="opg"):
    """直接下单 swing，返回 dict {order_id, status, fill_price}"""
    url = f"{ALPACA_BASE}/orders"
    headers = {
        "APCA-API-KEY-ID": env.get("ALPACA_SWING_KEY", ""),
        "APCA-API-SECRET-KEY": env.get("ALPACA_SWING_SECRET", ""),
        "Content-Type": "application/json",
    }
    body = json.dumps({
        "symbol": symbol,
        "qty": str(qty),
        "side": "buy",
        "type": "market",
        "time_in_force": time_in_force,
    }).encode("utf-8")
    import urllib.error, urllib.request as _urllib_req
    req = _urllib_req.Request(url, data=body, headers=headers, method="POST")
    try:
        resp = _urllib_req.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def write_scanner_picks(results, scan_date, env):
    """2026-05-19 改：扫描后直接自动下单到 swing（opg 单），写 status='submitted' + cohort='auto_pending'。
    成交结果由次日 9:45 EDT sync_fill_prices.py 按 Alpaca 实际 status reconcile：
      filled → 'filled' / cohort='auto_filled' + 回填 fill 字段
      expired/canceled/rejected → 同名 status，cohort 保持 auto_pending（DB-broker 一致）
    （2026-05-18 早期版本写死 'filled' / 'auto_filled' 导致 5/19 OPG 1/6 成交时 5 只 ghost positions 复发；
      RCA: rca/2026_05_19_opg_expired_anti_pattern_recurrence.md）
    Sanity check 四层（A1 方案 2026-05-18 加 buying_power）：
      (0) 单次扫描下单数量上限 AUTO_EXECUTE_BATCH_MAX 只
      (1) 已存在 candidate/filled/filled_late/auto_filled 持仓 → dedup
      (2) price 有效性
      (3) 仓位限制（单股 / 板块）
      (4) qty hard cap（单只 notional 不超 AUTO_EXECUTE_NOTIONAL_MAX）
      (5) buying_power 充足（剩余 >= AUTO_EXECUTE_NOTIONAL_TARGET）← 新增
    """
    conn = sqlite3.connect(DB_PATH)
    executed_summary = []
    placed_count = 0
    # A1 新增：扫描开始时拉 buying_power，下单过程中累计已 placed notional
    buying_power = fetch_buying_power(env)
    placed_notional = 0.0
    print(f"[A1 sanity] 起始 buying_power = ${buying_power:,.0f}", flush=True)
    try:
        ensure_scanner_picks_schema(conn)
        for item in results:
            symbol = item.get("symbol")
            price = fetch_current_price(symbol)

            # Sanity 0: 单次扫描下单上限
            if placed_count >= AUTO_EXECUTE_BATCH_MAX:
                executed_summary.append({"symbol": symbol, "status": "rejected",
                                         "note": f"单次扫描 >= {AUTO_EXECUTE_BATCH_MAX} 只上限"})
                continue

            # Sanity 5 (A1 新增): buying_power 剩余检查（在最前面，省后续无用计算）
            remaining_bp = buying_power - placed_notional
            if remaining_bp < AUTO_EXECUTE_NOTIONAL_TARGET:
                executed_summary.append({"symbol": symbol, "status": "rejected",
                                         "note": f"buying_power 剩 ${remaining_bp:,.0f} < ${AUTO_EXECUTE_NOTIONAL_TARGET:.0f}（A1 拒）"})
                continue

            # Sanity 1: dedup
            existing = conn.execute(
                "SELECT id, status FROM scanner_picks WHERE symbol=? AND status IN ('candidate','submitted','filled','filled_late','auto_filled') LIMIT 1",
                (symbol,),
            ).fetchone()
            if existing:
                executed_summary.append({"symbol": symbol, "status": "rejected",
                                         "note": f"已有 {existing[1]} 持仓 (id={existing[0]})"})
                continue

            # Sanity 2: price 有效性
            if not price or price <= 0:
                executed_summary.append({"symbol": symbol, "status": "rejected",
                                         "note": "current_price 无效"})
                continue

            # Sanity 3: 仓位限制
            sector_etf = DEFAULT_SECTOR_ETF
            limit_check = check_position_limits(conn, symbol, sector_etf, AUTO_EXECUTE_NOTIONAL_TARGET)
            if not limit_check["allowed"]:
                send_position_limit_alert(env, symbol, sector_etf,
                    limit_check["symbol_exposure"], limit_check["sector_exposure"])
                executed_summary.append({"symbol": symbol, "status": "rejected",
                                         "note": "仓位限制触发"})
                continue

            # Compute qty
            qty = max(1, round(AUTO_EXECUTE_NOTIONAL_TARGET / price))
            notional = qty * price
            # Sanity 4: qty hard cap
            if notional > AUTO_EXECUTE_NOTIONAL_MAX:
                executed_summary.append({"symbol": symbol, "status": "rejected",
                                         "note": f"notional ${notional:.0f} > 上限 ${AUTO_EXECUTE_NOTIONAL_MAX:.0f}"})
                continue

            # 自动下单 opg
            order = auto_place_order(env, symbol, qty, time_in_force="opg")
            if "error" in order:
                executed_summary.append({"symbol": symbol, "status": "rejected",
                                         "note": f"Alpaca 拒绝: {order['error'][:80]}"})
                continue

            order_id = order.get("id")
            order_status = order.get("status", "submitted")
            fill_px = order.get("filled_avg_price")  # opg 单当时一般是 None

            spy_entry = fetch_current_price(BENCHMARK_SYMBOL)
            sector_etf_entry = fetch_current_price(sector_etf)
            conn.execute(
                """
                INSERT OR IGNORE INTO scanner_picks
                (symbol, entry_price, scan_date, score, old_label, new_signal,
                 invalidation, explosion_catalyst, status, spy_entry, sector_etf, sector_etf_entry,
                 theme, secondary_themes, bear_thesis, hidden_risk,
                 signal_date, signal_entry_price, cohort)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'submitted', ?, ?, ?, ?, ?, ?, ?, ?, ?, 'auto_pending')
                """,
                (
                    symbol, price, scan_date, item.get("total_score", 0),
                    item.get("old_label"), item.get("new_signal"),
                    item.get("invalidation_conditions"), item.get("explosion_catalyst"),
                    spy_entry, sector_etf, sector_etf_entry,
                    item.get("theme"), item.get("secondary_themes"),
                    item.get("bear_thesis"), item.get("hidden_risk"),
                    scan_date, price,
                ),
            )
            # Record trade (fill_price NULL，等 sync_fill_prices.py 次日 9:45 EDT 回填)
            conn.execute(
                """INSERT OR IGNORE INTO trades (symbol, side, order_id, entry_date, qty, fill_price, status)
                   VALUES (?, 'buy', ?, ?, ?, ?, 'open')""",
                (symbol, order_id, scan_date, qty, float(fill_px) if fill_px else None),
            )
            placed_count += 1
            placed_notional += notional  # A1: 累计已下单 notional 用于 buying_power 跟踪
            executed_summary.append({"symbol": symbol, "status": order_status,
                                     "order_id": order_id, "qty": qty,
                                     "notional": notional, "note": "opg → 次日开盘成交"})
            print(f"  ✅ {symbol} auto-filled qty={qty} order_id={order_id[:8] if order_id else '?'} (累计 placed ${placed_notional:,.0f} / bp ${buying_power:,.0f})",
                  flush=True)

        conn.commit()
        print(f"scanner_picks 自动下单 {placed_count} 条 / 总入围 {len(results)} 只", flush=True)
    finally:
        conn.close()
    return executed_summary


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


def write_system_log(submitted_count, dedup_count, analyzed_count, scanned_count):
    from datetime import timezone, timedelta
    edt = timezone(timedelta(hours=-4))
    now = datetime.now(edt).strftime("%Y-%m-%d %H:%M EDT")
    line = f"[{now}] ✅ cognitive_scan: scanned={scanned_count} analyzed={analyzed_count} submitted={submitted_count} dedup_skip={dedup_count} | Alpaca:OK\n"
    try:
        with open(SYSTEM_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)
        print(f"[INFO] system_log 已追加：{line.strip()}", flush=True)
    except Exception as e:
        print(f"[WARN] system_log 写入失败：{e}", flush=True)


def send_scan_email(results, executed_summary, scan_date, scanned_count):
    try:
        from send_email import send_email
    except ImportError:
        print("[WARN] send_email 模块不可用，跳过邮件", flush=True)
        return
    executed_summary = executed_summary or []
    submitted = [s for s in executed_summary if s.get("status") in ("accepted", "submitted", "filled", "pending_new", "new")]
    rejected = [s for s in executed_summary if s.get("status") == "rejected"]
    total_notional = sum(s.get("notional", 0) for s in submitted)

    rows = ""
    for item in results:
        sym = item["symbol"]
        exe = next((s for s in executed_summary if s["symbol"] == sym), None)
        if exe and exe.get("status") in ("accepted", "submitted", "filled", "pending_new", "new"):
            tag = f"✅ 已下单 {exe['qty']}股 (${exe.get('notional',0):,.0f})"
            row_color = "#e6f4ea"
        elif exe and exe.get("status") == "rejected":
            tag = f"❌ 拒绝：{exe.get('note','')}"
            row_color = "#fce8e6"
        else:
            tag = "⏸️ 无记录"
            row_color = "#fff"
        rows += f"""
        <tr style="background:{row_color}">
          <td style="padding:8px;font-weight:bold">{sym}</td>
          <td style="padding:8px">{item.get('total_score',0)}/12</td>
          <td style="padding:8px">{tag}</td>
        </tr>
        <tr style="background:{row_color}">
          <td colspan="3" style="padding:4px 8px 2px;font-size:12px;color:#555">
            <b>旧标签：</b>{item.get('old_label','')}<br>
            <b>新信号：</b>{item.get('new_signal','')}<br>
            <b>爆发条件：</b>{item.get('explosion_catalyst','')}<br>
            <b>失效条件：</b>{item.get('invalidation_conditions','')}
          </td>
        </tr>
        <tr><td colspan="3" style="padding:2px"></td></tr>"""

    rejected_html = ""
    if rejected:
        items = "".join(f"<li>{r['symbol']}: {r.get('note','')}</li>" for r in rejected)
        rejected_html = f"<p><b>⚠️ 被拒绝（{len(rejected)}只）：</b><ul>{items}</ul></p>"

    html = f"""
    <h2>📋 TIDE 认知滞后扫描报告 — {scan_date}</h2>
    <p>扫描 <b>{scanned_count}</b> 家 → 入围 <b>{len(results)}</b> 家 → 已下单 <b>{len(submitted)}</b> 只 | 预计 notional <b>${total_notional:,.0f}</b></p>
    {rejected_html}
    <table style="border-collapse:collapse;width:100%;font-family:sans-serif;font-size:13px">
      <tr style="background:#1a73e8;color:#fff">
        <th style="padding:8px">股票</th><th style="padding:8px">评分</th><th style="padding:8px">状态</th>
      </tr>
      {rows}
    </table>
    <p style="color:#888;font-size:11px">由 TIDE cognitive_scanner 自动生成，OPG 单将在下一交易日开盘成交</p>
    """
    try:
        send_email(
            subject=f"TIDE 扫描报告 {scan_date} | {len(submitted)} 只已下单",
            body=html,
            html=True,
        )
        print(f"[INFO] 扫描结果邮件已发送至 zhitao776@gmail.com", flush=True)
    except Exception as e:
        print(f"[WARN] 邮件发送失败：{e}", flush=True)


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
    write_watchlist(top_results, scan_date)
    executed_summary = write_scanner_picks(top_results, scan_date, env)
    send_discord_report(env, top_results, scan_date, scanned_count, executed_summary=executed_summary)

    submitted = [s for s in executed_summary if s.get("status") in ("accepted", "submitted", "filled", "pending_new", "new")]
    rejected = [s for s in executed_summary if s.get("status") == "rejected"]
    write_system_log(len(submitted), len(rejected), analyzed_count, scanned_count)
    send_scan_email(top_results, executed_summary, scan_date, scanned_count)


if __name__ == "__main__":
    main()
