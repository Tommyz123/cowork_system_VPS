#!/usr/bin/env python3
import json
import sqlite3
import urllib.request
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import yfinance as yf

DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
ENV_PATH = Path("/home/cowork/cowork/config/api_keys.env")
LOG_PATH = Path("/home/cowork/cowork/trading/weekly.log")


def log(message: str) -> None:
    timestamped = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    print(timestamped)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(timestamped + "\n")


def load_env():
    env = {}
    with ENV_PATH.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
    return env


def format_avg(value):
    return "n/a" if value is None else f"{value:.2f}%"


def fetch_summary():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        one_week_ago = (datetime.now(UTC) - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        counts = conn.execute(
            """
            SELECT
                COUNT(*) AS total_count,
                SUM(CASE WHEN signal_verdict = 'closed' THEN 1 ELSE 0 END) AS closed_count,
                SUM(CASE WHEN signal_verdict = 'pending' THEN 1 ELSE 0 END) AS pending_count,
                SUM(CASE WHEN created_at >= ? THEN 1 ELSE 0 END) AS new_this_week
            FROM outcome_tracking
            """
            ,
            (one_week_ago,),
        ).fetchone()

        averages = conn.execute(
            """
            SELECT
                AVG(return_30d) AS avg_30d,
                AVG(return_60d) AS avg_60d,
                AVG(return_90d) AS avg_90d
            FROM outcome_tracking
            """
        ).fetchone()

        recent = conn.execute(
            """
            SELECT symbol, tagged_date, return_30d
            FROM outcome_tracking
            ORDER BY tagged_date DESC, id DESC
            LIMIT 10
            """
        ).fetchall()
        return counts, averages, recent
    finally:
        conn.close()


def fetch_iwm_returns() -> dict:
    try:
        ticker = yf.Ticker("IWM")
        hist = ticker.history(period="100d")
        if hist.empty:
            return {}
        result = {}
        current = hist["Close"].iloc[-1]
        for days, key in [(30, "iwm_30d"), (60, "iwm_60d"), (90, "iwm_90d")]:
            if len(hist) > days:
                past = hist["Close"].iloc[-(days + 1)]
                result[key] = round((current - past) / past * 100, 2)
        return result
    except Exception:
        return {}


def fetch_position_health():
    """当前持仓走势体检（复盘观察，非交易信号）。
    读 filled 持仓，用 yfinance 算「入场至今累计%」+「近1周走向」，
    阴跌打标。涨跌%是事实，状态标签是固定阈值判定（非主观）。
    返回 list[dict]，无持仓返回 []。"""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT symbol, entry_price FROM scanner_picks "
            "WHERE status IN ('filled', 'filled_late')"
        ).fetchall()
    finally:
        conn.close()

    health = []
    for symbol, entry_price in rows:
        try:
            hist = yf.Ticker(symbol).history(period="10d")
            if hist.empty or not entry_price:
                continue
            current = float(hist["Close"].iloc[-1])
            since_entry = (current - entry_price) / entry_price * 100
            # 近1周走向：取约5个交易日前
            week_ago = float(hist["Close"].iloc[-6]) if len(hist) >= 6 else float(hist["Close"].iloc[0])
            week_chg = (current - week_ago) / week_ago * 100
        except Exception:
            continue

        # 状态标签：固定阈值判定（事实派生，非主观臆测）
        if since_entry <= -10 and week_chg < 0:
            status = "🔴 阴跌中"
        elif since_entry <= -10:
            status = "🟠 深亏待观察"
        elif week_chg <= -5:
            status = "🟠 近期走弱"
        elif since_entry > 0:
            status = "🟢 走强" if week_chg >= 0 else "🟢 持稳"
        else:
            status = "🟡 小幅承压"
        health.append({
            "symbol": symbol, "since_entry": since_entry,
            "week_chg": week_chg, "status": status,
        })
    # 按入场至今涨跌升序（最惨的排最上，方便复盘抓重点）
    health.sort(key=lambda x: x["since_entry"])
    return health


def build_position_health_block(health):
    if not health:
        return ""
    lines = [
        "",
        "📊 持仓走势体检（复盘观察，非交易信号）",
        "  入场至今 | 近1周 | 状态（按入场至今升序，最惨在上）",
    ]
    for h in health:
        arrow = "↗" if h["week_chg"] > 1 else ("↘" if h["week_chg"] < -1 else "→")
        lines.append(
            f"  {h['symbol']:<6} {h['since_entry']:+6.1f}%  {arrow} {h['week_chg']:+5.1f}%   {h['status']}"
        )
    flagged = [h["symbol"] for h in health if h["status"].startswith(("🔴", "🟠"))]
    if flagged:
        lines.append(f"  ⚠️ 走弱/深亏 {len(flagged)} 只（{', '.join(flagged)}）→ 12月复盘重点看 thesis 是否失效")
    return "\n".join(lines)


def build_message(counts, averages, recent, iwm=None, health=None):
    iwm = iwm or {}
    lines = [
        "P9 TIDE Weekly Outcome Review",
        f"New this week: {counts['new_this_week'] or 0}",
        f"Total: {counts['total_count'] or 0}",
        f"Closed: {counts['closed_count'] or 0}",
        f"Pending: {counts['pending_count'] or 0}",
        "",
        "Performance vs IWM (Russell 2000):",
        f"  30d  Portfolio: {format_avg(averages['avg_30d'])}   IWM: {format_avg(iwm.get('iwm_30d'))}",
        f"  60d  Portfolio: {format_avg(averages['avg_60d'])}   IWM: {format_avg(iwm.get('iwm_60d'))}",
        f"  90d  Portfolio: {format_avg(averages['avg_90d'])}   IWM: {format_avg(iwm.get('iwm_90d'))}",
        "",
        "Last 10 records:",
    ]
    if recent:
        for row in recent:
            ret = "n/a" if row["return_30d"] is None else f"{row['return_30d']:.2f}%"
            lines.append(f"- {row['symbol']} | {row['tagged_date']} | 30d {ret}")
    else:
        lines.append("- no records")
    block = build_position_health_block(health or [])
    if block:
        lines.append(block)
    return "\n".join(lines)


def send_email(env: dict, subject: str, body: str) -> None:
    payload = json.dumps({
        "sender": {"name": "Cowork VPS", "email": env["GMAIL_USER"]},
        "to": [{"email": env["GMAIL_TO"]}],
        "subject": subject,
        "textContent": body,
    }).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={"api-key": env["BREVO_API_KEY"], "Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=15)


def main():
    env = load_env()
    counts, averages, recent = fetch_summary()
    iwm = fetch_iwm_returns()
    health = fetch_position_health()
    message = build_message(counts, averages, recent, iwm, health)
    log("weekly summary generated")
    for line in message.splitlines():
        log(line)

    subject = "P9 TIDE Weekly Review " + datetime.now().strftime("%Y-%m-%d")
    try:
        send_email(env, subject, message)
        log("email sent")
    except Exception as exc:
        log(f"warning: email send failed: {exc}")


if __name__ == "__main__":
    main()
