#!/usr/bin/env python3
"""
TIDE系统 - 每日价格守门人（每天4:30PM EDT收盘后自动跑）
检查所有open持仓的当日跌幅，跌≥7%立即发Discord告警。
与thesis_monitor解耦：只看价格，不判断叙事。
"""
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import yfinance as yf

ENV_PATH = Path("/home/cowork/cowork/config/api_keys.env")
DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
DROP_THRESHOLD = -0.07  # -7%


def load_env():
    env = {}
    with ENV_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def get_open_positions():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT symbol, entry_price FROM scanner_picks WHERE status='open'"
    ).fetchall()
    conn.close()
    return rows


def get_day_return(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if len(hist) < 2:
            return None, None, None
        prev_close = hist["Close"].iloc[-2]
        today_close = hist["Close"].iloc[-1]
        day_return = (today_close - prev_close) / prev_close
        return day_return, prev_close, today_close
    except Exception:
        return None, None, None


def send_discord_alert(env, message):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        print("[discord] 缺少配置，跳过")
        return
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, json={"content": message}, timeout=10)
        r.raise_for_status()
        print(f"[discord] 告警已发送")
    except Exception as e:
        print(f"[discord] 发送失败：{e}")


def main():
    env = load_env()
    positions = get_open_positions()
    if not positions:
        print("[price_guard] 无open持仓，跳过")
        return

    edt = timezone(timedelta(hours=-4))
    today = datetime.now(edt).strftime("%Y-%m-%d")
    alerts = []

    for symbol, entry_price in positions:
        day_return, prev_close, today_close = get_day_return(symbol)
        if day_return is None:
            print(f"[price_guard] {symbol}: 无法获取价格，跳过")
            continue
        print(f"[price_guard] {symbol}: 今日涨跌={day_return:.2%} (${prev_close:.2f}→${today_close:.2f})")
        if day_return <= DROP_THRESHOLD:
            alerts.append(
                f"⚠️ **{symbol}** 今日跌幅 **{day_return:.1%}**\n"
                f"  昨收 ${prev_close:.2f} → 今收 ${today_close:.2f}\n"
                f"  买入价 ${entry_price:.2f}，请检查是否有突发利空"
            )

    if alerts:
        msg = f"🚨 **TIDE价格守门告警** [{today}]\n\n" + "\n\n".join(alerts)
        send_discord_alert(env, msg)
    else:
        print(f"[price_guard] 所有持仓今日跌幅<7%，正常")


if __name__ == "__main__":
    from tide_utils import run_with_alert
    run_with_alert("price_guard", main)
