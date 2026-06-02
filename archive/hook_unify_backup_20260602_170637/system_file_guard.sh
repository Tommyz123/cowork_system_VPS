#!/bin/bash
# system_file_guard.sh - 任务级别文件修改守卫
# 策略：白名单文件（日志/进度/临时）直接放行；其他文件需要 /tmp/task_approved token
source /home/cowork/.claude/hooks/_log_hit.sh 2>/dev/null && log_hit system_file_guard PreToolUse:Edit_Write

STDIN_DATA=$(timeout 2 cat 2>/dev/null || echo "")

# 解析目标文件路径
FILE_PATH=$(echo "$STDIN_DATA" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', {})
    print(ti.get('file_path', ti.get('path', '')))
except:
    print('')
" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# 白名单：这些路径/文件名直接放行（无需任务审批）
WHITELIST=(
    "/tmp/"
    "cowork_log.md"
    "CURRENT_SESSION.md"
    "friction_log.md"
    "INSIGHTS.md"
    "auto_pending.md"
    "/archive/"
    "/.claude/"
    "cowork_log_2026"
    "run.log"
    ".log"
)

for w in "${WHITELIST[@]}"; do
    if [[ "$FILE_PATH" == *"$w"* ]]; then
        exit 0  # 白名单文件，直接放行
    fi
done

# 检查任务级别授权 token（整个任务有效，不消耗）
if [ -f /tmp/task_approved ]; then
    exit 0  # 已有任务授权，放行
fi

# 拦截：提示 Claude 先汇报计划、等主公确认
BASENAME=$(basename "$FILE_PATH")
echo "⚠️ [任务守卫] 拦截：准备修改 $BASENAME" >&2
echo "" >&2
echo "请先完成以下步骤：" >&2
echo "  1. 列出本次任务将修改的所有文件和改动内容" >&2
echo "  2. 通过 Discord 发送计划，等主公确认" >&2
echo "  3. 主公确认后执行：touch /tmp/task_approved" >&2
echo "  4. 任务完成后执行：rm -f /tmp/task_approved" >&2
exit 2
