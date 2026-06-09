#!/bin/bash
# Cowork Opus Claude Code watchdog runner
# 独立 HOME 指向 opus_home，共享 cowork/ 工作目录
# 无限循环自重启，不依赖 systemd（cowork 不在 sudoers）

TMUX_BIN="/usr/bin/tmux -L opus_socket"
SESSION=cowork_opus
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/home/cowork/.local/bin/claude
export HOME=/home/cowork/opus_home

while true; do
    if ! $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
        $TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official
        echo "$(date -Iseconds) [claude_opus_runner] (re)started session $SESSION" >&2
    fi
    sleep 5
done
