#!/usr/bin/env python3
"""
FERC 裁决自动哨兵（趋势主线观察池 E1，一次性使命）
- 每天 17:05 EDT 自动搜 FERC co-location/large load 裁决新闻
- 命中"裁决落地"特征 → Discord 报警（标题+链接）；没消息一声不吭
- 裁决落地报警后：人工删 cron 行 + 归档本脚本（一次性哨兵）
- 调用: python3 ferc_watch.py [--test]（--test 强制发送当前搜索结果，验证管道）
- 创建: 2026-06-12（趋势主线第2层；背景见 trading/notes/趋势观察池.md E1）

依赖: SerpAPI Google News（KEY1→KEY2 fallback，抄 gtrends_collector 2026-06-10 教训）
      newscripts/send_discord_dm.py
"""
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime

ENV_PATH = "/home/cowork/cowork/config/api_keys.env"
SERPAPI_URL = "https://serpapi.com/search"
SERPAPI_KEY_NAMES = ("SERPAPI_KEY", "SERPAPI_KEY2")
TEST_MODE = "--test" in sys.argv
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

QUERY = "FERC ruling colocation data center interconnection large load"
# 命中条件：标题/摘要含「裁决动作词」+「主题词」（宁可偶尔误报，不可漏报；误报成本=一条消息）
ACTION_WORDS = ("ruling", "rules", "ruled", "order", "decision", "decides",
                "approves", "rejects", "issues", "votes")
TOPIC_WORDS = ("colocation", "co-located", "co-location", "large load",
               "interconnection", "data center")


def load_env(path):
    env = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def search_news(env):
    """SerpAPI Google News 搜索，KEY1→KEY2 fallback。"""
    last_err = None
    for name in SERPAPI_KEY_NAMES:
        key = env.get(name)
        if not key:
            continue
        params = {"engine": "google_news", "q": QUERY, "gl": "us", "hl": "en",
                  "api_key": key}
        url = SERPAPI_URL + "?" + urllib.parse.urlencode(params)
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data = json.loads(r.read())
            if "error" in data:
                last_err = RuntimeError(name + ": " + str(data["error"]))
                print("[key-fallback] " + name + " 失败 → 换下一个 key", flush=True)
                continue
            return data.get("news_results", [])
        except Exception as e:
            last_err = e
            print("[key-fallback] " + name + " 异常: " + str(e), flush=True)
    raise last_err or RuntimeError("无可用 SerpAPI key")


def is_hit(item):
    text = (item.get("title", "") + " " + item.get("snippet", "")).lower()
    # 只看近 2 天的新闻（date 字段形如 "06/12/2026, 10:00 AM, +0000 UTC" 或相对时间）
    date_str = item.get("date", "")
    recent = any(w in date_str.lower() for w in ("hour", "minute", "day ago", "1 day"))
    if not recent and "/" in date_str:
        try:
            d = datetime.strptime(date_str.split(",")[0], "%m/%d/%Y")
            recent = (datetime.now() - d).days <= 2
        except ValueError:
            recent = False
    has_action = any(w in text for w in ACTION_WORDS)
    has_topic = any(w in text for w in TOPIC_WORDS)
    return recent and has_action and has_topic


def send_discord(msg):
    result = subprocess.run(
        ["python3", "/home/cowork/cowork/newscripts/send_discord_dm.py", msg],
        capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR send_discord: " + result.stderr, file=sys.stderr)
        sys.exit(1)


def ops_log(line):
    try:
        with open("/home/cowork/cowork/ops_log.md", "a") as f:
            f.write("[" + NOW + " EDT] CRON[ferc_watch] | " + line + "\n")
    except Exception as e:
        print("WARN ops_log: " + str(e), file=sys.stderr)


def main():
    env = load_env(ENV_PATH)
    items = search_news(env)
    hits = [it for it in items if is_hit(it)]

    if TEST_MODE:
        top = "\n".join("· " + it.get("title", "?")[:80] for it in items[:5]) or "(无结果)"
        send_discord("🧪 [FERC哨兵测试] 管道正常。今日搜索 top5：\n" + top +
                     "\n\n命中数: " + str(len(hits)) + "（正式模式只在命中时报警）")
        ops_log("test | ✅ | 搜到 " + str(len(items)) + " 条, 命中 " + str(len(hits)))
        return

    if hits:
        lines = []
        for it in hits[:3]:
            lines.append("📰 **" + it.get("title", "?") + "**\n" +
                         (it.get("snippet", "") or "")[:150] + "\n" +
                         it.get("link", ""))
        send_discord("🚨 [FERC哨兵] 疑似裁决落地新闻（观察池 E1）！\n\n" +
                     "\n\n".join(lines) +
                     "\n\n→ 下一步：BB 将人工确认；确认落地后出电力链一页纸方案（首仓前置条件①）")
        ops_log("daily | 🚨 | 命中 " + str(len(hits)) + " 条，已报警")
    else:
        ops_log("daily | ✅ | 无命中（静默）")


if __name__ == "__main__":
    main()
