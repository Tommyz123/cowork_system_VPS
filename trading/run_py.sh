#!/bin/bash
# 通用 Python 脚本包装器，失败时发 Gmail 告警
# 用法：bash run_py.sh /path/to/script.py
set -e
SCRIPT="$1"
SCRIPT_NAME=$(basename "$SCRIPT" .py)
API_KEYS="/home/cowork/cowork/config/api_keys.env"
TRADING_DIR="/home/cowork/cowork/trading"

trap 'python3 - << PYEOF
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

env = {}
with open("'"$API_KEYS"'") as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

body = "P9脚本运行失败\n脚本：'"$SCRIPT_NAME"'\n时间：" + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n请检查 trading/'"$SCRIPT_NAME"'.log"
msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = "⚠️ P9运行失败 ['"$SCRIPT_NAME"'] " + datetime.now().strftime("%Y-%m-%d")
msg["From"] = env["GMAIL_USER"]
msg["To"] = env["GMAIL_TO"]
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(env["GMAIL_USER"], env["GMAIL_APP_PASSWORD"])
    s.sendmail(env["GMAIL_USER"], env["GMAIL_TO"], msg.as_string())
PYEOF
' ERR

cd "$TRADING_DIR"
python3 "$SCRIPT"
