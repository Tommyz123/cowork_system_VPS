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

from tide_utils import load_env

DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
DROP_THRESHOLD = -0.07  # -7%

# 评级/分析师动作关键词：归因时优先展示这类新闻（暴跌常由投行集体下调触发）
RATING_KEYWORDS = (
    "downgrade", "upgrade", "price target", "lowers", "raises",
    "cut", "slash", "initiate", "underweight", "overweight", "neutral",
)
# 噪音标题特征：泛市场异动汇总新闻，对单票归因无价值，过滤掉
NOISE_PATTERNS = (
    "stocks moving", "top gainers", "gainers and losers", "session",
    "before the opening bell", "premarket session", "intraday session",
    "moving lower", "moving higher", "gaps during",
)


def get_open_positions():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT symbol, entry_price FROM scanner_picks WHERE status IN ('filled', 'filled_late')"
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


def fetch_attribution(symbol, today, conn):
    """暴跌归因附文（纯查 signals 表，零 token）：抓当天该票新闻，
    评级动作类优先、噪音汇总类过滤，返回拼好的归因文本（无则返回 None）。
    只取客观事实（新闻标题），不做主观推断。"""
    rows = conn.execute(
        "SELECT headline, full_text FROM signals "
        "WHERE symbol=? AND date=? AND signal_type='news'",
        (symbol, today),
    ).fetchall()
    if not rows:
        return None

    rated, others = [], []
    for headline, full_text in rows:
        h = (headline or "").strip()
        if not h:
            continue
        low = h.lower()
        if any(p in low for p in NOISE_PATTERNS):
            continue  # 过滤泛市场异动汇总
        # 评级动作类带上正文细节（含目标价数字），更有信息量
        if any(k in low for k in RATING_KEYWORDS):
            detail = (full_text or "").strip()
            rated.append(f"  • {h}" + (f"\n    └ {detail[:140]}" if detail else ""))
        else:
            others.append(f"  • {h}")

    picks = rated[:5] if rated else others[:3]
    if not picks:
        return None
    head = "📰 当天相关新闻（事实，未含主观判断）："
    return head + "\n" + "\n".join(picks)


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

    conn = sqlite3.connect(DB_PATH)
    for symbol, entry_price in positions:
        day_return, prev_close, today_close = get_day_return(symbol)
        if day_return is None:
            print(f"[price_guard] {symbol}: 无法获取价格，跳过")
            continue
        print(f"[price_guard] {symbol}: 今日涨跌={day_return:.2%} (${prev_close:.2f}→${today_close:.2f})")
        if day_return <= DROP_THRESHOLD:
            block = (
                f"⚠️ **{symbol}** 今日跌幅 **{day_return:.1%}**\n"
                f"  昨收 ${prev_close:.2f} → 今收 ${today_close:.2f}\n"
                f"  买入价 ${entry_price:.2f}，请检查是否有突发利空"
            )
            attribution = fetch_attribution(symbol, today, conn)
            if attribution:
                block += "\n" + attribution
            alerts.append(block)
    conn.close()

    if alerts:
        msg = f"🚨 **TIDE价格守门告警** [{today}]\n\n" + "\n\n".join(alerts)
        send_discord_alert(env, msg)
    else:
        print(f"[price_guard] 所有持仓今日跌幅<7%，正常")


if __name__ == "__main__":
    from tide_utils import run_with_alert
    run_with_alert("price_guard", main)
