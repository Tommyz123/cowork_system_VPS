#!/usr/bin/env python3
"""UserPromptSubmit Hook: 检测评级/排名类问题，注入警告提醒禁止编造数据"""
import json
import re
import sys

RATING_PATTERN = re.compile(
    r'(什么(水平|等级|级别|段位|层次)'
    r'|算.{0,5}(高手|厉害|重度用户|大神|专家|强)'
    r'|算不算.{0,8}(高手|厉害|大神|专家|重度)'
    r'|我的.{0,6}(水平|能力).{0,4}(怎么样|如何)'
    r'|和别人比|比别人(强|厉害)'
    r'|我(厉害|牛)吗'
    r'|top\s*\d+%)',
    re.UNICODE | re.IGNORECASE
)

_CHANNEL_BODY_RE = re.compile(r'<channel[^>]*>(.*?)</channel>', re.DOTALL)


def extract_user_text(prompt: str) -> str:
    m = _CHANNEL_BODY_RE.search(prompt)
    return m.group(1).strip() if m else prompt


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        return

    prompt = data.get("prompt", "")
    user_text = extract_user_text(prompt)

    if not RATING_PATTERN.search(user_text):
        return

    warning = (
        "⚠️ [评级问题警告] 用户在问水平/等级/排名类问题。"
        "禁止编造百分比、Top X%、等级分布、「我见过的用户里」等话术。"
        "没有跨用户数据集，直接说「无法度量」，"
        "只能列用户实际做了什么，不给等级。"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": warning
        }
    }))


if __name__ == "__main__":
    main()
