---
name: feedback_preview_before_execute
description: 涉及视觉输出（HTML邮件/UI改动）的任务，必须先生成样本预览发给主公确认，再执行
type: feedback
originSessionId: de13293d-0df9-45a3-a72c-1a0b8eda8f03
---
涉及 HTML 邮件格式、邮件排版、或任何用户可见的视觉输出改动，执行前必须先生成样本预览发到 Discord，等主公说"可以"/"同意"后再动文件。

**Why:** 2026-04-23 P7 Mac 价格监控 HTML 改动，在主公说"先发样本"之前就已执行完，顺序搞反了被主公纠正。主公明确要求："做之前先发出样本给我看一下，同意了，然后才继续执行"，并说"以后都这样执行"。

**How to apply:**
- 触发场景：修改邮件格式（plain→html）、改邮件 prompt 模板、修改 Discord 消息格式
- 步骤：① 先用 Python 生成 HTML 样本（用模拟数据），② 将样本发到 Discord（可贴代码块或用 Playwright 截图），③ 等主公确认，④ 再执行 `touch /tmp/task_approved` 并修改文件
- 注意：这步在 task_approved 流程之前，属于"展示效果预览"，不是替代审批，是额外加的前置步骤
