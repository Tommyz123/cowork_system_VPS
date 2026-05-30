#!/usr/bin/env python3
"""
P9 TIDE 首批 hit rate 一次性提醒（2026-06-18 EDT）
- 16 只 5 月持仓全部满 30 天，可算第一批完整 hit rate
- 满 30 天日期：5/6 那 7 只→6/5；5/18 那 8 只→6/17；5/19 那 1 只→6/18
- 触发后自删 crontab 条目，只发一次
背景：2026-05-30 主公确认设 6/18 完整 hit rate 提醒（B 方案）。
"""
import os
import sys
import sqlite3
import subprocess
from datetime import datetime

GUARD_DATE = "2026-06-18"
TODAY = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

if TODAY != GUARD_DATE:
    print(f"SKIP: today={TODAY} != guard={GUARD_DATE}")
    sys.exit(0)

# 查 outcome_tracking 满 30 天的样本数 + 已填 return_30d 的条数
DB = "/home/cowork/cowork/trading/trading.db"
matured = filled_30d = 0
try:
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT COUNT(*), COUNT(return_30d) FROM outcome_tracking"
    ).fetchone()
    matured, filled_30d = row[0], row[1]
    conn.close()
except Exception as e:
    print(f"WARN: DB 查询失败: {e}", file=sys.stderr)

MSG = f"""🔔 [P9 首批 hit rate 到期提醒] 2026-06-18

主公，今天 16 只 5 月持仓【全部满 30 天】了，可以算第一批完整 hit rate（命中率）。

📊 当前 outcome_tracking：共 {matured} 条，已填 return_30d 的 {filled_30d} 条

📌 今天该做的：
1️⃣ 跑一次 weekly_review / 直接查 outcome_tracking 的 return_30d 分布
2️⃣ 看：埋的这些里，几只真按叙事涨上去了（hit rate）
3️⃣ 重点验证三个假设（playbooks/p9_trading.md 底部）：
   · 假设 1：alpha 是否集中在前 5 天（90 天持仓是否过长）
   · 假设 2：低分析师覆盖股是否跑赢（池子组成是否真 edge）
   · 假设 3：alpha 窗口是否被压缩（绝对收益量级）
4️⃣ 任一假设验证为真 → 触发 v1→v2 策略切换评估

⚠️ 这是【纸账号】数据，第一批只是起点，样本仍小，别过度解读单批。

— 发送时间: {NOW} EDT"""

result = subprocess.run(
    ["python3", "/home/cowork/cowork/newscripts/send_discord_dm.py", MSG],
    capture_output=True,
    text=True,
)
if result.returncode != 0:
    print(f"ERROR: {result.stderr}", file=sys.stderr)
    sys.exit(1)
print(f"✅ P9 hit rate 提醒已发送: {result.stdout.strip()}")

# 自删本 cron 条目（一次性）
try:
    cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    kept = [ln for ln in cur.splitlines() if "p9_first_hitrate_reminder.py" not in ln]
    subprocess.run(["crontab", "-"], input="\n".join(kept) + "\n", text=True)
    print("✅ 一次性 cron 条目已自删")
except Exception as e:
    print(f"WARN: cron 自删失败（请手动 crontab -e 删除）: {e}", file=sys.stderr)

LOG = f"[{NOW} EDT] CRON[p9_first_hitrate_reminder] | matured={matured} filled_30d={filled_30d} | ✅ | 首批 hit rate 提醒已发 + cron 自删\n"
try:
    with open("/home/cowork/cowork/ops_log.md", "a") as f:
        f.write(LOG)
except Exception as e:
    print(f"WARN: ops_log 写入失败: {e}", file=sys.stderr)
