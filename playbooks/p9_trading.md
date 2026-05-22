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
cd /mnt/c/Users/zhi89/Desktop/cowork/trading && bash run_scanner.sh
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
