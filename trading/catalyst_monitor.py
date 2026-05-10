#!/usr/bin/env python3
import json
import os
import sqlite3
import sys
import urllib.request
from datetime import date

import yfinance as yf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from transcript_fetcher import fetch_sec_10q

DB_PATH = "/home/cowork/cowork/trading/trading.db"
ENV_PATH = "/home/cowork/cowork/config/api_keys.env"


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def send_email(env, subject, body):
    api_key = env.get("BREVO_API_KEY")
    gmail_user = env.get("GMAIL_USER")
    gmail_to = env.get("GMAIL_TO")
    if not api_key or not gmail_user or not gmail_to:
        print(f"[email] 缺少邮件配置，跳过发送")
        return
    payload = json.dumps({
        "sender": {"name": "Cowork VPS", "email": gmail_user},
        "to": [{"email": gmail_to}],
        "subject": subject,
        "textContent": body,
    }).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
        print(f"[email] 已发送：{subject}")
    except Exception as e:
        print(f"[email] 发送失败：{e}")


def fetch_current_price(symbol):
    try:
        info = yf.Ticker(symbol).info or {}
    except Exception:
        return None
    price = info.get("currentPrice")
    if price is None:
        price = info.get("regularMarketPrice")
    try:
        return float(price)
    except (TypeError, ValueError):
        return None


def main():
    env = load_env()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT symbol, catalyst_date, catalyst_note, entry_price
        FROM scanner_picks
        WHERE status='open' AND catalyst_date IS NOT NULL
        """
    ).fetchall()
    conn.close()

    today = date.today()
    alerts = []
    for symbol, catalyst_date, catalyst_note, entry_price in rows:
        try:
            days_until = (date.fromisoformat(catalyst_date) - today).days
        except Exception:
            continue
        if days_until < 0 or days_until > 3:
            continue

        current_price = fetch_current_price(symbol)
        if current_price is None or not entry_price:
            continue

        pct = (current_price - entry_price) / entry_price * 100
        message = (
            f"⏰ {symbol} | {days_until}天后（{catalyst_date}）\n"
            f"{catalyst_note or ''}\n"
            f"当前价：${current_price:.2f} | 建仓价：${entry_price:.2f} | 浮动：{pct:+.1f}%"
        )
        if days_until == 0:
            message += "\n⚡ 今日催化剂到期 — 建议手动检查thesis"
        alerts.append(message)

    if alerts:
        body = "\n\n---\n\n".join(alerts)
        subject = f"⏰ 催化剂提醒 | {today.isoformat()} | {len(alerts)}个"
        send_email(env, subject, body)

    sync_open_positions_10q()


def sync_open_positions_10q():
    """对所有 open 持仓检查 SEC 是否有新 10-Q，缺就抓。失败不影响主流程。"""
    try:
        conn = sqlite3.connect(DB_PATH)
        symbols = [r[0] for r in conn.execute("SELECT DISTINCT symbol FROM scanner_picks WHERE status='open'").fetchall()]
        conn.close()
    except Exception as e:
        print(f"[ERROR] 10-Q 同步：读 open 持仓失败: {e}", flush=True)
        return

    for sym in symbols:
        try:
            result = fetch_sec_10q(sym, skip_if_exists=True)
            if result:
                tag = "cached" if result.get("cached") else "new"
                print(f"[10Q] {sym} {result['filing_date']} ({tag}, {result['size_kb']}KB)", flush=True)
            else:
                print(f"[10Q] {sym} 抓取失败或无 10-Q filing", flush=True)
        except Exception as e:
            print(f"[ERROR] 10-Q 同步 {sym} 异常: {e}", flush=True)


if __name__ == "__main__":
    from tide_utils import run_with_alert
    run_with_alert("catalyst_monitor", main)
