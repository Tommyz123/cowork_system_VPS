---
name: 时区规则
description: 主公在纽约，所有时间必须用纽约时间（EDT/EST）表达，不说UTC
type: feedback
originSessionId: b769602c-d31f-44f4-88dc-c7f33006fd41
---
永远用纽约时间（EDT = UTC-4 夏令，EST = UTC-5 冬令）和主公沟通时间。
不说 UTC，不说"16:00 UTC"，直接说"12PM 纽约时间"。

**Why:** 主公说 UTC 让他"云里雾里"，2026-04-20 明确要求，且已纠正多次。

**How to apply:**
- cron 设置时内部用 UTC 计算，但向主公汇报时只说纽约时间
- 看到 Discord 消息的 ts 字段（UTC）时，必须先减4小时（EDT）换算再使用，不能直接读 ts 数字就说时间
- 判断"现在几点"时，先从 ts 换算 EDT，不依赖系统时间直觉
