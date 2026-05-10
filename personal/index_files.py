#!/usr/bin/env python3
"""
index_files.py — 扫描个人文件文件夹，生成向量并存入 personal.db

用法：
  python3 personal/index_files.py                # 扫描所有配置的文件夹
  python3 personal/index_files.py --force        # 重新索引已存在的文件
"""
import os
import sqlite3
import struct
import sys
import argparse
from datetime import datetime, timezone

from docx import Document
import pdfplumber

DB_PATH = "/home/cowork/cowork/personal/personal.db"
ENV_PATH = "/home/cowork/cowork/config/api_keys.env"

# 要索引的文件夹列表（递归扫描）
SCAN_DIRS = [
    "/mnt/c/Users/zhi89/Desktop/资料/个人文档/简历",
    "/mnt/c/Users/zhi89/Desktop/资料/出租lease",
    "/mnt/c/Users/zhi89/Desktop/资料/个人财务税务",
    "/mnt/c/Users/zhi89/Desktop/资料/证书",
    "/mnt/c/Users/zhi89/Desktop/资料/cannabis",
]


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


def vec_to_blob(vec):
    return struct.pack(f"{len(vec)}f", *vec)


def ensure_table(conn):
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS personal_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            category TEXT DEFAULT 'resume',
            content TEXT,
            embedding BLOB,
            indexed_at TEXT
        )
    """)
    c.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_personal_files_filepath
        ON personal_files(filepath)
    """)
    conn.commit()


def extract_docx_text(filepath):
    doc = Document(filepath)
    parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(parts)


def extract_pdf_text(filepath):
    parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                parts.append(text.strip())
    return "\n".join(parts)


def infer_category(filename, content):
    lower = filename.lower()
    content_lower = content.lower()
    if "租约" in filename or "租房合同" in filename or "lease" in lower or "申请表" in filename:
        return "lease"
    if "certificate" in lower or "证书" in filename or "coursera" in lower or "bmcc" in lower or "ibm" in lower or "abp" in lower:
        return "certificate"
    if "w2" in lower or "税务" in filename or "财务" in filename or "tax" in lower or "1099" in lower:
        return "finance"
    if "cannabis" in lower or "dispensary" in lower or "mbe" in lower or "药房" in filename or "cannabis" in content_lower:
        return "cannabis"
    if "cover" in lower:
        return "cover_letter"
    if "interview" in lower:
        return "interview_prep"
    if "cannabis" in content_lower or "budtender" in content_lower or "dispensary" in content_lower or "resumew" in lower:
        return "budtender_resume"
    if "bartender" in content_lower or "resumewb" in lower:
        return "bartender_resume"
    if "resume" in lower or "cv" in lower:
        return "resume"
    return "document"


def scan_files(dirs):
    found = []
    for d in dirs:
        if not os.path.exists(d):
            print(f"⚠️ 文件夹不存在，跳过：{d}")
            continue
        for root, subdirs, files in os.walk(d):
            # 跳过历史归档目录
            subdirs[:] = [s for s in subdirs if not s.startswith("_历史归档")]
            for f in files:
                if f.startswith("~$"):
                    continue
                if f.lower().endswith(".docx") or f.lower().endswith(".pdf"):
                    found.append(os.path.join(root, f))
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="重新索引已存在的文件")
    args = parser.parse_args()

    env = load_env()
    api_key = env.get("VOYAGE_API_KEY") or os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        print("❌ 未找到 VOYAGE_API_KEY，请检查 config/api_keys.env")
        sys.exit(1)

    import voyageai
    vo = voyageai.Client(api_key=api_key)

    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)
    c = conn.cursor()

    c.execute("SELECT filepath FROM personal_files")
    existing = {row[0] for row in c.fetchall()}

    all_files = scan_files(SCAN_DIRS)
    targets = []
    skipped = 0
    for path in sorted(all_files):
        if path in existing and not args.force:
            skipped += 1
            continue
        targets.append(path)

    if skipped:
        print(f"⏭️ 已跳过 {skipped} 个已索引文件（用 --force 重新索引）")

    if not targets:
        print("✅ 无新文件需要索引")
        conn.close()
        return

    texts = []
    meta = []
    for path in targets:
        try:
            if path.lower().endswith(".pdf"):
                text = extract_pdf_text(path)
            else:
                text = extract_docx_text(path)
            if not text.strip():
                print(f"⚠️ 空内容，跳过：{os.path.basename(path)}")
                continue
            category = infer_category(os.path.basename(path), text)
            texts.append(text)
            meta.append((os.path.basename(path), path, category, text))
        except Exception as e:
            print(f"❌ 读取失败，跳过：{os.path.basename(path)} — {e}")

    if not texts:
        print("⚠️ 没有可索引的有效文件")
        conn.close()
        return

    # 分批embed，每批最多20个文件，避免超出Voyage token限制
    BATCH_SIZE = 20
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    indexed = 0
    for i in range(0, len(meta), BATCH_SIZE):
        batch_meta = meta[i:i + BATCH_SIZE]
        batch_texts = texts[i:i + BATCH_SIZE]
        result = vo.embed(batch_texts, model="voyage-3", input_type="document")
        for (name, path, category, text), embedding in zip(batch_meta, result.embeddings):
            if args.force:
                c.execute("DELETE FROM personal_files WHERE filepath = ?", (path,))
            c.execute("""
                INSERT OR IGNORE INTO personal_files (filename, filepath, category, content, embedding, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, path, category, text, vec_to_blob(embedding), now))
            indexed += 1
            print(f"✓ [{category}] {name}")
        conn.commit()

    conn.close()
    print(f"\n已索引 {indexed} 个文件")


if __name__ == "__main__":
    main()
