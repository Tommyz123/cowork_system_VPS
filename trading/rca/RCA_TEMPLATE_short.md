---
date: YYYY-MM-DD
incident: <一句话事件名>
severity: minor
status: <draft / fixed / monitoring>
---

# Minor RCA — <事件标题>

> Minor 模板：3 分钟填完。**4 个字段必填，不许糊弄**。

## 1. 表面错误
（一句话——哪里出错了，谁/什么报的）

## 2. 根因（5-why 至少 3 层）
- Why 1: ...
- Why 2: ...
- Why 3: ...
（如果到第 3 层就是结构性问题 → 升级为 Major，换 RCA_TEMPLATE_full.md）

## 3. 修复方式（≥ 2 options + 推荐）
- A. ...（优/缺点 1 行）
- B. ...（优/缺点 1 行）
- ⭐ 推荐：<A 或 B>，因为 <1 句话理由>

## 4. 防止复发（不许写"以后小心"）
- 具体行动：...
- 触发条件 / 监控信号：...
- 验证标准：<达成什么就算预防成功>
