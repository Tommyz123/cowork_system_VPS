#!/bin/bash
# Cowork Claude Code watchdog runner
# 起 tmux session 跑 claude，session 死了脚本退出 1，systemd Restart=on-failure 自动拉起

TMUX_BIN=/usr/bin/tmux
SESSION=cowork
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/home/cowork/.local/bin/claude

# 清残留 session（确保干净起步）
if $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
    $TMUX_BIN kill-session -t $SESSION
fi

# 起新 session（detached）
$TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official

# Watchdog: 5 秒轮询 session 存活 + Claude 活跃状态
while $TMUX_BIN has-session -t $SESSION 2>/dev/null; do
    CURRENT_CMD=$($TMUX_BIN list-panes -t $SESSION -F '#{pane_current_command}' 2>/dev/null | head -1)
    if [ "$CURRENT_CMD" != "claude" ]; then
        echo "$(date -Iseconds) [claude_runner] Claude idle (cmd=$CURRENT_CMD), restarting..." >&2
        $TMUX_BIN send-keys -t $SESSION "claude --channels plugin:discord@claude-plugins-official" Enter
    fi
    sleep 5
done

echo "$(date -Iseconds) [claude_runner] tmux session $SESSION died, exiting for systemd restart" >&2
exit 1
