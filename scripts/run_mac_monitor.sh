#!/bin/bash
# Mac mini M4 价格监控 - cron 调用
# cron: 30 17 * * * bash /home/cowork/cowork/scripts/run_mac_monitor.sh >> /home/cowork/cowork/scripts/mac_monitor.log 2>&1

set -e
export PATH="/home/cowork/.local/bin:$PATH"
SCRIPTS="/home/cowork/cowork/scripts"
API_KEYS="/home/cowork/cowork/config/api_keys.env"
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
    "subject": f"⚠️ P7运行失败 {now[:10]}",
    "textContent": f"P7 Mac价格监控今日运行失败\n时间：{now}\n请检查 scripts/mac_monitor.log"
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
    f.write(f"[{now2}] CRON[P7] | mac_monitor | ❌ | 失败→Brevo告警已发\n")
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
    NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
    echo "[$NOW] CRON[P7] | mac_monitor | ✅ | 价格正常，无告警" >> "$OPS_LOG"
    exit 0
fi

# SILENT 表示价格正常，不发 Email
if echo "$REPORT" | grep -q "^SILENT:"; then
    echo "[$LOG_DATE] $REPORT"
    NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
    echo "[$NOW] CRON[P7] | mac_monitor | ✅ | 价格正常，无告警" >> "$OPS_LOG"
    exit 0
fi

echo "[$LOG_DATE] Low price detected! Sending email..."

BREVO_KEY=$(grep "^BREVO_API_KEY=" "$API_KEYS" | cut -d= -f2 | tr -d '[:space:]')
GMAIL_TO=$(grep "^GMAIL_TO=" "$API_KEYS" | cut -d= -f2 | tr -d '[:space:]')
GMAIL_USER=$(grep "^GMAIL_USER=" "$API_KEYS" | cut -d= -f2 | tr -d '[:space:]')
TODAY=$(date +%Y-%m-%d)

echo "$REPORT" > /tmp/mac_report_email.txt

python3 - << PYEOF
import json, urllib.request

brevo_key = "$BREVO_KEY"
gmail_to = "$GMAIL_TO"
gmail_user = "$GMAIL_USER"
today = "$TODAY"

with open("/tmp/mac_report_email.txt") as f:
    body = f.read()

payload = json.dumps({
    "sender": {"name": "Cowork VPS", "email": gmail_user},
    "to": [{"email": gmail_to}],
    "subject": f"🔥 Mac mini 低价提醒！{today}",
    "htmlContent": body,
}).encode()
req = urllib.request.Request("https://api.brevo.com/v3/smtp/email", data=payload,
    headers={"api-key": brevo_key, "Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(req, timeout=15)
print("Alert email sent!")
PYEOF

rm -f /tmp/mac_report_email.txt
echo "[$LOG_DATE] Done."

NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
echo "[$NOW] CRON[P7] | mac_monitor | ✅ | 低价提醒邮件已发" >> "$OPS_LOG"
