---
triggers: ["P9", "量化交易", "trading", "TIDE", "thesis", "scanner", "候选股", "主题"]
---

# Playbook: AI量化交易系统 TIDE [P9]

**⚠️ 第一系统（RSI/MACD/run_trading.py/strategy.yaml/stats_engine）已于2026-05-06彻底停用删除，不要引用。**

## ⚠️ 账号规则（必读）
- **TIDE系统全部使用 `swing` 账号**，禁止使用 `intraday`
- `intraday` = 第一系统遗留，已停用，不要动
- 2026-05-18 起**物理锁死**：`config.P9_ACCOUNT='swing'` + `assert_p9_account()`；close_position.py / alpaca_mcp.py 的 place_order/cancel_order 写入 intraday 会 raise ValueError

## 状态机 & Cohort 系统（2026-05-19 根治版）

**scanner_picks.status 状态机**：
- `submitted` → 扫描到 + OPG 下单（cognitive_scanner 写入时）
- `filled` / `auto_filled` → 次日 9:45 EDT reconciler 确认 Alpaca 成交
- `filled_late` → 手动补仓标记（5/18 ghost 修复批）
- `expired` / `auto_expired` → OPG 未成交（gap up 超 limit 价，Alpaca 自动作废）
- `canceled` / `rejected` → broker 层撤单/拒单

**scanner_picks.cohort 分类**：
- `early_filled`：5/11 手动第一批（6 只）
- `late_fill`：5/18 ghost 修复补仓（8 只）
- `auto_filled` / `auto_pending` / `auto_expired`：自动 OPG 流程

**当前持仓（2026-05-19 对账后）**：
- **15 只真实持仓**：status IN ('filled','filled_late','auto_filled')
- **5 只 expired**：GNTX/GWRE/OLLI/CXT/APPF（auto_expired，DB 与 Alpaca 一致）
- Ghost positions 已完全根治：RCA 见 `trading/rca/2026_05_18_*.md` / `2026_05_19_*.md`

## 📊 Attribution 框架 v1（2026-05-18 上线）
- scanner_picks 表新增 7 字段：`theme / secondary_themes / bear_thesis / hidden_risk / verdict (default tentative) / mistake_type / real_reason`
- `verdict` 必须在 close_position 时人工选（success/partial/failure/tentative）；failure/partial 必须填 mistake_type (7 选 1)
- `theme` 词表（5 选 1）：AI电力 / AI软件 / 公用事业现代化 / 分析师重定价 / 行业重分类
- cognitive_scanner.py prompt 强制四件套：Bull Thesis / Bear Thesis / Invalidation / Hidden Risk
- thesis 写作规则：hypothesis 语气强制（may/could/historically），不许 declarative 断言；未验证精确数字只能放监测信号，不进 thesis 散文（详见 memory/feedback_thesis_normalization.md）
- 完整 case study 示例：`trading/case_studies/ORA_2026_05_18.md`（含 red team adversarial review）

## 🚨 错误处理（auto-rca 流程）
- 任何 P9 错误事件触发 Skill `auto-rca`（自动启动，不等主公提醒）
- 三档分级：trivial 不记 / minor friction_log 一行 / major 详细 RCA / critical + 立刻 Discord
- 规则：`memory/feedback_auto_rca.md`；模板：`trading/rca/RCA_TEMPLATE_short.md` + `_full.md`

## 快速启动
路径：`/home/cowork/cowork/trading/`

手动触发季度扫描：
```bash
cd /home/cowork/cowork/trading && bash run_scanner.sh
```

平仓 TIDE 持仓（swing，默认）：
```bash
python3 close_position.py ORA        # ✅ 默认swing
# ❌ 不要用: python3 close_position.py ORA intraday
```

开盘后同步成交价：
```bash
python3 sync_fill_prices.py
```

查当前持仓：
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/cowork/cowork/trading/trading.db')
for r in conn.execute(\"SELECT symbol, entry_price, scan_date, status FROM scanner_picks WHERE status IN ('filled','filled_late','auto_filled') ORDER BY scan_date\"):
    print(r)
conn.close()
"
```

查最新signals积累：
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/cowork/cowork/trading/trading.db')
for r in conn.execute('SELECT date, symbol, source, COUNT(*) as cnt FROM signals GROUP BY date, symbol, source ORDER BY date DESC LIMIT 20'):
    print(r)
conn.close()
"
```

## 策略定位
主题驱动季度埋伏（不是技术面短线）：
- 当前主题：AI电网基础设施
- 打分6维度：叙事变化 / 市场认知滞后 / 行业尾风 / 催化剂 / 可交易性 / 否定风险
- 持仓窗口：3-6个月

## 自动运行流程（纽约时间 EDT）
- 每天 **16:00**：signal_collector / signal_alert / catalyst_monitor（三件套）
- 每天 **20:30**（工作日）：price_guard（持仓跌幅 >7% 告警）
- 每天 **21:00**：price_snapshot（30/60/90 天节点价格记录）
- 每周一 **16:30**：scanner_tracker（持仓周报→Discord）
- 每周一 **16:45**：price_tracker（补历史价格）
- 每周三 **16:30**：thesis_monitor（thesis 失效→Discord 告警，不自动平仓）
- 每周日 **15:45**：gtrends_collector（alt-data sidecar 关键词趋势）
- 每周日 **16:00**：weekly_review（结果追踪周报→Gmail）
- 每月第一周一 **15:00**：screener（刷新候选股池）
- 每季度第一周一 **19:30**：run_scanner（季度主题扫描+自动 OPG 下单）
- 每季度第一周一 **18:30**：quarterly_review（季度复盘→Gmail）

## 架构原则
- thesis_monitor失效只告警，不自动平仓，等主公人工决策
- signal_collector积累60-90天后建theme_discovery.py（约2026年8月）
- 有效前置信号：8-K 8.01+1.01密集 / backlog跳升 / 政策信号；分析师首次覆盖是滞后指标

## 🔧 Screener 设计原则（2026-05-24 入库）
**核心：样本量 > 过滤严格度；数据质量不可靠的过滤条件不加（噪音 > 信号）**

加新过滤条件前必过的 3 道关：
1. **数据来源可靠吗**？（如 yfinance 小盘股年化现金流数据质量差 → 不可用）
2. **加了之后样本量缩到多少**？（< 20 只就过严，宁可宽松不漏不可严而漏）
3. **过滤条件本身是 hypothesis 还是 fact**？（hypothesis 不加，等数据验证再说）

**实战参考（2026-05-24 决策）**：
- ✅ **加入**：grossMargins 非负硬过滤（grossMargins < 0 拒绝，None / 0 放行）—— 数据可靠 + 经济直觉强 + 样本影响小
- ❌ **拒绝**：现金跑道 Condition 2（yfinance 年化 CF 数据质量差 + 样本量优先 → 否决）

**适用**：任何 screener 过滤条件提案 / 季度 review 时 / v1→v2 策略切换时

## MCP工具快速查询
本项目配置了两个MCP工具，新对话直接可用：

### trading-db（SQLite直查）
**核心表：**
- `scanner_picks` — 持仓/候选股，字段：symbol/entry_price/scan_date/score/status(open/closed_watching/archived)/catalyst_date/spy_entry/return_pct等
- `signals` — 每日积累的叙事信号，字段：symbol/date/signal_type/headline/source/signal_quality
- `thesis_alerts` — thesis状态告警记录，字段：symbol/alert_date/thesis_status/headline_summary

**常用查询示例：**
```sql
-- 当前开仓
SELECT symbol, entry_price, scan_date, score, status FROM scanner_picks WHERE status IN ('filled','filled_late','auto_filled')

-- 最近信号积累
SELECT date, symbol, source, COUNT(*) cnt FROM signals GROUP BY date, symbol, source ORDER BY date DESC LIMIT 20

-- thesis告警
SELECT symbol, alert_date, thesis_status, headline_summary FROM thesis_alerts ORDER BY alert_date DESC LIMIT 10
```

### alpaca-trading（实时账户）
工具：`mcp__alpaca-trading__get_account` / `get_positions` / `get_orders`
- 默认账号：swing（纸交易 $1M）
- 支持 account 参数切换：`"swing"` 或 `"intraday"`

## 当前阶段（2026-05-19 更新）
积累阶段（纸账号 swing $1M）：
- **15 只真实持仓**（early_filled 6 / late_fill 8 / auto_filled 1）
- OPG fill 率实测 17%（1/6，5/19），Q3 满载 15 只预期成交 2-3 只
- 次季度扫描：8/4 周一 19:30 EDT（Q3 首次真正实战）
- 下一个关键节点：5/25 自动扫描验证 retry / 5/26 reconciler 首跑 / 6/14 首批 30 天 outcome
- alt-data sidecar：4-8 周只观察，1 年后 sample 累积 50+ 才考虑入评分

---

## 🔬 未验证假设（待 2026-12 节点验证）

> ⚠️ 这些是**怀疑**不是事实。在数据回来之前**不改策略**，但记下来好让半年后看到数据时知道"当初为什么要测"。

### 假设 1：90 天持仓可能太长，真正 alpha 在前 5 天

**怀疑内容**：小盘叙事股的 alpha 可能主要在 **T+0~T+5** 释放，后 85 天持有期可能是噪音（甚至负贡献）。

**怀疑来源**：2026-05-24 主公 + Opus + Codex 联合策略评估。

**验证方式**：6/14 首批 30 天 outcome + 6 月底全样本 hit rate 数据。看：
- 5 天内涨幅 vs 30/60/90 天涨幅分布
- 后 85 天是否反而冲掉前 5 天的 alpha

**如果验证为真**：改策略从"持 90 天"→"持 5-7 天就卖"，把资金循环利用率提升 15-18 倍。
**如果验证为假**：维持现状 90 天持仓。

### 假设 2：真正的 edge 不是"读新闻快"，是"股票池组成"

**怀疑内容**：现在做这类小盘叙事交易的人多了，"AI 读新闻速度"已经不是护城河。真正的 edge 来自股票池本身——**小市值 + 分析师覆盖 ≤2**（别人很难看到 / 很难下单的标的）。

**比喻**：抢限量球鞋——知道发售消息的人很多，**真正能抢到货的是手快+排队早的人**。

**验证方式**：看持仓股的"分析师覆盖数"分布 vs 实际收益分布。如果低覆盖股（≤2）跑赢高覆盖股，说明池子组成是真 edge。

**如果验证为真**：screener 加"分析师覆盖 ≤2"硬过滤，缩小但优化池子。
**如果验证为假**：维持现有 screener 过滤逻辑。

### 假设 3：Alpha 窗口正在压缩

**怀疑内容**：历史上类似策略可以拿 **3x alpha**，但竞争者越来越多，现在可能只剩 **30% 量级**。叙事本身的传播周期还是 1-2 年，只是涨幅被压缩。

**验证方式**：6 月底 hit rate 数据看绝对收益分布。

**如果验证为真**：调低预期收益 / 加大样本量补偿。
**如果验证为假**：维持现有预期。

---

**统一验证节点**：2026-06 月底 hit rate 数据 + 2026-12 全年 outcome → 三个假设一起评估，**任何一个验证为真都触发 v1→v2 策略切换**。
