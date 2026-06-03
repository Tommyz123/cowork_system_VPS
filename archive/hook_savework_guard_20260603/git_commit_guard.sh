#!/bin/bash
# git_commit_guard.sh - 硬拦截：git commit/push 必须等主公确认
source /home/cowork/.claude/hooks/_log_hit.sh 2>/dev/null && log_hit git_commit_guard PreToolUse:Bash

# 按实例推导授权 token 后缀（防三实例 /tmp token 串用）
case "$HOME" in
    /home/cowork/opus_home)  INSTANCE=BB ;;
    /home/cowork/opus2_home) INSTANCE=CC ;;
    /home/cowork)            INSTANCE=AA ;;
    *) echo '{"decision":"block","reason":"⛔ [实例守卫] 无法从 $HOME 推导实例身份，拒绝放行 git 操作。"}'; exit 0 ;;
esac
GIT_TOKEN="/tmp/git_approved_${INSTANCE}"

# 从 stdin 读取工具输入（Claude Code 通过 stdin 传 JSON）
STDIN_DATA=$(timeout 2 cat 2>/dev/null || echo "")

# 解析命令
COMMAND=$(echo "$STDIN_DATA" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# 拦截 Claude 自己执行 touch /tmp/task_approved（含带实例后缀的变体）
if echo "$COMMAND" | grep -qE "touch /tmp/task_approved"; then
    echo '{"decision":"block","reason":"⛔ [授权守卫] Claude 无权自行执行 touch /tmp/task_approved。请主公在 Discord 回复授权关键词（如「可以执行」）触发授权。"}'
    exit 0
fi

# 检测是否是 git commit 或 git push
if echo "$COMMAND" | grep -qE "(^|&&|\|\||;|\|)\s*git (commit|push)"; then
    # 检查解锁文件是否存在
    if [ -f "$GIT_TOKEN" ]; then
        # 收工授权（token 内容为 savework）：放行但不消耗，让一次收工覆盖 commit+push
        # 直到收工结束由 UserPromptSubmit 的 rm 清理逻辑清掉。
        # 手动 touch 的空 token：保持 one-shot（消耗后删除）。
        if grep -q "savework" "$GIT_TOKEN" 2>/dev/null; then
            exit 0
        fi
        rm "$GIT_TOKEN"
        exit 0
    fi

    echo "⚠️ [Git守卫] 拦截：git commit/push 是不可逆操作，必须先等主公确认。" >&2
    echo "" >&2
    echo "请完成以下步骤：" >&2
    echo "  1. 运行 git status + git diff，列出将要变更的文件" >&2
    echo "  2. 说明每个文件的改动内容" >&2
    echo "  3. 等主公明确确认" >&2
    echo "" >&2
    echo "主公确认后，执行以下命令解锁，然后重新 commit：" >&2
    echo "  touch $GIT_TOKEN" >&2
    exit 2
fi

exit 0
