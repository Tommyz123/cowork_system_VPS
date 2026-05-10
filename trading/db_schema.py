#!/usr/bin/env python3
"""
TIDE系统 - trading.db schema helper。

scanner_picks.status 当前约定：
- open: 持仓中
- closed: 已平仓
- closed_watching: 已平仓，但继续观察平仓后走势
- archived: 平仓后观察期结束，归档
"""
import sqlite3


SCANNER_PICKS_EXTRA_COLUMNS = {
    "spy_entry": "REAL",
    "sector_etf": "TEXT",
    "sector_etf_entry": "REAL",
    "exit_reason": "TEXT",
    "exit_thesis_note": "TEXT",
    "spy_exit": "REAL",
    "sector_etf_exit": "REAL",
    "max_drawdown_pct": "REAL",
    "post_exit_prices": "TEXT",
    "post_exit_peak": "REAL",
    "post_exit_3m_return": "REAL",
}


def get_columns(conn, table_name):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}


def ensure_columns(conn, table_name, columns):
    existing = get_columns(conn, table_name)
    changed = False
    for name, column_type in columns.items():
        if name in existing:
            continue
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {name} {column_type}")
        changed = True
    if changed:
        conn.commit()


def ensure_scanner_picks_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scanner_picks (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            entry_price REAL,
            scan_date TEXT,
            score INTEGER,
            old_label TEXT,
            new_signal TEXT,
            invalidation TEXT,
            explosion_catalyst TEXT,
            exit_price REAL,
            return_pct REAL,
            status TEXT DEFAULT 'open'
        )
        """
    )
    ensure_columns(
        conn,
        "scanner_picks",
        {
            "catalyst_date": "TEXT",
            "catalyst_note": "TEXT",
            **SCANNER_PICKS_EXTRA_COLUMNS,
        },
    )


def ensure_thesis_alerts_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS thesis_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            alert_date TEXT,
            thesis_status TEXT,
            headline_summary TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()


def migrate_db(db_path):
    conn = sqlite3.connect(db_path)
    try:
        ensure_scanner_picks_schema(conn)
        ensure_thesis_alerts_table(conn)
    finally:
        conn.close()
