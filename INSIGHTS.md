# Insights — 临时缓冲区

> **工作流：** 新经验写这里 → 健康检查触发审核 → 有价值的迁入 `reference/knowledge_base.md` → 清空
> 格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
> 已审核的稳定参考知识在：`reference/knowledge_base.md`

---











[2026-06-07] [cowork系统/能力对照] cowork自建memory vs Claude Code原生memory → 原生(CLAUDE.md静态需手动维护 + Auto Memory只记技术性内容/机器本地/不跨设备共享/超200行或25KB不全加载),不支持模型自主跨对话记任意事实;cowork自建(86条结构化业务+个人+偏好/MEMORY.md索引/三实例symlink共享/分类型)功能更接近Claude API的memory tool(memory_20250818)。结论:记忆是cowork不该让位给原生的部分,反而是护城河。来源:claude-code-guide查官文docs.claude.com/memory(2026-06-07)。[ref-worthy]
[2026-06-10] [cowork系统/记忆架构] memory双目录漂移根治 → 根因:自建规矩写cowork/memory、CC原生机制写$HOME/.claude/projects/<cwd>/memory,两套各写各的;且"三实例symlink共享"实际只链了BB漏了CC(CC裸跑无记忆注入)。修法:双向合并后三实例projects/memory全做symlink→cowork/memory(git正本),原生+自建落同一份物理文件。教训:跨实例"都已配置"的断言必须逐实例ls -ld实测。备份/tmp/memory_backup_20260610.tar.gz+old_memory_AA_20260610(重启即清)。[ref-worthy]
[2026-06-19] [系统/监测架构] 软告警hook对幻觉模型无效→关键监测必须会话外 → AA幻觉卡死事故证明:挂在会话内的监测(context_watch挂PostToolUse/reply_check软告警)在会话本身烂掉时全体失效("让卡死的实例自救=死循环")。关键监测必须放会话外独立进程(systemd/cron),不受工具失效/幻觉影响。已落地instance_watchdog.sh。[src:2107f99d] [ref-worthy]
[2026-06-19] [诊断/三实例] 别的实例署名出现在我频道≠串台,先用API author字段证伪 → 查 GET /channels/<chan>/messages/<id> 的author.id:是主公(811758070534766613)=主公转述给我看;是bot id=才真串台。辅证跨频道fetch报403=物理隔离正常。别看到名字就推理串台(我两度栽此坑)。[src:2107f99d]
[2026-07-01] [三实例诊断] Claude回复里工具调用格式偶发故障 → 表现为回合提前结束/看起来"卡住"，实际是assistant文本里出现裸文本形式的伪XML(如"card\n<invoke name=\"Bash\">...")而非真正被harness解析的tool_use block，导致该次工具调用没有真正执行就结束回合；排查法：读该实例最新jsonl的assistant消息，检查content是纯text还是有独立tool_use block，text里出现<invoke>字样即中招 [ref-worthy]
