#!/usr/bin/env python3
"""
扫描 open 候选股当天 SEC 8-K，发现高价值信号后立即发 Email 告警。
"""
import argparse
import json
import sqlite3
import time
import urllib.request
from datetime import date, datetime
from pathlib import Path

import requests

DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
ENV_PATH = Path("/home/cowork/cowork/config/api_keys.env")
SEC_URL = "https://efts.sec.gov/LATEST/search-index"

ITEM_MEANINGS = {
    "8.01": "其他重大事件",
    "1.01": "新合同/协议签署",
    "1.02": "重要协议终止",
    "7.01": "公司主动新闻稿",
    "5.02": "高管变动",
}

GRADE_RULES = {
    "HIGH": {"8.01", "1.01"},
    "MEDIUM": {"7.01", "5.02", "1.02"},
    "LOW": {"2.02", "9.01"},
}


def load_env():
    env = {}
    with ENV_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
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


def load_open_symbols():
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT DISTINCT symbol FROM scanner_picks WHERE status IN ('filled', 'filled_late') AND symbol IS NOT NULL AND symbol != '' ORDER BY symbol"
        ).fetchall()
        return [row[0].strip().upper() for row in rows if row and row[0]]
    finally:
        conn.close()


def coerce_text(value):
    if isinstance(value, list):
        return ", ".join(str(v).strip() for v in value if str(v).strip())
    return str(value or "").strip()


def coerce_items(value):
    if isinstance(value, list):
        raw_items = [str(v).strip() for v in value if str(v).strip()]
    else:
        raw = str(value or "").replace(";", ",")
        raw_items = [part.strip() for part in raw.split(",") if part.strip()]
    items = []
    seen = set()
    for item in raw_items:
        if item not in seen:
            items.append(item)
            seen.add(item)
    return items


def filing_matches_symbol(symbol, filing):
    display_names = coerce_text(
        filing.get("display_names") or filing.get("display_name") or filing.get("displayNames")
    ).upper()
    return f"({symbol})" in display_names or symbol in display_names


def classify_items(items):
    if any(item in GRADE_RULES["HIGH"] for item in items):
        grade = "HIGH"
    elif any(item in GRADE_RULES["MEDIUM"] for item in items):
        grade = "MEDIUM"
    elif any(item in GRADE_RULES["LOW"] for item in items):
        grade = "LOW"
    else:
        grade = "LOW"
    matched_items = [
        item for item in items if item in GRADE_RULES["HIGH"] or item in GRADE_RULES["MEDIUM"] or item in GRADE_RULES["LOW"]
    ]
    return grade, matched_items


def fetch_symbol_filings(symbol, target_day):
    params = {
        "q": symbol,
        "forms": "8-K",
        "dateRange": "custom",
        "startdt": target_day.isoformat(),
        "enddt": target_day.isoformat(),
    }
    headers = {
        "User-Agent": "cowork-signal-collector/1.0 (local automation)",
        "Accept": "application/json",
    }
    try:
        response = requests.get(SEC_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return []

    raw_hits = payload.get("hits", {})
    if isinstance(raw_hits, dict):
        raw_hits = raw_hits.get("hits", [])
    if not isinstance(raw_hits, list):
        return []

    filings = []
    for hit in raw_hits:
        filing = hit.get("_source", hit) if isinstance(hit, dict) else {}
        if not isinstance(filing, dict):
            continue
        if not filing_matches_symbol(symbol, filing):
            continue
        items = coerce_items(filing.get("items") or filing.get("item") or filing.get("document_items"))
        if not items:
            continue
        grade, matched_items = classify_items(items)
        if grade == "LOW":
            continue
        filings.append(
            {
                "symbol": symbol,
                "date": coerce_text(filing.get("file_date") or filing.get("filedAt") or filing.get("date"))[:10]
                or target_day.isoformat(),
                "grade": grade,
                "items": matched_items or items,
            }
        )
    return filings


def build_alert_message(symbol, filing_date, grade, items):
    item_text = ", ".join(items)
    meanings = "；".join(f"{item}: {ITEM_MEANINGS.get(item, '未定义')}" for item in items)
    return (
        f"📡 **8-K信号告警** | {symbol} | {filing_date}\n"
        f"类型：{grade}（{item_text}）\n"
        f"含义：{meanings}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Scan daily SEC 8-K filings for open picks.")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="扫描日期，格式 YYYY-MM-DD，默认今天。",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    target_day = datetime.strptime(args.date, "%Y-%m-%d").date()
    env = load_env()
    symbols = load_open_symbols()

    alerts = []
    for symbol in symbols:
        filings = fetch_symbol_filings(symbol, target_day)
        for filing in filings:
            alerts.append(build_alert_message(
                filing["symbol"],
                filing["date"],
                filing["grade"],
                filing["items"],
            ))
        time.sleep(0.3)

    if alerts:
        body = "\n\n---\n\n".join(alerts)
        subject = f"📡 8-K信号日报 | {target_day.isoformat()} | {len(alerts)}条告警"
        send_email(env, subject, body)

    print(f"扫描完成，共扫描 {len(symbols)} 个ticker，{len(alerts)}条告警")


if __name__ == "__main__":
    from tide_utils import run_with_alert
    run_with_alert("signal_alert", main)
