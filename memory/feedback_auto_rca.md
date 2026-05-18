---
name: 犯错时自动 RCA（三档分级 + 多元触发器 + 反糊弄）
description: 任何符合触发条件的错误事件，我必须自动启动 RCA 流程（不等主公提醒）。三档分级（trivial 不记 / minor friction 一行 / major 详细 RCA 文档），多元触发器（不只我自判）。
type: feedback
originSessionId: b68a0307-4fb1-4816-ae90-9f3443efdd9c
---
错误自动 RCA 是 cowork 系统的固化习惯。我**不需要等主公提醒**，符合触发条件就自动启动。

**Why**: 2026-05-18 P9 ghost positions 事件后主公指示固化这个流程。背后逻辑：错误如果只是被纠正然后跳过，知识就丢失；如果每次都被主公提醒"记一下"，就增加主公心智负担。**自动化错误处理流程 = AI 协作者基本职业素养**。

---

## 触发器（5 种，五选一即触发）

任一发生即启动 RCA 流程：

1. **主公明确纠正我**（"不是这样"/"错了"/"为什么会这样"）
2. **Hook / 测试 / 脚本报错**（PreToolUse hook 拒绝 / pytest 失败 / cron 任务红字）
3. **数据/状态不一致被发现**（DB ↔ 外部系统差异 / 多文档冲突）
4. **工具/API 出意外失败**（连续失败 / 错误信息超出预期）
5. **我自判**（事后反思发现刚才做错了，但主公还没注意到）

⚠️ 注意：单纯打错字（typo）/ 临时命令小错 / 思考延迟 — **不触发**，属于 trivial。

---

## 三档分级（决定记录形式）

### Trivial（不记录）
- 标准：可在 30 秒内修复 + 影响范围只在当下对话 + 不涉及代码改动 + 主公没纠正过
- 例子：打错字、命令参数搞错重试一次、文件路径写错
- 处理：默认不记录。但**重复发生** 3 次同类 trivial → 升级 minor

### Minor（friction_log 一行）
- 标准：单点错误 + 5 分钟内修复 + 不涉及结构性问题
- 例子：脚本一行写错、忘了 import、用了错的常量
- 处理：在 `friction_log.md` 追加一行：
  ```
  [YYYY-MM-DD HH:MM] ⚠️ 类型 | 场景 | 表面错误 | 根因（1 句话）| 修复方式 | 状态
  ```
- 不写单独文档，不更新 memory，除非主公说"以后别这样"

### Major / Critical（详细 RCA 文档）
- **Major 标准**：结构性问题 + 影响多个文件/模块 + 可能复发 + 涉及设计缺陷
- **Critical 标准**：影响数据完整性 + 影响主公决策依据 + 涉及金额 / 安全 / 合规
- 例子：今晚 P9 ghost positions 事件、tide_utils 6 脚本复发、IWM bug
- 处理：
  1. **Critical 必须立刻 Discord 同步主公**（不只是写文档；可能需要暂停其他工作等主公拍板）
  2. 写完整 RCA 文档：`<项目>/rca/YYYY_MM_DD_<短描述>.md`，用 `RCA_TEMPLATE_full.md` 模板
  3. friction_log 追加一行链接到 RCA 文档
  4. 涉及行为规则的 → 写 / 更新 memory feedback
  5. 涉及多个项目可复用的 → memory 放到 `feedback_xxx.md`；项目专属 → 进 playbook
- **Major** 可以略简，但**至少要有 5-why + 修复方式 + 防止复发**三段

---

## 反糊弄条款

任何 RCA 必须满足：

1. **5-why 至少追到第 3 层 why**——只写"哪行代码错了"不算 RCA
2. **修复方式必须列 ≥ 2 个 options + 推荐**——单选项 = 没思考过
3. **防止复发必须分层**——不是"以后小心" / "下次注意"这种空话
4. **不许填充模板凑字数**——如果某段确实没有内容（如 minor 没有 6 层防御），明确写"N/A 因为 …"

**模板存放**：
- minor: `<项目>/rca/RCA_TEMPLATE_short.md`（4 字段，3 分钟填完）
- major/critical: `<项目>/rca/RCA_TEMPLATE_full.md`（仿 2026-05-18 P9 ghost positions RCA 结构）

---

## How to apply（执行规则）

### 1. 进入 RCA 时机
- 错误发现后**立即触发**（不要等"先把当前任务做完"）
- 如果当前任务紧急，至少在 friction_log 留 placeholder：`[YYYY-MM-DD HH:MM] ⚠️ PENDING-RCA | 待 RCA | 描述...`
- 当前任务完成后立即回来补全

### 2. 跨项目通用根因 → memory
- 如果根因是"跨项目都可能复发"（如"token 读取路径不一致"/"语义模糊状态字段"）→ 写 memory feedback
- 项目专属 → 写 playbook
- 单次事件 → 只 RCA 文档不进 memory

### 3. Critical 同步主公的格式
Discord 推送：
```
🚨 [Critical RCA 触发] <一句话总结>

根因：<1-2 句>
修复 options：A. ... / B. ... / C. ...（推荐 X）
影响：<对主公决策/数据/资金的影响>
RCA 文档：<path>

需要主公拍板：<具体问题>
```

### 4. 每季度审计
- 季度系统复盘时 audit RCA 集合
- 过时的 → 归档到 `rca/archive/YYYY_QX/`
- 重复出现的根因 → 升级为 Hook 或 CLAUDE.md 规则（按 feedback_rule_vs_hook）

---

## 防止流程本身腐化

如果出现下列任一情况，**这条规则本身需要重新评估**：

- 月度 RCA 数量 > 30 条 → 触发器过宽，需要收紧
- 月度 RCA 数量 < 2 条 → 触发器过窄或我在回避，主公提醒
- 同一根因 RCA 重复 ≥ 3 次 → 流程没起预防作用，需要升级为 Hook
- RCA 完成后没采取防复发措施 → 流程沦为形式，主公介入

---

## 相关 memory / 文档

- `feedback_rule_vs_hook.md` — 规则 vs Hook 升级判断
- `feedback_artifact_indexing.md` — 写完 RCA 后必须索引
- `friction_log.md` (项目内) — minor 入口
- `<project>/rca/` — major/critical 文档目录（每个项目自建）
