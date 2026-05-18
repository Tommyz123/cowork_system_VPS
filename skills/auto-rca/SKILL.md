---
name: auto-rca
description: 自动 RCA（Root Cause Analysis）流程。错误事件触发后按三档分级（trivial/minor/major）处理，不依赖主公提醒。规则正文在 memory/feedback_auto_rca.md，本 Skill 是可执行流程。当出现：主公纠正/hook 报错/数据不一致/工具失败/我自判错误 时触发。
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

# Auto-RCA 流程

> 错误自动 RCA 是 cowork 协作基本素养。
> 规则正文：`memory/feedback_auto_rca.md`
> 本 Skill：可执行流程清单。
> ⚠️ Skill 触发后必须执行到底，不许中途跳出"等主公确认"——RCA 写作本身不修复任何代码，只产出分析文档。

---

## Step 1：判断严重性

按下列三档分级，**先选档位再选模板**：

| 档位 | 判定标准 | 输出 |
|---|---|---|
| **Trivial** | 30 秒可修复 + 无代码改动 + 主公没纠正过 + 影响只在当下对话 | 不记录（除非重复 3 次同类→升级 minor） |
| **Minor** | 单点错误 + 5 分钟内修复 + 不涉及结构性问题 | friction_log 一行 |
| **Major** | 结构性问题 + 影响多文件/模块 + 可能复发 | 完整 RCA 文档 |
| **Critical** | 影响数据完整性 + 影响主公决策依据 + 涉及金额/安全/合规 | RCA 文档 **+ 立刻 Discord 同步主公** |

不确定 minor vs major：**默认升一档**。RCA 写多了不会出事，写少了会重复犯错。

---

## Step 2：按档位执行

### A. Trivial — 跳过

直接修复，不记录。但**如果发现这是第 3 次同类问题**→ 升级 minor，回到 Step 1 重新走。

### B. Minor — friction_log 一行

在项目根目录的 `friction_log.md` 追加一行：

```
[YYYY-MM-DD HH:MM] ⚠️ 类型 | 场景 | 表面错误 | 根因（1 句话）| 修复方式 | 状态：已自行修复 / 需主公确认
```

类型词表：`系统限制 / 工具限制 / 复发 / 被主公纠正 / 数据不一致 / 设计缺陷 / 流程缺失`

完成报告：✅ 已记录 minor RCA 到 friction_log

### C. Major — 详细 RCA 文档

执行 4 步：

**1. 创建 RCA 文档**
- 路径：`<项目>/rca/YYYY_MM_DD_<短描述>.md`（如 `trading/rca/2026_05_18_ghost_positions.md`）
- 项目没有 rca/ 目录 → `mkdir -p`
- 复制 `RCA_TEMPLATE_full.md` 作为骨架（项目 rca/ 目录里应该有；没有就从 `trading/rca/RCA_TEMPLATE_full.md` 复制）

**2. 填写 RCA**（不许糊弄）
必填 4 段：
- 一句话总结 + 事件时间线
- 根因 5-why（**至少追到第 3 层 why**）
- 修复方式（**≥ 2 个 options + 推荐**）
- 防止复发（**分层防御，不许写"以后小心"**）

**3. friction_log 同步一行链接**
```
[YYYY-MM-DD HH:MM] ⚠️ Major-RCA | <事件名> | 详见 <project>/rca/YYYY_MM_DD_xxx.md
```

**4. 跨项目根因 → memory**
如果根因是"跨项目可复发"（如"token 路径不一致"/"语义模糊状态"），写 / 更新 memory feedback。

### D. Critical — Major 全做 + 立即 Discord 同步

在 Major 的 4 步基础上**先**做：

**0. 立即 Discord 推送主公**（在写 RCA 文档前）：

```
🚨 [Critical RCA 触发] <一句话总结>

根因：<1-2 句>
修复 options：A. ... / B. ... / C. ...（推荐 X）
影响：<对主公决策/数据/资金的影响>
RCA 文档：<path>（即将写）

需要主公拍板：<具体问题>
```

然后再写 RCA 文档 + friction_log + memory。

---

## Step 3：反糊弄自检

写完 RCA 后**自检 4 项**：

- [ ] 5-why 真的追到第 3 层？还是停在表层"代码错了"？
- [ ] 修复方式真的列了 ≥ 2 个？还是单选项假装思考？
- [ ] 防止复发是具体行动？还是"以后小心"空话？
- [ ] 模板里没有内容的段落是明确写了"N/A 因为..."，还是填充空话？

任一项 No → 重写那段。

---

## Step 4：完成报告

执行完后报告：

```
✅ Auto-RCA 完成
- 档位：<trivial / minor / major / critical>
- 记录位置：<friction_log 行号 / RCA 文档路径>
- 跨项目规则更新：<是 / 否，如是列出 memory 文件>
- Critical 同步主公：<是 / 否>
```

---

## 反例（不该触发的）

- "刚才命令打错重输" → trivial，不触发
- "我理解延迟了 1 分钟才回答" → trivial
- "yfinance 偶发超时一次" → trivial（连续 3 次才 minor）
- "Discord plugin 漏抓消息一次" → trivial（除非重复）

---

## 反例（应该触发但容易漏的）

- ✅ "主公说'我们之前讨论过这个'" → 我忘了，触发（看不见自己盲区）
- ✅ "subagent 返回内容明显不对劲" → 触发（数据质量问题）
- ✅ "测试通过但实际行为不对" → 触发（测试覆盖问题）
- ✅ "刚才写的代码主公没说，但我事后发现是错的" → 自判，触发

---

## 与其他 Skill 的关系

- `保存进度` / `收工` → 不冲突。RCA 完成后照常保存
- `系统复盘` → 季度跑一次时 audit RCA 集合
- 触发期间如有未完成的其他 Skill：先 placeholder `friction_log` 留 PENDING-RCA 标记，完成原任务后回来补
