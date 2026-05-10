#!/usr/bin/env python3
"""
setup_db.py — 初始化 cowork.db
运行：python setup_db.py
"""
import sqlite3
import os

DB_PATH = "/home/cowork/cowork/cowork.db"

def setup():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # FTS5 全文搜索表（unicode61支持中文）
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS conversations USING fts5(
            session_id,
            date,
            timestamp,
            role,
            content,
            tokenize="unicode61"
        )
    """)

    # 结构化会话表（收工时写入）
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            date TEXT,
            end_time TEXT,
            project_ids TEXT,
            summary TEXT,
            next_steps TEXT,
            corrections INTEGER DEFAULT 0,
            files_changed TEXT
        )
    """)

    # date 索引（加速日期过滤查询）
    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date)")

    # 增量追踪表
    c.execute("""
        CREATE TABLE IF NOT EXISTS indexed_sessions (
            filename TEXT PRIMARY KEY,
            indexed_at TEXT,
            message_count INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print(f"✅ cowork.db 初始化完成：{DB_PATH}")

if __name__ == "__main__":
    setup()
