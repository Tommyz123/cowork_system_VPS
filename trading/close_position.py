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
from config import BENCHMARK_SYMBOL

DB_PATH = "/home/cowork/cowork/trading/trading.db"
ENV_PATH = "/home/cowork/cowork/config/api_keys.env"
DISCORD_API_BASE = "https://discord.com/api/v10"

EXIT_REASON_OPTIONS = {
    "1": "thesis_invalidated",
    "2": "stop_loss",
    "3": "target_hit",
    "4": "theme_rotation",
    "5": "manual",
}


def usage():
    print("用法：python3 close_position.py SYMBOL [swing|intraday]（默认swing）")


def load_env():
    env = {}
    with open(ENV_PATH) as f:
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


def alpaca_headers(env, account="swing"):
    if account == "swing":
        key = env.get("ALPACA_SWING_KEY", "")
        secret = env.get("ALPACA_SWING_SECRET", "")
    else:
        key = env.get("ALPACA_API_KEY", "")
        secret = env.get("ALPACA_SECRET_KEY", "")
    return {
        "APCA-API-KEY-ID": key,
        "APCA-API-SECRET-KEY": secret,
        "Content-Type": "application/json",
    }


def alpaca_base_url(env, account="swing"):
    if account == "swing":
        base_url = env.get("ALPACA_SWING_ENDPOINT", "https://paper-api.alpaca.markets/v2")
    else:
        base_url = (
            env.get("ALPACA_BASE_URL")
            or env.get("ALPACA_ENDPOINT")
            or "https://paper-api.alpaca.markets/v2"
        )
    base_url = base_url.rstrip("/")
    if base_url.endswith("/v2"):
        base_url = base_url[:-3]
    return base_url


def fetch_alpaca_qty(env, symbol, account="swing"):
    req = urllib.request.Request(
        f"{alpaca_base_url(env, account)}/v2/positions/{symbol}",
        headers=alpaca_headers(env, account),
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    qty = payload.get("qty")
    if qty is None:
        raise RuntimeError(f"Alpaca 持仓里没有 {symbol} 的 qty")
    return str(qty)


def submit_alpaca_sell_order(env, symbol, account="swing"):
    qty = fetch_alpaca_qty(env, symbol, account)
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
        f"{alpaca_base_url(env, account)}/v2/orders",
        data=body,
        headers=alpaca_headers(env, account),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    if len(sys.argv) < 2:
        usage()
        return

    symbol = sys.argv[1].strip().upper()
    account = sys.argv[2].strip() if len(sys.argv) > 2 else "swing"
    if account not in ("swing", "intraday"):
        print(f"无效账号: {account}，使用 'swing' 或 'intraday'")
        return
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
            post_exit_peak = ?
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
            row["id"],
        ),
    )
    conn.commit()
    conn.close()

    env = load_env()
    try:
        submit_alpaca_sell_order(env, symbol, account)
        print(f"Alpaca 市价卖单已提交: {symbol} ({account})")
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
