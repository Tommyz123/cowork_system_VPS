#!/usr/bin/env python3
"""
TIDE系统 - 结果价格快照（工作日 9:00PM EDT 自动跑）
为 outcome_tracking 补齐 30/60/90 天价格与收益率。
"""
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import yfinance as yf

DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
SYSTEM_LOG_PATH = Path("/home/cowork/cowork/trading/system_log.md")


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def get_target_rows(conn):
    return conn.execute(
        """
        SELECT
            id,
            symbol,
            tagged_date,
            tagged_price,
            price_30d,
            price_60d,
            price_90d
        FROM outcome_tracking
        WHERE signal_verdict != 'invalid' OR signal_verdict IS NULL
        """
    ).fetchall()


def get_latest_close(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if hist.empty or "Close" not in hist.columns:
            return None
        close_series = hist["Close"].dropna()
        if close_series.empty:
            return None
        return float(close_series.iloc[-1])
    except Exception:
        return None


def compute_return(price, tagged_price):
    return (price - tagged_price) / tagged_price * 100


def write_system_log(updated, skipped):
    edt = timezone(timedelta(hours=-4))
    now = datetime.now(edt).strftime("%Y-%m-%d %H:%M EDT")
    line = f"[{now}] ✅ price_snapshot: updated={updated} skipped={skipped}\n"
    with SYSTEM_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)
    print(f"[system_log] {line.strip()}")


def process_row(conn, row, today):
    (
        row_id,
        symbol,
        tagged_date,
        tagged_price,
        price_30d,
        price_60d,
        price_90d,
    ) = row

    if not symbol or not tagged_date or tagged_price in (None, 0):
        return False

    try:
        tagged_day = date.fromisoformat(str(tagged_date)[:10])
    except ValueError:
        try:
            tagged_day = datetime.strptime(str(tagged_date)[:10], "%Y-%m-%d").date()
        except ValueError:
            return False

    days_elapsed = (today - tagged_day).days
    targets = []
    if days_elapsed >= 30 and price_30d is None:
        targets.append((30, "price_30d", "return_30d"))
    if days_elapsed >= 60 and price_60d is None:
        targets.append((60, "price_60d", "return_60d"))
    if days_elapsed >= 90 and price_90d is None:
        targets.append((90, "price_90d", "return_90d"))

    if not targets:
        return False

    latest_close = get_latest_close(symbol)
    if latest_close is None:
        return False

    updates = {}
    for _, price_field, return_field in targets:
        updates[price_field] = latest_close
        updates[return_field] = compute_return(latest_close, tagged_price)

    updates["last_updated"] = datetime.now().isoformat(timespec="seconds")
    assignments = ", ".join(f"{field} = ?" for field in updates)
    params = list(updates.values()) + [row_id]
    conn.execute(
        f"UPDATE outcome_tracking SET {assignments} WHERE id = ?",
        params,
    )
    return True


def main():
    conn = get_db_connection()
    try:
        rows = get_target_rows(conn)
        today = date.today()
        updated = 0
        skipped = 0
        earliest_pending = None

        for row in rows:
            modified = process_row(conn, row, today)
            if modified:
                updated += 1
            else:
                skipped += 1
                tagged_date_str = row[2]
                if tagged_date_str:
                    try:
                        td = date.fromisoformat(str(tagged_date_str)[:10])
                        if earliest_pending is None or td < earliest_pending:
                            earliest_pending = td
                    except ValueError:
                        pass

        conn.commit()
        write_system_log(updated, skipped)

        milestone_hint = ""
        if skipped > 0 and earliest_pending is not None:
            milestone_30d = earliest_pending + timedelta(days=30)
            if milestone_30d > today:
                milestone_hint = f" (earliest milestone: {milestone_30d})"
        print(f"[price_snapshot] examined={len(rows)} updated={updated} skipped={skipped}{milestone_hint}")
    finally:
        conn.close()


if __name__ == "__main__":
    from tide_utils import run_with_alert

    run_with_alert("price_snapshot", main)
