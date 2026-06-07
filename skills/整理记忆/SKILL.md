---
name: 整理记忆
description: 执行 cowork 系统的记忆整理流程。主公说"整理记忆"时触发。处理 auto_pending 待审条目、扫描增量来源、写入正式 memory/ 文件、更新 MEMORY.md 索引。
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

# 整理记忆流程

> 按顺序执行以下步骤，每步完成后报告结果，不要跳步。

---

## 步骤0：处理 auto_pending.md

读 `/home/cowork/.claude/projects/-home-cowork-cowork/memory/auto_pending.md`，检查有无 `[` 开头的待审条目。

- **无**：直接进入步骤1
- **有**：通过 Discord reply 列出所有条目，每条附上建议处理方式（✅写入 / ❌删除），**然后停在这里等主公回复**。收到回复后按指示处理，再继续步骤1。禁止使用 AskUserQuestion 弹窗（主公在 Discord 遥控，看不到 UI 弹窗）。

---

## 步骤1：确定增量扫描范围

读取 `CURRENT_SESSION.md` 中的 `last_memory_sync` 时间戳。

只扫 `last_memory_sync` 时间戳之后的 `cowork_log.md` 条目和 Discord 消息（无时间戳则全量扫），找出值得入库的偏好/决策/背景/资源位置。

> 唯一记忆源是 `/home/cowork/cowork/memory/`（git 追踪、三实例共享）。平台原生 auto-memory 路径留空不用，**不需要对比双路径**（旧机制已于 2026-06-07 废除，详见 ARCHITECTURE.md memory 层）。

---

## 步骤2：列出建议

逐条列出建议：
- **新增**：哪些内容值得写入 memory/
- **更新**：原内容 → 新内容
- **删除**：原因

判断标准：下次对话会影响行为的偏好/决策/背景/资源位置，且不可从代码推导。不满足则跳过（大多数情况不需要写）。

---

## 步骤3：写入

主公逐条确认后统一写入对应 memory/ 文件，更新 `memory/MEMORY.md` 索引。

---

## 步骤4：检查 MEMORY.md 行数

```bash
wc -l /home/cowork/cowork/memory/MEMORY.md
```

超过180行则提醒主公精简（目标上限200行）。

---

## 步骤5：更新时间戳

将 `last_memory_sync` 更新为当前时间，写入 `CURRENT_SESSION.md` 顶部元数据区。

> commit 由收工流程统一处理，整理记忆不单独 commit。

---

## 完成

报告：✅ 整理记忆完成 | 新增X条 / 更新X条 / 删除X条
