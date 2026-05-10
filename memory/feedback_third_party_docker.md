---
name: 第三方项目Docker隔离规则
description: 遇到非我们自己写的GitHub项目/工具时，主动询问是否用Docker隔离运行
type: feedback
originSessionId: bfe57df7-8f01-40af-bab3-4584c0d2ff02
---
遇到任何第三方GitHub项目/工具（非我们自己写的），主动询问主公是否在Docker里运行。

**Why:** 第三方代码可能有恶意行为（读取文件、偷数据发外部服务器）。Docker隔离+网络监控能防住约80%常见威胁。典型案例：career-ops开源求职工具。

**How to apply:** 主公要跑第三方项目时，先问"要不要配Docker隔离？"。完整方案在BACKLOG.md（第三方项目安全沙箱条目）。现在不配，等主公说要用时再做。
