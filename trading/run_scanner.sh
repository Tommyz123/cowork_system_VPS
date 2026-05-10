#!/bin/bash
set -eo pipefail
API_KEYS="/home/cowork/cowork/config/api_keys.env"
trap 'python3 - << PYEOF
import os, smtplib
from email.mime.text import MIMEText
from datetime import datetime

env = {}
with open("'"$API_KEYS"'") as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

body = "TIDE季度扫描失败\n时间：" + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n请检查 trading/run_scanner.log"
msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = "⚠️ TIDE失败 - run_scanner " + datetime.now().strftime("%Y-%m-%d")
msg["From"] = env["GMAIL_USER"]
msg["To"] = env["GMAIL_TO"]
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(env["GMAIL_USER"], env["GMAIL_APP_PASSWORD"])
    s.sendmail(env["GMAIL_USER"], env["GMAIL_TO"], msg.as_string())
PYEOF
' ERR

cd /home/cowork/cowork
echo "=== $(date) 开始季度扫描 ==="
python3 trading/screener.py
python3 trading/cognitive_scanner.py
echo "=== $(date) 季度扫描完成 ==="
