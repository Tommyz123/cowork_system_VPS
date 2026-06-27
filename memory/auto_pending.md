# 待审记忆（Auto Pending）

> 由系统自动捕获，Claude 审核后写入正式 memory/
> 格式：[时间][类型] 内容
> 类型：user / feedback / project / reference

[2026-06-25][reference] 一次性 cron 的"自删逻辑"必须放在脚本最前面（发通知/查API等易崩操作之前），否则那些操作一旦失败（如 Discord 403/API 429）会崩在自删之前→cron 变僵尸，每年/每周到点复活再崩。2026-06-25 系统审核实锤 p9_ora_premarket_reminder.py：自删在第114行、发Discord在前，5/18 发送 403 崩了→自删没执行→cron 赖到 6/25。教训=自删/清理类收尾动作前置，不依赖"主流程跑完"。（候选写入 reference/knowledge_base.md「脚本/自动化」区）

[2026-06-26][reference] DO VPS root 救援通道 + cowork 用户已获 sudo（2026-06-26 根治）。① cowork 用户日常无 sudo 且密码曾锁定→改 /etc/systemd 等系统级操作以前只能搬 root。② root 救援走法：DO 网页 cloud.digitalocean.com → Droplets → 点服务器名进详情 → 右上角 Console 按钮开网页终端；忘 root 密码用详情页左侧 Access → Reset Root Password，临时密码发邮箱(zhitao776@gmail.com)，首登强制改密(Current password 先输临时密码再设新)。③ 2026-06-26 已根治:usermod -aG sudo cowork + passwd cowork 解锁设新密码,sudo whoami 验证返回 root。以后系统级操作 cowork 直接 sudo 输密码,不必再走 DO 重置 root。注意:三 Claude 实例进程是加组前启动的,需实例重启才刷新带 sudo 组;且 sudo 仍要 cowork 密码,实例无法无人值守 sudo。关联 [[reference_dual_bot]]。（候选写入 reference_dual_bot.md 或 knowledge_base.md「VPS运维」）
