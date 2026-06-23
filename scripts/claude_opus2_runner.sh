#!/bin/bash
# Cowork Opus2 Claude Code watchdog runner
# 第 3 个独立 claude 实例（=CC），HOME=opus2_home，DM 频道 1509045714808737842
# 注：1466957346310717636 是 guild「TT基地」ID，非频道号，勿混淆（见 memory/feedback_instance_mapping.md）
# 无限循环自重启：session不存在→新建；Claude进程idle→重拉

TMUX_BIN="/usr/bin/tmux -L opus2_socket"
SESSION=cowork_opus2
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/home/cowork/.local/bin/claude
export HOME=/home/cowork/opus2_home

while true; do
    if ! $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
        $TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official
        echo "$(date -Iseconds) [claude_opus2_runner] (re)started session $SESSION" >&2
    else
        CURRENT_CMD=$($TMUX_BIN list-panes -t $SESSION -F '#{pane_current_command}' 2>/dev/null | head -1)
        if [ "$CURRENT_CMD" != "claude" ]; then
            echo "$(date -Iseconds) [claude_opus2_runner] Claude idle (cmd=$CURRENT_CMD), restarting..." >&2
            $TMUX_BIN send-keys -t $SESSION "claude --channels plugin:discord@claude-plugins-official" Enter
        fi
    fi
    sleep 5
done
