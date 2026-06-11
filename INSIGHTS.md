# Insights — 临时缓冲区

> **工作流：** 新经验写这里 → 健康检查触发审核 → 有价值的迁入 `reference/knowledge_base.md` → 清空
> 格式：`[YYYY-MM-DD] [项目/领域] 标题 → 内容（一两行，说清楚怎么用）`
> 已审核的稳定参考知识在：`reference/knowledge_base.md`

---











[2026-06-07] [cowork系统/能力对照] cowork自建memory vs Claude Code原生memory → 原生(CLAUDE.md静态需手动维护 + Auto Memory只记技术性内容/机器本地/不跨设备共享/超200行或25KB不全加载),不支持模型自主跨对话记任意事实;cowork自建(86条结构化业务+个人+偏好/MEMORY.md索引/三实例symlink共享/分类型)功能更接近Claude API的memory tool(memory_20250818)。结论:记忆是cowork不该让位给原生的部分,反而是护城河。来源:claude-code-guide查官文docs.claude.com/memory(2026-06-07)。[ref-worthy]
[2026-06-10] [cowork系统/记忆架构] memory双目录漂移根治 → 根因:自建规矩写cowork/memory、CC原生机制写$HOME/.claude/projects/<cwd>/memory,两套各写各的;且"三实例symlink共享"实际只链了BB漏了CC(CC裸跑无记忆注入)。修法:双向合并后三实例projects/memory全做symlink→cowork/memory(git正本),原生+自建落同一份物理文件。教训:跨实例"都已配置"的断言必须逐实例ls -ld实测。备份/tmp/memory_backup_20260610.tar.gz+old_memory_AA_20260610(重启即清)。[ref-worthy]
[2026-06-10] [P9/Alpaca] OPG订单"expired"状态可能含部分成交 → Alpaca OPG单开盘竞价只成交一部分时，订单终态仍是expired但filled_qty>0、持仓真实存在；对账逻辑只看order.status会漏掉真实持仓（GNTX 97/132、WTS 9/10实例）。任何订单级对账必须同时检查filled_qty；更稳的是持仓级对账：定期比对Alpaca /positions vs DB持仓清单。 [ref-worthy]
[2026-06-10] [P9/趋势主线/方法论] 检查清单类系统必须用hard negative测特异性 → 验证打分清单不能只用"明显赢家+明显泡沫"（考题太简单必然全对），必须找"信号全亮但结局崩盘"的硬对照组实测拦截率（趋势手册v1.0实锤：ZIM/Zoom/Moderna摊牌信号全亮、清单0/3拦截、事后-75~90%）；同理回测打分只能用"决策日当天可知信息"，禁止后见数据。适用：任何评分/筛选/清单系统（P9评分、趋势清单、未来agent评审）。另：自产方法论文档发布前派独立agent对抗审核，作者自审有立场盲区。[ref-worthy]
