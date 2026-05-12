#!/usr/bin/env python3
"""
NY 大麻 December Queue 诉讼追踪提醒
- 周一 09:00 EDT: 常规周提醒（查 NYSCEF docket）
- 关键日 (2026-05-29/30/31): 特别提醒
- 调用: python cannabis_docket_reminder.py [weekly|critical]

发送至 cowork bot DM channel (1485128242808619079)。
案件: Organic Blooms LLC v. NYS CCB, Index No. 904497-24, Albany County Supreme Court。
追踪文档: /home/cowork/legal_library/18_Organic_Blooms_v_CCB_Tracking.md
"""
import os
import sys
from datetime import datetime
import subprocess

MODE = sys.argv[1] if len(sys.argv) > 1 else "weekly"

NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

if MODE == "critical":
    HEADER = "🚨 [关键日提醒] NY 大麻 December Queue 诉讼"
    EXTRA = (
        "\n⚡ **今天是 OCM 答辩或和解关键节点附近**\n"
        "5/29: OCM 答辩 deadline（已延期自 5/8）\n"
        "5/30-31: 后续 reply / 和解可能公告\n"
    )
else:
    HEADER = "🔔 [周一提醒] NY 大麻 December Queue 诉讼追踪"
    EXTRA = ""

MSG = f"""{HEADER}

📋 案号: Index No. **904497-24**
⚖️ 案件: Organic Blooms LLC v. NYS Cannabis Control Board
🏛️ 法院: Albany County Supreme Court
👨‍⚖️ 法官: Hon. Sharon A. Graff, J.S.C.
{EXTRA}
⏰ 下个关键节点: **2026-05-29**（OCM 答辩或和解 deadline）

📌 今天该做的:
1️⃣ 登录 NYSCEF: https://iapps.courts.state.ny.us/nyscef/CaseSearch
2️⃣ 查询 Index No. 904497-24
3️⃣ 看最近 7 天 docket 有无新 Doc（最新已知 Doc 112，2026-05-01）
4️⃣ 重点关注: 法官 order / 双方信件 / 和解 stipulation

📁 本地追踪文档: legal_library/18_Organic_Blooms_v_CCB_Tracking.md

💡 最新状态 (2026-05-01 Doc 112):
"the parties are continuing their efforts to reach a settlement"
OCM 在积极审视和解方案，原告同意延期 → 友好谈判中

— 发送时间: {NOW}"""

# 调用 send_discord_dm.py 发消息
result = subprocess.run(
    ["python3", "/home/cowork/cowork/newscripts/send_discord_dm.py", MSG],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print(f"ERROR: {result.stderr}", file=sys.stderr)
    sys.exit(1)

print(f"✅ 提醒已发送 ({MODE}): {result.stdout.strip()}")

# 写入 ops_log
LOG = f"[{NOW} EDT] CRON[cannabis_docket_reminder] | mode={MODE} | ✅ | 案号 904497-24 提醒已发\n"
try:
    with open("/home/cowork/cowork/ops_log.md", "a") as f:
        f.write(LOG)
except Exception as e:
    print(f"WARN: ops_log 写入失败: {e}", file=sys.stderr)
