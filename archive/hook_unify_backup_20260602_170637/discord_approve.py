#!/usr/bin/env python3
# Discord 授权检测：检测主公在 Discord 回复了授权关键词，自动 touch /tmp/task_approved
import json
import re
import sys
import subprocess

sys.path.insert(0, '/home/cowork/.claude/hooks')
try:
    from _log_hit import log_hit
    log_hit("discord_approve", "UserPromptSubmit")
except Exception:
    pass

# 精确匹配关键词（要求前后是非汉字字符，或消息边界，防止"收工时/执行中"等误触发）
# "收工"是固定触发指令（直接执行），主公说收工即隐含授权收工流程内的所有文件修改
APPROVE_KEYWORDS = [
    "可以执行", "开始执行", "直接开始", "可以开始", "执行吧",
    "执行", "做吧", "去做", "好的做", "开始",
    "可以",
    "收工", "保存进度",
    "go ahead", "proceed", "approved",
]

# 从 Discord channel 标签中提取用户消息正文（去掉 XML 标签）
_CHANNEL_BODY_RE = re.compile(r'<channel[^>]*>(.*?)</channel>', re.DOTALL)


def extract_user_text(prompt: str) -> str:
    m = _CHANNEL_BODY_RE.search(prompt)
    return m.group(1).strip() if m else prompt


def keyword_matches(kw: str, text: str) -> bool:
    """关键词必须出现在句子边界（前后是空格/标点/行首尾），防止从句误触发。"""
    pattern = r'(?:^|(?<=[\s，。！？、\n]))' + re.escape(kw) + r'(?=$|[\s，。！？、\n])'
    return bool(re.search(pattern, text))


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

    user_text = extract_user_text(prompt)

    # 检测授权关键词（边界匹配）
    for kw in APPROVE_KEYWORDS:
        if keyword_matches(kw, user_text):
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
