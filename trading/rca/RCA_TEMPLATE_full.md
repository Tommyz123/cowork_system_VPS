---
date: YYYY-MM-DD
incident: <一句话事件名>
severity: <major | critical>
status: <draft | fixed | monitoring | archived>
related: <link to friction_log entry / related memory>
---

# <Major/Critical> RCA — <事件标题>

> Major/Critical 模板：仿 `2026_05_18_ghost_positions_and_intraday_contamination.md` 结构。
> 用于结构性问题 / 影响多模块 / 影响数据完整性 / 涉及主公决策依据的事件。
> 不许填空式糊弄——每段都要有实质内容，没有的明确写 "N/A 因为 …"。

---

## 一句话总结
（事件是什么 + 影响范围）

## 事件时间线
| 时间 | 事件 |
|---|---|
| ... | ... |

---

## 根因分析（5-why）

### 表层错误
（哪里出错了，立即可见的现象）

### Why 1: <一句话提问>
<答案>

### Why 2: <基于 Why 1 的答案再问 why>
<答案>

### Why 3: <继续追>
<答案>

### Why 4 / Why 5
<追到结构性根因——通常涉及设计、流程、信任模型、命名语义等>

### 真正的根因（结构性）
（一句话总结深层原因，区别于表层 fix）

---

## 修复方式

### Priority P0（数据/状态立即一致）
**Option A**: ...
- 优点：...
- 缺点：...
- 副作用：...

**Option B**: ...
**Option C**: ...

### Priority P1（防止复发 — 结构性改造）
<列出长期改造方案，可以是多个 Fix 项>

---

## 怎么防止下次不会再犯（结构性预防）

按层级列防御：

### Level 1: 语义/命名层
...

### Level 2: Trust boundary 层
...

### Level 3: Reconciliation / 一致性检查层
...

### Level 4: 流程层
...

### Level 5: 监控/告警层
...

### Level 6: 文化/规则层（memory / playbook / CLAUDE.md）
...

---

## 当前已采取的临时措施
（哪些已经做了，哪些还没动）

- ✅ ...
- ⏳ ...

---

## 元数据 / 复盘锚点
- 关联 friction_log 条目：[YYYY-MM-DD HH:MM] ...
- 关联 memory（如有）：...
- 季度复盘 / RCA audit 时回看本文档的检查点：...
