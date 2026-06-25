# 待审记忆（Auto Pending）

> 由系统自动捕获，Claude 审核后写入正式 memory/
> 格式：[时间][类型] 内容
> 类型：user / feedback / project / reference

[2026-06-25][reference] 一次性 cron 的"自删逻辑"必须放在脚本最前面（发通知/查API等易崩操作之前），否则那些操作一旦失败（如 Discord 403/API 429）会崩在自删之前→cron 变僵尸，每年/每周到点复活再崩。2026-06-25 系统审核实锤 p9_ora_premarket_reminder.py：自删在第114行、发Discord在前，5/18 发送 403 崩了→自删没执行→cron 赖到 6/25。教训=自删/清理类收尾动作前置，不依赖"主流程跑完"。（候选写入 reference/knowledge_base.md「脚本/自动化」区）
