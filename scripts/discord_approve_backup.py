#!/usr/bin/env python3
# Discord 授权检测：检测主公在 Discord 回复了授权关键词，自动 touch /tmp/task_approved
import json
import sys
import subprocess

APPROVE_KEYWORDS = [
    "可以执行", "开始执行", "直接开始", "可以开始", "执行吧",
    "执行", "做吧", "去做", "好的做", "开始",
    "可以",
    "收工",  # 收工指令本身即全程授权
    "go ahead", "proceed", "approved",
]

def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        return

    # 只处理 Discord 消息
    prompt = data.get("prompt", "")
    if 'source="plugin:discord:discord"' not in prompt and "source=\"plugin:discord:discord\"" not in prompt:
        return

    # 检测授权关键词
    for kw in APPROVE_KEYWORDS:
        if kw in prompt:
            subprocess.run(["touch", "/tmp/task_approved"], check=False)
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"✅ [任务授权] 检测到「{kw}」，已自动授权 task_approved"
                }
            }))
            return

if __name__ == "__main__":
    main()
