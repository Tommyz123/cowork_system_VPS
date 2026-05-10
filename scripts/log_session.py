#!/usr/bin/env python3
"""
log_session.py — 收工时写入 sessions 表
用法：
  python log_session.py \
    --project-ids "P2,P3" \
    --summary "完成了XXX" \
    --next-steps "下一步XXX" \
    --corrections 1 \
    --files "CLAUDE.md,CURRENT_SESSION.md"
"""
import sqlite3
import argparse
import os
import subprocess
from datetime import datetime, timezone

DB_PATH = "/home/cowork/cowork/cowork.db"
JSONL_DIR = os.path.expanduser(
    "~/.claude/projects/-home-cowork-cowork/"
)
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def ensure_db(conn):
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


def find_current_session_id():
    """找最近修改的 JSONL 文件作为当前 session"""
    files = [
        os.path.join(JSONL_DIR, f)
        for f in os.listdir(JSONL_DIR)
        if f.endswith(".jsonl")
    ]
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    return os.path.basename(latest).replace(".jsonl", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-ids", default="", help="涉及项目，如 P2,P3")
    parser.add_argument("--summary", default="", help="本次完成摘要")
    parser.add_argument("--next-steps", default="", help="下一步")
    parser.add_argument("--corrections", type=int, default=0, help="被纠正次数")
    parser.add_argument("--files", default="", help="修改的核心文件")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    session_id = find_current_session_id()
    if not session_id:
        print("⚠️  无法找到当前 session，跳过写入")
        return

    conn = sqlite3.connect(DB_PATH)
    ensure_db(conn)
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO sessions
            (session_id, date, end_time, project_ids, summary, next_steps, corrections, files_changed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        date_str,
        time_str,
        args.project_ids,
        args.summary,
        args.next_steps,
        args.corrections,
        args.files,
    ))
    conn.commit()
    conn.close()

    print(f"✅ session 已记录：{session_id[:8]}... | {date_str} {time_str} | 项目：{args.project_ids}")

    # 触发增量索引
    index_script = os.path.join(SCRIPTS_DIR, "index_conversations.py")
    if os.path.exists(index_script):
        print("🔄 触发增量索引...")
        subprocess.run(["python3", index_script], check=False)

    # 触发向量embedding（仅对新session）
    embed_script = os.path.join(SCRIPTS_DIR, "embed_sessions.py")
    if os.path.exists(embed_script):
        print("🧠 生成session向量...")
        subprocess.run(["python3", embed_script, "--min-msgs", "10"], check=False)


if __name__ == "__main__":
    main()
