#!/bin/bash
# Cowork Opus2 Claude Code watchdog runner
# 第 3 个独立 claude 实例，HOME=opus2_home，监听 Discord 频道 1466957346310717636
# 无限循环自重启，由 systemd 或手动启动

TMUX_BIN="/usr/bin/tmux -L opus2_socket"
SESSION=cowork_opus2
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/home/cowork/.local/bin/claude
export HOME=/home/cowork/opus2_home

while true; do
    if ! $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
        $TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official
        echo "$(date -Iseconds) [claude_opus2_runner] (re)started session $SESSION" >&2
    fi
    sleep 5
done
