import sys
import re
import json
from datetime import datetime

def utc_to_nyc(ts_str):
    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    try:
        from zoneinfo import ZoneInfo
        nyc_dt = dt.astimezone(ZoneInfo("America/New_York"))
        tz_abbr = nyc_dt.strftime("%Z")
        return nyc_dt.strftime(f"%Y-%m-%d %H:%M {tz_abbr}")
    except ImportError:
        from datetime import timedelta
        month = dt.month
        if 3 <= month <= 11:
            nyc_dt = dt + timedelta(hours=-4)
            return nyc_dt.strftime("%Y-%m-%d %H:%M EDT")
        else:
            nyc_dt = dt + timedelta(hours=-5)
            return nyc_dt.strftime("%Y-%m-%d %H:%M EST")

def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
        content = data.get('prompt', raw)
    except (json.JSONDecodeError, ValueError):
        content = raw

    pattern = r'ts="(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)"'
    matches = re.findall(pattern, content)

    if not matches:
        sys.exit(0)

    ts_utc = matches[-1]
    ts_nyc = utc_to_nyc(ts_utc)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"⏰ Discord消息时间：{ts_nyc}（UTC: {ts_utc}）"
        }
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
