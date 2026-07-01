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
- **⚠️ 部分成交规则（2026-06-10）**：Alpaca OPG 单部分成交后终态仍是 `expired` 但 `filled_qty>0`、持仓真实存在——reconciler 必须先查 filled_qty 再定状态（GNTX 97/132、WTS 9/10 漏记 3 周教训，已修 sync_fill_prices.py）

**scanner_picks.cohort 分类**：
- `early_filled`：5/11 手动第一批（6 只）
- `late_fill`：5/18 ghost 修复补仓（8 只）
- `auto_filled` / `auto_pending` / `auto_expired`：自动 OPG 流程

**当前持仓（2026-06-10 对账后）**：
- **15 只真实持仓**：status IN ('filled','filled_late')，与 Alpaca /positions 逐 symbol 一致（含 6/10 补录的 GNTX/WTS 部分成交）
- **双层对账（2026-06-10 上线）**：订单级=每日 9:45 sync_fill_prices.py；持仓级=每周一 scanner_tracker.py 比对 Alpaca /positions vs DB，不一致 🚨 Discord 告警
- Ghost positions 家族 RCA：`trading/rca/2026_05_18_*.md` / `2026_05_19_*.md`；第3次复发（部分成交反向幽灵）2026-06-10 根治

## 📊 Attribution 框架 v1（2026-05-18 上线）
- scanner_picks 表新增 7 字段：`theme / secondary_themes / bear_thesis / hidden_risk / verdict (default tentative) / mistake_type / real_reason`
- `verdict` 必须在 close_position 时人工选（success/partial/failure/tentative）；failure/partial 必须填 mistake_type (7 选 1)
- `theme` 词表（5 选 1）：AI电力 / AI软件 / 公用事业现代化 / 分析师重定价 / 行业重分类
- cognitive_scanner.py prompt 强制四件套：Bull Thesis / Bear Thesis / Invalidation / Hidden Risk
- thesis 写作规则：hypothesis 语气强制（may/could/historically），不许 declarative 断言；未验证精确数字只能放监测信号，不进 thesis 散文（详见 memory/feedback_thesis_normalization.md）
- **bear_thesis 强制检查项（2026-06-09 入库，VRRM -$2,211 教训）**：单一客户/合同占收入 >10% 的公司，bear_thesis 必须单独写"客户集中度风险"段（客户名/占比/合同到期日/历史续签率），否则视为不完整。VRRM 案例：Avis 占收入 >10%，合同终止单日 -70.6%，当时 bear_thesis 只写了政治/政府合同风险，漏了私人大客户集中度
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

## 🛑 止损操作流程（2026-05-28 VRRM 实战，2026-06-09 入库）
持仓基本面永久损伤（thesis 失效）时的完整步骤：
1. 查暴跌原因（新闻/基本面），区分噪音 vs 实质损伤
2. 确认 DB `thesis_status=invalidated`
3. 过 4 层 sanity check（见 memory/feedback_p9_auto_execute.md）
4. Alpaca API 提交市价卖单（`python3 close_position.py <SYMBOL>`，默认 swing）
5. 次日确认成交
6. 更新 DB `realized_pnl` + `mistake_type`（7 选 1）+ `verdict`

## 📈 平仓后追踪（post_exit_tracker，2026-06-03 上线）
- `post_exit_tracker.py`（周一 17:00 cron）记录已平仓票平仓日后走势（post_exit_peak / 3m_return），验证卖出时机
- 纯观察不碰选股/下单；首样本 VRRM 显示砍早了（平仓后 +7.27%）
- 用途：等 8 月样本累积后，作为"长期持有 vs 及时止损"决策的数据支撑

## 策略定位
主题驱动季度埋伏（不是技术面短线）：
- 当前主题：AI电网基础设施
- 打分6维度：叙事变化 / 市场认知滞后 / 行业尾风 / 催化剂 / 可交易性 / 否定风险
- 持仓窗口：3-6个月

## 🎯 验证哲学：「先改进，再认输」（2026-06-02 确立）
> 主公定的标准。判断 P9 是否值得继续做的根本准则——不是「跑输就关掉」，而是「先想办法跑赢，真没机会才认输」。

1. **比就比狠的**：每次评估和 IWM(小盘) + SPY(大盘) + QQQ(科技) 三个指数一起比，且看风险调整后(Sharpe)。绝不只挑最弱的小盘股比、赢了就自我感觉良好。
2. **跑输 ≠ 关掉，而是 = 找原因改进**：哪个指数跑输了，先复盘根因（选股逻辑 / 参数 / 板块押错），再想办法跑赢。禁止亏了就乱调参数骗自己（改进必须有依据）。
3. **认输门槛很高**：必须多次迭代、跨多季度、风险调整后依然稳定跑输，才承认「这个方向没机会」、老实买指数。只要还有有依据的改进空间，就继续做。

⚠️ 这条是「带证伪心态做」的总纲：主动选股长期跑赢大盘极难（专业基金大多输给指数），所以验证标准必须狠，但认输标准也必须高。

## 自动运行流程（纽约时间 EDT）
- 每天 **08:00**：narrative_earnings_watch（叙事追踪财报哨兵：追踪票财报临近≤5天提醒对答案）
- 每天 **16:00**：signal_collector / signal_alert / catalyst_monitor（三件套）
- 每周一 **08:30**：narrative_weekly_sentinel（叙事追踪周记哨兵：抓新闻+AI出周记草稿+Discord发，只出草稿不落库）
- 每天 **20:30**（工作日）：price_guard（持仓跌幅 >7% 告警）
- 每天 **21:00**：price_snapshot（30/60/90 天节点价格记录）
- 每周一 **16:30**：scanner_tracker（持仓周报→Discord）
- 每周一 **16:45**：price_tracker（补历史价格）
- 每周三 **16:30**：thesis_monitor（thesis 失效→Discord 告警，不自动平仓）
- 每周日 **15:45**：gtrends_collector（alt-data sidecar 关键词趋势）
- 每周日 **16:00**：weekly_review（结果追踪周报→Gmail）
- 每周一 **09:30**：dossier_autowrite（趋势主线第2层 阶段2-B：**从档案自动解析对象**(读`**追踪代码**`字段,不硬编码)→yfinance 查价→给每对象轨迹表追加数据行；逻辑状态留🔍待校准等人工补；有崩溃告警；先于10:00周报让其读到最新轨迹）
- 每周一 **10:00**：dossier_weekly（趋势主线第2层 AI 周报：读趋势追踪档案→判逻辑状态→归档 trading/reports/weekly/ + email；护栏只事实分析不写买卖）
- 每周一 **17:15**：trend_verdict_check（第2层提速实验对答案：补信号层基线价+到期窗口机械判定落 trend_verdicts+Discord 报；BB 无权改判）
- 每月第一周一 **15:00**：screener（刷新候选股池）
- 每季度第一周一 **19:30**：run_scanner（季度主题扫描+自动 OPG 下单）
- 每季度第一周一 **18:30**：quarterly_review（季度复盘→Gmail）

## 🧪 第2层提速攒样本实验（2026-07-01 上线）
> 完整方案（唯一权威源）：`trading/notes/第2层提速攒样本方案_20260701.md` v0.2（经 Fable5 对抗审核修订，审核存档同目录 fable_audit_*）

- **一句话**：intraday 纸账户放开出手门槛——凡六维打分过的趋势全登记冻结，passed/borderline 建纸仓（统一 $25k/笔），rejected 只信号层记账当对照分布；对答案拆三本账（A排序力/B方向/C上下车）机械判定；验证"六维方法方向对不对"
- **账户物理隔离**：第2层实验=intraday（trend_paper_trade.py 锁死）；第1层 TIDE=swing（原样不动）。两账本永不交叉
- **DB**：trading.db 的 trend_* 5 表（judgments 冻结层 trigger 禁改 / signal_prices+paper_trades 数据层 / verdicts 判断层只 INSERT / scan_longlist 供给留痕）
- **操作入口**：登记 `python3 trend_registry.py add <json>`；建仓/平仓 `python3 trend_paper_trade.py buy|sell <judgment_id>`；对答案 cron 自动（周一17:15）
- **纪律红线**：verdict 机械落库 BB 无权改判；每月扫描长名单必留痕；rejected 不建仓不设下车信号；真钱双闸原纪律不动；**预注册映射=6个月主判 passed 组无优势→自动暂停第2层真钱新开仓+根因复盘**
- **里程碑**：2026-10 第1批3个月初判 / 2027-01 第1批6个月主判+第0批排序力初判 / 2027年中约30笔全走完出正式报告

## 架构原则
- thesis_monitor失效只告警，不自动平仓，等主公人工决策
- signal_collector积累60-90天后建theme_discovery.py（约2026年8月）
- 有效前置信号：8-K 8.01+1.01密集 / backlog跳升 / 政策信号；分析师首次覆盖是滞后指标
- **调试/临时脚本直接 `python3 xxx.py` 跑，不走 `run_py.sh`**（2026-06-22）：run_py.sh 内置失败 trap 告警，只服务正式 cron；拿来跑临时调试脚本时调试报错会误触发告警邮件（误报）。只有正式 cron 走 run_py.sh

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
- 默认账号：swing（纸交易）。**权益/现金一律实时查 Alpaca，文档不写死数字**（数字会过期，写死=埋雷）。注：旧记的 "$1M" 是错的，已废弃。
- 支持 account 参数切换：`"swing"` 或 `"intraday"`

## 🏗️ 双层结构（2026-06-10 主公定案；2026-06-12 趋势主线基建落地）
- **第1层 P9 = AI 自动实验田**（本 playbook 范围）：swing 账号、纸钱、全自动；任务=验证"AI 自动选股行不行"，**12 月验收定去留，期间不动不加码**
- **第2层 趋势主线 = 主力方向**：**intraday 账号**（至今未接任何代码、0 交易；余额实时查 Alpaca，旧记 "$1M" 是误记勿引用；真试水时建议重置 $20-50k）；人机分工=我参谋出报告+主公司令拍板（主公只出手 2 次：拍板买/拍板卖）；策略=吃鱼身；**六维判断框架**（v1.1 起：真金白银/利润上财报/巨头capex投票/供需缺口/渗透率S曲线/**利润来源分解-量vs价**）；双保险丝=成本-25%强制讨论+峰值-30%信号核查
- **隔离四层**：账号（P9 代码硬锁 `config.py:29 ALLOWED_WRITE_ACCOUNTS=("swing",)`）/数据库（trading.db 只有 P9）/cron（P9 交易系列 vs 趋势只有提醒+哨兵）/文档（本 playbook vs trading/notes/）；唯一交集=复用方法论与告警基建，不复用账号数据
- **趋势主线实体（全在 trading/notes/，INDEX.md 有登记）**：①趋势判断手册.md v1.1（尺子；两轮对抗审核后定稿）②趋势地图_2026Q2.md（排行榜；电力 5/5/国防 83% 领跑，NAND 一票否决）③电力链选股候选_2026Q2.md（选股模块 v0.1）④趋势观察池.md（W1-W7 信号+事件日历）
- **盯防三频率**：每天 17:05 FERC 哨兵（scripts/ferc_watch.py，一次性）→ 每周一 09:35 周检 W1-W7（scripts/trend_watch_reminder.py）→ 每季度全市场重扫地图
- **喂趋势协议**：主公丢一句话方向 → 我 24h 内交"硬数据+六维打分+像案例库谁+三选一归宿（过线入图深挖/苗头进观察池/不亮存档讲原因）"
- **当前状态（2026-06-12）**：等待触发——FERC 裁决落地（哨兵报警）→ 第一份一页纸方案（CEG/VST 重估）→ 7 月底 capex 季检 → 双闸过 → 第一仓讨论
- **2026-06-10 实证（方向定案依据）**：15 只持仓分析师覆盖 5-11 个、无一 ≤2——P9 赚钱票全是趋势股（AGYS +30%/LIF +20%）、亏钱票全是捡漏逻辑（SOUN/LZ/VRRM），实际赚的就是主题趋势钱

## 📓 公司叙事追踪系统（2026-06-27 上线，MVP）
P9 子系统，「主题累积研究 Loop」的**公司粒度分支**。方案全文 `trading/notes/新闻追踪方案_2026-06-27.md`。
- **核心哲学**：「新闻不是资产，假设才是资产。绑不到任何假设的信息不准进档案。」防沦为"勤奋新闻笔记库"。
- **补的空白**：现有 thesis_monitor/scanner_picks/dossier 全盯"已建仓持仓票"，这套补"**建仓前/观察期**对象的持续假设追踪+对答案"。**边界铁律=建仓即移交**（对象真建仓→假设追踪移交持仓监控，status 置`已移交持仓监控`，本系统只管建仓前）。
- **5 表**（trading.db）：narrative_hypotheses(假设主角) / narrative_evidence(证据,绑假设id+adoption采纳字段) / narrative_weekly_checkins(周记) / narrative_discard_log(被丢标题) / narrative_draft_archive(草稿存档)。
- **3 脚本**：`narrative_dossier.py`(手动录入CLI:init/add-hypo/add-evi/checkin/show) / `narrative_earnings_watch.py`(每天08:00财报哨兵,数据驱动解析追踪票) / `narrative_weekly_sentinel.py`(每周一08:30周记哨兵,抓新闻+claude CLI出草稿+Discord发,**红线=只出草稿不落库**)。
- **记录透明度铁律（三级）**：🔴动账本(改假设/信心/判应验失效/采纳驳回)逐条报"记什么+为什么"｜🟡证据入库(选哪条新闻/归因)让人看见可拦(MVP靠手动dossier天然满足)｜🟢纯留痕(草稿/快照/日志)汇总报+声明未改判断。判断线=透明对象是"语义动作"非"数据库动作"。
- **当前状态**：VST 1 只试点（假设A核心=AI电力需求含核电观察点/假设C次要=量vs价，均信心3、复看8/6）。先跑 6-8 周验流程，**结论限定"工作流值不值得扩展"非"系统有效"**，通过再铺3只。**8/6 VST财报=第一次对答案+补实"待核实"阈值**。人机分工=哨兵自动+CC每周绑证据出判断+主公审稿+关键点拍板。

## 当前阶段（2026-06-10 更新）
积累阶段（纸账号 swing；equity/cash 实时查 Alpaca，不写死）：
- **15 只真实持仓**（filled 7 / filled_late 8，含 6/10 补录 GNTX/WTS）
- OPG fill 率实测 17%（1/6，5/19）；注意部分成交规则（见状态机）
- **C项扩展（2026-06-10 上线）**：6 分项分数 + analyst_count/avg_dollar_volume 入库（scanner_picks+watchlist）；watchlist 改全量留底（含 <5 分低分票=评分系统对照组）+scan_price；8/4 扫描自动生效。已知问题：评分通胀（全 9-11 分，market_lag/tradability 缺数据基础 LLM 编分）——prompt 重校准属改策略，等 6 月底数据后议
- **2026-05-30 攒样本提速（季度框架内，节奏不变）**：每只下单金额 $3000→$1000、单只硬上限 $5000→$2000、季度埋伏上限 top10→top25、batch_max 15→30。理由：hit rate 算 return% 与金额无关，缩小金额+拓宽广度→同现金埋更多票→更快攒够 30+ 样本（统计门槛），且引入分数梯度验证评分系统。⚠️ 不改扫描频率（季度叙事埋伏是策略本身，数据回来前不改策略）。
- 次季度扫描：8/4 周一 19:30 EDT（按新参数最多埋 25 只，C项扩展字段自动生效）
- 下一个关键节点：6/17-18 晚批首批 30 天 outcome（提醒 cron 6/18 09:15 已就位）/ 6 月底 hit rate / 8/4 Q3 扫描
- alt-data sidecar：4-8 周只观察，1 年后 sample 累积 50+ 才考虑入评分；**gtrends_collector 已加 SerpAPI KEY1→KEY2 自动 fallback + 全失败邮件告警（2026-06-10，KEY1 配额耗尽断供 2 周教训）**

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

---

## 🔮 玄学分隔离观察（2026-06-01 上线）

**这是什么**：scanner_picks 多了 5 个列（meihua_score / meihua_hexagram / meihua_relation / meihua_random / listing_date），P9 建仓时由 `trading/meihua.py` 自动算一个梅花易数"玄学分" + 一个 hash 随机对照分写库。

**⚠️ 关键边界 — 只记录，绝不参与决策**：meihua 在 `cognitive_scanner.py` 里只出现在 import + 写库两处，不入任何筛选/打分/排序/下单逻辑。算分异常（如 yfinance 拿不到上市日）会留空，绝不影响下单。**改 P9 选股/下单逻辑时不要去读这几个列**。

**起卦规则（v4，100% 可复现）**：本命=上市日(yfinance首个交易日)月/日；当下=建仓日/时辰（历史无时分用午时占位，实时建仓用真实 datetime）。主分=体用五行生克(base50)，微调=动爻位置 ±3 + 互卦 ±3。

**验证计划**：攒 1-2 季度、平仓后用真实收益验证。**玄学分必须跑赢随机对照分(meihua_random)才算真信号**，否则就是噪声。当前 n=14 浮盈下与收益轻微负相关(Spearman -0.125)但统计不显著。

代码：`trading/meihua.py`（独立模块，可 `python3 meihua.py` 自测）。

---

## 🎨 P9 前端作品集 Dashboard（2026-06-04 规划，待开工）

**定位**：把 P9 硬核后端做成**求职作品集**（情况A，主公 2026-06-04 确认）——给招聘方/面试官看，不是给自己爽。
**Why**：P9 是主公最硬核作品(AI驱动+量化+全自动+真实数据)；可视化 Dashboard 让招聘方 30 秒看懂能力，面试直接演示——**还能绕过主公英文口语弱点（东西会说话）**。这是把"已存在的后端"变现成求职敲门砖 = "砍柴"非"磨刀"。

**数据源**：`trading/trading.db`（数据齐全，不用补）——scanner_picks / outcome_tracking / trades / thesis_alerts。

**MVP 范围（只做4块，多一块都不做）**：
1. 总览卡片：总收益% vs IWM/SPY基准 + 胜率 + 持仓数
2. AI选股逻辑展示：点开个股看 AI 生成 thesis（差异化核心，证明"AI驱动"）
3. 收益曲线图：组合 vs 基准曲线
4. 自动化流程图：扫描→AI分析→下单→对账→追踪 全自动链路（证明工程能力）

**技术选型**：Streamlit（Python，最快出活，零前端基础可做）；不用 React/Vue（那是磨刀）。

**执行3步**：①30min 搭骨架(只总览卡片)能打开 → ②2-3天填另3块,始终保持可演示 → ③4-5天抛光+部署 Streamlit Cloud 得公开链接塞简历/LinkedIn。**时间盒：1周出可演示 MVP。**

**⚠️ 磨刀红线（防火土旺无限完善）**：❌不做登录/实时刷新/手机适配/多主题/重构后端/优化DB。✅只要"打开网页招聘方能看懂这是个AI量化系统"就算砍下这根柴。

**下一步**：主公说"开始"→ 写 `trading/dashboard.py` 第1步骨架。

---

## 📚 投资学习笔记库（怎么思考投资）

本 playbook 记"怎么操作 P9 系统"；投资思维/方法论笔记另存 `trading/notes/`（读 `notes/INDEX.md`）。
首篇 `认知内的钱_瓶颈理论.md`：只赚认知内的钱 + Serenity 瓶颈理论 + P9 与之的关系（2026-06-04）。
