#!/usr/bin/env python3
"""
TIDE系统 - 每周三 thesis 追踪（12PM EDT自动跑）
取 Top 3 open 持仓，抓最新新闻，问 Claude thesis 是否往预期方向走。
invalidated → Discord 告警，等主公人工决策，不自动平仓。
"""
import json
import re
import sqlite3
import subprocess
import urllib.request
import requests
from datetime import datetime

from db_schema import ensure_scanner_picks_schema, ensure_thesis_alerts_table
from tide_utils import load_env

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"


def fetch_recent_news(symbol, conn, limit=20):
    """从本地 signals 表读取新闻，无需外部 API。"""
    rows = conn.execute(
        """
        SELECT date, headline FROM signals
        WHERE symbol=? AND signal_type='news' AND headline IS NOT NULL
        ORDER BY date DESC LIMIT ?
        """,
        (symbol, limit),
    ).fetchall()
    return [f"[{r[0]}] {r[1]}" for r in rows]


def build_monitor_prompt(symbol, new_signal, explosion_catalyst, invalidation, headlines):
    news_block = "\n".join(f"- {h}" for h in headlines) or "无新闻"
    return f"""你是一个投资 thesis 追踪助手。根据最新新闻判断原始 thesis 是否在往预期方向发展。

公司：{symbol}

原始 thesis（叙事变化信号）：
{new_signal}

预期爆发条件：
{explosion_catalyst}

失效条件：
{invalidation}

最近新闻标题（按时间倒序）：
{news_block}

请严格按 JSON 输出：
{{
  "status": "confirmed" 或 "neutral" 或 "invalidated",
  "status_reason": "一句话说明判断依据（必须引用原文）",
  "catalyst_progress": "爆发条件是否有进展（一句话，没有原文支撑说'无明确进展'）",
  "key_headline": "最能支持你判断的原文标题（没有则填null）",
  "alert": "有没有需要立即关注的风险信号（没有填null）"
}}"""


def run_claude(prompt):
    try:
        proc = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True,
            text=True,
            cwd="/tmp",
            timeout=120,
            check=False,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        cleaned = proc.stdout.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end == -1:
            return None
        return json.loads(cleaned[start: end + 1])
    except Exception:
        return None


def send_discord(env, message):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        return
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    chunks = []
    while message:
        if len(message) <= 1900:
            chunks.append(message)
            break
        split_at = message.rfind("\n", 0, 1900)
        if split_at == -1:
            split_at = 1900
        chunks.append(message[:split_at].strip())
        message = message[split_at:].strip()
    for chunk in chunks:
        try:
            requests.post(
                f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
                headers=headers,
                json={"content": chunk},
                timeout=15,
            ).raise_for_status()
        except Exception:
            pass


STATUS_EMOJI = {"confirmed": "🟢", "neutral": "🟡", "invalidated": "🔴"}


def ensure_thesis_status_column(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(scanner_picks)").fetchall()]
    if "thesis_status" not in cols:
        conn.execute("ALTER TABLE scanner_picks ADD COLUMN thesis_status TEXT DEFAULT 'neutral'")
        conn.commit()


def insert_thesis_alert(conn, symbol, thesis_status, headlines):
    headline_summary = "\n".join(headlines)[:200]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """
        INSERT INTO thesis_alerts
        (symbol, alert_date, thesis_status, headline_summary, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (symbol, datetime.now().strftime("%Y-%m-%d"), thesis_status, headline_summary, now),
    )
    conn.commit()


def close_alpaca_position(env, symbol):
    # P9 路由：swing 唯一账号（2026-05-18 ghost positions 事件后锁定）
    api_key = env.get("ALPACA_SWING_KEY", "")
    api_secret = env.get("ALPACA_SWING_SECRET", "")
    base_url = (
        env.get("ALPACA_SWING_ENDPOINT")
        or "https://paper-api.alpaca.markets"
    ).rstrip("/")
    if base_url.endswith("/v2"):
        base_url = base_url[:-3]
    headers = {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}
    try:
        req = urllib.request.Request(
            f"{base_url}/v2/positions/{symbol}",
            method="DELETE",
            headers=headers,
        )
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
        fill_price = float(resp.get("fill_price") or resp.get("limit_price") or 0)
        return fill_price
    except Exception as e:
        print(f"平仓失败 {symbol}: {e}")
        return None


def write_thesis_status(conn, symbol, status):
    conn.execute(
        "UPDATE scanner_picks SET thesis_status=? WHERE symbol=? AND status IN ('filled', 'filled_late')",
        (status, symbol),
    )
    conn.commit()


def main():
    env = load_env()

    conn = sqlite3.connect(DB_PATH)
    ensure_scanner_picks_schema(conn)
    ensure_thesis_alerts_table(conn)
    ensure_thesis_status_column(conn)

    top3 = conn.execute(
        """
        SELECT symbol, score, new_signal, invalidation, explosion_catalyst, scan_date, entry_price
        FROM scanner_picks
        WHERE status IN ('filled', 'filled_late')
        ORDER BY score DESC
        """
    ).fetchall()

    if not top3:
        print("没有 open 持仓")
        conn.close()
        return

    today = datetime.now().strftime("%Y-%m-%d")
    lines = [f"📋 Thesis 追踪 - {today}", ""]

    for row in top3:
        symbol, score, new_signal, invalidation, explosion_catalyst, scan_date, entry_price = row
        print(f"追踪 {symbol}...", flush=True)
        headlines = fetch_recent_news(symbol, conn)

        prompt = build_monitor_prompt(symbol, new_signal, explosion_catalyst, invalidation, headlines)
        result = run_claude(prompt)

        if not result:
            lines.append(f"❓ {symbol} | LLM 分析失败")
            lines.append("")
            continue

        status = result.get("status", "neutral")
        emoji = STATUS_EMOJI.get(status, "❓")
        entry_str = f"{entry_price:.2f}" if entry_price else "N/A"
        lines.append(f"{emoji} **{symbol}** | {status.upper()} | 评分 {score}/12 | 入场 {entry_str}")
        lines.append(f"  {result.get('status_reason', '')}")
        lines.append(f"  爆发条件: {result.get('catalyst_progress', '')}")
        if result.get("key_headline"):
            lines.append(f"  关键新闻: {result['key_headline']}")
        if result.get("alert"):
            lines.append(f"  ⚠️ 警报: {result['alert']}")
        lines.append("")

        # 写回数据库
        write_thesis_status(conn, symbol, status)

        if status == "invalidated":
            insert_thesis_alert(conn, symbol, status, headlines)
            send_discord(
                env,
                "\n".join(
                    [
                        "🔴 THESIS 失效 — 待主公决策，暂不平仓",
                        f"{symbol} | 入场价 {entry_price}",
                        f"失效原因：{result.get('status_reason', '')}",
                        "请主公确认是否平仓。",
                    ]
                ),
            )

    conn.close()

    message = "\n".join(lines).strip()
    print(message)
    send_discord(env, message)


if __name__ == "__main__":
    from tide_utils import run_with_alert
    run_with_alert("thesis_monitor", main)
