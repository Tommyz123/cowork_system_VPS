---
name: P9 研究阶段自动下单规则
description: 研究阶段（paper trading）P9 cognitive_scanner 扫描后直接下单 swing，3 层 sanity check 替代人工 approve gate；转真钱时必须重新设计
type: feedback
originSessionId: 0d07266c-759a-4496-87e2-e643a71c00e1
---
P9 研究阶段（2026-05-18 主公明确"目前研究策略状态，不会用真钱"）→ cognitive_scanner 扫描后**直接 paper 下单**，不再需要人工 approve。

**Why**：
1. 纸账户没真钱，approve gate 是为真钱设计的风控，研究阶段过度工程化
2. 人工 approve 引入"我看哪只顺眼"的认知偏差，污染量化信号 attribution
3. 减少主公认知负担 + 提升 sample size 入库节奏
4. 5/11 ghost positions 事件揭示：scanner 写 DB 但不下单 + 缺乏明确提醒 = ghost data 风险 → 自动下单消除中间环节

**How to apply**:

1. **cognitive_scanner.py 行为**（已固化 2026-05-18）：
   - 扫到 top picks（评分 ≥ 5）→ 立即调 alpaca swing place_order opg 单（次日开盘成交）
   - DB INSERT `status='filled', cohort='auto_filled', signal_date=scan_date, signal_entry_price=current_price`
   - trades 表同步写入（fill_price 为 NULL，等 sync_fill_prices.py 次日 9:45 EDT 回填）

2. **4 层 sanity check（顺序执行，任一拒绝就跳过该只）**（2026-05-18 A1 方案升级）：
   - **(a) Dedup**：scanner_picks 已有 status IN ('candidate','filled','filled_late','auto_filled') → 跳过
   - **(b) 单只 notional 上限 $5000**：qty=round(3000/price)；qty*price > 5000 → 拒绝
   - **(c) 单次扫描下单数量上限 15 只**：防 scanner bug 量级失控
   - **(d) buying_power 充足检查**（A1 新增）：扫描开始拉 swing buying_power，每只下单前检查剩余 buying_power >= $3000 (NOTIONAL_TARGET)，不足则拒所有后续 + Discord 警报。防止 paper account 耗尽时 Alpaca 403 拒单产生 ghost positions。
   - 已存在的"仓位限制"check（单股 $150k / 板块 $600k）仍生效

3. **下单参数**：market + time_in_force='opg'（next-open）
   - 季度扫描跑在周一 17:00 EDT（盘后），opg 单周二 9:30 EDT 开盘自动成交
   - fill_price 反映 overnight gap，与 signal_entry_price 的差额 = "执行延迟成本"研究维度

4. **Discord 推送变成事后通知**（不再"待审核"）：
   - 标题："📋 P9 认知滞后扫描 已自动下单"
   - 内容：每只标 ✅ 已下单 N 股 / ❌ 拒绝 (原因)
   - 总 notional + 单次入围 / 实际下单 / 拒绝 三个数字

5. **🚨 转真钱阶段时必须重新评估**：
   - 自动下单仅限纸账户
   - 真钱前必须：① 恢复 'candidate' 状态值 ② 重启 approve gate 机制 ③ 加强 sanity check（buying_power 实时查 + 单日下单总额上限 + 异常 ticker 黑名单）
   - 不要假设"paper 跑得好真钱也能直接上"

6. **每只仓位标准化为 $3000**（与历史 5/06 + 5/11 + 5/18 三个 cohort 一致），保证 attribution 横向可比

**配套机制**：
- `submit_pending_picks.py` + `approve` 机制已 2026-05-18 删除（研究阶段不需要）
- DISCORD_AUTHORIZED_USER_ID 配置保留在 api_keys.env，未来转真钱时重新启用
- weekly_review_preview.py 新增 'auto_filled' cohort 分段显示
