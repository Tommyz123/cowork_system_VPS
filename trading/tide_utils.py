#!/usr/bin/env python3
"""
TIDE系统公共工具：统一失败告警。
"""
import json
import traceback
import urllib.request
from datetime import datetime
from pathlib import Path

ENV_PATH = Path("/home/cowork/cowork/config/api_keys.env")
DISCORD_ENV_PATH = Path("/home/cowork/.claude/channels/discord/.env")


def load_env():
    env = {}
    with ENV_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    if not env.get("DISCORD_BOT_TOKEN") and DISCORD_ENV_PATH.exists():
        with DISCORD_ENV_PATH.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DISCORD_BOT_TOKEN="):
                    env["DISCORD_BOT_TOKEN"] = line.split("=", 1)[1]
                    break
    return env


def _send_failure_email(env, script_name, error_text):
    api_key = env.get("BREVO_API_KEY")
    gmail_user = env.get("GMAIL_USER")
    gmail_to = env.get("GMAIL_TO")
    if not api_key or not gmail_user or not gmail_to:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M EDT")
    subject = f"⚠️ TIDE失败 - {script_name} {datetime.now().strftime('%Y-%m-%d')}"
    body = f"脚本：{script_name}\n时间：{now}\n\n错误详情：\n{error_text}"
    payload = json.dumps({
        "sender": {"name": "Cowork VPS", "email": gmail_user},
        "to": [{"email": gmail_to}],
        "subject": subject,
        "textContent": body,
    }).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={"api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception:
        pass


def run_with_alert(script_name, main_func):
    try:
        main_func()
    except Exception:
        error_text = traceback.format_exc()
        print(f"[{script_name}] 崩溃：\n{error_text}")
        try:
            env = load_env()
            _send_failure_email(env, script_name, error_text)
        except Exception:
            pass
        raise
