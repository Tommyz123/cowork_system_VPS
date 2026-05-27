#!/usr/bin/env python3
"""
扫描 write_events.log，找 10 秒内被两个不同 HOME 实例写过的共享文件。
发现新冲突：追加到 conflict_log.md + 发 Discord 告警到 Cowork 频道。
适合 cron 每分钟跑一次。
"""
import os
import sys
import datetime
import pathlib
import requests

LOG_PATH = "/home/cowork/cowork/logs/write_events.log"
CONFLICT_LOG = "/home/cowork/cowork/reference/conflict_log.md"
ALERTED_PATH = "/home/cowork/cowork/logs/.conflict_alerted"
WINDOW_SECONDS = 10
DISCORD_CHANNEL_ID = "1485128242808619079"  # DM 频道（与现有 cron 告警一致）
DISCORD_ENV = "/home/cowork/.claude/channels/discord/.env"


def load_token() -> str | None:
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        return token
    try:
        with open(DISCORD_ENV, encoding="utf-8") as f:
            for line in f:
                if line.startswith("DISCORD_BOT_TOKEN="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        pass
    return None


def parse_events() -> list[dict]:
    if not os.path.exists(LOG_PATH):
        return []
    events = []
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) < 4:
                continue
            try:
                ts = datetime.datetime.fromisoformat(parts[0])
            except ValueError:
                continue
            events.append({"ts": ts, "home": parts[1], "file": parts[2], "tool": parts[3]})
    return events


def find_conflicts(events: list[dict]) -> list[tuple[dict, dict, float]]:
    events_sorted = sorted(events, key=lambda e: e["ts"])
    conflicts = []
    for i, e1 in enumerate(events_sorted):
        for e2 in events_sorted[i + 1:]:
            delta = (e2["ts"] - e1["ts"]).total_seconds()
            if delta > WINDOW_SECONDS:
                break
            if e2["file"] != e1["file"]:
                continue
            if e2["home"] == e1["home"]:
                continue
            conflicts.append((e1, e2, delta))
    return conflicts


def get_alerted() -> set[str]:
    if not os.path.exists(ALERTED_PATH):
        return set()
    with open(ALERTED_PATH, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def mark_alerted(key: str) -> None:
    pathlib.Path(ALERTED_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(ALERTED_PATH, "a", encoding="utf-8") as f:
        f.write(key + "\n")


def send_discord(message: str) -> bool:
    token = load_token()
    if not token:
        return False
    try:
        resp = requests.post(
            f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages",
            headers={"Authorization": f"Bot {token}", "Content-Type": "application/json"},
            json={"content": message},
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        print(f"Discord 发送失败: {exc}", file=sys.stderr)
        return False


def append_conflict_log(rows: list[tuple[dict, dict, float, str]]) -> None:
    pathlib.Path(CONFLICT_LOG).parent.mkdir(parents=True, exist_ok=True)
    write_header = not os.path.exists(CONFLICT_LOG)
    with open(CONFLICT_LOG, "a", encoding="utf-8") as f:
        if write_header:
            f.write("# Cowork 共享文件冲突记录\n\n")
            f.write("由 `scripts/detect_conflict.py` 自动写入。窗口 10 秒。\n\n")
            f.write("---\n")
        for e1, e2, delta, key in rows:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_name = e1["file"].split("/")[-1]
            f.write(f"\n## [{now}] {file_name}\n")
            f.write(f"- 文件: `{e1['file']}`\n")
            f.write(f"- 实例 A: `{e1['home']}` 用 {e1['tool']} 在 {e1['ts'].isoformat()}\n")
            f.write(f"- 实例 B: `{e2['home']}` 用 {e2['tool']} 在 {e2['ts'].isoformat()}\n")
            f.write(f"- 时间差: {delta:.2f} 秒\n")
            f.write(f"- 事件键: `{key}`\n")


def main() -> None:
    events = parse_events()
    conflicts = find_conflicts(events)
    alerted = get_alerted()

    new_rows = []
    for e1, e2, delta in conflicts:
        key = f"{e1['ts'].isoformat()}__{e2['ts'].isoformat()}__{e1['file']}"
        if key in alerted:
            continue
        new_rows.append((e1, e2, delta, key))

    if not new_rows:
        return

    append_conflict_log(new_rows)

    files_seen = sorted({row[0]["file"].split("/")[-1] for row in new_rows})
    homes_seen = sorted({h for row in new_rows for h in (row[0]["home"], row[1]["home"])})
    msg_lines = [
        f"⚠️ **共享文件冲突告警** | 新冲突 {len(new_rows)} 起",
        f"文件: {', '.join(files_seen)}",
        f"实例: {', '.join(homes_seen)}",
        f"详情见 `cowork/reference/conflict_log.md`",
    ]
    sent = send_discord("\n".join(msg_lines))

    for _, _, _, key in new_rows:
        mark_alerted(key)

    if not sent:
        print("ALERT (Discord 发送失败) " + " | ".join(msg_lines))


if __name__ == "__main__":
    main()
