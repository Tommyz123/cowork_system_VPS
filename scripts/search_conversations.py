#!/usr/bin/env python3
"""
search_conversations.py — 搜索历史对话（混合搜索：FTS5关键词 + 向量语义）
用法：
  python search_conversations.py "关键词"
  python search_conversations.py "关键词" --project P3
  python search_conversations.py "关键词" --date 2026-04
  python search_conversations.py "关键词" --limit 30
  python search_conversations.py "关键词" --mode keyword   # 仅关键词
  python search_conversations.py "关键词" --mode semantic  # 仅语义
  python search_conversations.py "关键词" --mode hybrid    # 混合（默认）
"""
import sqlite3
import argparse
import os
import re
import struct
import sys

DB_PATH = "/home/cowork/cowork/cowork.db"
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPTS_DIR, ".env")
API_KEYS_PATH = "/home/cowork/cowork/config/api_keys.env"


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


def blob_to_vec(blob):
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


def cosine_similarity(a, b):
    import math
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def keyword_search(conn, query, project=None, date=None, limit=20):
    c = conn.cursor()
    sql = """
        SELECT
            c.session_id,
            c.date,
            c.role,
            snippet(conversations, 4, '【', '】', '...', 20) AS snippet,
            s.project_ids
        FROM conversations c
        LEFT JOIN sessions s ON c.session_id = s.session_id
        WHERE conversations MATCH ?
    """
    params = [query]
    if date:
        sql += " AND c.date LIKE ?"
        params.append(f"{date}%")
    if project:
        sql += " AND s.project_ids LIKE ?"
        params.append(f"%{project}%")
    sql += " ORDER BY c.date DESC, rank LIMIT ?"
    params.append(limit)
    try:
        c.execute(sql, params)
        return c.fetchall()
    except Exception as e:
        print(f"⚠️  关键词搜索失败：{e}")
        return []


def semantic_search(conn, query, limit=10):
    """双路语义搜索：消息级向量 + session摘要向量，分别返回
    Returns: (msg_results, session_results)
      msg_results: [(session_id, date, role, content_preview, similarity), ...]
      session_results: [(session_id, date, summary, similarity), ...]
    """
    env = load_env()
    api_key = env.get("VOYAGE_API_KEY") or os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        return [], []

    c = conn.cursor()

    try:
        import voyageai
        vo = voyageai.Client(api_key=api_key)
        result = vo.embed([query], model="voyage-3-lite", input_type="query")
        query_vec = result.embeddings[0]
    except Exception as e:
        print(f"⚠️  语义搜索embedding失败：{e}")
        return [], []

    # 消息级向量（细粒度：找具体内容）
    msg_scored = []
    c.execute("SELECT session_id, date, role, content_preview, embedding FROM message_embeddings")
    for session_id, date, role, preview, blob in c.fetchall():
        if blob:
            sim = cosine_similarity(query_vec, blob_to_vec(blob))
            msg_scored.append((session_id, date or "", role, preview, sim))
    msg_scored.sort(key=lambda x: x[4], reverse=True)

    # session摘要向量（粗粒度：找决策/方向，随收工自动增长）
    sess_scored = []
    c.execute("""
        SELECT se.session_id, MIN(cv.date), s.summary, se.embedding
        FROM session_embeddings se
        LEFT JOIN conversations cv ON se.session_id = cv.session_id
        LEFT JOIN sessions s ON se.session_id = s.session_id
        GROUP BY se.session_id
    """)
    for session_id, date, summary, blob in c.fetchall():
        if blob and summary:
            sim = cosine_similarity(query_vec, blob_to_vec(blob))
            sess_scored.append((session_id, date or "", summary, sim))
    sess_scored.sort(key=lambda x: x[3], reverse=True)

    return msg_scored[:limit], sess_scored[:3]


BOILERPLATE_PREFIXES = (
    "读取进度", "读取项目", "继续上次", "继续，", "重启", "保存进度",
    "This session is being continued", "<task-notification", "<command-name",
    "[Request interrupted", "收工", "早，", "早", "进入进度",
)

def get_session_snippet(conn, session_id):
    c = conn.cursor()
    # 优先用sessions表的summary
    c.execute("SELECT summary FROM sessions WHERE session_id = ? AND summary != ''", (session_id,))
    row = c.fetchone()
    if row:
        return row[0][:150]

    # 找第一条有实质内容的用户消息（跳过无效开头）
    c.execute("""
        SELECT content FROM conversations
        WHERE session_id = ? AND role = 'user'
        ORDER BY rowid LIMIT 20
    """, (session_id,))
    for (content,) in c.fetchall():
        content = content.strip()
        if len(content) < 10:
            continue
        if content.startswith("<"):  # XML/系统标签
            continue
        if any(content.startswith(p) for p in BOILERPLATE_PREFIXES):
            continue
        return content[:150]
    return "（无有效摘要）"


def classify_intent(query):
    """规则分类查询意图，返回推荐搜索模式"""
    q = query.lower()

    # 时间信号 → keyword（精确匹配时间词效果更好）
    temporal = ["最近", "上周", "上个月", "昨天", "今天", "这周", "本月", "前几天"]
    if any(w in q for w in temporal):
        return "keyword"

    # 项目编号信号（P2/p3等）→ keyword
    if re.search(r'\bp\d+\b', q):
        return "keyword"

    # 概念/方法信号 → semantic
    conceptual = ["如何", "为什么", "怎么", "原理", "方案", "策略", "区别", "对比", "思路", "设计"]
    if any(w in q for w in conceptual):
        return "semantic"

    return "hybrid"


def search(query, project=None, date=None, limit=20, mode="auto"):
    if not os.path.exists(DB_PATH):
        print("❌ cowork.db 不存在，请先运行 setup_db.py + index_conversations.py")
        return

    # 意图分类（auto 模式时自动推断）
    if mode == "auto":
        mode = classify_intent(query)
        print(f"🎯 意图：{mode} 模式")

    conn = sqlite3.connect(DB_PATH)

    # 关键词搜索
    kw_results = []
    if mode in ("keyword", "hybrid"):
        kw_results = keyword_search(conn, query, project=project, date=date, limit=limit)

    # 语义搜索
    msg_results, sess_results = [], []
    if mode in ("semantic", "hybrid"):
        msg_results, sess_results = semantic_search(conn, query, limit=10)

    sem_results = msg_results  # 保持向后兼容的变量名

    if mode == "keyword" or not sem_results:
        # 纯关键词模式或语义搜索不可用
        conn.close()
        if not kw_results:
            print(f"未找到与「{query}」相关的对话")
            return
        print(f"\n🔍 搜索「{query}」— 找到 {len(kw_results)} 条（关键词模式）\n")
        print("─" * 60)
        for row in kw_results:
            session_id, date_r, role, snippet, project_ids = row
            proj_label = project_ids if project_ids else "未标记"
            role_label = "🙋 主公" if role == "user" else "🤖 Claude"
            print(f"📅 {date_r}  📁 {proj_label}  {role_label}")
            print(f"   {snippet}")
            print(f"   Session: {session_id[:8]}...")
            print()
        return

    if mode == "semantic":
        conn.close()
        if not msg_results and not sess_results:
            print(f"未找到与「{query}」相关的对话（语义模式）")
            return
        # Session 摘要段（决策/方向）
        if sess_results:
            print(f"\n📋 Session 摘要命中（Top {len(sess_results)}）\n")
            print("─" * 60)
            for session_id, date_r, summary, sim in sess_results:
                print(f"📅 {date_r}  相似度：{sim:.3f}")
                print(f"   {summary[:150]}")
                print(f"   Session: {session_id[:8]}...")
                print()
        # 消息级段（具体内容）
        if msg_results:
            print(f"🧠 消息级命中（Top {len(msg_results[:5])}）\n")
            print("─" * 60)
            for session_id, date_r, role, preview, sim in msg_results[:5]:
                role_label = "🙋 主公" if role == "user" else ("🤖 Claude" if role else "")
                snippet_text = f"{role_label}: {preview}" if preview else ""
                print(f"📅 {date_r}  相似度：{sim:.3f}")
                if snippet_text:
                    print(f"   {snippet_text[:120]}")
                print(f"   Session: {session_id[:8]}...")
                print()
        return

    # 混合模式：关键词 + 语义双路结果
    seen = set()
    merged = []

    # Session 摘要命中（放最前面，粗粒度定位）
    c = conn.cursor()
    for sid, date_r, summary, sim in sess_results:
        if sim > 0.4 and sid not in seen:
            seen.add(sid)
            c.execute("SELECT project_ids FROM sessions WHERE session_id = ?", (sid,))
            sr = c.fetchone()
            proj = sr[0] if sr else None
            merged.append({
                "session_id": sid,
                "date": date_r,
                "project_ids": proj,
                "snippet": summary[:120],
                "source": "📋",
                "sim": sim
            })

    # 关键词命中（高优先级）
    for row in kw_results:
        sid = row[0]
        if sid not in seen:
            seen.add(sid)
            c.execute("SELECT project_ids FROM sessions WHERE session_id = ?", (sid,))
            sr = c.fetchone()
            proj = sr[0] if sr else None
            merged.append({
                "session_id": sid,
                "date": row[1],
                "project_ids": proj or row[4],
                "snippet": row[3],
                "source": "🔑",
                "sim": 0.0
            })

    # 消息级语义命中（按相似度补充）
    kw_empty = len(kw_results) == 0
    for sid, date_r, role, preview, sim in msg_results:
        threshold = 0.35 if kw_empty else 0.5
        if sim <= threshold:
            continue
        entry_key = f"{sid}:{preview[:30]}" if preview else sid
        if entry_key not in seen:
            seen.add(entry_key)
            c.execute("SELECT project_ids FROM sessions WHERE session_id = ?", (sid,))
            sr = c.fetchone()
            proj = sr[0] if sr else None
            role_label = "🙋 主公" if role == "user" else ("🤖 Claude" if role else "")
            snippet_text = f"{role_label}: {preview}" if preview else get_session_snippet(conn, sid)
            merged.append({
                "session_id": sid,
                "date": date_r,
                "project_ids": proj,
                "snippet": snippet_text,
                "source": "🧠",
                "sim": sim
            })

    conn.close()

    if not merged:
        print(f"未找到与「{query}」相关的对话")
        return

    merged = merged[:limit]
    print(f"\n🔍 搜索「{query}」— {len(merged)} 条结果（📋摘要 🔑关键词 🧠消息）\n")
    print("─" * 60)
    for item in merged:
        proj_label = item["project_ids"] or "未标记"
        sim_label = f"  相似度：{item['sim']:.3f}" if item["sim"] > 0 else ""
        print(f"📅 {item['date']}  📁 {proj_label}  {item['source']}{sim_label}")
        print(f"   {item['snippet'][:120]}")
        print(f"   Session: {item['session_id'][:8]}...")
        print()


def main():
    parser = argparse.ArgumentParser(description="搜索 cowork 历史对话")
    parser.add_argument("query", help="搜索关键词/语义描述")
    parser.add_argument("--project", help="过滤项目（如 P3）")
    parser.add_argument("--date", help="过滤日期前缀（如 2026-04）")
    parser.add_argument("--limit", type=int, default=20, help="最多显示条数（默认20）")
    parser.add_argument("--mode", choices=["keyword", "semantic", "hybrid", "auto"], default="auto",
                        help="搜索模式（默认auto=意图分类）")
    args = parser.parse_args()

    search(args.query, project=args.project, date=args.date, limit=args.limit, mode=args.mode)


if __name__ == "__main__":
    main()
