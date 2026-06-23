---
name: project_p9_trading
description: P9 交易体系双层结构：第1层 P9=AI自动实验田(swing纸账号,12月验收)；第2层 趋势主线=主力方向(人机协作,六维框架,实体在trading/notes/)
type: project
originSessionId: fb2ad148-a891-4de5-9022-d0c801600b4e
---
P9 量化交易系统（TIDE 系统），路径：`/home/cowork/cowork/trading/`（VPS；旧 WSL 路径已迁移，勿引用）。

**⚠️ 第一系统（RSI/MACD/strategy.yaml/stats_engine/run_trading.py）已于 2026-05-06 彻底停用删除，技术指标无 alpha 已验证，不要引用或建议恢复。**

---

## 双层结构（2026-06-10 主公定案 / 2026-06-12 趋势主线基建落地）

**第1层 P9 = AI 自动实验田**
- swing 账号、纸钱（实际 equity ~$10万，以实时查询为准，旧记 $1M 是错的）、全自动
- 任务 = 验证"AI 自动选股行不行"；**12 月验收定去留，期间不动不加码**
- 这一层就是下面的 TIDE 系统

**第2层 趋势主线 = 主力方向**
- intraday 账号（$1M 纸钱是历史误记，至今 0 交易未接代码；真试水建议重置 $20-50k）
- 人机分工 = 我参谋出报告 + 主公司令拍板（主公只出手 2 次：拍板买 / 拍板卖）
- 策略 = 吃鱼身（等摊牌信号上车 + 下车信号）
- **六维判断框架（v1.1）**：真金白银 / 利润上财报 / 巨头 capex 投票 / 供需缺口持续性 / 渗透率 S 曲线 / **利润来源分解（量 vs 价）**
- **双保险丝**：成本 -25% 强制讨论 + 峰值 -30% 信号核查
- 实体全在 `trading/notes/`（INDEX.md 登记）：趋势判断手册.md(尺子) / 趋势地图.md(排行榜) / 选股候选.md / 趋势观察池.md
- 投资纲领见 [[feedback_investment_thesis]]（押时代级大趋势）；标的范围见 [[feedback_us_stock_only]]（只做美股）

**隔离四层**：账号（P9 代码硬锁 `ALLOWED_WRITE_ACCOUNTS=("swing",)`）/ 数据库（trading.db 只有 P9）/ cron（P9 交易系列 vs 趋势只有提醒+哨兵）/ 文档（playbook vs trading/notes/）。唯一交集 = 复用方法论与告警基建，不复用账号数据。

> 详细操作/命令/cron 见 `playbooks/p9_trading.md`（权威来源，本条只记结构定位）。

---

## 第1层 TIDE 核心投资哲学
**叙事先于价格**：目标是 NVDA/PLTR 级别的框架切换机会，不是跑赢 SP500。
- 收入增速 >15% 是滞后指标——埋伏期公司收入往往平/跌（用增速过滤会漏掉 NVDA/PLTR 早期）
- 真正的信号：叙事已在变，市场还在用旧框架定价
- **⚠️ 验证缺口（幸存者偏差）**：目前只验证了 9 个成功案例，未验证假阳性率。纸账号阶段核心任务 = 积累数据验证假阳性率。

## 有效前置信号（已验证 9 个案例）
- **8-K Item 8.01 + 1.01 密集出现** → 强预信号（TSLA/MSTR/SMCI/NVDA/AXON/CELH 验证）；7.01 密集也是信号
- 跨行业财报语言同步变化 / backlog 跳升 / 政策立法信号
- ❌ 分析师首次覆盖集中 = 滞后指标，不用
- 数据源：Finnhub 新闻（signal_collector.py）+ SEC EDGAR 8-K

## 里程碑
- 2026-05-06：**ORA 首单验证** — Q1 财报盘后 +6.6%，261 股浮盈 +$1978，TIDE 叙事先于价格逻辑首次成立。**ORA 已于 2026-05-18 平仓**。

---

## 当前阶段原则（第1层）
学习阶段（纸账号 swing，~$10.6万 equity / ~$6.1万 cash），积累 signal 数据是第一优先级。

**快速验证模式**：操作偏向执行不过度分析；全买候选池+等权分配最大化数据点；进实盘前才切换谨慎模式。**所有 P9 建议必须基于此框架**，不要在纸账号阶段给"谨慎/等更多数据再买"类建议。

**积累阶段完成（2026-05-08）**：系统全自动运行，主公只需响应 Discord 周报 + thesis_monitor 告警。

**明确不做（纸账号阶段，过度工程化）**：心跳监控 / 备份单点消除 / 每日价格记录 / 自动调规则（需同类信号 ≥30 个才启动）。真账号上线前再评估。

---

## 下单模式（第1层）
**人工审核 + Claude 执行**：主公判断要买 → 通过 MCP alpaca-trading 的 `place_order` 下单（默认 swing），自动写 trades/decisions 表归因。
- **下单后手动步骤**：每次成交后手动跑 `sync_fill_prices.py` 同步 fill_price 到 trades/scanner_picks 表（不在 crontab，需手动触发）。

## 双层对账（2026-06-10 上线）
订单级=每日 9:45 `sync_fill_prices.py`；持仓级=每周一 `scanner_tracker.py` 比对 Alpaca /positions vs DB，不一致 🚨 Discord 告警。**对账以 broker 为准**（见 [[feedback_p9_no_ghost_data]]）；OPG expired 含部分成交陷阱见 knowledge_base。

## 已弃用表（deprecated，保留不删）
- `news` / `insider_transactions`（停 2026-05-06，0 脚本引用，留底等长期确认再删）
- ⚠️ 活表勿删：`alt_signals`（gtrends_collector 写）/ `decisions`（alpaca_mcp 下单写）
