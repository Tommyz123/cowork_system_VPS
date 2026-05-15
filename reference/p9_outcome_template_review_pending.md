# P9 Outcome 模板设计 - 5/17 待评估

> 创建：2026-05-15
> 评估时间：2026-05-17（周日）weekly_review 邮件后
> 决策：评估"是否需要补 outcome_report 工具" / "如何补"

---

## 起因

主公 2026-05-15 在 P9 IWM bug 修完后，深入讨论几个问题：
1. P9 系统的"特征是否可分析"
2. 是否需要固定一个分析的标准模板
3. 担心"跑 1-2 年发现特征没用"

---

## Claude 设计的 6 大块模板（初版）

```
1. 基础统计（hit rate / 平均 alpha / 标准差 / 最强最弱）
2. 维度分析
   - 评分 vs return
   - 主题分类
   - 入场批次
   - catalyst 远近
   - 信号源
3. 个股 detail（symbol / score / entry / now / return / alpha / thesis_status）
4. 告警事件汇总（price_guard / thesis_monitor / 重大新闻）
5. vs 市场环境（IWM / SPY / VIX / sector ETF）
6. 主公观察笔记（手填区域）
```

---

## 子 Agent (Explore) 独立审核（关键反馈）

**审核结论：模板方向有问题。**

### 子 Agent 的 3 个发现：

**A. 关键维度被遗漏 ✅ 对**
- 缺 **Thesis 失效触发点（invalidation_conditions）验证模块**
- 没有结构化"thesis 完全验证 vs 部分验证 vs 已否定"
- 看 ORA 报告，这恰恰是最关键的决策指标

**B. 维度冗余 ⚠️ 部分对**
- "维度分析 + 个股 detail" 高度重复
- "告警事件 + 个股 thesis_status" 重复
- "vs 市场环境" 周报已在做 (scanner_tracker.py:188)，季度复盘也在做 (quarterly_review.py:105-107)

**C. 方向性问题（最严重）✅ 对**
- weekly_review.py 已做：new_this_week + total_count + 平均 return_30/60/90d + vs IWM
- quarterly_review.py 已做：win_rate + avg_return + alpha vs IWM + 评分桶胜率 + thesis 告警损失率
- **Claude 的"outcome 报告"如果做跨票聚合 → 完全重叠**

**D. 子 Agent 推荐方向：Per-Trade Outcome 模板**
- 不做跨票聚合，做单笔交易事后验证
- 学 ORA outcome 报告（2026-05-08 已有的雏形）
- 重点：thesis 验证度 / catalyst 实际 vs 预期 / invalidation 触发检查 / 推荐动作

---

## Claude 二次反思（不盲信子 Agent）

子 Agent 帮 Claude 看出了一个真问题（**可能跟 weekly_review 重叠**），但**推荐的 per-trade 自动化模板工程量被低估**：
- ORA outcome 报告是主公手写的（5000+ 行 10-Q 全文 + 人工分析）
- 自动化 per-trade 需要 LLM 读 10-Q + 判断 thesis 兑现
- 工程量比 Claude 估的大 5-10 倍

**结论**：两个 Claude 都不能盲信。

---

## 5/17 周日评估清单

**等 5/17 16:00 EDT weekly_review 第 1 次发邮件后**，主公需要做的评估：

### Step 1：看 weekly_review 实际邮件
- [ ] 邮件内容长什么样？
- [ ] 包含哪些维度？
- [ ] 缺哪些维度？

### Step 2：评估 gap
- [ ] weekly_review 已经做了：__________
- [ ] Claude 建议的模板想做：6 大块（见上）
- [ ] **真实缺的 = 想做的 - 已做的**

### Step 3：决策
| 选项 | 描述 | 工程量 |
|------|------|--------|
| A | 啥都不做（weekly + quarterly + ORA outcome 已够）| 0 |
| B | 只补 invalidation_conditions 检查（子 agent 唯一确认对的发现）| 30 分钟 |
| C | 做轻量跨票模板（删冗余部分）| 1-2 小时 |
| D | 做 per-trade outcome 自动化（子 agent 推荐）| 1-2 天 |

### Step 4：执行 or 不执行
- 选 A → playbook 标注"已评估，无需补"
- 选 B/C/D → 列实施计划 + task_approved

---

## 关键链接

- weekly_review.py: `/home/cowork/cowork/trading/weekly_review.py`
- quarterly_review.py: `/home/cowork/cowork/trading/quarterly_review.py`
- scanner_tracker.py:188 (vs IWM 逻辑): 已在做
- ORA outcome 雏形: `/home/cowork/cowork/trading/outcomes/ORA_*.md`
- ORA thesis 封存: `/home/cowork/cowork/trading/prompts/ORA_thesis_sealed_20260508.md`

---

## 历史背景（对话脉络）

2026-05-14 深度对话 8 小时 → Cannabis Retail 主线确立
2026-05-15 早上 → 主公问"P9 现在怎么样" → 暴露 IWM 基准 bug
2026-05-15 中午 → 修复 IWM bug + 引入 config.py + 真实 alpha -1.14%
2026-05-15 下午 → 讨论 P9 模板设计 → 子 agent 审核 → **暂缓动手**
2026-05-17 18:00 EDT → 自动 Discord 提醒（cron + p9_template_review_reminder.py）
2026-05-17 18:00+ → 主公评估 → 决策
