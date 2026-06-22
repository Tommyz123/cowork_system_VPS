#!/bin/bash
# 通用 Python 脚本包装器，失败时发 Brevo 告警（含真实报错） + 写入 ops_log
# 用法：bash run_py.sh /path/to/script.py
# 注意：只服务正式 cron 脚本；临时/调试脚本请直接 python3 xxx.py 跑，避免误报告警
set -e
set -o pipefail   # 关键：让 `python3 ... | tee` 的退出码反映 python 失败，否则 tee 永远成功→trap ERR 漏触发→漏报
SCRIPT="$1"
SCRIPT_NAME=$(basename "$SCRIPT" .py)
TRADING_DIR="/home/cowork/cowork/trading"
OPS_LOG="/home/cowork/cowork/ops_log.md"
ERR_FILE=$(mktemp /tmp/p9_run_${SCRIPT_NAME}.XXXXXX.log)

# 失败时：把脚本输出末尾报错传给 ops_alert.py，邮件直接带上 Traceback
trap 'python3 /home/cowork/cowork/trading/ops_alert.py "'"$SCRIPT_NAME"'" "'"$ERR_FILE"'"; rm -f "'"$ERR_FILE"'"' ERR

cd "$TRADING_DIR"
# tee 到临时文件：终端/cron 输出照旧，同时留一份给告警读取
python3 "$SCRIPT" 2>&1 | tee "$ERR_FILE"

NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
echo "[$NOW] CRON[P9] | $SCRIPT_NAME | ✅ | 完成" >> "$OPS_LOG"
rm -f "$ERR_FILE"
