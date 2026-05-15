#!/usr/bin/env python3
"""
P9 Outcome 模板设计评估提醒（一次性）
- 触发时间：2026-05-17 18:00 EDT（weekly_review 跑完 2 小时后）
- 目的：提醒主公看 weekly_review 邮件 + 评估"是否需要补 outcome_report 工具"
- 记录文档：/home/cowork/cowork/reference/p9_outcome_template_review_pending.md
- 触发后：脚本会自动从 crontab 删除自己的 cron 条目（防重复触发）
"""
import os
import subprocess
from datetime import datetime

NOW = datetime.now().strftime("%Y-%m-%d %H:%M")
TODAY = datetime.now().strftime("%Y-%m-%d")

# 只在 2026-05-17 当天才发送（防止脚本被手动跑时意外触发）
if TODAY != "2026-05-17":
    print(f"今天 {TODAY} 不是触发日，跳过")
    exit(0)

MSG = """📬 **P9 Outcome 模板设计 - 5/17 评估提醒**

📅 上下文：5/15 下午我们讨论了 P9 outcome 分析标准模板
🤖 子 agent 发现：可能跟 weekly_review.py / quarterly_review.py 重叠
⏸️ 当时决定：等 5/17 weekly_review 第 1 次邮件出来再评估

---

📋 **现在请主公做的事**：

☐ **Step 1**：去 Gmail 看 weekly_review 邮件（应该 16:00 EDT 已发）
☐ **Step 2**：评估邮件内容
   - 包含什么维度？（return / alpha / drawdown / thesis 状态？）
   - 缺什么维度？（评分桶 / 主题分类 / catalyst 远近？）
☐ **Step 3**：决策（4 选 1）：
   - A. 啥都不做（已经够了）
   - B. 只补 invalidation_conditions 检查（30 分钟）
   - C. 做轻量跨票模板（1-2 小时）
   - D. 做 per-trade outcome 自动化（1-2 天）

---

📂 完整背景文档（含子 agent 审核结论）：
`/home/cowork/cowork/reference/p9_outcome_template_review_pending.md`

直接告诉 Claude "评估完了，选 X" 即可。

⏰ 提醒时间：{NOW} EDT
""".format(NOW=NOW)


def send_discord(msg):
    """通过 cowork bot 发到主公 DM channel"""
    DISCORD_TOKEN = None
    env_path = "/home/cowork/cowork/config/api_keys.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith("DISCORD_BOT_TOKEN="):
                    DISCORD_TOKEN = line.split("=", 1)[1].strip()
                    break

    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in api_keys.env")
        return False

    # 主公 DM channel (cowork bot DM)
    CHANNEL_ID = "1485128242808619079"

    import urllib.request
    import json

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    data = json.dumps({"content": msg}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Discord OK: {resp.status}")
            return True
    except Exception as e:
        print(f"Discord error: {e}")
        return False


def remove_self_from_crontab():
    """触发后从 crontab 删除自己的条目，防止重复触发"""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode != 0:
            return
        lines = result.stdout.split("\n")
        filtered = [l for l in lines if "p9_template_review_reminder.py" not in l]
        new_crontab = "\n".join(filtered)
        subprocess.run(["crontab", "-"], input=new_crontab, text=True)
        print("已从 crontab 删除自己")
    except Exception as e:
        print(f"crontab 清理失败（不影响功能）: {e}")


if __name__ == "__main__":
    success = send_discord(MSG)
    if success:
        remove_self_from_crontab()
        # 写日志
        log_line = f"[{NOW} EDT] CRON[P9] | template_review_reminder | ✅ | 5/17 一次性提醒已发送+自删\n"
        with open("/home/cowork/cowork/ops_log.md", "a") as f:
            f.write(log_line)
