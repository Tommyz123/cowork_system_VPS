---
date: 2026-05-18
incident: P9 数据完整性事件
severity: 高（影响所有 alpha 计算 + ORA case study 决策依据 + weekly_review）
status: 已诊断，未修复（主公 2026-05-18 06:03 指示"先记录原因和修复方式，别着急执行"）
---

# 2026-05-18 P9 数据完整性事件 RCA

## 一句话总结

P9 数据库里 14 只标 `status='open'` 的"持仓"，实际只有 6 只真在 Alpaca swing 账号成交；另外 8 只是 DB-only 虚拟记录。同时 intraday 账号有 ORA 261 股遗留持仓（手动操作，非 P9 系统）。所有下游分析（alpha 计算、weekly_review、ORA case study 里"14 只里 alpha 第一"）都建立在不一致的前提上。

---

## 事件时间线

| 时间 | 事件 |
|---|---|
| 2026-05-06 | cognitive_scanner 扫描第一批 6 只入 DB（ORA/CPK/CSW/LZ/VRRM/WTRG），主公**手动**下单到 swing |
| 2026-05-06 | 同日某时刻主公**手动**下 ORA 261 股到 **intraday 账号**（原因待主公确认：测试？误操作？） |
| 2026-05-11 | cognitive_scanner 扫描第二批 8 只入 DB（AGYS/ARLO/FSS/HCC/LIF/MIR/SOUN/VSEC），**未真实下单** |
| 2026-05-15 | IWM 基准 bug 修复，alpha 计算切换到 IWM——但底层 entry_price 仍是"虚拟"价格 |
| 2026-05-17 | 周日做 weekly_review V2 + ORA case study，全部基于"14 只都真实持仓"的错误前提 |
| 2026-05-18 00:30 | 主公要求 audit 双账号 |
| 2026-05-18 06:00 | audit 跑完发现两个独立问题 |

---

## 根因分析（5-why）

### 表层错误
14 只 `status='open'` 里 8 只其实是 DB-only 虚拟记录；ORA 在两个账号同时持仓。

### Why 1: 为什么 5/11 批没真实下单？
因为 cognitive_scanner.py 的 `write_scanner_picks` 函数**完全没有调用 Alpaca place_order**。整个文件里所有 `requests.post` 调用都是发 Discord 消息（line 228 + 252），不是下单。

### Why 2: 为什么 cognitive_scanner.py 没下单功能？
**by design**——这个脚本的设计是"扫描 + 评分 + 写 watchlist"，下单是主公手动通过 alpaca_mcp.place_order 或 close_position.py 或 Alpaca Web UI 完成。这是"AI 出 candidate，人决定下不下"的解耦设计。

### Why 3: 为什么解耦设计会导致数据混乱？
因为 scanner_picks 表用 **`status='open'`** 这个**语义模糊的状态**——它在 P9 设计里意思是"已 INSERT 到 watchlist 等手动下单"，但 'open' 在金融行业普遍意味着"已成交持仓"。所有下游脚本（scanner_tracker / weekly_review / thesis_monitor / 我的 case study）都默认 `status='open'` = 真实持仓。

### Why 4: 为什么没有 reconciliation 机制发现这个不一致？
**没有任何脚本对账 DB ↔ Alpaca**。最接近的是 `sync_fill_prices.py`，但它只同步**已成交订单的 fill_price**——不会发现"DB 有但 Alpaca 没下单"的差异（这是单向 sync 而非 reconciliation）。

### Why 5: 为什么连续两次（5/06 + 5/11）出现都没被发现？
- 5/06 那次主公真的手动下单了（fill_price 同步成功），表象上没问题
- 5/11 那次主公**没下单**，但因为没人对账，DB 继续显示 'open'
- 每日 scanner_tracker / weekly_review 用 yfinance 实时价 + DB entry_price 算 alpha——计算逻辑能跑，**结果数字看起来合理**，所以没暴露异常
- 5/15 的 IWM bug 修复反而让数据看起来"更专业"了，进一步掩盖底层问题

### 真正的根因（结构性）

**"open" 状态的语义不明 + 缺少 DB-Alpaca reconciliation + 信任 DB 而不信任 broker"** 三者叠加。

最深层是**信任模型错误**：P9 系统当前把 DB 视为权威数据源（source of truth），但实际上 **Alpaca 才是权威**——DB 应该是"对 Alpaca 状态的本地视图"，定期 reconciled。

### 附加：ORA intraday 261 股的成因（推测，待主公确认）

可能场景：
- A. 主公早期测试 alpaca_mcp.place_order 时下到默认账号（intraday 当时是默认）
- B. 第一系统遗留——5/06 删除第一系统前，scanner 把 ORA 当 candidate 但用 intraday 默认下了单
- C. 主公手动测试 P9 时，账号参数没指定，默认走 intraday

需要主公回忆/确认。但**根因不变**：alpaca_mcp.place_order 当时默认 swing，但能接受 intraday——**没有写白名单**就让 intraday 下单成为可能。已在 2026-05-18 锁死（assert_p9_account）。

---

## 修复方式

### 修复优先级 P0（数据立即一致）

**Option 1.A: 重新分类 8 只虚拟持仓**
- 把 5/11 那批 8 只的 `status='open'` 改成 `status='candidate'`（新增 status 值）
- 所有下游计算（alpha / weekly_review）排除 candidate
- 不下追单
- **优点**：诚实承认数据现实；与"hypothesis 研究框架"定位一致
- **缺点**："组合"瞬间从 14 只变 6 只，叙事调整
- **副作用**：之前发的 weekly_review / case study 需要修订或标注

**Option 1.B: 追单**
- 按 5/11 entry_price 追单到 swing，让数据对齐
- **优点**：保留 14 只组合连续性
- **缺点**：slippage 真实存在（5/11 → 5/18 价格有变化），追单价格不是真实 entry；本质上是"用未来数据回溯下单"，是数据捏造的另一种形式
- **副作用**：未来 outcome 数据带 slippage bias，attribution 失真

**Option 1.C: 当下重新建仓**
- 5/11 那批 8 只今天市价重建仓位
- entry_price 改成今天的市价
- **优点**：建仓真实
- **缺点**：丢失 5/11 那批的"原始 thesis 入场价"信息；entry_price 和 thesis 写作时间脱节
- **副作用**：14 只持仓时间线散乱（6 只 5/06 + 8 只 5/18）

### 修复优先级 P0（ORA intraday）

**Option 2.A: 保留 + 标记**
- intraday 的 ORA 261 股保留，但在 DB 加一行 `source='manual_legacy', account='intraday'`
- 所有 P9 计算只看 swing 账号那 27 股
- **优点**：不动既有持仓
- **缺点**：两个账号持续存在，主公仍然要管两个账号资金

**Option 2.B: 清仓**
- 明天开盘卖掉 intraday 的 261 股
- **优点**：彻底统一到 swing 账号
- **缺点**：放弃 261 股 ORA 的潜在上行（如果 ORA 继续涨）；变现操作真实发生
- **副作用**：变成纯粹"清理动作"，与 P9 thesis 无关

**Option 2.C: 合并到 P9 体系**
- intraday 的 261 股加入 P9 ORA 总敞口计算（27 + 261 = 288 股）
- 但实际下单/平仓仍只走 swing
- **优点**：账面真实
- **缺点**：两个账号继续存在，复杂度增加；仍违反"统一一个账号"原则

### 修复优先级 P1（防止复发 — 结构性）

**Fix 3.A: 语义清理 — scanner_picks.status 增加 'candidate'**
- 新增 status: `candidate` (DB only, 等待手动 review) → `filled` (Alpaca 已成交) → `closed` → `archived`
- Migration: 现有 'open' 拆成 'filled' (实有 6 只) + 'candidate' (虚拟 8 只)
- 下游脚本只查 `status='filled'` 做真实持仓分析
- 'candidate' 在 weekly_review 单独成段（"待主公审核的扫描结果"）

**Fix 3.B: 新增 reconciliation 脚本**
- `trading/reconcile_positions.py`：每日 17:00 EDT（盘后 1 小时）跑
- 三方比对：scanner_picks DB ↔ Alpaca swing positions ↔ Alpaca swing orders（30d）
- 不一致告警（Discord + Email）：
  - DB filled 但 Alpaca 没有 → 数据捏造警告
  - Alpaca 有但 DB 没记录 → 主公私下下单警告
  - qty 不匹配 → 部分成交/部分平仓警告
- 同时校验 intraday 账号没有 P9 symbol（防 ORA 类污染复发）

**Fix 3.C: cognitive_scanner.py 行为调整**
- 新增 `submit_pending_picks.py`：扫描后 Discord 推 candidate 列表，主公**显式 reply "approve TICKER"** 才下单
- 默认仍只写 DB candidate，**永不自动下单**（保留人工决策最终权威）
- 主公审核后才更新 status='filled'

**Fix 3.D: 文档 + Memory**
- playbook 顶部加 ⚠️ box：**"scanner_picks.status='open' ≠ 真实持仓"**
- memory 新增 `feedback_p9_data_reconciliation.md`：未来读 scanner_picks 必须先 reconcile
- weekly_review 第一段加"data integrity check"：自动跑 reconciliation 不通过则标 ⚠️

---

## 怎么防止下次不会再犯（结构性预防）

### Level 1: 语义层
**永不允许"语义模糊的状态字段"** — `open` 这种词在不同上下文意思不同（candidate vs filled vs visible）。所有状态字段必须用**领域明确的词**（candidate / filled / partially_filled / closed / cancelled / invalidated）。

代码层：scanner_picks 的 status 值必须从 `STATUS_VOCAB` 这个 Enum 来，不能自由字符串。

### Level 2: Trust boundary 层
**Single source of truth 必须明示** —
- 实盘持仓：**Alpaca 是 SoT**，DB 是缓存
- thesis / attribution / 历史 narrative：**DB 是 SoT**
- 任何脚本读取 "持仓数量 / fill_price / 实际敞口" 必须从 Alpaca 拉，不能信任 DB

### Level 3: Reconciliation 层
**每日强制对账**（cron 17:00 EDT）—
- 三方比对：DB ↔ Alpaca swing ↔ Alpaca intraday（防污染）
- 任何不一致自动 Discord 告警，主公需要 acknowledge 后才能继续 weekly_review

### Level 4: 流程层
**Candidate → Filled 必须有"主公明确动作"** —
- AI 不自动下单
- AI 只发 candidate 列表
- 主公 reply "approve X, qty Y, account swing" 才下单
- 下单成功后才 UPDATE status='filled'，并记录 broker_order_id

### Level 5: 监控层
**周报必须含 data integrity 段** —
- weekly_review V3 第一段：
  - DB filled count vs Alpaca position count（必须 match）
  - intraday 账号是否有 P9 symbol（必须 0）
  - 任何不一致直接红字 ⚠️ + 阻止周报继续输出

### Level 6: 文化层
**"AI 写的数据需要被验证"** —
- memory 新增 feedback：任何 P9 数据分析（subagent / 主分析 / case study）开头必须先调 reconciliation 函数验证数据可信度
- 失败则标"基于 unverified data"

---

## 当前已采取的临时措施（2026-05-18 06:00 已完成）

- ✅ close_position.py 强制 account=swing，移除 intraday 参数
- ✅ alpaca_mcp.py 的 place_order / cancel_order 加 `assert_p9_account(account)` 守卫
- ✅ config.py 新增 `P9_ACCOUNT = "swing"` + `ALLOWED_WRITE_ACCOUNTS` + `assert_p9_account()` 函数
- ⏳ 5/11 虚拟 8 只 + ORA intraday 261 股 = **未处理**（主公拍板后再动）
- ⏳ Reconciliation 脚本 = **未实现**（主公拍板后再写）
- ⏳ status 语义清理 = **未实现**（同上）

---

## 元数据 / 复盘锚点

- 本次事件揭示了 P9 系统"AI 写 DB + 人工下单"的解耦设计存在 trust boundary 失明
- GPT 5/17 文档警告"市场可能是 theme beta 不是 stock alpha"——但实际更深的问题是 **DB 数据本身就部分是虚拟**，alpha 计算的分子（持仓收益）和分母（资本占用）都有可能是假的
- 此 RCA 应作为 P9 设计文档的一部分长期保留
- 6 月 5 日第一批 30 天 outcome 入库前**必须**完成 status 语义清理 + reconciliation
