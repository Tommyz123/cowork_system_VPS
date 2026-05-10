#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB_PATH = Path("/home/cowork/cowork/trading/trading.db")

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS outcome_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    tagged_date TEXT NOT NULL,
    scanner_pick_id INTEGER,
    tagged_price REAL,
    price_30d REAL,
    price_60d REAL,
    price_90d REAL,
    return_30d REAL,
    return_60d REAL,
    return_90d REAL,
    signal_verdict TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    last_updated TEXT DEFAULT (datetime('now')),
    UNIQUE(symbol, tagged_date)
);
"""


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(CREATE_SQL)
        conn.commit()
        print("outcome_tracking migration applied")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
