# Claude Code Routines 官方规则

> 来源：官方文档 https://code.claude.com/docs/en/routines  
> 保存日期：2026-04-18

---

## 什么是 Routines

保存好的 Claude Code 配置（prompt + 仓库 + MCP连接器），在 Anthropic 云端基础设施自动运行。不需要本地电脑常开。

---

## 创建方式

**Web UI**（推荐）：claude.ai/code/routines → New routine → 填写 prompt / 选仓库 / 选触发类型 / 选环境

**CLI**：`/schedule "daily PR review at 9am"`  
- `/schedule list` — 查看所有  
- `/schedule run` — 立即触发  
- 注意：CLI 只能创建定时触发，API/GitHub 触发需在 Web 编辑

**Desktop App**：Schedule > New task > **New remote task**（不要选 New local task，那是本地定时任务）

---

## 触发类型（可组合）

### 定时触发（Scheduled）
- 预设：hourly / daily / weekdays / weekly
- 自定义：cron 表达式
- **最短间隔：1小时**（更频繁的表达式会被拒绝）
- 运行时间可能晚几分钟（固定偏移量）

### API 触发
- 创建专属 HTTP endpoint，POST 请求触发
- 需要 Bearer token（每个 Routine 独立 token）
- 可传 `text` 字段作为上下文（如告警内容）

```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/trig_01.../fire \
  -H "Authorization: Bearer sk-ant-oat01-xxxxx" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Alert details here"}'
```

### GitHub 触发
- 响应 PR / Release 事件
- 支持事件：pull_request.opened/closed, release.created 等
- 可按 author / title / branch / labels 过滤
- 每个匹配事件独立启动一个 session

---

## 网络访问权限（每个环境选一个）

| 级别 | 说明 |
|------|------|
| None | 无外网访问 |
| Trusted | 白名单域名（包管理器、GitHub、云SDK等） |
| Full | 任意域名 |
| Custom | 自定义白名单（可含默认域名） |

**发 Discord 通知需要 Full 或 Custom（加 discord.com）权限。**

Trusted 默认白名单包含：npm、PyPI、GitHub、GitLab、Docker Hub、AWS/GCP/Azure 等开发工具，**不含 Discord**。

---

## Discord 通知实现方式

没有内置 Discord 功能，但可以：

**方案1：curl webhook（推荐）**
```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Routine 完成：xxx"}'
```
- 需要把 webhook URL 存入环境变量 `DISCORD_WEBHOOK_URL`
- 网络权限需要 Full 或 Custom（允许 discord.com）

**方案2：MCP 连接器**
- 如果有 Discord MCP 连接器可加入 Routine

---

## Pro vs Max 计划差异

| 计划 | 每日运行次数 |
|------|------------|
| Pro | **5次/天** |
| Max | **15次/天** |
| Team | 25次/天 |
| Enterprise | 25次/天 |

- 超出限制：被拒绝，等次日重置
- 可开 extra usage（设置 > Billing），超额按量计费

---

## 资源限制（所有计划相同）

- 4 vCPU / 16 GB RAM / 30 GB 磁盘
- 每次运行独立 VM，**无持久化状态**（运行间数据不保留）
- 仓库每次运行重新 clone

---

## 可用工具

预装：Python 3.x / Node.js 20-22 / Ruby / PHP / Java / Go / Rust / C++ / Docker / PostgreSQL / Redis / git / jq 等

MCP 连接器：Slack、Linear、Google Drive 等（可在 Routine 里配置）

不支持：交互式 auth（AWS SSO 等）、本地文件访问

---

## 重要限制和坑

- **分支限制**：默认只能 push 到 `claude/` 前缀的分支，需手动开"Allow unrestricted branch pushes"
- **GitHub 触发限额**：超出每小时上限的事件会被丢弃
- **Bun 已知问题**：Bun 在云端 session 里包管理有代理兼容性问题
- **setup script 缓存**：~7天，只缓存文件不缓存进程（服务每次需重启）
- **secrets**：没有专门的密钥存储，环境变量对能编辑该环境的人可见，禁止硬编码 token
- **API beta header**：`experimental-cc-routine-2026-04-01`，研究预览期间可能变化
