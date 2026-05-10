#!/bin/bash
# Mac mini M4 价格监控 - cron 调用
# cron: 30 17 * * * bash /home/cowork/cowork/scripts/run_mac_monitor.sh >> /home/cowork/cowork/scripts/mac_monitor.log 2>&1
# 注：17:30 UTC = 13:30 EDT，每天运行，只在低于目标价时发Email

set -e
export PATH="/home/cowork/.local/bin:$PATH"
SCRIPTS="/home/cowork/cowork/scripts"
API_KEYS="/home/cowork/cowork/config/api_keys.env"
trap 'python3 - << PYEOF
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def _load_env():
    env = {}
    with open("'"$API_KEYS"'") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

env = _load_env()
body = "P7 Mac价格监控今日运行失败\n日期：" + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n请检查 scripts/mac_monitor.log"
msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = "⚠️ P7运行失败 " + datetime.now().strftime("%Y-%m-%d")
msg["From"] = env["GMAIL_USER"]
msg["To"] = env["GMAIL_TO"]
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(env["GMAIL_USER"], env["GMAIL_APP_PASSWORD"])
    s.sendmail(env["GMAIL_USER"], env["GMAIL_TO"], msg.as_string())
    print("失败告警已发送")
PYEOF
' ERR
LOG_DATE=$(date +"%Y-%m-%d %H:%M")

echo "[$LOG_DATE] Starting Mac mini price monitor..."

REPORT=$(python3 "$SCRIPTS/mac_monitor.py" 2>/tmp/mac_err.log) || {
    echo "[$LOG_DATE] mac_monitor.py failed:"
    cat /tmp/mac_err.log 2>/dev/null || true
    exit 1
}

if [ -z "$REPORT" ]; then
    echo "[$LOG_DATE] No output from mac_monitor.py."
    exit 0
fi

# SILENT表示价格正常，不发Email
if echo "$REPORT" | grep -q "^SILENT:"; then
    echo "[$LOG_DATE] $REPORT"
    exit 0
fi

echo "[$LOG_DATE] Low price detected! Sending email..."

export GMAIL_USER=$(grep GMAIL_USER /home/cowork/cowork/config/api_keys.env | cut -d= -f2 | tr -d '[:space:]')
export GMAIL_APP_PASSWORD=$(grep GMAIL_APP_PASSWORD /home/cowork/cowork/config/api_keys.env | cut -d= -f2 | tr -d '[:space:]')
export GMAIL_TO=$(grep GMAIL_TO /home/cowork/cowork/config/api_keys.env | cut -d= -f2 | tr -d '[:space:]')

echo "$REPORT" > /tmp/mac_report_email.txt

python3 - << 'PYEOF'
import os, smtplib
from email.mime.text import MIMEText
from datetime import datetime

with open("/tmp/mac_report_email.txt") as f:
    body = f.read()
subject = f"🔥 Mac mini 低价提醒！{datetime.now().strftime('%Y-%m-%d')}"

msg = MIMEText(body, "html", "utf-8")
msg["Subject"] = subject
msg["From"] = os.environ["GMAIL_USER"]
msg["To"] = os.environ["GMAIL_TO"]

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"])
    s.sendmail(os.environ["GMAIL_USER"], os.environ["GMAIL_TO"], msg.as_string())
    print("Alert email sent!")
PYEOF

rm -f /tmp/mac_report_email.txt
echo "[$LOG_DATE] Done."
