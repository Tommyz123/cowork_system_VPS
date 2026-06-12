#!/usr/bin/env python3
"""
趋势观察池周检提醒（趋势主线第2层）
- 每周一 09:35 EDT 提醒按观察池清单执行周检
- 调用: python3 trend_watch_reminder.py
- 清单实体: /home/cowork/cowork/trading/notes/趋势观察池.md（W1-W6 + E事件）
- 创建: 2026-06-11（趋势地图 2026-Q2 首版配套）

发送至 cowork bot DM channel（复用 send_discord_dm.py）。
"""
import subprocess
import sys
from datetime import datetime

NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

MSG = f"""📡 [周一提醒] 趋势观察池周检

按 `trading/notes/趋势观察池.md` 清单执行（对 BB 说"趋势周检"即可触发）：

🚨 下车信号：
W1 NAND 现货/合约价拐头？（TrendForce 新闻）
W2 巨头 capex 黄灯（仅财报季 1/4/7/10 月底查）
W3 光模块单周 -20%+ 或砍单新闻？

🔔 摊牌报警：
W4 Alphabet 首次单独披露 Waymo 分部 / 单城盈利？
W5 储能龙头指引上调≥20%？Tesla Q2 部署（7月初）？
W6 机器人万台级真实商业采购？

🔭 新趋势嗅探（W7，市场赶集四动静）：
本周谁家指引上调≥20%？哪个板块整体齐涨？
哪个方向≥3家巨头集体砸钱？什么东西缺货/排队/涨价？
→ 地图外新面孔 = 初筛后跑六维打分，周报汇报

⚡ 事件日历：
E1 FERC waiver 裁决（2026-06 在即）→ CEG/VST 重估
E2 四巨头 Q2 财报 7月底 | E3 GENIUS 规则 7/18 | E4 SK Hynix 赴美 8月

输出格式：无触发=一行字周报；触发=单独报警+记入观察池"命中记录"

— 发送时间: {NOW}"""

result = subprocess.run(
    ["python3", "/home/cowork/cowork/newscripts/send_discord_dm.py", MSG],
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("ERROR: " + result.stderr, file=sys.stderr)
    sys.exit(1)

print("✅ 趋势周检提醒已发送: " + result.stdout.strip())

LOG = "[" + NOW + " EDT] CRON[trend_watch_reminder] | weekly | ✅ | 趋势观察池周检提醒已发\n"
try:
    with open("/home/cowork/cowork/ops_log.md", "a") as f:
        f.write(LOG)
except Exception as e:
    print("WARN: ops_log 写入失败: " + str(e), file=sys.stderr)
