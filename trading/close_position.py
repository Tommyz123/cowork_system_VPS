#!/usr/bin/env python3
"""
交互式平仓工具。
用法：python3 close_position.py SYMBOL
"""
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime

import requests
import yfinance as yf

from db_schema import ensure_scanner_picks_schema
from config import BENCHMARK_SYMBOL, P9_ACCOUNT, assert_p9_account
from tide_utils import load_env

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"

EXIT_REASON_OPTIONS = {
    "1": "thesis_invalidated",
    "2": "stop_loss",
    "3": "target_hit",
    "4": "theme_rotation",
    "5": "manual",
}

VERDICT_OPTIONS = {
    "1": "success",
    "2": "partial",
    "3": "failure",
    "4": "tentative",
}

MISTAKE_TYPE_OPTIONS = {
    "1": "timing",
    "2": "narrative",
    "3": "valuation",
    "4": "liquidity",
    "5": "catalyst",
    "6": "macro",
    "7": "thesis",
}


def usage():
    print(f"用法：python3 close_position.py SYMBOL  (P9 账号锁死在 '{P9_ACCOUNT}'，不再接受账号参数)")


def fetch_price(symbol):
    try:
        hist = yf.Ticker(symbol).history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return None


def prompt_exit_reason():
    print("请选择 exit_reason：")
    print("1) thesis_invalidated")
    print("2) stop_loss")
    print("3) target_hit")
    print("4) theme_rotation")
    print("5) manual")
    while True:
        choice = input("输入编号: ").strip()
        reason = EXIT_REASON_OPTIONS.get(choice)
        if reason:
            return reason
        print("无效选择，请重新输入。")


def prompt_verdict():
    print("\n请选择 verdict（attribution 用）：")
    print("1) success    — thesis 成立 + alpha > 0")
    print("2) partial    — thesis 部分成立")
    print("3) failure    — thesis 失败 / alpha < 0")
    print("4) tentative  — 样本不足，暂不下结论（30 单已退出之前推荐用这个）")
    while True:
        choice = input("输入编号: ").strip()
        verdict = VERDICT_OPTIONS.get(choice)
        if verdict:
            return verdict
        print("无效选择，请重新输入。")


def prompt_mistake_type():
    print("\n请选择 mistake_type（7 选 1）：")
    print("1) timing     — thesis 对，但太早")
    print("2) narrative  — 市场根本不 care")
    print("3) valuation  — 已 fully priced in")
    print("4) liquidity  — 小盘无人接盘")
    print("5) catalyst   — 催化剂未发生")
    print("6) macro      — 市场环境突变")
    print("7) thesis     — thesis 本身错误")
    while True:
        choice = input("输入编号: ").strip()
        mt = MISTAKE_TYPE_OPTIONS.get(choice)
        if mt:
            return mt
        print("无效选择，请重新输入。")


def send_discord(env, message):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        return
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


def alpaca_headers(env):
    """P9 账号锁死 swing，不再接受 account 参数。"""
    return {
        "APCA-API-KEY-ID": env.get("ALPACA_SWING_KEY", ""),
        "APCA-API-SECRET-KEY": env.get("ALPACA_SWING_SECRET", ""),
        "Content-Type": "application/json",
    }


def alpaca_base_url(env):
    """P9 账号锁死 swing，不再接受 account 参数。"""
    base_url = env.get("ALPACA_SWING_ENDPOINT", "https://paper-api.alpaca.markets/v2")
    base_url = base_url.rstrip("/")
    if base_url.endswith("/v2"):
        base_url = base_url[:-3]
    return base_url


def fetch_alpaca_qty(env, symbol):
    req = urllib.request.Request(
        f"{alpaca_base_url(env)}/v2/positions/{symbol}",
        headers=alpaca_headers(env),
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    qty = payload.get("qty")
    if qty is None:
        raise RuntimeError(f"Alpaca 持仓里没有 {symbol} 的 qty")
    return str(qty)


def submit_alpaca_sell_order(env, symbol):
    """P9 卖单。账号锁死在 P9_ACCOUNT (swing)，不接受 account 参数。"""
    assert_p9_account(P9_ACCOUNT)  # 显式断言，防止常量被意外修改
    qty = fetch_alpaca_qty(env, symbol)
    body = json.dumps(
        {
            "symbol": symbol,
            "qty": qty,
            "side": "sell",
            "type": "market",
            "time_in_force": "day",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{alpaca_base_url(env)}/v2/orders",
        data=body,
        headers=alpaca_headers(env),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    if len(sys.argv) < 2:
        usage()
        return
    if len(sys.argv) > 2:
        print(f"⚠️ 已忽略额外参数 '{sys.argv[2]}' — P9 账号锁死在 '{P9_ACCOUNT}'（2026-05-18 锁定）")

    symbol = sys.argv[1].strip().upper()
    if not symbol:
        usage()
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_scanner_picks_schema(conn)

    row = conn.execute(
        """
        SELECT *
        FROM scanner_picks
        WHERE status = 'open' AND symbol = ?
        ORDER BY scan_date DESC, id DESC
        LIMIT 1
        """,
        (symbol,),
    ).fetchone()

    if not row:
        conn.close()
        print(f"未找到 {symbol} 的 open 持仓")
        usage()
        return

    close_price = fetch_price(symbol)
    spy_exit = fetch_price(BENCHMARK_SYMBOL)
    sector_etf = row["sector_etf"]
    sector_etf_exit = fetch_price(sector_etf) if sector_etf else None

    if close_price is None:
        conn.close()
        print(f"无法获取 {symbol} 当前价格")
        return

    exit_reason = prompt_exit_reason()
    exit_thesis_note = input("请输入 exit_thesis_note（可回车跳过）: ").strip()

    verdict = prompt_verdict()
    mistake_type = None
    if verdict in ("failure", "partial"):
        mistake_type = prompt_mistake_type()
    real_reason = input("\n请输入 real_reason（最终真实原因，与 thesis 可能不同，可回车跳过）: ").strip()

    return_pct = None
    if row["entry_price"]:
        return_pct = (close_price - row["entry_price"]) / row["entry_price"]

    exit_date = datetime.now().strftime("%Y-%m-%d")
    post_exit_prices = json.dumps([{"date": exit_date, "price": close_price}], ensure_ascii=False)

    conn.execute(
        """
        UPDATE scanner_picks
        SET exit_price = ?,
            return_pct = ?,
            spy_exit = ?,
            sector_etf_exit = ?,
            exit_reason = ?,
            exit_thesis_note = ?,
            status = 'closed_watching',
            post_exit_prices = ?,
            post_exit_peak = ?,
            verdict = ?,
            mistake_type = ?,
            real_reason = ?
        WHERE id = ?
        """,
        (
            close_price,
            return_pct,
            spy_exit,
            sector_etf_exit,
            exit_reason,
            exit_thesis_note or None,
            post_exit_prices,
            close_price,
            verdict,
            mistake_type,
            real_reason or None,
            row["id"],
        ),
    )
    conn.commit()
    conn.close()

    env = load_env()
    try:
        submit_alpaca_sell_order(env, symbol)
        print(f"Alpaca 市价卖单已提交: {symbol} ({P9_ACCOUNT})")
    except urllib.error.HTTPError as e:
        print(f"Alpaca 卖单失败 {symbol}: HTTP {e.code}")
    except Exception as e:
        print(f"Alpaca 卖单失败 {symbol}: {e}")

    ret_pct_text = "N/A" if return_pct is None else f"{return_pct * 100:+.2f}%"
    message = f"✅ 平仓 {symbol} @ {close_price:.2f} | 收益 {ret_pct_text} | 原因：{exit_reason} | 进入 closed_watching 追踪"
    print(message)
    send_discord(env, message)


if __name__ == "__main__":
    from tide_utils import run_with_alert

    run_with_alert("close_position", main)
