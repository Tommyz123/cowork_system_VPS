---
name: feedback_discord_ts_hook
description: Discord消息ts字段解析必须先json.loads()，直接搜原始stdin会因JSON转义失败
type: feedback
---
UserPromptSubmit stdin 是 JSON 格式，必须先 `json.loads()` 解析成 Python 对象，再正则搜索 `ts` 字段；直接搜原始 stdin 字符串会失败（JSON 转义导致格式不干净）。

脚本：`cowork/scripts/discord_ts_convert.py`

**Why:** 直接搜原始 stdin 踩过坑，JSON 转义让正则匹配失败。

**How to apply:** 凡是需要从 UserPromptSubmit Hook stdin 提取 Discord 字段（ts、chat_id 等），先 json.loads() 再取字段。
