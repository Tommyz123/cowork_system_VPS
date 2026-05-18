---
name: P9 thesis 写作必须 hypothesis 化（不许 declarative + 不许未验证精确数字）
description: 写 bull/bear thesis 时强制 hypothesis 语气，不许"是 contra-indicator/反映 X"等 declarative；未验证精确数字不许出现在 thesis 散文，只能放监测信号
type: feedback
originSessionId: b68a0307-4fb1-4816-ae90-9f3443efdd9c
---
写 P9 bull thesis / bear thesis / case study 时，**强制 hypothesis 语气**，不许 declarative 断言。

**Why**: 2026-05-18 主公转发 GPT 第二次方法论纠偏（Thesis Language Normalization），指出之前我写的 3 条 bear thesis "方向对、结构对、但写得过于确定"。具体问题：
- ❌ "Hold→Buy 升级是 contra-indicator（top tick 信号）" — declarative，假装有统计支持
- ❌ "PE <7x 反映 terminal value 折价" — declarative
- ❌ "forward P/S >30x，比 PLTR 还激进" — 未验证精确数字会因时间漂移失效
- ✅ "Late-cycle analyst upgrades **can sometimes** coincide with earnings/sentiment peak rather than durable rerating"
- ✅ "Valuation **appears elevated** relative to many software peers"

我自己写 ORA case study 时也犯同样毛病——把主观加权写成精确概率（"45% / 20% / 35%"）、把方向性判断写成精确数字（"+1.2% 90 天期望"）、把范围推荐写成单点（"trim 1/2"）。

**How to apply**:

1. **Hypothesis vocabulary 强制使用**：may / could / potentially / historically / suggests / appears / market skepticism / durability concerns / structurally / tends to / often
2. **禁止 declarative 断言**当缺乏统计支持时——区分"已被广泛验证的规律"（OK 用 declarative）vs"empirical 倾向但有反例"（必须用 hypothetical）
3. **未验证精确数字不许出现在散文**（thesis 主体）。具体阈值只能放在 hidden_risk 或监测信号里，且明确标为"研究者主观设定的监测阈值"，不是 fact
4. **范围 > 单点**：推荐操作时用区间（"trim 30-60%"），不用精确百分比（"trim 1/2"）。1/2 vs 1/3 vs 2/3 的边界 historically 是任意的
5. **可证伪结构**：每条 thesis 必须 specific 到能被 invalidation 触发，同时 hypothetical 到 6 个月后被打脸不会摧毁可信度
6. **历史 pattern 引用规范**：引用 Bloom Energy / Sunnova / Calpine 等公司时用"historically" "曾经"语气，不用"always" / "is"
7. **简单 vs 聪明不是分水岭**：真正分水岭是"可证伪 vs 不可证伪"。简单 thesis（如"市场低估 AI 电力需求"）如不能 falsify 同样是 narrative noise；聪明 thesis 如给出精确 monitoring signal 就是 high quality hypothesis

**适用范围**：
- cognitive_scanner.py 的 LLM prompt（已加入 2026-05-18）
- 写 case study（如 trading/case_studies/*.md）
- 写 weekly_review / quarterly_review 报告时的 thesis 评估部分
- 任何在 Discord 给主公推荐 P9 持仓操作的语言

**反向例外**：技术性表述、客观事实陈述（"ORA 当前 EV/EBITDA 12-14x" 如来自实时数据可保留）、合规性声明 — 这些可用 declarative。

**第二次违反 → 升级**：按 feedback_rule_vs_hook 规则，第二次发生（Claude 仍写 declarative bear thesis 或精确未验证数字）→ 评估升级为 PreToolUse Hook（拦截 Write/Edit 时检测 thesis 散文中的 declarative pattern）。
