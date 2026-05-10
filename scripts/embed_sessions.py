#!/usr/bin/env python3
"""
embed_sessions.py — 为历史 sessions 生成向量并存入 cowork.db
用法：
  python embed_sessions.py           # embed所有≥10条消息的sessions
  python embed_sessions.py --min-msgs 5  # 自定义最小消息数
  python embed_sessions.py --force   # 重新embed已有向量的sessions
"""
import sqlite3
import argparse
import os
import json
import struct
import sys

DB_PATH = "/home/cowork/cowork/cowork.db"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = "/home/cowork/cowork/config/api_keys.env"

MAX_CHARS = 3000  # 每个session截取的最大字符数


def load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def ensure_embeddings_table(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS session_embeddings (
            session_id TEXT PRIMARY KEY,
            embedding BLOB,
            model TEXT,
            created_at TEXT
        )
    """)
    conn.commit()


def get_session_text(conn, session_id, max_chars=MAX_CHARS):
    c = conn.cursor()
    c.execute("""
        SELECT role, content FROM conversations
        WHERE session_id = ?
        ORDER BY rowid
        LIMIT 60
    """, (session_id,))
    rows = c.fetchall()
    parts = []
    total = 0
    for role, content in rows:
        label = "主公" if role == "user" else "Claude"
        line = f"{label}: {content}"
        if total + len(line) > max_chars:
            parts.append(line[:max_chars - total])
            break
        parts.append(line)
        total += len(line)
    return "\n".join(parts)


def vec_to_blob(vec):
    return struct.pack(f"{len(vec)}f", *vec)


def blob_to_vec(blob):
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-msgs", type=int, default=10, help="最小消息数（默认10）")
    parser.add_argument("--force", action="store_true", help="重新embed已有向量的sessions")
    args = parser.parse_args()

    env = load_env()
    api_key = env.get("VOYAGE_API_KEY") or os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        print("❌ 未找到 VOYAGE_API_KEY，请检查 scripts/.env")
        sys.exit(1)

    import voyageai
    vo = voyageai.Client(api_key=api_key)

    conn = sqlite3.connect(DB_PATH)
    ensure_embeddings_table(conn)
    c = conn.cursor()

    # 找出有效sessions
    c.execute("""
        SELECT session_id, COUNT(*) as cnt, MIN(date)
        FROM conversations
        GROUP BY session_id
        HAVING cnt >= ?
        ORDER BY MIN(date) DESC
    """, (args.min_msgs,))
    sessions = c.fetchall()
    print(f"📊 找到 {len(sessions)} 个有效sessions（≥{args.min_msgs}条消息）")

    if not args.force:
        c.execute("SELECT session_id FROM session_embeddings")
        existing = {row[0] for row in c.fetchall()}
        sessions = [(s, cnt, d) for s, cnt, d in sessions if s not in existing]
        print(f"⏭️  跳过已有向量：{len(existing)}个，需处理：{len(sessions)}个")

    if not sessions:
        print("✅ 无需处理")
        conn.close()
        return

    # 批量生成文本
    texts = []
    session_ids = []
    for session_id, cnt, date in sessions:
        text = get_session_text(conn, session_id)
        if text.strip():
            texts.append(text)
            session_ids.append(session_id)

    print(f"🔄 正在生成 {len(texts)} 个embeddings...")

    # Voyage AI 批量embed（每批最多128条）
    all_embeddings = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        result = vo.embed(batch, model="voyage-3-lite", input_type="document")
        all_embeddings.extend(result.embeddings)
        print(f"  ✓ {min(i + batch_size, len(texts))}/{len(texts)}")

    # 写入DB
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    for session_id, embedding in zip(session_ids, all_embeddings):
        blob = vec_to_blob(embedding)
        c.execute("""
            INSERT OR REPLACE INTO session_embeddings (session_id, embedding, model, created_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, blob, "voyage-3-lite", now))

    conn.commit()
    conn.close()
    print(f"\n✅ 完成！{len(all_embeddings)} 个sessions已向量化，存入 cowork.db")


if __name__ == "__main__":
    main()
