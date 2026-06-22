#!/bin/bash
# Cowork Opus Claude Code watchdog runner
# 独立 HOME 指向 opus_home，共享 cowork/ 工作目录
# 无限循环自重启：session不存在→新建；Claude进程idle→重拉

TMUX_BIN="/usr/bin/tmux -L opus_socket"
SESSION=cowork_opus
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/home/cowork/.local/bin/claude
export HOME=/home/cowork/opus_home

while true; do
    if ! $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
        $TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official
        echo "$(date -Iseconds) [claude_opus_runner] (re)started session $SESSION" >&2
    else
        CURRENT_CMD=$($TMUX_BIN list-panes -t $SESSION -F '#{pane_current_command}' 2>/dev/null | head -1)
        if [ "$CURRENT_CMD" != "claude" ]; then
            echo "$(date -Iseconds) [claude_opus_runner] Claude idle (cmd=$CURRENT_CMD), restarting..." >&2
            $TMUX_BIN send-keys -t $SESSION "claude --channels plugin:discord@claude-plugins-official" Enter
        fi
    fi
    sleep 5
done
