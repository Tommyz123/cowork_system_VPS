#!/bin/bash
# Cowork Opus Claude Code watchdog runner
# 独立 HOME 指向 opus_home，共享 cowork/ 工作目录

TMUX_BIN=/usr/bin/tmux
SESSION=cowork_opus
WORKDIR=/home/cowork/cowork
CLAUDE_BIN=/usr/bin/claude
export HOME=/home/cowork/opus_home

# 清残留 session
if $TMUX_BIN has-session -t $SESSION 2>/dev/null; then
    $TMUX_BIN kill-session -t $SESSION
fi

# 起新 session
$TMUX_BIN new-session -d -s $SESSION -c $WORKDIR $CLAUDE_BIN --channels plugin:discord@claude-plugins-official

# Watchdog: 5 秒轮询 session 存活
while $TMUX_BIN has-session -t $SESSION 2>/dev/null; do
    sleep 5
done

echo "$(date -Iseconds) [claude_opus_runner] tmux session $SESSION died, exiting for systemd restart" >&2
exit 1
