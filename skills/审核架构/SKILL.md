---
name: 审核架构
description: 执行 cowork 系统架构审核流程（7维度）。主公说"审核系统架构"或"审核架构"时触发。逐维度检查规则健康、文件结构、流程一致性、记忆系统、项目健康、摩擦积累、文档同步度，输出问题清单，等主公确认后执行修改。
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

# 审核系统架构流程

> 逐一检查以下7个维度，每条输出状态（✅正常 / ⚠️注意 / ❌问题）+ 发现的具体问题。
> 最后汇总"需处理清单"，等主公确认后再执行任何修改。

---

## 步骤0：Preamble（读取上次状态）

```bash
cat ~/.claude/skills/审核架构/state.md 2>/dev/null || echo "（首次运行，无历史状态）"
```

- **有 state.md** → 加载上次各维度的 known_issues；本次对每个问题标注：`已知`（继续存在）/ `已修`（本次消失）/ `新增`（本次首次出现）/ `复发`（上次已修，本次又出现）
- **无 state.md** → 全量审核，当作首次运行

---

## 维度1：规则健康

检查 `CLAUDE.md`：
- 有无矛盾的规则（A说做X，B说不做X）
- 有无模糊表达（"适当时候"、"必要时"等不可执行的描述）
- 有无死角（某类场景没有对应规则）

```bash
wc -l /home/cowork/cowork/CLAUDE.md
```

行数超过180行则标注 ⚠️。

---

## 维度2：文件结构

核心文件是否存在：
```bash
ls /home/cowork/cowork/{CLAUDE.md,ARCHITECTURE.md,context.md,CURRENT_SESSION.md,BACKLOG.md,INSIGHTS.md,friction_log.md,cowork_log.md,reference/knowledge_base.md}
```

**检查仓库可见性（安全触发器）：**
```bash
gh api repos/Tommyz123/cowork_system --jq '.private' 2>/dev/null
```
- 返回 `true` = 私有，正常
- 返回 `false` = ⚠️ 仓库已公开！立即提醒主公处理 BACKLOG 中的"[公开前]安全与可移植性闭环"清单

检查：
- 有无过大文件（cowork_log.md接近280行？）
- 有无明显过时文件

---

## 维度3：流程一致性

检查以下流程之间有无冲突：
- 收工 vs 整理记忆（记忆写入时机是否重叠）
- 保存进度 vs 收工（步骤是否是超集关系）
- 任务审批 vs 白名单文件（边界是否清晰）

---

## 维度4：记忆系统

```bash
wc -l /home/cowork/cowork/memory/MEMORY.md
ls /home/cowork/cowork/memory/ | wc -l
cat /home/cowork/cowork/memory/auto_pending.md
```

检查：
- MEMORY.md行数（超180行提醒）
- memory/文件数量是否合理
- auto_pending.md有无积压未审条目
- 有无明显过时的记忆文件

---

## 维度5：项目健康

读 `CURRENT_SESSION.md` 活跃区块：
- **需人工干预项目**：列出名称+状态，数量超5个 ⚠️（这才是注意力负担）
- **自动运行项目**：列出名称+状态（显示但不计入阈值，它们不占注意力）
- 有无僵尸项目（last_updated超30天且状态不是"暂停"）
- BACKLOG未实现条目数（超8条 ⚠️）

---

## 维度6：摩擦积累

```bash
grep -c "⚠️" /home/cowork/cowork/friction_log.md
```

- 未解决条目数（超11条 ⚠️）
- 有无同一场景出现≥2次的复发问题

---

## 维度7：文档同步度

逐项核对：
- 改了CLAUDE.md规则 → ARCHITECTURE.md对应区块是否同步？
- 新增/改了Hook → ARCHITECTURE.md Hook表格是否更新？
- 项目路径/命令变 → playbooks/是否一致？
- context.md项目状态 → 与CURRENT_SESSION.md是否匹配？

---

## 输出格式

**信心评分规则**：每个维度发现的具体问题在输出前先打分（1-10）：
- ≥7 → 完整展开（问题描述+建议）
- 4-6 → 只列问题标题，不展开
- <4 → 静默跳过

```
🏗️ 系统架构审核报告

1. 规则健康：[✅/⚠️/❌] [新增/复发/已知/已修] [≥7分问题完整展开，4-6分仅标题]
2. 文件结构：[✅/⚠️/❌] [同上]
3. 流程一致性：[✅/⚠️/❌] [同上]
4. 记忆系统：[✅/⚠️/❌] [同上]
5. 项目健康：[✅/⚠️/❌] [同上]
6. 摩擦积累：[✅/⚠️/❌] [同上]
7. 文档同步度：[✅/⚠️/❌] [同上]

📋 需处理清单（仅≥7分问题）：
- [优先级] [新增/复发] 具体问题 → 建议处理方式
```

审核完毕后等主公确认再执行任何修改。

---

## 最终步骤：写回状态文件

修改执行完毕后，更新 `~/.claude/skills/审核架构/state.md`：

```bash
cat > ~/.claude/skills/审核架构/state.md << 'EOF'
last_run: [YYYY-MM-DD]
overall: [X/7 维度正常]
known_issues:
  维度1_规则健康: [问题摘要] | 状态：已知/已修/复发/新增
  维度2_文件结构: [问题摘要] | 状态：...
  维度3_流程一致性: [问题摘要] | 状态：...
  维度4_记忆系统: [问题摘要] | 状态：...
  维度5_项目健康: [问题摘要] | 状态：...
  维度6_摩擦积累: [问题摘要] | 状态：...
  维度7_文档同步度: [问题摘要] | 状态：...
EOF
```
