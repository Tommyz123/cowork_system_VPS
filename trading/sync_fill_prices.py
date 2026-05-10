#!/usr/bin/env python3
"""
开盘后价格同步工具。
查询 Alpaca swing 账号已成交订单，把 fill_price 写回 trades 表和 scanner_picks.entry_price。
用法：python3 sync_fill_prices.py
"""
import json
import os
import sqlite3
import urllib.request
from pathlib import Path

DB_PATH = "/home/cowork/cowork/trading/trading.db"
ENV_PATH = "/home/cowork/cowork/config/api_keys.env"


def load_env():
    env = {}
    for line in Path(ENV_PATH).read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def alpaca_get(env, path):
    endpoint = env.get("ALPACA_SWING_ENDPOINT", "https://paper-api.alpaca.markets/v2").rstrip("/v2").rstrip("/")
    url = f"{endpoint}/v2{path}"
    headers = {
        "APCA-API-KEY-ID": env.get("ALPACA_SWING_KEY", ""),
        "APCA-API-SECRET-KEY": env.get("ALPACA_SWING_SECRET", ""),
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main():
    env = load_env()
    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute(
        "SELECT id, symbol, order_id FROM trades WHERE fill_price IS NULL AND status = 'open'"
    ).fetchall()

    if not rows:
        print("没有需要同步的记录。")
        conn.close()
        return

    for trade_id, symbol, order_id in rows:
        if not order_id:
            print(f"[{symbol}] 无 order_id，跳过")
            continue
        try:
            order = alpaca_get(env, f"/orders/{order_id}")
            fill_price = order.get("filled_avg_price")
            status = order.get("status")
            print(f"[{symbol}] order_id={order_id[:8]} status={status} fill_price={fill_price}")

            if fill_price and status == "filled":
                fill_price = float(fill_price)
                conn.execute(
                    "UPDATE trades SET fill_price = ? WHERE id = ?",
                    (fill_price, trade_id),
                )
                conn.execute(
                    "UPDATE scanner_picks SET entry_price = ? WHERE symbol = ? AND status = 'open'",
                    (fill_price, symbol),
                )
                conn.execute(
                    "UPDATE outcome_tracking SET tagged_price = ?, last_updated = datetime('now') WHERE symbol = ?",
                    (fill_price, symbol),
                )
                print(f"  → trades id={trade_id} fill_price={fill_price}")
                print(f"  → scanner_picks {symbol} entry_price={fill_price}")
                print(f"  → outcome_tracking {symbol} tagged_price={fill_price}")
            else:
                print(f"  → 尚未成交，跳过")
        except Exception as e:
            print(f"[{symbol}] 查询失败: {e}")

    conn.commit()
    conn.close()
    print("\n同步完成。")


if __name__ == "__main__":
    main()
