---
name: Daily News Digest 配置
description: 每日新闻日报编辑决策：新闻分类偏好、过滤逻辑、格式要求
type: project
originSessionId: 537ea206-ab28-4b2f-b682-aed45c8289c9
---

**Why:** 需要 AI 总结（AI点评），本地 cron + claude --print 方案无需额外 API key；操作配置见 VPS 脚本。

## 用户新闻偏好
分类：政治/地缘（影响市场的）、股市/宏观、虚拟币、AI技术、大麻(NY)

**过滤逻辑：** 只要跟美国市场直接相关的。以色列/伊朗要（因为美国下场了），纯人道主义新闻不要。

**格式要求：**
1. 事实描述（2-3句，含具体数字）
2. 🧠 AI 点评（我的判断 + 对读者实际影响 + 是否值得行动）

每条必须有真实文章链接，不能用 RSS feed 地址代替。
