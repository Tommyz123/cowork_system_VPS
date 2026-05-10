#!/bin/bash
# Cowork 每日云端加密备份
# 范围：/home/cowork/cowork/ 全部 (排除 personal/personal.db/config/api_keys.env/*.log/__pycache__/.git)
# 目标：gcrypt: (= gdrive:cowork-backup-encrypted/，AES-256 加密)
# 历史：覆盖/删除的文件移到 gcrypt:_history/{YYYY-MM-DD}/
# cron: 每天 02:00 EDT
set -eo pipefail

DATE=$(date +%Y-%m-%d)
LOG=/home/cowork/cowork/scripts/rclone_backup.log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始备份 ===" >> "$LOG"

rclone sync /home/cowork/cowork/ gcrypt:current/ \
    --backup-dir "gcrypt:_history/$DATE/" \
    --transfers 4 \
    --exclude "personal/**" \
    --exclude "personal.db" \
    --exclude "config/api_keys.env" \
    --exclude "*.log" \
    --exclude "**/__pycache__/**" \
    --exclude ".git/**" \
    --exclude "scripts/rclone_backup.log" \
    --log-file "$LOG" \
    --log-level INFO

CLOUD_SIZE=$(rclone size gcrypt: 2>&1 | tail -1)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 备份完成 ($CLOUD_SIZE) ===" >> "$LOG"
