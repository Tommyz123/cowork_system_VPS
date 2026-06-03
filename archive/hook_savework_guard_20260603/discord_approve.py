#!/usr/bin/env python3
# Discord 授权检测：检测主公在 Discord 回复了授权关键词，自动 touch /tmp/task_approved_<实例>
import json
import os
import re
import sys
import subprocess

# 按实例推导授权 token 后缀（防三实例 /tmp token 串用）；推导失败则不授权
_INSTANCE_MAP = {
    "/home/cowork/opus_home": "BB",
    "/home/cowork/opus2_home": "CC",
    "/home/cowork": "AA",
}


def _instance():
    return _INSTANCE_MAP.get(os.environ.get("HOME", ""))


def task_token_path():
    inst = _instance()
    if inst is None:
        return None
    return f"/tmp/task_approved_{inst}"


def git_token_path():
    inst = _instance()
    if inst is None:
        return None
    return f"/tmp/git_approved_{inst}"

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

# 收工专属关键词：这类是固定全自动流程，主公说一次即授权整个流程（含 git commit/push）。
# 命中时额外 touch git_approved，让 git 守卫放行收工内的 commit/push（普通授权词不碰 git）。
SAVEWORK_KEYWORDS = ["收工", "保存进度"]

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

    token = task_token_path()
    if token is None:
        return  # 无法推导实例身份，不授权（fail-safe）

    # 检测授权关键词（边界匹配）
    for kw in APPROVE_KEYWORDS:
        if keyword_matches(kw, user_text):
            subprocess.run(["touch", token], check=False)
            # 收工专属词：额外授权 git（commit/push），让收工成为真正全自动流程
            git_token = git_token_path()
            if kw in SAVEWORK_KEYWORDS and git_token:
                # 写入 "savework" 标记（非空）：git 守卫见此标记会放行但不消耗，
                # 让一次收工授权覆盖 commit + push；手动 touch 的空 token 仍是 one-shot。
                try:
                    with open(git_token, "w") as f:
                        f.write("savework\n")
                except Exception:
                    pass
                ctx = f"✅ [收工授权] 检测到「{kw}」，已授权 {token} + {git_token}（git 放行至收工结束，不逐次消耗）"
            else:
                ctx = f"✅ [任务授权] 检测到「{kw}」，已自动授权 {token}"
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": ctx
                }
            }))
            return

if __name__ == "__main__":
    main()
