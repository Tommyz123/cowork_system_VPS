#!/usr/bin/env python3
"""
PostToolUse hook: 记录每次 Edit/Write/MultiEdit 共享文件的事件。
Stdin: Claude Code 传入的 JSON。
Output: 追加一行到 write_events.log。
"""
import sys
import json
import os
import datetime
import pathlib

SHARED_FILES = {
    "/home/cowork/cowork/cowork_log.md",
    "/home/cowork/cowork/CURRENT_SESSION.md",
    "/home/cowork/cowork/friction_log.md",
    "/home/cowork/cowork/INSIGHTS.md",
}

LOG_PATH = "/home/cowork/cowork/logs/write_events.log"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        return

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        return

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return

    try:
        abs_path = str(pathlib.Path(file_path).resolve())
    except Exception:
        return

    if abs_path not in SHARED_FILES:
        return

    home = os.environ.get("HOME", "unknown")
    ts = datetime.datetime.now().isoformat(timespec="microseconds")

    try:
        pathlib.Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts}|{home}|{abs_path}|{tool_name}\n")
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit(0)
