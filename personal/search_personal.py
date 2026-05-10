#!/usr/bin/env python3
"""
search_personal.py — 搜索个人文件（关键词 + 向量混合）

用法：
  python3 personal/search_personal.py "简历"
  python3 personal/search_personal.py "cover letter"
"""
import argparse
import os
import re
import sqlite3
import struct
import sys

DB_PATH = "/home/cowork/cowork/personal/personal.db"
ENV_PATH = "/home/cowork/cowork/config/api_keys.env"


def load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
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


def tokenize_query(query):
    # 切词：空格/下划线/连字符，再按中英文边界分割
    parts = re.split(r'[\s\-_]+', query)
    tokens = []
    for part in parts:
        sub = re.findall(r'[a-zA-Z0-9]+|[一-鿿]+', part)
        tokens.extend(sub)
    return [t for t in tokens if len(t) >= 2]


def keyword_search(conn, query):
    c = conn.cursor()
    tokens = tokenize_query(query)
    if not tokens:
        tokens = [query]

    # filename/category命中=2分，content命中=1分，分高优先
    hit_score = {}
    rows_by_id = {}
    for token in tokens:
        like_q = f"%{token}%"
        # filename/category命中（高权重）
        c.execute("""
            SELECT id, filename, filepath, content
            FROM personal_files
            WHERE filename LIKE ? OR category LIKE ?
        """, (like_q, like_q))
        for row in c.fetchall():
            fid = row[0]
            hit_score[fid] = hit_score.get(fid, 0) + 2
            rows_by_id[fid] = row
        # content命中（低权重）
        c.execute("""
            SELECT id, filename, filepath, content
            FROM personal_files
            WHERE content LIKE ?
        """, (like_q,))
        for row in c.fetchall():
            fid = row[0]
            hit_score[fid] = hit_score.get(fid, 0) + 1
            rows_by_id[fid] = row

    sorted_ids = sorted(hit_score.keys(), key=lambda x: hit_score[x], reverse=True)
    return [rows_by_id[fid] for fid in sorted_ids]


def semantic_search(conn, query):
    env = load_env()
    api_key = env.get("VOYAGE_API_KEY") or os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        print("❌ 未找到 VOYAGE_API_KEY，请检查 config/api_keys.env")
        sys.exit(1)

    import voyageai
    vo = voyageai.Client(api_key=api_key)
    result = vo.embed([query], model="voyage-3", input_type="query")
    query_vec = result.embeddings[0]

    c = conn.cursor()
    c.execute("""
        SELECT id, filename, filepath, content, embedding
        FROM personal_files
        WHERE embedding IS NOT NULL
    """)
    rows = c.fetchall()

    scored = []
    for row in rows:
        file_id, filename, filepath, content, blob = row
        vec = blob_to_vec(blob)
        sim = cosine_similarity(query_vec, vec)
        scored.append((file_id, filename, filepath, content, sim))
    scored.sort(key=lambda x: x[4], reverse=True)
    return scored


def make_snippet(content, query, limit=200):
    if not content:
        return ""
    text = content.replace("\n", " ").strip()
    lower_text = text.lower()
    lower_query = query.lower()

    pos = lower_text.find(lower_query)
    if pos == -1:
        return text[:limit]

    start = max(0, pos - 60)
    end = min(len(text), pos + len(query) + 140)
    snippet = text[start:end]
    return snippet[:limit]


def search(query, limit=3):
    if not os.path.exists(DB_PATH):
        print("❌ personal.db 不存在")
        return

    conn = sqlite3.connect(DB_PATH)

    kw_rows = keyword_search(conn, query)
    kw_ids = {row[0] for row in kw_rows}

    sem_rows = semantic_search(conn, query)

    merged = []
    seen = set()

    for file_id, filename, filepath, content in kw_rows:
        if file_id in seen:
            continue
        seen.add(file_id)
        merged.append({
            "filename": filename,
            "filepath": filepath,
            "snippet": make_snippet(content, query),
            "source": "🔑",
            "score": 1.0,
        })

    for file_id, filename, filepath, content, sim in sem_rows:
        if file_id in seen:
            continue
        if sim < 0.10 and file_id not in kw_ids:
            continue
        seen.add(file_id)
        merged.append({
            "filename": filename,
            "filepath": filepath,
            "snippet": make_snippet(content, query),
            "source": "🧠",
            "score": sim,
        })
        if len(merged) >= limit:
            break

    conn.close()

    if not merged:
        print(f"未找到与「{query}」相关的文件")
        return

    merged = merged[:limit]
    print(f"\n🔍 搜索「{query}」— Top {len(merged)}\n")
    print("─" * 60)
    for item in merged:
        sim_label = f"  相似度：{item['score']:.3f}" if item["source"] == "🧠" else ""
        print(f"{item['source']} {item['filename']}{sim_label}")
        print(f"路径：{item['filepath']}")
        print(f"片段：{item['snippet']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="搜索个人文件")
    parser.add_argument("query", help="搜索关键词/语义描述")
    parser.add_argument("--limit", type=int, default=3, help="返回条数（默认3）")
    args = parser.parse_args()
    search(args.query, limit=args.limit)


if __name__ == "__main__":
    main()
