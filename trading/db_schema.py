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
    "theme": "TEXT",
    "secondary_themes": "TEXT",
    "bear_thesis": "TEXT",
    "hidden_risk": "TEXT",
    "verdict": "TEXT DEFAULT 'tentative'",
    "mistake_type": "TEXT",
    "real_reason": "TEXT",
    # 玄学分隔离观察列(只记录, 不参与任何选股/下单决策)
    "meihua_score": "INTEGER",
    "meihua_hexagram": "TEXT",
    "meihua_relation": "TEXT",
    "meihua_random": "INTEGER",
    "listing_date": "TEXT",
    # 2026-06-10 C项扩展：6 分项分数入库（此前只存总分，无法分析哪个维度真能预测收益）
    "score_narrative": "INTEGER",
    "score_market_lag": "INTEGER",
    "score_tailwind": "INTEGER",
    "score_catalyst": "INTEGER",
    "score_tradability": "INTEGER",
    "score_disconfirmation": "INTEGER",
    # 2026-06-10 C项扩展：硬数据记录（LLM 打 market_lag/tradability 时没喂这些数据，
    # 先记录不改打分；也是假设2"低分析师覆盖=真edge"年底验证的必需数据）
    "analyst_count": "INTEGER",
    "avg_dollar_volume": "REAL",
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
