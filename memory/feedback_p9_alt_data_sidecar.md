---
name: P9 alt-data sidecar 设计与研究纪律
description: P9 alt_signals 表 + gtrends_collector.py 完全独立于 P9 主线，静默收集不入评分，主公 on-demand query
type: feedback
originSessionId: 0d07266c-759a-4496-87e2-e643a71c00e1
---
P9 alt-data sidecar（2026-05-18 建立）：完全独立的旁路模块，收集 Google Trends theme search volume，**不影响 P9 主线任何流程**。

**Why（设计原则）**：
1. 林奇 mall observation 在 P9 直接 emulation 不适用——14 只持仓 79% 是 B2B 小盘股，公司名 brand search 几乎全是 noise floor
2. 改用 **theme-level 搜索热度**（5 个 theme 关键词）作为替代——跟 P9 评分体系的 tailwind 维度对齐
3. INSIGHTS.md 历史只有 1 条 insight → 主公不是会主动记录的人，所以走 **静默后台 + on-demand query** 模式，不强迫主公手动操作
4. 4-8 周内不入 cognitive_scanner 评分，避免未验证的信号污染选股

**How to apply**:

1. **架构 0 耦合**：
   - alt_signals 表跟 scanner_picks/trades 表**互不交叉**
   - gtrends_collector.py 跟 cognitive_scanner.py / weekly_review_preview.py **零代码依赖**
   - 删 sidecar 不影响 P9 主线运行

2. **5 个 theme 关键词**（2026-05-18 dry-run 验证有强信号）：
   - AI 软件 → `generative AI software`（非零 100%, avg 53.5）
   - 公用事业现代化 → `utility infrastructure`（非零 100%, avg 45.8）
   - AI 电力 → `data center energy demand`（非零 81%, avg 32.8）
   - 分析师重定价 → `stock upgrade`（非零 100%, avg 47.9）
   - 行业重分类 → `sector rotation`（非零 98%, avg 36.7）

3. **数据流**：
   - 周日 15:45 EDT cron 跑 gtrends_collector.py
   - SerpAPI Google Trends interest_over_time 拉 5 个 theme 12 个月 weekly 数据
   - 写入 alt_signals 表（UNIQUE(signal_type, keyword, week_start) dedup）
   - 跑完发 Discord 简要回执

4. **主公 on-demand 查询**：
   - 主公任何时候 Discord 问"看下 AI 软件最近搜索热度" → 我 SQL query alt_signals 表 → 给数字 / 趋势图
   - 6/14 + 8/9 outcome 出来时主动给主公拉 14 只 theme search 4 周变化 vs 30/90 天 alpha 对比表

5. **研究纪律（关键）**：
   - **4-8 周内只观察不量化**——不进 cognitive_scanner 评分、不影响选股
   - **1 年后 sample 累积 50+ 持仓 + 50+ outcome** 才考虑做正式 IC / Sharpe uplift 检验
   - 如果 1 年后验证有 alpha → 加入 cognitive_scanner 评分；如果没有 → 写 `negative_result_p9_gtrends.md` 删模块
   - **不堆 feature**：现在只做 theme-level 1 维，不扩展到个股层 / 不加 Reddit / JD 等其他 alt-data 源（除非这一维度先验证有价值）

6. **SerpAPI quota 共享原则**：
   - SerpAPI 双 key 200 query/月共享池
   - 机票监控（周二/周四）≈ 40-80 query/月
   - gtrends_collector（周日 × 5 theme）= 20 query/月
   - 剩余 quota 充足，未来扩展（个股层 / 其他 alt-data 源）前必须先查 quota

7. **不破坏现有 P9 架构边界**（关键）：
   - 任何修改 cognitive_scanner.py 评分逻辑 / 改 weekly_review 引入 alt_signals / 改自动下单 → 都属于"破墙"行为
   - 破墙前必须：① 4-8 周观察验证 ② 写 RFC ③ 等主公拍板
