#!/usr/bin/env python3
"""
季度复盘：统计已关闭交易表现，并评估 thesis 告警有效性。
"""
import json
import sqlite3
from datetime import datetime

import requests

from db_schema import ensure_scanner_picks_schema, ensure_thesis_alerts_table
from tide_utils import load_env

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"


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


def load_post_exit_prices(raw_value):
    if not raw_value:
        return []
    try:
        data = json.loads(raw_value)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_exit_date(row):
    history = load_post_exit_prices(row["post_exit_prices"])
    if not history:
        return None
    date_str = history[0].get("date")
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None


def pct_text(value):
    return "N/A" if value is None else f"{value * 100:+.2f}%"


def build_score_bucket_summary(rows):
    buckets = [("9-10", 9, 10), ("7-8", 7, 8), ("5-6", 5, 6)]
    summaries = []
    win_rates = {}
    for label, low, high in buckets:
        bucket_rows = [row for row in rows if row["score"] is not None and low <= row["score"] <= high and row["return_pct"] is not None]
        wins = [row for row in bucket_rows if row["return_pct"] > 0]
        rate = (len(wins) / len(bucket_rows)) if bucket_rows else None
        win_rates[label] = rate
        rate_text = "N/A" if rate is None else f"{rate * 100:.1f}%"
        summaries.append(f"评分 {label}: {len(bucket_rows)} 笔 | 胜率 {rate_text}")

    warnings = []
    adjacent_pairs = [("9-10", "7-8"), ("7-8", "5-6")]
    for left, right in adjacent_pairs:
        left_rate = win_rates.get(left)
        right_rate = win_rates.get(right)
        if left_rate is None or right_rate is None:
            continue
        if abs(left_rate - right_rate) < 0.10:
            warnings.append(f"⚠️ 评分桶 {left} vs {right} 胜率差 <10%，打分区分度偏弱")
    return summaries, warnings


def compute_alert_loss_ratio(rows, alerts_by_symbol):
    alerted_closed = []
    for row in rows:
        exit_date = get_exit_date(row)
        if exit_date is None or row["return_pct"] is None:
            continue
        alert_dates = alerts_by_symbol.get(row["symbol"], [])
        if any(alert_date <= exit_date for alert_date in alert_dates):
            alerted_closed.append(row)

    if not alerted_closed:
        return None, 0

    losses = [row for row in alerted_closed if row["return_pct"] < 0]
    return len(losses) / len(alerted_closed), len(alerted_closed)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_scanner_picks_schema(conn)
    ensure_thesis_alerts_table(conn)

    rows = conn.execute(
        """
        SELECT *
        FROM scanner_picks
        WHERE status IN ('closed_watching', 'closed', 'archived')
        ORDER BY scan_date DESC, id DESC
        """
    ).fetchall()

    alert_rows = conn.execute(
        """
        SELECT symbol, alert_date
        FROM thesis_alerts
        WHERE symbol IS NOT NULL AND alert_date IS NOT NULL
        ORDER BY alert_date ASC, id ASC
        """
    ).fetchall()
    conn.close()

    alerts_by_symbol = {}
    for row in alert_rows:
        try:
            alert_date = datetime.strptime(row["alert_date"], "%Y-%m-%d").date()
        except Exception:
            continue
        alerts_by_symbol.setdefault(row["symbol"], []).append(alert_date)

    closed_rows = [row for row in rows if row["return_pct"] is not None]
    if not closed_rows:
        message = "📘 Quarterly Review\n暂无 closed_watching / closed / archived 交易数据"
        print(message)
        send_discord(load_env(), message)
        return

    wins = [row for row in closed_rows if row["return_pct"] > 0]
    win_rate = len(wins) / len(closed_rows)
    avg_return = sum(row["return_pct"] for row in closed_rows) / len(closed_rows)

    alpha_values = []
    for row in closed_rows:
        if row["spy_entry"] and row["spy_exit"]:
            spy_return = (row["spy_exit"] - row["spy_entry"]) / row["spy_entry"]
            alpha_values.append(row["return_pct"] - spy_return)
    avg_alpha = sum(alpha_values) / len(alpha_values) if alpha_values else None

    alert_loss_ratio, alerted_trade_count = compute_alert_loss_ratio(rows, alerts_by_symbol)
    bucket_lines, bucket_warnings = build_score_bucket_summary(rows)

    lines = [
        f"📘 Quarterly Review - {datetime.now().strftime('%Y-%m-%d')}",
        f"样本数: {len(closed_rows)}",
        f"总胜率: {win_rate * 100:.1f}%",
        f"平均收益率: {avg_return * 100:+.2f}%",
        f"平均 Alpha vs IWM: {'N/A' if avg_alpha is None else f'{avg_alpha * 100:+.2f}%'}",
        f"告警后实际平仓且亏损比例: {'N/A' if alert_loss_ratio is None else f'{alert_loss_ratio * 100:.1f}%'} (样本 {alerted_trade_count})",
        "",
    ]
    lines.extend(bucket_lines)
    if bucket_warnings:
        lines.append("")
        lines.extend(bucket_warnings)

    message = "\n".join(lines).strip()
    print(message)
    send_discord(load_env(), message)


if __name__ == "__main__":
    from tide_utils import run_with_alert

    run_with_alert("quarterly_review", main)
