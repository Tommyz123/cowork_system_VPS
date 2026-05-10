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


def build_message(counts, averages, recent, iwm=None):
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
    message = build_message(counts, averages, recent, iwm)
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
