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

**原则③：扩授权词表必须先跑否定句/疑问句测试（2026-06-23）**
新增授权词前，必须用「含该词的否定句/疑问句」实测——会被「就这样做不太好」「这个不可以」这类误判为授权的短词，一律不加。
判断：短词（≤3字）放进 APPROVE_KEYWORDS 靠边界 regex 兜底；够长的同意话（如"按你推荐的做"）才进 LOOSE_APPROVE_KEYWORDS 宽松包含匹配。宁可漏收一个不常用说法，也不破坏「否定句绝不放行」的安全底线。

**Why:** ①2026-05-14 修复前 "收工" 用子字符串匹配，"收工时整理文档"误授权。②2026-06-23 治"反复授权"痛点扩词表时，"就这样做" 被 "就这样做不太好" 误触发，当场撤回——这正是原则②警告的从句误触发的活案例。
**How to apply:** 修改 discord_approve.py 新增关键词前问：①是 Skill 命令吗？是→不加；②会被否定/疑问句误触发吗？写否定句测试验证，会→不加或改用边界 regex 的严格清单。改完跑回归测试覆盖：真实漏过案例（应授权）+ 原有词（不能坏）+ 否定/疑问句（安全底线，绝不放行）。
