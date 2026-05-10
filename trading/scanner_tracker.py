#!/usr/bin/env python3
"""
每周对账脚本：追踪 open 和 closed_watching 状态，发 Discord 周报。
用法：python3 trading/scanner_tracker.py
"""
import json
import sqlite3
from datetime import datetime

import requests
import yfinance as yf

from db_schema import ensure_scanner_picks_schema

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"


def load_env():
    env = {}
    with open("/home/cowork/cowork/config/api_keys.env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def fetch_price(symbol):
    try:
        hist = yf.Ticker(symbol).history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return None


def send_discord(env, message):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        return
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
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
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


def append_weekly_price(history, date_str, price):
    if history and history[-1].get("date") == date_str:
        history[-1]["price"] = price
        return history
    history.append({"date": date_str, "price": price})
    return history


def get_exit_date(history):
    if not history:
        return None
    first_date = history[0].get("date")
    if not first_date:
        return None
    try:
        return datetime.strptime(first_date, "%Y-%m-%d").date()
    except Exception:
        return None


def update_closed_watching_row(conn, row, today_str):
    current_price = fetch_price(row["symbol"])
    if current_price is None or not row["exit_price"]:
        return None

    history = load_post_exit_prices(row["post_exit_prices"])
    if not history:
        history = [{"date": today_str, "price": float(row["exit_price"])}]
    history = append_weekly_price(history, today_str, current_price)

    peak = row["post_exit_peak"] or row["exit_price"]
    if current_price > peak:
        peak = current_price

    post_exit_return = (current_price - row["exit_price"]) / row["exit_price"] * 100
    status = row["status"]
    post_exit_3m_return = row["post_exit_3m_return"]
    exit_date = get_exit_date(history)
    if exit_date and (datetime.now().date() - exit_date).days >= 90:
        post_exit_3m_return = post_exit_return
        status = "archived"

    conn.execute(
        """
        UPDATE scanner_picks
        SET post_exit_prices = ?, post_exit_peak = ?, post_exit_3m_return = ?, status = ?
        WHERE id = ?
        """,
        (json.dumps(history, ensure_ascii=False), peak, post_exit_3m_return, status, row["id"]),
    )
    return {
        "symbol": row["symbol"],
        "exit_price": row["exit_price"],
        "current_price": current_price,
        "post_exit_return": post_exit_return,
        "post_exit_peak": peak,
        "status": status,
    }


def update_open_drawdown(conn, row, return_pct):
    if return_pct is None:
        return
    current_drawdown = min(return_pct, row["max_drawdown_pct"]) if row["max_drawdown_pct"] is not None else return_pct
    conn.execute(
        "UPDATE scanner_picks SET max_drawdown_pct = ? WHERE id = ?",
        (current_drawdown, row["id"]),
    )


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_scanner_picks_schema(conn)

    rows = conn.execute(
        """
        SELECT *
        FROM scanner_picks
        WHERE status IN ('open', 'closed_watching')
        ORDER BY score DESC, scan_date DESC
        """
    ).fetchall()

    if not rows:
        conn.close()
        print("没有 open 或 closed_watching 状态的持仓")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    spy_current = fetch_price("SPY")
    open_lines = [f"📊 P9扫描器追踪周报 - {today}", ""]
    watching_lines = ["🧭 Closed Watching", ""]
    open_count = 0
    watching_count = 0

    for row in rows:
        if row["status"] == "open":
            open_count += 1
            current_price = fetch_price(row["symbol"])
            if current_price and row["entry_price"]:
                ret = (current_price - row["entry_price"]) / row["entry_price"] * 100
                ret_str = f"{ret:+.1f}%"
                trend = "📈" if ret > 0 else "📉"
            else:
                ret = None
                ret_str = "N/A"
                trend = "❓"

            if spy_current and row["spy_entry"]:
                spy_ret = (spy_current - row["spy_entry"]) / row["spy_entry"] * 100
                spy_ret_str = f"{spy_ret:+.1f}%"
            else:
                spy_ret_str = "N/A"

            update_open_drawdown(conn, row, ret)

            current_str = f"{current_price:.2f}" if current_price else "N/A"
            open_lines.append(
                f"{trend} {row['symbol']} | 入场 {row['entry_price']:.2f} → 现价 {current_str} | 收益 {ret_str} | SPY同期 {spy_ret_str} | 评分 {row['score']}/12 | 入场日 {row['scan_date']}"
            )
            if row["new_signal"]:
                open_lines.append(f"   thesis: {row['new_signal'][:80]}...")
            open_lines.append("")
            continue

        watching_count += 1
        updated = update_closed_watching_row(conn, row, today)
        if not updated:
            watching_lines.append(f"❓ {row['symbol']} | 无法获取平仓后价格")
            watching_lines.append("")
            continue

        watching_lines.append(
            f"🔭 {updated['symbol']} | 平仓 {updated['exit_price']:.2f} → 现价 {updated['current_price']:.2f} | 平仓后 {updated['post_exit_return']:+.1f}% | 峰值 {updated['post_exit_peak']:.2f} | 状态 {updated['status']}"
        )
        watching_lines.append("")

    conn.commit()
    conn.close()

    open_lines.insert(1, f"Open 持仓 {open_count} 家")
    if watching_count:
        watching_lines.insert(1, f"追踪中 {watching_count} 家")
        lines = open_lines + watching_lines
    else:
        lines = open_lines

    message = "\n".join(lines).strip()
    print(message)

    env = load_env()
    send_discord(env, message)


if __name__ == "__main__":
    from tide_utils import run_with_alert

    run_with_alert("scanner_tracker", main)
