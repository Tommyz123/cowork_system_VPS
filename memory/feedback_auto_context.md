---
name: feedback_auto_context
description: 新对话开始需要处理任务时，主动读取 Desktop/cowork/context.md，无需等主公提醒
type: feedback
---

每次新对话，当主公发出任何需要操作文件、查找内容或处理项目的请求时，必须主动执行以下步骤，无需主公提醒：

1. 请求访问桌面目录（~/Desktop）
2. 读取 `Desktop/cowork/context.md`
3. 基于内容了解文件结构后再开始工作

**Why:** context.md 是主公电脑的全局索引，不读它就相当于不知道文件在哪里，每次都要重新探索。

**How to apply:** 纯聊天或简单问答不需要读。一旦涉及"找文件"、"处理项目"、"访问文件夹"等操作，立即主动读取。
