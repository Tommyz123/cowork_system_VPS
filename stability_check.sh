#!/bin/bash
# stability_check.sh - 系统稳定性周检查
# cron: 0 17 * * 3  每周三 17:00 UTC（13:00 EDT）

BASELINE_FILE="/home/cowork/cowork/.stability_baseline"
FRICTION_LOG="/home/cowork/cowork/friction_log.md"
TOKEN=$(grep DISCORD_BOT_TOKEN /home/cowork/.claude/channels/discord/.env | cut -d= -f2 | tr -d '[:space:]')
CHANNEL="1485128242808619079"
TODAY=$(date +"%Y-%m-%d")

# 当前 friction 数量
CURRENT=$(grep -c "⚠️" "$FRICTION_LOG" 2>/dev/null || echo 0)

# 读取上次基准
if [ ! -f "$BASELINE_FILE" ]; then
    echo "$CURRENT|$TODAY" > "$BASELINE_FILE"
    echo "Baseline initialized: $CURRENT entries on $TODAY"
    exit 0
fi

LAST_COUNT=$(cut -d'|' -f1 "$BASELINE_FILE")
LAST_DATE=$(cut -d'|' -f2 "$BASELINE_FILE")
NEW=$((CURRENT - LAST_COUNT))

# 判断状态
if [ "$NEW" -eq 0 ]; then
    STATUS="✅ 稳定"
    MSG="过去一周无新摩擦记录，系统运行正常。"
elif [ "$NEW" -le 2 ]; then
    STATUS="⚠️ 轻微波动"
    MSG="新增 ${NEW} 条摩擦，建议查看 friction_log.md。"
else
    STATUS="❌ 需关注"
    MSG="新增 ${NEW} 条摩擦，建议执行「系统复盘」。"
fi

# 发送 Discord 报告
python3 - <<PYEOF
import urllib.request, json

token = "$TOKEN"
channel = "$CHANNEL"
text = """🔍 **系统稳定性周报**（${LAST_DATE} → ${TODAY}）

状态：$STATUS
新增 friction：${NEW} 条（上次 ${LAST_COUNT} → 当前 ${CURRENT}）
$MSG"""

data = json.dumps({"content": text}).encode()
req = urllib.request.Request(
    f"https://discord.com/api/v10/channels/{channel}/messages",
    data=data, method="POST",
    headers={
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://github.com, 1.0)"
    }
)
with urllib.request.urlopen(req) as r:
    print(f"Sent: {r.status}")
PYEOF

# 更新基准为本次
echo "$CURRENT|$TODAY" > "$BASELINE_FILE"
echo "[$TODAY] Stability check done. friction: $LAST_COUNT → $CURRENT (new: $NEW)"

NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
echo "[$NOW] CRON[SYS] | stability_check | ✅ | $STATUS 新增friction:${NEW}条(${LAST_COUNT}→${CURRENT})" >> /home/cowork/cowork/ops_log.md
