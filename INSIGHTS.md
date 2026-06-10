# Insights — 临时缓冲区

> **工作流：** 新经验写这里 → 健康检查触发审核 → 有价值的迁入 `reference/knowledge_base.md` → 清空
> 格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
> 已审核的稳定参考知识在：`reference/knowledge_base.md`

---











[2026-06-07] [cowork系统/能力对照] cowork自建memory vs Claude Code原生memory → 原生(CLAUDE.md静态需手动维护 + Auto Memory只记技术性内容/机器本地/不跨设备共享/超200行或25KB不全加载),不支持模型自主跨对话记任意事实;cowork自建(86条结构化业务+个人+偏好/MEMORY.md索引/三实例symlink共享/分类型)功能更接近Claude API的memory tool(memory_20250818)。结论:记忆是cowork不该让位给原生的部分,反而是护城河。来源:claude-code-guide查官文docs.claude.com/memory(2026-06-07)。[ref-worthy]
[2026-06-10] [cowork系统/记忆架构] memory双目录漂移根治 → 根因:自建规矩写cowork/memory、CC原生机制写$HOME/.claude/projects/<cwd>/memory,两套各写各的;且"三实例symlink共享"实际只链了BB漏了CC(CC裸跑无记忆注入)。修法:双向合并后三实例projects/memory全做symlink→cowork/memory(git正本),原生+自建落同一份物理文件。教训:跨实例"都已配置"的断言必须逐实例ls -ld实测。备份/tmp/memory_backup_20260610.tar.gz+old_memory_AA_20260610(重启即清)。[ref-worthy]
