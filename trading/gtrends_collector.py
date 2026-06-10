#!/usr/bin/env python3
"""P9 alt-data sidecar: Google Trends theme search volume 收集器。

2026-05-18 建立。Plan C：静默后台收集 + on-demand 展示。
- 完全独立于 P9 主线（cognitive_scanner / weekly_review / scanner_picks）
- 不影响下单 / 不进评分 / 不污染主表
- 数据写入 alt_signals 表，主公任何时候问我可 query 展示
- 每周日 15:45 EDT cron 自动拉一次（在 weekly_review 16:00 之前）

研究纪律：现在只观察不量化，等 1 年累积 50+ sample 后再考虑入 cognitive_scanner 评分。
详见 memory/feedback_p9_alt_data_sidecar.md
"""
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tide_utils import load_env

DB_PATH = "/home/cowork/cowork/trading/trading.db"
SERPAPI_URL = "https://serpapi.com/search"

# P9 5 个 theme 对应的 Google Trends 关键词（2026-05-18 dry-run 验证过有强信号）
THEME_KEYWORDS = {
    "AI 软件":        "generative AI software",
    "公用事业现代化":  "utility infrastructure",
    "AI 电力":        "data center energy demand",
    "分析师重定价":    "stock upgrade",
    "行业重分类":      "sector rotation",
}


def serpapi_trends(api_key: str, keyword: str, date: str = "today 12-m", geo: str = "US"):
    """调 SerpAPI Google Trends interest_over_time。返回 timeline_data list 或 raise。"""
    params = {
        "engine": "google_trends",
        "q": keyword,
        "data_type": "TIMESERIES",
        "date": date,
        "geo": geo,
        "api_key": api_key,
    }
    url = SERPAPI_URL + "?" + urllib.parse.urlencode(params)
    try:
        resp = urllib.request.urlopen(url, timeout=30)
        data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"SerpAPI HTTP {e.code}: {e.read().decode()[:200]}")
    if "error" in data:
        raise RuntimeError(f"SerpAPI error: {data['error']}")
    return data.get("interest_over_time", {}).get("timeline_data", [])


# 2026-06-10 key 自动 fallback：KEY1 免费版 250 次/月，5/31 起耗尽导致连续 2 周收集失败。
# 配额耗尽的 key 记入此集合，本次运行内不再重试（429 不耗配额但浪费请求）。
SERPAPI_KEY_NAMES = ("SERPAPI_KEY", "SERPAPI_KEY2")
_exhausted_keys = set()


def _is_quota_error(err) -> bool:
    s = str(err).lower()
    return "429" in s or "run out of searches" in s


def serpapi_trends_fallback(env, keyword: str):
    """按 SERPAPI_KEY → SERPAPI_KEY2 顺序尝试，配额耗尽自动换下一个。
    返回 (timeline_data, key_name)；所有 key 失败则 raise。"""
    last_err = None
    for name in SERPAPI_KEY_NAMES:
        key = env.get(name)
        if not key or name in _exhausted_keys:
            continue
        try:
            return serpapi_trends(key, keyword), name
        except RuntimeError as e:
            if _is_quota_error(e):
                _exhausted_keys.add(name)
                print(f"[key-fallback] {name} 配额耗尽 → 换下一个 key", flush=True)
                last_err = e
                continue
            raise
    raise last_err or RuntimeError(f"无可用 SerpAPI key（配置检查 {SERPAPI_KEY_NAMES}）")


def upsert_signal(conn, theme: str, keyword: str, week_start: str, value: int):
    """INSERT OR IGNORE alt_signals，避免重复入历史数据。"""
    cur = conn.cursor()
    cur.execute(
        """INSERT OR IGNORE INTO alt_signals
           (signal_type, theme, keyword, week_start, value, source)
           VALUES ('gtrends_theme', ?, ?, ?, ?, 'serpapi')""",
        (theme, keyword, week_start, value),
    )
    return cur.rowcount


def collect_one_theme(conn, env, theme: str, keyword: str):
    """拉一个 theme 的 12 个月 weekly 数据 + 写入。返回 (new_rows, total_weeks)。"""
    timeline, key_name = serpapi_trends_fallback(env, keyword)
    if key_name != SERPAPI_KEY_NAMES[0]:
        print(f"[{theme}] 使用备用 key: {key_name}", flush=True)
    if not timeline:
        return 0, 0
    new_rows = 0
    for row in timeline:
        ts = row.get("timestamp")
        values = row.get("values", [])
        if not ts or not values:
            continue
        try:
            week_start = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d")
            value = int(values[0].get("extracted_value", 0))
        except (ValueError, KeyError, IndexError):
            continue
        if upsert_signal(conn, theme, keyword, week_start, value):
            new_rows += 1
    return new_rows, len(timeline)


def send_discord_summary(env, summary):
    """跑完发 Discord 通知主公"""
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        return
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(
        f"https://discord.com/api/v10/channels/{channel_id}/messages",
        data=json.dumps({"content": summary}).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception:
        pass  # 静默失败，不阻塞 collector


def main():
    env = load_env()
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime("%Y-%m-%d")
    summary_lines = [f"📊 P9 alt-data Google Trends 收集 - {today}"]
    total_new = 0
    failed_themes = []
    for theme, keyword in THEME_KEYWORDS.items():
        try:
            new_rows, total_weeks = collect_one_theme(conn, env, theme, keyword)
            total_new += new_rows
            summary_lines.append(f"  ✅ {theme} (\"{keyword}\"): {new_rows} 周新增 / {total_weeks} 周返回")
            print(f"[{theme}] '{keyword}' → +{new_rows} new rows ({total_weeks} weeks)", flush=True)
        except Exception as e:
            failed_themes.append(theme)
            summary_lines.append(f"  ❌ {theme} (\"{keyword}\"): {str(e)[:100]}")
            print(f"[{theme}] FAILED: {e}", flush=True)
    conn.commit()
    conn.close()

    if failed_themes:
        summary_lines[0] = f"⚠️ P9 alt-data Google Trends 收集 - {today}（{len(failed_themes)}/{len(THEME_KEYWORDS)} 个主题失败）"
    summary_lines.append(f"\n总计新增 {total_new} 条记录")
    summary_lines.append(f"主公任何时候 Discord 问'看下 [theme] 最近搜索量'，我从 alt_signals 表取数据展示。")
    send_discord_summary(env, "\n".join(summary_lines))
    print(f"\n总计新增 {total_new} 条记录")

    # 全部主题失败 = 数据收集中断，raise 让 run_with_alert 发失败邮件（5/31-6/9 静默断 2 周的教训）
    if failed_themes and len(failed_themes) == len(THEME_KEYWORDS):
        raise RuntimeError(f"全部 {len(THEME_KEYWORDS)} 个主题收集失败（SerpAPI key 全不可用）")


if __name__ == "__main__":
    from tide_utils import run_with_alert
    run_with_alert("gtrends_collector", main)
