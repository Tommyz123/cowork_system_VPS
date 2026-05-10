---
name: 写入即扫描（Write Triggers Scan）
description: 每次更新playbook或memory文件时，自动扫描同项目相关文档是否有过时内容需清理
type: feedback
originSessionId: fb2ad148-a891-4de5-9022-d0c801600b4e
---
每次更新playbook或memory文件时，必须自动扫描同一项目的相关文档（其他memory条目、playbook区块、CURRENT_SESSION）是否有内容与本次更新冲突或已过时，有则一并清理。

**Why:** 不能只等"确认是停用/重大转向/功能删除"才触发清理——那个判断本身容易漏。直接绑定到"写操作"上更可靠，防止旧信息污染新对话（P9案例：AAPL/RSI/MACD两次混入TIDE系统对话）。

**How to apply:** 适用于所有项目，任何playbook/memory写入时触发。扫描范围：同项目相关的memory条目、playbook区块、CURRENT_SESSION说明。发现冲突/过时内容 → 同步清理。
