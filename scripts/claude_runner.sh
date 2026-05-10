#!/bin/bash
# Cowork Claude Code watchdog runner
# 起 tmux session 跑 claude，session 死了脚本退出 1，systemd Restart=on-failure 自动拉起

TMUX_BIN=/usr/bin/tmux
SESSION=cowork
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/usr/bin/claude

# 清残留 session（确保干净起步）
if $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
    $TMUX_BIN kill-session -t $SESSION
fi

# 起新 session（detached）
$TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official

# Watchdog: 5 秒轮询 session 存活
while $TMUX_BIN has-session -t $SESSION 2>/dev/null; do
    sleep 5
done

echo "$(date -Iseconds) [claude_runner] tmux session $SESSION died, exiting for systemd restart" >&2
exit 1
