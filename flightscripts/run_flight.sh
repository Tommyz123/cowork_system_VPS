#!/bin/bash
# 机票监控日报 - cron 调用
# cron: 30 17 * * 2,4 bash /home/cowork/cowork/flightscripts/run_flight.sh >> /home/cowork/cowork/flightscripts/run.log 2>&1

set -e
export PATH="/home/cowork/.local/bin:$PATH"
SCRIPTS="/home/cowork/cowork/flightscripts"
API_KEYS_ENV="/home/cowork/cowork/config/api_keys.env"
OPS_LOG="/home/cowork/cowork/ops_log.md"

trap 'python3 - << '"'"'PYEOF'"'"'
import json, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

def _load_env():
    env = {}
    with open("/home/cowork/cowork/config/api_keys.env") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

env = _load_env()
now = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M EDT")
payload = json.dumps({
    "sender": {"name": "Cowork VPS", "email": env["GMAIL_USER"]},
    "to": [{"email": env["GMAIL_TO"]}],
    "subject": f"⚠️ P6运行失败 {now[:10]}",
    "textContent": f"P6机票监控今日运行失败\n时间：{now}\n请检查 flightscripts/run.log"
}).encode()
req = urllib.request.Request("https://api.brevo.com/v3/smtp/email", data=payload,
    headers={"api-key": env["BREVO_API_KEY"], "Content-Type": "application/json"}, method="POST")
try:
    urllib.request.urlopen(req, timeout=15)
    print("失败告警已发送")
except Exception as e:
    print(f"告警发送失败: {e}")

now2 = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M EDT")
with open("/home/cowork/cowork/ops_log.md", "a") as f:
    f.write(f"[{now2}] CRON[P6] | flight_monitor | ❌ | 失败→Brevo告警已发\n")
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

# Step 4: 发送 Email（Brevo HTTP API）
echo "[$LOG_DATE] Sending email..."
BREVO_KEY=$(grep "^BREVO_API_KEY=" "$API_KEYS_ENV" | cut -d= -f2 | tr -d '[:space:]')
GMAIL_TO=$(grep "^GMAIL_TO=" "$API_KEYS_ENV" | cut -d= -f2 | tr -d '[:space:]')
GMAIL_USER=$(grep "^GMAIL_USER=" "$API_KEYS_ENV" | cut -d= -f2 | tr -d '[:space:]')
TODAY=$(date +%Y-%m-%d)

python3 - << PYEOF
import json, urllib.request

brevo_key = "$BREVO_KEY"
gmail_to = "$GMAIL_TO"
gmail_user = "$GMAIL_USER"
today = "$TODAY"
body_text = """$FULL_REPORT"""
html_body = "<div style='font-family:monospace;font-size:14px;line-height:1.6;padding:16px;'><pre>" + body_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre></div>"

payload = json.dumps({
    "sender": {"name": "Cowork VPS", "email": gmail_user},
    "to": [{"email": gmail_to}],
    "subject": f"✈️ 机票日报 {today}",
    "htmlContent": html_body,
}).encode()
req = urllib.request.Request("https://api.brevo.com/v3/smtp/email", data=payload,
    headers={"api-key": brevo_key, "Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(req, timeout=15)
print("Email sent.")
PYEOF

echo "[$LOG_DATE] Done."

NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
echo "[$NOW] CRON[P6] | flight_monitor | ✅ | 机票日报发送完成" >> "$OPS_LOG"
