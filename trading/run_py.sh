#!/bin/bash
# 通用 Python 脚本包装器，失败时发 Brevo 告警 + 写入 ops_log
# 用法：bash run_py.sh /path/to/script.py
set -e
SCRIPT="$1"
SCRIPT_NAME=$(basename "$SCRIPT" .py)
TRADING_DIR="/home/cowork/cowork/trading"
OPS_LOG="/home/cowork/cowork/ops_log.md"

trap 'python3 /home/cowork/cowork/trading/ops_alert.py "'"$SCRIPT_NAME"'"' ERR

cd "$TRADING_DIR"
python3 "$SCRIPT"

NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
echo "[$NOW] CRON[P9] | $SCRIPT_NAME | ✅ | 完成" >> "$OPS_LOG"
