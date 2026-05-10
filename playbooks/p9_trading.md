---
triggers: ["P9", "量化交易", "trading", "TIDE", "thesis", "scanner", "候选股", "主题"]
---

# Playbook: AI量化交易系统 TIDE [P9]

**⚠️ 第一系统（RSI/MACD/run_trading.py/strategy.yaml/stats_engine）已于2026-05-06彻底停用删除，不要引用。**

## ⚠️ 账号规则（必读）
- **TIDE系统全部使用 `swing` 账号**，禁止使用 `intraday`
- `intraday` = 第一系统遗留，已停用，不要动

## 快速启动
路径：`/mnt/c/Users/zhi89/Desktop/cowork/trading/`

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
conn = sqlite3.connect('/mnt/c/Users/zhi89/Desktop/cowork/trading/trading.db')
for r in conn.execute(\"SELECT symbol, entry_price, scan_date, status FROM scanner_picks WHERE status='open' ORDER BY scan_date\"):
    print(r)
conn.close()
"
```

查最新signals积累：
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/mnt/c/Users/zhi89/Desktop/cowork/trading/trading.db')
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

## 五层自动运行流程
- 每天12PM EDT：signal_collector / signal_alert / catalyst_monitor
- 每周一12PM EDT：scanner_tracker（持仓周报→Discord）
- 每周三12PM EDT：thesis_monitor（thesis失效判断→Discord告警，不自动平仓）
- 每月第一周一12PM EDT：screener（刷新候选股池）
- 每季度第一个周一8AM UTC：run_scanner（季度主题扫描）

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
SELECT symbol, entry_price, scan_date, score, status FROM scanner_picks WHERE status='open'

-- 最近信号积累
SELECT date, symbol, source, COUNT(*) cnt FROM signals GROUP BY date, symbol, source ORDER BY date DESC LIMIT 20

-- thesis告警
SELECT symbol, alert_date, thesis_status, headline_summary FROM thesis_alerts ORDER BY alert_date DESC LIMIT 10
```

### alpaca-trading（实时账户）
工具：`mcp__alpaca-trading__get_account` / `get_positions` / `get_orders`
- 默认账号：swing（纸交易 $1M）
- 支持 account 参数切换：`"swing"` 或 `"intraday"`

## 当前阶段
学习阶段（纸账号 $1M），积累signal原料，等2026年8月建自动主题发现。
