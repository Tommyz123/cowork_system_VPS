---
name: project_p9_trading
description: P9 AI量化交易系统TIDE：主题驱动季度埋伏，叙事先行+基本面验证，当前主题AI电网基础设施，纸账号学习阶段
type: project
originSessionId: fb2ad148-a891-4de5-9022-d0c801600b4e
---
P9 AI量化交易系统（TIDE系统），路径：`/home/cowork/cowork/trading/`（VPS；旧 WSL 路径 /mnt/c/Users/zhi89/Desktop/cowork/ 已迁移，勿引用）

**⚠️ 第一系统（RSI/MACD/strategy.yaml/stats_engine/run_trading.py）已于2026-05-06彻底停用删除，技术指标无alpha已验证，不要引用或建议恢复。**

---

## 核心投资哲学
**叙事先于价格**：目标是NVDA/PLTR级别的框架切换机会，不是跑赢SP500。
- 收入增速>15%是滞后指标——埋伏期公司收入往往平/跌（用增速过滤会漏掉NVDA/PLTR早期）
- 真正的信号：叙事已在变，市场还在用旧框架定价

**⚠️ 验证缺口（幸存者偏差）**：目前只验证了9个成功案例，未验证假阳性率。类似信号出现但没爆发的公司有多少？这是核心未解问题，纸账号阶段的核心任务就是积累数据来验证。

---

## 有效前置信号（已验证9个案例）
- **8-K Item 8.01（其他事项）+ 1.01（重大协议）密集出现** → 强预信号（TSLA/MSTR/SMCI/NVDA/AXON/CELH验证）；7.01密集也是信号
- 跨行业财报语言同步变化 / backlog/订单积压跳升 / 政策立法信号
- ❌ 分析师首次覆盖集中 = 滞后指标，不用
- APP/PLTR/ENPH无信号（算法/政策/估值驱动，不适用TIDE）

**数据源：** Finnhub新闻（signal_collector.py，2026-05-08替代FMP）+ SEC EDGAR 8-K；FMP Free plan不含新闻端点仅保留备用；FMP财报transcript需付费跳过。

---

## 里程碑
- 2026-05-06：**ORA首单验证** — Q1财报盘后+6.6%（$114.86→$122.44），261股浮盈+$1978，TIDE叙事先于价格逻辑首次成立

---

## 已知待解决Gap
1. **基准对比**：已统一IWM（小盘成长基准）；spy_entry列名保留但存IWM数据（$286.80，2026-05-08）；⚠️ column命名遗留问题，不影响计算，不要当bug修
2. **LLM打分偏慷慨**：48家→10家全≥9分，threshold需收紧；**暂不优化**，等outcome_tracking积累30+条数据后再做（当前<10条）
3. **季度重叠无去重**：同一公司可能被多个季度重复选入

---

## 当前阶段原则
学习阶段（纸账号），积累signal数据是第一优先级。

**快速验证模式**：操作偏向执行不过度分析；全买候选池+等权分配最大化数据点；进实盘前才切换谨慎模式。**所有P9建议必须基于此框架给出**，不要在纸账号阶段给出"谨慎/等更多数据再买"类建议。

**积累阶段完成（2026-05-08）**：Finnhub+system_log+DB备份+prompt快照+API失效告警全部上线；系统全自动运行，主公只需响应Discord周报+thesis_monitor告警。**下次人工决策时刻=ORA第一次平仓**。

**明确不做（纸账号阶段，过度工程化）**：任务冲突处理/signal时序精调/price_guard扩展/心跳监控/备份单点消除/积累期缺项/每日价格记录（无daily_price DB表，max_drawdown_pct等日线指标延迟到真账号前做，price_guard -7%告警已覆盖紧急情况）。真账号上线前再评估。

**延迟决策（等条件触发）**：叙事记忆库+失败案例库——等ORA平仓后有真实闭环数据再建（约2026年8月，30+条结果后）。

---

## Outcome Tracking（2026-05-08上线）
新增 `outcome_tracking` 独立表，记录叙事信号结果（30/60/90天涨跌）。
新增脚本：`price_tracker.py` / `weekly_review.py`

**设计原则（最小闭环）：**
- 头2年：只积累数据 + 人工复盘
- 自动调规则需同类信号 ≥30个才启动
- 不为工程而工程，数据量不够时不做自动化

---

## 已弃用表（deprecated，保留不删）
- `news`（停 2026-05-06，0 脚本引用）、`insider_transactions`（停 2026-05-06，0 脚本引用）：2026-05-30 数据质量审计确认无活脚本引用，标 deprecated 留底（删表不可逆，几百行收益≈0，留着等长期确认再删）。
- ⚠️ 反例（活表，勿删）：`alt_signals` 仍被 gtrends_collector 写（alt-data sidecar 积累中）、`decisions` 仍被 alpaca_mcp 下单时写。
- signals 表 8-K 信号 2026-05-30 已重写全链路（symbol→CIK 精确查/Item 字段评级/真正文/喂 LLM），旧 1146 条占位符垃圾已删并 backfill 重抓。

## 下单模式
**人工审核 + Claude执行**：主公判断要买，通过 MCP alpaca-trading 的 `place_order` 工具下单；同时自动写入 trades/decisions 表归因。
- MCP工具：`mcp__alpaca-trading__place_order`（默认swing账号）
- **下单后手动步骤**：每次下单等成交后，手动跑 `sync_fill_prices.py` 同步Alpaca fill_price到trades/scanner_picks表；此脚本不在crontab，需手动触发。
