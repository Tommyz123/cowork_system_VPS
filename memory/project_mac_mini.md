---
name: Mac Mini 个人助理服务器计划
description: 主公计划购买Mac mini M4作为24小时AI助理服务器的方案和决策
type: project
originSessionId: 2e3688c5-0e19-491d-8ed7-89865661c95b
---
主公计划购买 Mac mini 作为24小时在线个人AI助理服务器，仍在考虑 M4 vs M5。

**RAM决策（2026-04-22）：** 24GB是底线（可跑Qwen 2.5 32B Q4），32GB是有余量的选择；16GB不够跑本地模型。本地模型定位是多agent架构里的低成本worker（高频廉价任务），不是secretary/记忆管理。

**Why:** 现在必须开笔记本才能用Claude Code，手机无法直接使用，需要24小时随时可用的方案。

**方案架构：**
- Mac mini 常开作为服务器
- Windows笔记本通过SSH（局域网）连接管理
- 手机通过Discord日常交互
- launchd配置Claude Code开机自启+崩溃自重启
- SSH密钥白名单，只允许指定设备连接
- 路由器绑定固定本地IP

**通信分工：**
- Discord = 实时对话、任务交互
- Email = 每日定时报告、提醒、摘要

**Email配置：**
- 发件/收件：zhitao776@gmail.com（App Password已配好，测试通过）
- cowork8939@gmail.com 新账号暂时无法生成App Password，待成熟后迁移

**How to apply:** 主公买Mac mini后按此方案配置，我负责全程协助（SSH/固定IP/launchd自启/系统迁移）。
