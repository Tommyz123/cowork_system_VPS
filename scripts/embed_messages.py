#!/usr/bin/env python3
"""
embed_messages.py — 为历史对话消息生成向量并存入 cowork.db
用法：
  python embed_messages.py           # embed所有未处理的有效消息
  python embed_messages.py --force   # 重新embed所有消息
"""
import sqlite3
import argparse
import os
import struct
import sys

DB_PATH = "/home/cowork/cowork/cowork.db"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPTS_DIR, ".env")
API_KEYS_PATH = "/home/cowork/cowork/config/api_keys.env"

MIN_LENGTH = 20  # 过滤过短消息
MAX_LENGTH = 2000  # 截断过长消息


def load_env():
    env = {}
    for path in [ENV_PATH, API_KEYS_PATH]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        if k.strip() not in env:
                            env[k.strip()] = v.strip()
    return env


def vec_to_blob(vec):
    return struct.pack(f"{len(vec)}f", *vec)


SKIP_PREFIXES = (
    "<", "[Request interrupted", "This session is being continued",
    "<task-notification", "<command-name", "---", "```",
    "API Error:", "Please run /login",
    "你是每日新闻助手", "你是每日新闻精华日报",
    "Read and follow instructions in",
    "**步骤8：写入 cowork.db**",
    "开始执行收工流程。", "收工开始，按",
)

SKIP_EXACT = {
    "好的主公，正在退出，3秒后自动重启...",
    "No response requested.",
    "You've hit your limit · resets 4pm (America/New_York)",
    "✅ 进度已保存（P9）  **步骤2：记忆处理**",
}

SKIP_KEYWORDS = (
    "tool_use", "tool_result", "<function_calls>",
)


def is_valid_message(role, content):
    if not content or len(content.strip()) < MIN_LENGTH:
        return False
    content = content.strip()
    if content in SKIP_EXACT:
        return False
    for p in SKIP_PREFIXES:
        if content.startswith(p):
            return False
    for kw in SKIP_KEYWORDS:
        if kw in content:
            return False
    return True


def ensure_table(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS message_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            message_rowid INTEGER UNIQUE,
            role TEXT,
            date TEXT,
            content_preview TEXT,
            embedding BLOB,
            model TEXT,
            created_at TEXT
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_me_session ON message_embeddings(session_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_me_date ON message_embeddings(date)")
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="重新embed所有消息")
    args = parser.parse_args()

    env = load_env()
    api_key = env.get("VOYAGE_API_KEY") or os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        print("❌ 未找到 VOYAGE_API_KEY，请检查 scripts/.env")
        sys.exit(1)

    import voyageai
    vo = voyageai.Client(api_key=api_key)

    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)
    c = conn.cursor()

    if args.force:
        c.execute("DELETE FROM message_embeddings")
        conn.commit()
        print("🗑️  已清空旧向量，重新处理")

    # 获取已处理的rowid 和 已有的content（用于去重）
    c.execute("SELECT message_rowid FROM message_embeddings")
    existing = {row[0] for row in c.fetchall()}
    c.execute("SELECT content_preview FROM message_embeddings")
    existing_content = {row[0] for row in c.fetchall()}

    # 读取所有消息
    c.execute("""
        SELECT rowid, session_id, date, role, content
        FROM conversations
        ORDER BY date, rowid
    """)
    all_msgs = c.fetchall()

    # 过滤有效消息
    to_embed = []
    for rowid, session_id, date, role, content in all_msgs:
        if rowid in existing:
            continue
        if role not in ("user", "assistant"):
            continue
        if not is_valid_message(role, content):
            continue
        preview = content[:100].replace("\n", " ")
        if preview in existing_content:
            continue  # 内容已存在，跳过（去重）
        existing_content.add(preview)
        to_embed.append((rowid, session_id, date, role, content[:MAX_LENGTH]))

    print(f"📊 总消息：{len(all_msgs)}条，需处理：{len(to_embed)}条")

    if not to_embed:
        print("✅ 无需处理")
        conn.close()
        return

    texts = [item[4] for item in to_embed]

    print(f"🔄 正在生成 {len(texts)} 个embeddings...")

    import time
    all_embeddings = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            result = vo.embed(batch, model="voyage-3-lite", input_type="document")
            all_embeddings.extend(result.embeddings)
            print(f"  ✓ {min(i + batch_size, len(texts))}/{len(texts)}")
            if i + batch_size < len(texts):
                time.sleep(0.5)  # 避免速率限制
        except Exception as e:
            print(f"  ❌ 批次 {i} 失败：{e}")
            break

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    for (rowid, session_id, date, role, content), embedding in zip(to_embed, all_embeddings):
        blob = vec_to_blob(embedding)
        preview = content[:100].replace("\n", " ")
        c.execute("""
            INSERT OR REPLACE INTO message_embeddings
            (session_id, message_rowid, role, date, content_preview, embedding, model, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, rowid, role, date, preview, blob, "voyage-3-lite", now))

    conn.commit()
    conn.close()
    print(f"\n✅ 完成！{len(all_embeddings)} 条消息已向量化，存入 message_embeddings 表")


if __name__ == "__main__":
    main()
