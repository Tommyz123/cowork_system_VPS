#!/bin/bash
set -eo pipefail
API_KEYS="/home/cowork/cowork/config/api_keys.env"
OPS_LOG="/home/cowork/cowork/ops_log.md"

trap 'python3 /home/cowork/cowork/trading/ops_alert.py "run_scanner"' ERR

cd /home/cowork/cowork
echo "=== $(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT") 开始季度扫描 ==="
python3 trading/screener.py
python3 trading/cognitive_scanner.py
echo "=== $(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT") 季度扫描完成 ==="

NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
echo "[$NOW] CRON[P9] | run_scanner | ✅ | 季度扫描完成（screener+cognitive_scanner）" >> "$OPS_LOG"
