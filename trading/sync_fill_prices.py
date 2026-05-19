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


def fetch_iwm_close(date_str: str):
    """拉指定日期 IWM 收盘价（yfinance）。失败返回 None。"""
    try:
        import yfinance as yf
        from datetime import datetime, timedelta
        d = datetime.strptime(date_str, "%Y-%m-%d")
        h = yf.Ticker("IWM").history(start=date_str, end=(d + timedelta(days=2)).strftime("%Y-%m-%d"))
        if not h.empty:
            return float(h["Close"].iloc[0])
    except Exception as e:
        print(f"  ⚠️ fetch IWM {date_str} 失败: {e}")
    return None


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
            filled_at = order.get("filled_at", "")[:10] if order.get("filled_at") else None
            print(f"[{symbol}] order_id={order_id[:8]} status={status} fill_price={fill_price}")

            if fill_price and status == "filled":
                fill_price = float(fill_price)
                conn.execute(
                    "UPDATE trades SET fill_price = ? WHERE id = ?",
                    (fill_price, trade_id),
                )
                # 2026-05-18 修复：不再覆盖 entry_price（=signal price 保留语义），
                # 只更新 fill_entry_price + fill_date + spy_fill_entry（执行端字段）
                conn.execute(
                    """UPDATE scanner_picks SET
                       fill_entry_price = ?, fill_date = COALESCE(fill_date, ?)
                       WHERE symbol = ? AND status IN ('filled', 'filled_late')
                         AND fill_entry_price IS NULL""",
                    (fill_price, filled_at, symbol),
                )
                # 回填 spy_fill_entry（fill day IWM 价）— 让 weekly_review execution_alpha 无 IWM bias
                if filled_at:
                    iwm_fill = fetch_iwm_close(filled_at)
                    if iwm_fill:
                        conn.execute(
                            """UPDATE scanner_picks SET spy_fill_entry = ?
                               WHERE symbol = ? AND status IN ('filled', 'filled_late')
                                 AND spy_fill_entry IS NULL""",
                            (iwm_fill, symbol),
                        )
                        print(f"  → scanner_picks {symbol} spy_fill_entry={iwm_fill} (IWM {filled_at})")
                conn.execute(
                    "UPDATE outcome_tracking SET tagged_price = ?, last_updated = datetime('now') WHERE symbol = ?",
                    (fill_price, symbol),
                )
                print(f"  → trades id={trade_id} fill_price={fill_price}")
                print(f"  → scanner_picks {symbol} fill_entry_price={fill_price} fill_date={filled_at}")
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
