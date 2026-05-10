#!/usr/bin/env python3
"""
index_conversations.py — 解析 JSONL 对话历史 → 写入 FTS5
用法：
  python index_conversations.py              # 增量（默认）
  python index_conversations.py --rebuild    # 全量重建
"""
import json
import os
import sqlite3
import argparse
from datetime import datetime, timezone

# ── CONFIG ──────────────────────────────────────────────
JSONL_DIR = os.path.expanduser(
    "~/.claude/projects/-root-cowork/"
)
DB_PATH = "/home/cowork/cowork/cowork.db"
# ────────────────────────────────────────────────────────

SKIP_CONTENT_TYPES = {"thinking", "tool_use", "tool_result"}


def ensure_db(conn):
    c = conn.cursor()
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS conversations USING fts5(
            session_id, date, timestamp, role, content,
            tokenize="unicode61"
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS indexed_sessions (
            filename TEXT PRIMARY KEY,
            indexed_at TEXT,
            message_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()


def extract_text(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "").strip()
                if text:
                    parts.append(text)
        return "\n".join(parts)
    return ""


def index_file(conn, filepath, session_id):
    c = conn.cursor()
    count = 0
    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type")
            if entry_type not in ("user", "assistant"):
                continue
            if entry.get("isSidechain"):
                continue
            if entry.get("isMeta"):
                continue

            msg = entry.get("message", {})
            role = msg.get("role", entry_type)
            content_raw = msg.get("content", "")
            content = extract_text(content_raw)

            if not content:
                continue

            ts_raw = entry.get("timestamp", "")
            date = ts_raw[:10] if ts_raw else ""

            rows.append((session_id, date, ts_raw, role, content))
            count += 1

    if rows:
        c.executemany(
            "INSERT INTO conversations(session_id, date, timestamp, role, content) VALUES (?,?,?,?,?)",
            rows
        )

    now = datetime.now(timezone.utc).isoformat()
    c.execute(
        "INSERT OR REPLACE INTO indexed_sessions(filename, indexed_at, message_count) VALUES (?,?,?)",
        (os.path.basename(filepath), now, count)
    )
    conn.commit()
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="清空重建索引")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    ensure_db(conn)

    if args.rebuild:
        c = conn.cursor()
        c.execute("DELETE FROM conversations")
        c.execute("DELETE FROM indexed_sessions")
        conn.commit()
        print("🔄 已清空，开始全量重建...")

    # 查已处理文件及其消息数
    c = conn.cursor()
    c.execute("SELECT filename, message_count FROM indexed_sessions")
    already_indexed = {row[0]: row[1] for row in c.fetchall()}

    jsonl_files = sorted(
        [f for f in os.listdir(JSONL_DIR) if f.endswith(".jsonl")]
    )

    def count_messages_in_file(filepath):
        count = 0
        try:
            with open(filepath, encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("type") in ("user", "assistant"):
                            count += 1
                    except:
                        pass
        except:
            pass
        return count

    # 新文件 + 已索引但消息数增加的文件（同一session继续对话）
    files_to_index = []
    for f in jsonl_files:
        if f not in already_indexed:
            files_to_index.append(f)
        else:
            filepath = os.path.join(JSONL_DIR, f)
            current_count = count_messages_in_file(filepath)
            if current_count > already_indexed[f]:
                files_to_index.append(f)

    if not files_to_index:
        print("✅ 无新内容需要索引")
        conn.close()
        return

    # 对需要重新索引的文件，先删除旧记录
    for filename in files_to_index:
        if filename in already_indexed:
            session_id = filename.replace(".jsonl", "")
            c.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            c.execute("DELETE FROM indexed_sessions WHERE filename = ?", (filename,))
    conn.commit()

    total = 0
    for i, filename in enumerate(files_to_index, 1):
        filepath = os.path.join(JSONL_DIR, filename)
        session_id = filename.replace(".jsonl", "")
        try:
            count = index_file(conn, filepath, session_id)
            total += count
            print(f"[{i}/{len(files_to_index)}] {filename[:8]}... → {count} 条消息")
        except Exception as e:
            print(f"[{i}/{len(files_to_index)}] ⚠️ {filename[:8]}... 跳过（{e}）")

    conn.close()
    print(f"\n✅ 完成：{len(files_to_index)} 个文件，共 {total} 条消息写入索引")


if __name__ == "__main__":
    main()
