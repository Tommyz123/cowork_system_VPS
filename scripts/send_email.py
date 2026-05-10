import json
import os
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

API_KEYS_PATH = "/home/cowork/cowork/config/api_keys.env"

def _load_env():
    env = {}
    with open(API_KEYS_PATH) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

_env = _load_env()
GMAIL_USER = _env.get("GMAIL_USER")
BREVO_API_KEY = _env.get("BREVO_API_KEY")
GMAIL_TO = _env.get("GMAIL_TO")


def send_email(subject: str, body: str, to: str = None, html: bool = False):
    recipient = to or GMAIL_TO
    content_key = "htmlContent" if html else "textContent"
    payload = json.dumps({
        "sender": {"name": "Cowork VPS", "email": GMAIL_USER},
        "to": [{"email": recipient}],
        "subject": subject,
        content_key: body,
    }).encode()
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=15)


if __name__ == "__main__":
    send_email("测试邮件", "邮件配置成功！来自 cowork8939@gmail.com")
    print("发送成功")
