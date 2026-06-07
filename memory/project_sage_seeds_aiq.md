---
name: Sage Seeds Alpine IQ 数据能力边界
description: P8 Sage Seeds 营销分析能用 Alpine IQ 数据做什么、做不了什么（活动归因可做/优惠码核销查不了）
type: project
originSessionId: 4542a474-0cbf-47ba-9318-477a82d9b2b2
---
P8 Sage Seeds（主公在职大麻店）的客户数据存在 Alpine IQ，做营销效果分析时数据能力边界如下（2026-06-07 实拉数据探明）：

**能做：**
- **活动归因**：每笔流水带 `cmpID`（活动编号），共 166 个不同活动 → 能算每个活动带来多少购买/营收/回头率，排名"哪个活动最有效"。
- **触达漏斗**：`action.label` 记录 email_received/text_received/email_open/text_click/email_click → 能算每个活动的打开率/点击率/转化率，看哪一步掉人。
- **折扣力度分析**：order 层 `totalDiscount` → 可交叉看"折扣大小 vs 回头率"。

**做不了（缺口）：**
- **单优惠码核销**：`discID`（优惠码字段）在数据里**全是空的** → 查不到"哪个码被核销几次"。只能到"活动级"归因，到不了"单码级"。
- code 归因（用专属码 100% 确认"是因为这个活动回头"）**理论上 Alpine IQ 后台建码可行（discID 字段设计支持），但未实测有值情况**——需老板建测试码用一次后重拉看 discID 是否出现才能下结论。

**Why:** 主公反复问"怎么知道活动有效果/是不是这个活动的功劳"，核心是归因方法。摸清边界后才能给对的方案（用 cmpID+对照组，而非依赖暂时查不到的 code 核销）。

**How to apply:** 给 Sage Seeds 营销效果分析方案时：归因优先用 cmpID（活动级）+ 对照组（真增量）；别承诺"按优惠码查核销"除非老板已在 Alpine IQ 建码且实测 discID 有值。拉数据/字段详见 sage_seeds/aiq/API使用记录.md + 数据结构图.md。
