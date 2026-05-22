---
name: feedback_discord_approve_design
description: discord_approve.py 两个设计原则：Skill命令不进授权列表+边界regex防从句误触发
type: feedback
originSessionId: f80ef6e0-4363-4121-ac5d-b927f4613745
---
discord_approve.py（UserPromptSubmit hook）的两个设计原则：

**原则①：Skill 命令不放 APPROVE_KEYWORDS**
收工/整理记忆/保存进度等 Skill 命令有自己的路由机制，不应放进授权关键词列表。
APPROVE_KEYWORDS 只管"文件修改授权"，不管 Skill 触发。

**原则②：关键词匹配必须用边界 regex**
防止"收工时/执行中/开始前"等从句误触发。
正确 pattern：`r'(?:^|(?<=[\s，。！？、\n]))' + re.escape(kw) + r'(?=$|[\s，。！？、\n])'`

**Why:** 2026-05-14 修复前，"收工" 在 APPROVE_KEYWORDS 里用子字符串匹配，导致"收工时整理文档"这类从句误授权执行收工。
**How to apply:** 修改 discord_approve.py 时，新增关键词前问：①是 Skill 命令吗？是→不加；②是否有从句误触发风险？有→用边界 regex。
