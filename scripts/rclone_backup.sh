#!/bin/bash
# Cowork 每日云端加密备份
# 范围：/home/cowork/cowork/ 全部（只排除 .git）
# 目标：gcrypt: (= gdrive:cowork-backup-encrypted/，AES-256 加密)
# 策略：镜像同步，只保留最新版本，不保留历史
# cron: 每天 02:00 EDT
set -eo pipefail

LOG=/home/cowork/cowork/scripts/rclone_backup.log

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 开始备份 ===" >> "$LOG"

rclone sync /home/cowork/cowork/ gcrypt:current/ \
    --transfers 4 \
    --exclude ".git/**" \
    --log-file "$LOG" \
    --log-level INFO

CLOUD_SIZE=$(rclone size gcrypt:current/ 2>&1 | tail -1)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 备份完成 ($CLOUD_SIZE) ===" >> "$LOG"
