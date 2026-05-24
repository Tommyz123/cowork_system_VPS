#!/usr/bin/env python3
"""
backfill_sessions.py — 从历史JSONL提取会话总结，回填sessions表
用法：python backfill_sessions.py
"""
import sqlite3
import json
import os
import re
from datetime import datetime, timezone

DB_PATH = "/home/cowork/cowork/cowork.db"
JSONL_DIR = os.path.expanduser(
    "~/.claude/projects/-root-cowork/"
)

SUMMARY_PATTERNS = [
    "--- 📋 会话总结 ---",
    "会话总结：",
    "会话总结**",
    "**本次完成：",
    "本次完成：",
]


def extract_text(msg):
    mc = msg.get("message", {}).get("content", "")
    if isinstance(mc, str):
        return mc
    if isinstance(mc, list):
        parts = []
        for b in mc:
            if isinstance(b, dict) and b.get("type") == "text":
                parts.append(b.get("text", ""))
        return "".join(parts)
    return ""


def find_summary(text):
    """找到会话总结段落，返回总结内容（最多300字）"""
    for pattern in SUMMARY_PATTERNS:
        idx = text.find(pattern)
        if idx != -1:
            snippet = text[idx:idx + 400].strip()
            # 清理markdown符号
            snippet = re.sub(r'\*+', '', snippet)
            snippet = re.sub(r'---+', '', snippet)
            snippet = snippet.strip()
            return snippet[:300]
    return None


def get_session_date(jsonl_path):
    """从JSONL文件的最后一条消息获取日期"""
    date_str = None
    try:
        with open(jsonl_path) as f:
            for line in f:
                try:
                    msg = json.loads(line)
                    ts = msg.get("timestamp", "")
                    if ts:
                        date_str = ts[:10]
                except:
                    continue
    except:
        pass
    return date_str


def ensure_sessions_table(conn):
    c = conn.cursor()
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
    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date)")
    conn.commit()


def main():
    conn = sqlite3.connect(DB_PATH)
    ensure_sessions_table(conn)
    c = conn.cursor()

    # 已有记录的session_ids
    c.execute("SELECT session_id FROM sessions WHERE summary IS NOT NULL AND summary != ''")
    existing = {row[0] for row in c.fetchall()}
    print(f"已有摘要的sessions: {len(existing)}个")

    filled = 0
    skipped = 0

    for fname in os.listdir(JSONL_DIR):
        if not fname.endswith(".jsonl"):
            continue
        session_id = fname.replace(".jsonl", "")
        if session_id in existing:
            skipped += 1
            continue

        path = os.path.join(JSONL_DIR, fname)
        date_str = get_session_date(path)
        summary = None

        try:
            with open(path) as f:
                for line in f:
                    try:
                        msg = json.loads(line)
                    except:
                        continue
                    if msg.get("type") != "assistant":
                        continue
                    text = extract_text(msg)
                    if not text:
                        continue
                    found = find_summary(text)
                    if found:
                        summary = found
                        # 继续找更后面的（取最后一次会话总结）
        except Exception as e:
            continue

        if summary and date_str:
            c.execute("""
                INSERT OR IGNORE INTO sessions (session_id, date, summary)
                VALUES (?, ?, ?)
            """, (session_id, date_str, summary))
            filled += 1

    conn.commit()
    conn.close()

    print(f"✅ 回填完成：新增 {filled} 条摘要，跳过 {skipped} 条（已有或无总结）")

    # 验证
    conn2 = sqlite3.connect(DB_PATH)
    c2 = conn2.cursor()
    c2.execute("SELECT COUNT(*) FROM sessions WHERE summary IS NOT NULL AND summary != ''")
    total = c2.fetchone()[0]
    conn2.close()
    print(f"📊 sessions表现有摘要总数：{total} 条")


if __name__ == "__main__":
    main()
