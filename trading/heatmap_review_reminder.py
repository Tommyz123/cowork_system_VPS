#!/usr/bin/env python3
"""
信号升温榜 阶段0 验收提醒（一次性，2026-08-24 触发）。

【是什么】到 theme_heatmap 跑满 8 周排雷期那天，自动发 Discord 提醒主公来验收，
         不用主公记着一直问（loop engineering 的「上报」零件：到点系统主动叫人）。

【为什么这样设计】验收是人工决策点（要主公拍板升级或停止），不能自动判定；
         脚本只负责"到点叫人 + 附上当初定的标准"，把判断权留给主公。

【一次性】发完即过。cron 设在 2026-08-24，触发一次后该 cron 应手动删除（或留着无害，
         脚本只在 2026-08-24 当天逻辑生效，其他日期跑会提示未到日期直接退出）。

用法：python3 trading/heatmap_review_reminder.py
"""
import sqlite3
from datetime import datetime

import requests

from tide_utils import load_env

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"
REVIEW_DATE = "2026-08-24"   # 验收日（6/23 起 8 周）
DESIGN_DOC = "trading/notes/主题累积研究loop设计.md"


def count_weeks_data(conn):
    """统计排雷期内 signals 的周跨度，给主公一个"攒了多少"的直观数字。"""
    try:
        row = conn.execute(
            "SELECT MIN(date), MAX(date), COUNT(*) FROM signals WHERE date >= '2026-06-23'"
        ).fetchone()
        return row
    except Exception:
        return (None, None, 0)


def send_discord(env, message):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        print("[review_reminder] 缺 Discord 配置，跳过")
        return
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    try:
        requests.post(
            f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
            headers=headers,
            json={"content": message},
            timeout=15,
        ).raise_for_status()
    except Exception as e:
        print(f"[review_reminder] Discord 发送失败: {e}")


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    if today < REVIEW_DATE:
        print(f"[review_reminder] 今天 {today} 未到验收日 {REVIEW_DATE}，跳过")
        return
    env = load_env()
    conn = sqlite3.connect(DB_PATH)
    try:
        mn, mx, cnt = count_weeks_data(conn)
    finally:
        conn.close()
    message = (
        f"⏰ **主公，信号升温榜（theme_heatmap）8周排雷期到了，该验收了！**\n\n"
        f"自 2026-06-23 起已攒数据：{mn} → {mx}，共 {cnt} 条新信号。\n\n"
        f"**验收 3 条标准（当初定的，全满足才进下一步搭子agent自动化）**：\n"
        f"① 跑满 6-8 周 ✅（已到）\n"
        f"② BB 每周判断命中率 ≥ 60%（要 BB 统计这8周判断 vs 实际，跟我汇报）\n"
        f"③ 主公看统计后认可\"确实有用\"\n\n"
        f"**达标→进阶段1（审计员agent化+档案落库）；不到60%或跟瞎猜一样→停在这别浪费。**\n\n"
        f"📄 完整标准+设计：`{DESIGN_DOC}`\n"
        f"👉 主公说一句\"验收升温榜\"，BB 就把这8周命中率统计摆出来。"
    )
    print(message)
    send_discord(env, message)


if __name__ == "__main__":
    main()
