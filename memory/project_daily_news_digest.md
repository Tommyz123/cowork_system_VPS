---
name: Daily News Digest 配置
description: 每日新闻定时任务配置情况和用户新闻偏好
type: project
originSessionId: 537ea206-ab28-4b2f-b682-aed45c8289c9
---
## 定时任务配置（当前：WSL cron + claude CLI，最终方案）
- 平台: WSL cron（本地，电脑需开着）
- 时间: 每天 13:00 EDT (cron: 0 17 * * *)
- 脚本: `/mnt/c/Users/zhi89/Desktop/cowork/newscripts/run_daily_news.sh`
- 原理: cron 触发 → Python 抓 RSS → claude --print 生成 AI 总结 → Python 发 Discord
- 日志: `/mnt/c/Users/zhi89/Desktop/cowork/newscripts/run.log`

**Why:** 需要 AI 总结（🧠 AI点评），而 Anthropic CCR 云端无对外网络，GitHub Actions 无 claude CLI；本地方案可直接调用 claude --print，不需要额外 API key

**How to apply:** 修改格式/来源 → 改 run_daily_news.sh 中的 claude prompt 或 daily_news.py RSS 来源

## 用户新闻偏好
分类：政治/地缘（影响市场的）、股市/宏观、虚拟币、AI技术、大麻(NY)

**过滤逻辑：** 只要跟美国市场直接相关的。以色列/伊朗要（因为美国下场了），纯人道主义新闻不要。

**格式要求：**
1. 事实描述（2-3句，含具体数字）
2. 🧠 AI 点评（我的判断 + 对读者实际影响 + 是否值得行动）

每条必须有真实文章链接，不能用 RSS feed 地址代替。
