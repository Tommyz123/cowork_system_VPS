---
date: 2026-05-19
incident: OPG 单 5/6 expired → ghost positions 反模式复发
severity: major（数据不一致 + 昨天 RCA 识别的根因未根治 → 24h 内复发）
status: 已诊断并修复（cognitive_scanner.py + sync_fill_prices.py 升级 reconciler + 5 只数据修正）
related: rca/2026_05_18_ghost_positions_and_intraday_contamination.md（前置 RCA）
---

# 2026-05-19 OPG Expired → Ghost Positions 反模式复发 RCA

## 一句话总结

5/18 19:30 EDT cron 首次自动下单 6 只 OPG 单，5/19 9:30 开盘只有 ASTE 成交，5 只（GNTX/GWRE/OLLI/CXT/APPF）expired。但 DB 里 6 只全标 `status='filled' / cohort='auto_filled'`——5 只**没买进来的虚假持仓**被下游 13 个脚本当成真实持仓查询。这是 5/18 RCA 识别的 ghost positions 反模式在自动下单流程上的复发，相隔不到 24 小时。

---

## 事件时间线

| 时间 (EDT) | 事件 |
|---|---|
| 2026-05-18 06:00 | 5/18 RCA 识别 ghost positions 根因："信任 DB 而不信任 broker" + status 语义模糊 + 缺少 reconciliation |
| 2026-05-18 15:55 | ghost positions **数据修复**完成（5/11 批 8 只手动补单），但 `cognitive_scanner.write_scanner_picks` 写入逻辑未改 |
| 2026-05-18 19:30 | cron 首次自动扫描 → 6 只 OPG 单提交 → `scanner_picks` INSERT 时硬编码 `status='filled' / cohort='auto_filled'` |
| 2026-05-19 09:30 | 开盘 → ASTE filled / 5 只 expired |
| 2026-05-19 09:45 | sync_fill_prices.py cron 跑，但脚本仅在 Alpaca status=filled 时动手，对 expired 的 5 只不动 DB → 5 只虚假持仓在 DB 中"看起来仍正常" |
| 2026-05-19 10:20 | 主公询问 P9 情况，手动跑 sync 发现 5/6 expired |
| 2026-05-19 10:55 | 主公"好好想想"提示，识别反模式复发 |
| 2026-05-19 11:10 | 根治方案落地完成 |

---

## 根因分析（5-why）

### 表层错误
5 只 OPG expired 在 scanner_picks 表中 status='filled' / cohort='auto_filled'，污染下游 alpha 计算。

### Why 1: 为什么 DB 标 'filled' 但实际未成交？
`cognitive_scanner.py:518` INSERT 时**硬编码** `status='filled', cohort='auto_filled'`，不论 Alpaca 实际返回什么 status。

### Why 2: 为什么 cognitive_scanner 写入逻辑这么粗？
2026-05-18 12:30 修改时（主公"研究阶段不会用真钱"决定后），把 approve gate 砍掉直接自动下 OPG 单。当时假设"OPG 单基本都会成交"——**这个假设错了**（实测 OPG 1/6 fill 率）。

### Why 3: 为什么 5/18 RCA 已识别根因但未根治？
5/18 RCA 写完后主公指示"先记录原因和修复方式，别着急执行"，修复优先做了 P0 数据层（手动补单 + status 改成 IN('filled','filled_late')），**写入层的反模式未改**。然后 5/18 下午加了 auto_filled cohort 新功能时**直接复用了同样的硬编码模式**。

### Why 4: 为什么修复 ghost positions 数据时没顺便加 reconciler？
sync_fill_prices.py 当时职责只是"回填 fill_price"，只在 status=filled 时动手。对 expired/canceled/rejected 完全不处理——**单向 sync 而非 reconciliation**。RCA 文档里识别了这点，但没在数据修复阶段一起改。

### Why 5: 为什么连续两次反模式同款复发？
- 5/18 是手动下单 + INSERT 不实际下单（5/11 批 ghost）
- 5/19 是自动下单 + INSERT 假设全 fill（OPG ghost）
- **同样的反模式**："DB 状态由意图驱动而非现实驱动" + "缺少 reconciliation"
- 修第一次时只补数据没补流程 → 第二次以新形态复发

### 真正的根因（结构性）

**反模式的根治必须在代码层（写入路径 + reconciler 路径）同时改，只修数据是头痛医头。**

5/18 RCA 文档里明确写了根因，但修复阶段没把"代码层改造"列为 P0，导致同款问题以新形态在 24 小时内复发。

---

## 修复方式（已执行 2026-05-19 11:00-11:10 EDT）

### Code 层（防再复发）

1. **`cognitive_scanner.py:518`**：INSERT 状态 `'filled'/'auto_filled'` → `'submitted'/'auto_pending'`
2. **`cognitive_scanner.py:465`**：dedup 查询加 `'submitted'`，避免同股下次扫描重复下单
3. **`cognitive_scanner.py:428` docstring**：更新职责说明 + 加 RCA 反向链接
4. **`sync_fill_prices.py` 升级为 reconciler**：
   - filled → status='filled' / cohort='auto_pending'→'auto_filled' + 回填 fill 字段
   - expired/canceled/rejected → DB 同步成同名状态
   - accepted/pending_new/new/submitted → 不动 DB
   - 输出 reconciliation 简报（filled/expired/canceled/rejected/pending 计数）

### Data 层（当前 5 只历史遗留数据）

- 手动 UPDATE `scanner_picks` 5 行：status='expired' / cohort='auto_expired'（历史遗留数据无法靠新 reconciler 修，因为它们的 cohort 是老版 'auto_filled' 不是 'auto_pending'）
- trades 表已被 reconciler 标记为 status='expired'（5 行）
- ASTE 1 只正常 filled，cohort='auto_filled'，无需动

### 验证（已通过）
- weekly_review 查询 status IN('filled','filled_late') → 15 只（14 老 + ASTE），符合预期
- cohort × status 分布：early_filled/filled=6 / late_fill/filled_late=8 / auto_filled/filled=1 / auto_expired/expired=5
- 持仓 fill_entry_price 全部非 0，fill_date 全部非 NULL

---

## 防再复发措施

1. **检查清单（写入 DB 状态的所有 P9 脚本必检）**：
   - INSERT scanner_picks / trades 时，status 是否反映**broker 实际状态**而非"我们假设的状态"？
   - 如果是异步执行（如 OPG 单），用 'submitted' / 'auto_pending' 中间态，由 reconciler 后续更新

2. **sync_fill_prices.py 现在是真正的 reconciler**——下次有同类问题（任何异步 broker 状态变化）应优先增强它而非新建脚本

3. **RCA 修复执行清单**：
   - 数据层修复 ≠ 流程修复
   - 反模式识别后，**必须**列出"代码层改造任务"作为 P0/P1，不能只修数据

4. **memory 更新**（已写）：
   - `feedback_p9_no_ghost_data.md` 补充"反模式不能只在数据层修，必须在写入层根治"
   - 新增 `feedback_db_reflects_broker.md`：DB 状态必须反映 broker 真实状态原则

---

## 研究阶段发现（次要但有价值）

**OPG 单在 Alpaca paper account 的实测 fill 率：1/6 = 17%**

- ASTE filled $48.78（vs signal $47.50，gap up 2.7%）
- GNTX expired，但有 fill_price=22.56（partial fill 后 expire？需诊断）
- GWRE/OLLI/CXT/APPF expired，fill_price=None（开盘 gap up 超过 OPG limit 价）

**对 Q3（8/4 19:30 EDT）真正季度扫描的影响：**
- 若 fill 率仍 ~17%，15 只满载 × 17% = 2-3 只成交/周
- buying_power $155K 在 5/18 现状下能撑 ~3 周 → 实际 fill 率低则撑更久
- 但研究 cohort sample 也会更少（每周 2-3 只 vs 预期 15 只）

**待评估：**
- 是否改 OPG 单为 day market on open 单（保证成交但接受 gap 价）
- 还是接受 OPG 低 fill 率作为"筛选机制"（gap up 太多的不要）
- 此决策待主公在 Q3 实战前定（2026-08 之前）

---

## 给未来的我的一句话

**反模式识别后，列代码层改造任务为 P0。只修数据不修流程 = 等下次以新形态复发。**
