#!/bin/bash
# 机票监控日报 - cron 调用
# cron: 30 17 * * 2,4 bash /home/cowork/cowork/flightscripts/run_flight.sh >> /home/cowork/cowork/flightscripts/run.log 2>&1
# 注：cron 时间为 UTC，17:30 UTC = 13:30 EDT，每周二(2)和周四(4)运行

set -e
export PATH="/home/cowork/.local/bin:$PATH"
SCRIPTS="/home/cowork/cowork/flightscripts"
API_KEYS_ENV="/home/cowork/cowork/config/api_keys.env"
trap 'python3 - << PYEOF
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def _load_env():
    env = {}
    with open("'"$API_KEYS_ENV"'") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

env = _load_env()
body = "P6机票监控今日运行失败\n日期：" + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n请检查 flightscripts/run.log"
msg = MIMEText(body, "plain", "utf-8")
msg["Subject"] = "⚠️ P6运行失败 " + datetime.now().strftime("%Y-%m-%d")
msg["From"] = env["GMAIL_USER"]
msg["To"] = env["GMAIL_TO"]
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(env["GMAIL_USER"], env["GMAIL_APP_PASSWORD"])
    s.sendmail(env["GMAIL_USER"], env["GMAIL_TO"], msg.as_string())
    print("失败告警已发送")
PYEOF
' ERR
export SERPAPI_KEY=$(grep "^SERPAPI_KEY=" "$API_KEYS_ENV" | grep -v "SERPAPI_KEY2" | cut -d= -f2 | tr -d '[:space:]')
export SERPAPI_KEY_FALLBACK=$(grep "^SERPAPI_KEY2=" "$API_KEYS_ENV" | cut -d= -f2 | tr -d '[:space:]')
LOG_DATE=$(date +"%Y-%m-%d %H:%M")

echo "[$LOG_DATE] Starting flight monitor..."

# Step 1: 查价格，存 SQLite，输出 JSON 到临时文件
echo "[$LOG_DATE] Querying SerpAPI..."
pip install google-search-results -q --break-system-packages 2>/dev/null || true
python3 "$SCRIPTS/flight_monitor.py" > /tmp/flight_data.json 2>/tmp/flight_err.log

if [ ! -s /tmp/flight_data.json ]; then
    echo "[$LOG_DATE] ERROR: flight_monitor.py returned empty output"
    cat /tmp/flight_err.log
    exit 1
fi

# Step 2: 生成日报正文
echo "[$LOG_DATE] Building report..."
REPORT=$(python3 "$SCRIPTS/build_report.py" < /tmp/flight_data.json)

# Step 3: 用 claude 分析走势
echo "[$LOG_DATE] Analyzing with Claude..."
PROMPT=$(python3 -c "import sys,json; d=json.load(open('/tmp/flight_data.json')); print(d['prompt_for_claude'])")
(cd /tmp && claude --print --output-format text -p "$PROMPT") < /dev/null > /tmp/ai_advice.txt
AI_ADVICE=$(cat /tmp/ai_advice.txt)

FULL_REPORT="$REPORT

🤖 **AI建议：** $AI_ADVICE"

# Step 4: 发送 Email
echo "[$LOG_DATE] Sending email..."
export GMAIL_USER=$(grep GMAIL_USER /home/cowork/cowork/config/api_keys.env | cut -d= -f2 | tr -d '[:space:]')
export GMAIL_APP_PASSWORD=$(grep GMAIL_APP_PASSWORD /home/cowork/cowork/config/api_keys.env | cut -d= -f2 | tr -d '[:space:]')
export GMAIL_TO=$(grep GMAIL_TO /home/cowork/cowork/config/api_keys.env | cut -d= -f2 | tr -d '[:space:]')

python3 - <<PYEOF
import os, smtplib
from email.mime.text import MIMEText

subject = f"✈️ 机票日报 $(date +%Y-%m-%d)"
body = """$FULL_REPORT"""
html_body = "<div style='font-family:monospace;font-size:14px;line-height:1.6;padding:16px;'><pre>" + body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre></div>"
msg = MIMEText(html_body, "html", "utf-8")
msg["Subject"] = subject
msg["From"] = os.environ["GMAIL_USER"]
msg["To"] = os.environ["GMAIL_TO"]

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"])
    s.sendmail(os.environ["GMAIL_USER"], os.environ["GMAIL_TO"], msg.as_string())
    print("Email sent.")
PYEOF

echo "[$LOG_DATE] Done."
