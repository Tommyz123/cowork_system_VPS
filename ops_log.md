# Ops Log — 统一运营日志

> 记录所有自动任务（cron）和 Skill 执行情况，供追溯查询
> 格式：`[YYYY-MM-DD HH:MM EDT] 类型[项目] | 名称 | ✅/❌ | 摘要`
> 查询示例：
>   grep "P9" ops_log.md | tail -20           # P9 最近执行
>   grep "❌" ops_log.md | tail -20            # 最近失败记录
>   grep "SKILL" ops_log.md | tail -30         # 最近 Skill 执行
>   grep "2026-05-11" ops_log.md               # 某天所有记录
> 归档：满 300 行时移至 archive/ops_log_YYYY.md

---

[2026-05-11 20:30 EDT] CRON[P9] | price_guard | ✅ | 完成
[2026-05-11 21:00 EDT] CRON[P9] | price_snapshot | ✅ | 完成
[2026-05-11 21:14] SKILL[SYS] | 保存进度 | ✅ | P2 系统整理进度已保存
[2026-05-11 23:32 EDT] SKILL[SYS] | 收工 | ✅ | 项目:P2 commit:2afd267 草稿:1条(文档对齐1处+MEMORY清理2条)
[2026-05-12 02:03 EDT] CRON[SYS] | rclone_backup | ✅ | Total size: 102.594 MiB (107577962 Byte) → Google Drive
[2026-05-12 12:38 EDT] SKILL[SYS] | 收工 | ✅ | 项目:P2 commit:a9c3bdd 草稿:4条INSIGHTS+2条friction补记+主公真实世界产出建议; 顺手修复index_conversations.py JSONL_DIR bug
