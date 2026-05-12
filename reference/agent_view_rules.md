# Claude Code Agent View 参考

> 调研日期：2026-05-12
> 来源：派 claude-code-guide subagent 抓取官方文档（2 次）
> 用途：下次主公或 Claude 问起 Agent View 时直接读此文件，不再重复调研浪费 token

---

## 一、是什么

Claude Code 在 **2026-05-11** 发布的新功能，通过 `claude agents` 命令打开 CLI 仪表板，集中管理多个独立后台会话。

**状态：** Research Preview（接口和快捷键可能变化）
**要求：** Claude Code v2.1.139+ + Pro / Max / Team / Enterprise / Claude API 订阅

**官方文档：**
- https://code.claude.com/docs/en/agent-view
- https://claude.com/blog/agent-view-in-claude-code

---

## 二、核心能力

| 能力 | 说明 |
|---|---|
| **一屏看所有会话** | 状态分组（运行中/等待输入/已完成/失败），按目录或状态聚合 |
| **后台启动任务** | `claude --bg "任务"` 直接后台启动；或 `/bg` 命令把当前会话背景化 |
| **窥视+内联回复** | 不进入完整对话，`Space` 看最后一轮内容，可直接内联回复 |
| **自动 git worktree** | 每个后台会话自动创建独立 `.claude/worktrees/` 隔离目录，并行不冲突 |
| **多任务并行** | 同时跑多个独立任务，**每个消耗独立配额** |

**关键交互快捷键：**
- `claude agents` — 打开仪表板
- `←` — 从任何会话快速后台化并返回仪表板
- `Space` — 窥视会话最后一轮
- `Enter` — 附加到完整对话

---

## 三、限制

- **本地运行**：会话跑在你本地 Claude Code 进程里，**机器睡眠就停**
- **不能跨设备**：Windows 上开的 Agent View 会话，iPhone 看不到
- **删除时连带删除**：删会话时 git worktree 也一起被删
- **状态 Research Preview**：接口/快捷键可能变化

---

## 四、和现有工具的对比

| 工具 | 定位 | 通信机制 | 适用场景 |
|---|---|---|---|
| **Sub-agent** | 单会话内分派子任务 | 单会话内工具调用 | 一个会话里"派活"给子 agent，子 agent 完成后返回结果 |
| **Agent View** | 多独立后台会话仪表板 | ❌ **agent 间不能直接通信**——只 report to you | 多个独立任务并行跑，人工调度 |
| **Agent Teams** | 多会话协作 | ✅ "coordinate multiple sessions that **message each other**" | 多个 agent 互相协作通信（这才是协作工具） |

**关键事实（来自官方文档）：**
> "Sessions in agent view run independently and report only to you"

意思是：Agent View 里的 agent 之间**不能**直接发消息/对话，**没有** shared context / shared memory 机制，**不能**程序化互相启动。

需要 agent 间协作 → 应该用 **Agent Teams**，不是 Agent View。

---

## 五、对 cowork 系统的适用性结论

### 🔴 不启用，理由：

1. **使用场景不匹配**
   - Agent View 给的是"本地多窗口集中显示"
   - cowork 用 Discord 远程遥控（VPS + 双 bot），不是本地多窗口
   - 本质架构不同

2. **核心能力已有替代**
   - 远程触发任务 → Discord plugin ✅
   - 后台跑任务 → cron / systemd ✅
   - 异步结果推送 → Discord message ✅
   - 多 bot 架构 → cowork + opus_CC（虽然是固定 2 个，不是动态多个）

3. **缺失的 30% 用不到**
   - 动态创建多个临时会话 → 主公工作模式是单会话深度对话，用不到
   - 自动 git worktree 隔离 → 主公一次专注一件事，不会同时改同份代码
   - 多任务独立配额 → 瓶颈是注意力，不是并发数

4. **本地依赖问题**
   - Agent View 跑在本地，机器睡眠就停
   - 主公 VPS 是 24/7，但 Agent View 是本地工具，跨设备遥控反而不擅长

### 🟢 什么时候可能启用：

如果未来主公的工作模式变成"同时跑 3-4 个独立长任务（写求职信 + 改代码 + 分析竞品）"，并且**留在本地终端工作**（不靠 Discord 遥控），那时可重新评估。

目前没有这个需求。

---

## 六、调研记录（防止重复查）

**第一次调研（2026-05-12 上午）：**
- 关键词：agent view / FleetView
- 调研问题：是什么、能做什么、怎么用、稳定性、门槛
- subagent：claude-code-guide
- 关键发现：是多后台会话仪表板，Research Preview

**第二次调研（2026-05-12 上午）：**
- 关键词：agent 之间能否传信息 / shared memory / agent 互相调用
- subagent：claude-code-guide
- 关键发现：agent 间**不能**直接通信，**Agent Teams** 才是为协作设计的（不同功能）

**下次需要查 Agent Teams 时**：
- 派 claude-code-guide subagent
- URL 提示：官方有 `/en/agents` 和 `/en/agent-teams` 文档
- 重点查"sessions that message each other"的具体机制
