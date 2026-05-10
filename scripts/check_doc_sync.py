#!/usr/bin/env python3
"""
收工时自动跑：扫描 ARCHITECTURE.md + context.md 里提到的 .py 文件名，
对比文件系统实际存在的脚本，输出不匹配项。
"""
import re
import os
from pathlib import Path

BASE = Path("/home/cowork/cowork")
DOCS = [BASE / "ARCHITECTURE.md", BASE / "context.md"]


def extract_py_names(doc_path):
    names = set()
    text = doc_path.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r"`([a-zA-Z0-9_/]+\.py)`", text):
        names.add(m.group(1))
    return names


def find_py_files():
    found = {}
    for p in BASE.rglob("*.py"):
        found[p.name] = str(p)
        # also store basename-only for short matches
    return found


def main():
    mentioned = set()
    for doc in DOCS:
        if doc.exists():
            mentioned |= extract_py_names(doc)

    existing = find_py_files()

    missing = []
    for name in sorted(mentioned):
        # name may be "subdir/file.py" or just "file.py"
        basename = Path(name).name
        if basename not in existing:
            missing.append(name)

    if missing:
        print(f"⚠️  文档提到但文件系统找不到的脚本（{len(missing)}个）：")
        for m in missing:
            print(f"   - {m}")
        print("→ 请更新 ARCHITECTURE.md / context.md 或确认脚本路径")
    else:
        print("✅ 文档脚本引用全部验证通过")


if __name__ == "__main__":
    main()
