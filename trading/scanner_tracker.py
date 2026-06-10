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
from config import BENCHMARK_SYMBOL
from tide_utils import load_env

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"
ALPACA_BASE = "https://paper-api.alpaca.markets/v2"


def fetch_alpaca_positions(env):
    """拉 Alpaca swing 账户真实持仓。失败返回 None（跳过对账，不误报）。"""
    import urllib.request
    req = urllib.request.Request(
        f"{ALPACA_BASE}/positions",
        headers={
            "APCA-API-KEY-ID": env.get("ALPACA_SWING_KEY", ""),
            "APCA-API-SECRET-KEY": env.get("ALPACA_SWING_SECRET", ""),
        },
    )
    try:
        return json.loads(urllib.request.urlopen(req, timeout=15).read())
    except Exception as e:
        print(f"[reconcile] Alpaca positions 拉取失败: {e}")
        return None


def position_level_reconcile(conn, env):
    """持仓级对账：Alpaca /positions vs DB filled 清单，逐 symbol 比对。
    订单级对账（sync_fill_prices）堵不住所有洞——2026-06-10 发现 OPG 部分成交
    （终态 expired 但 filled_qty>0）让 GNTX/WTS 真实持仓漏记 3 周。
    返回 (告警行 list, broker 持仓数)；list 空 = 一致。"""
    positions = fetch_alpaca_positions(env)
    if positions is None:
        return ["⚠️ 持仓级对账跳过：Alpaca positions 拉取失败"], None
    broker = {p["symbol"]: float(p["qty"]) for p in positions}
    db_syms = {
        r[0]
        for r in conn.execute(
            "SELECT symbol FROM scanner_picks WHERE status IN ('filled', 'filled_late')"
        )
    }
    alerts = []
    for sym in sorted(set(broker) - db_syms):
        alerts.append(f"🚨 {sym}: Alpaca 持有 {broker[sym]:g} 股但 DB 无 filled 记录（幽灵持仓，监控全漏）")
    for sym in sorted(db_syms - set(broker)):
        alerts.append(f"🚨 {sym}: DB 记录 filled 但 Alpaca 无此持仓（DB 残留）")
    return alerts, len(broker)


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
        WHERE status IN ('filled', 'filled_late', 'closed_watching')
        ORDER BY score DESC, scan_date DESC
        """
    ).fetchall()

    if not rows:
        conn.close()
        print("没有 filled / filled_late / closed_watching 状态的持仓")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    spy_current = fetch_price(BENCHMARK_SYMBOL)
    open_lines = [f"📊 P9扫描器追踪周报 - {today}", ""]
    watching_lines = ["🧭 Closed Watching", ""]
    open_count = 0
    watching_count = 0

    for row in rows:
        if row["status"] in ("open", "filled", "filled_late"):
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
                f"{trend} {row['symbol']} | 入场 {row['entry_price']:.2f} → 现价 {current_str} | 收益 {ret_str} | {BENCHMARK_SYMBOL}同期 {spy_ret_str} | 评分 {row['score']}/12 | 入场日 {row['scan_date']}"
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

    env = load_env()
    reconcile_alerts, broker_count = position_level_reconcile(conn, env)

    conn.commit()
    conn.close()

    open_lines.insert(1, f"Open 持仓 {open_count} 家")
    if watching_count:
        watching_lines.insert(1, f"追踪中 {watching_count} 家")
        lines = open_lines + watching_lines
    else:
        lines = open_lines

    if reconcile_alerts:
        lines = [f"🚨 持仓级对账发现 {len(reconcile_alerts)} 处 DB-broker 不一致："] + reconcile_alerts + ["", "—" * 20, ""] + lines
    elif broker_count is not None:
        lines.append(f"🛡️ 持仓级对账：Alpaca {broker_count} 只 vs DB 一致")

    message = "\n".join(lines).strip()
    print(message)

    send_discord(env, message)


if __name__ == "__main__":
    from tide_utils import run_with_alert

    run_with_alert("scanner_tracker", main)
