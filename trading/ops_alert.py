#!/usr/bin/env python3
"""P9 脚本失败告警：发 Brevo 邮件 + 写入 ops_log。由 run_py.sh / run_scanner.sh trap ERR 调用。"""
import sys
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

script_name = sys.argv[1] if len(sys.argv) > 1 else "unknown"
API_KEYS = "/home/cowork/cowork/config/api_keys.env"
OPS_LOG = "/home/cowork/cowork/ops_log.md"

env = {}
with open(API_KEYS) as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

now = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M EDT")

payload = json.dumps({
    "sender": {"name": "Cowork P9", "email": env.get("GMAIL_USER", "noreply@cowork.ai")},
    "to": [{"email": env["GMAIL_TO"]}],
    "subject": f"⚠️ P9运行失败 [{script_name}] {now[:10]}",
    "textContent": f"P9脚本运行失败\n脚本：{script_name}\n时间：{now}\n请检查 trading/{script_name}.log"
}).encode()
req = urllib.request.Request(
    "https://api.brevo.com/v3/smtp/email", data=payload,
    headers={"api-key": env["BREVO_API_KEY"], "Content-Type": "application/json"},
    method="POST"
)
try:
    urllib.request.urlopen(req, timeout=15)
    print(f"[ops_alert] Brevo告警已发: {script_name}")
except Exception as e:
    print(f"[ops_alert] 发送失败: {e}")

with open(OPS_LOG, "a") as f:
    f.write(f"[{now}] CRON[P9] | {script_name} | ❌ | 失败→Brevo告警已发\n")
