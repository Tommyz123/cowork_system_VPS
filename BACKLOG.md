# Cowork 系统待办想法

> 记录有价值但暂时不做的**系统/项目改进想法**，等时机成熟再实现
> 格式：[日期] 想法 | 触发条件（何时值得做）
>
> **和 idea/ 的区别：**
> - `BACKLOG.md` = 短条目，系统优化类想法，一行一条
> - `idea/` = 详细计划文档（求职、方案、模板等），单独成文件

---

## 🔜 下次对话做

[2026-04-24] **整理 project_*.md 记忆文件** | 触发条件：下次P2整理时
- 8个 project_*.md 存了项目内容（配置/流程/决策），放错地方
- 正确做法：把独特内容补进对应 playbook，然后删掉 project_*.md（或清空只留路由指针）
- 文件清单：project_ai_skill / cannabis_advisor / cowork_roadmap / daily_news_digest / design_principles / insights_system / mac_mini / p9_trading
- 注意：playbook 是"怎么用"，project_*.md 是"是什么+为什么"，迁移前要补全
→ [决定 2026-05-02]：维持现状，边用边整理。一次性清理10个文件ROI低+有丢信息风险，等真正进某项目时顺带对齐 playbook 和 project_*.md 是否一致。
→ [决定 2026-05-07]：策略调整——确认两边有重复内容，应精简 project_*.md 只留背景/哲学/决策，操作内容留 playbook。P9已完成精简(86→51行)，其余7个下次对话第一件事处理。


[讨论于2026-04-16对话] **Discord Webhook 配置** | 触发条件：近期排期，解锁Remote Trigger + 每日新闻迁移
→ [决定 2026-05-02]：暂不做。当前本地cron够用，不是紧急需求，等真正需要Remote Trigger或新闻迁移上云时再配置。
- Discord频道右键→编辑频道→整合→Webhook→新建→复制URL存入cowork系统
- 解锁：①Remote Trigger发Discord通知 ②每日新闻迁移上云（不再依赖本地常开）

---

## ⏳ 等触发条件

[2026-03-23] **自动系统对齐扫描** | 触发条件：项目超过5个，或系统运行稳定后
- 每天定时扫描 cowork_log.md + 各项目状态文件
- 检查各层文件是否说同一件事（context.md / CURRENT_SESSION.md / memory 是否一致）
- 检查有活跃项目但缺 playbook、有授权文件夹但未注册等结构漏洞
- 扫描 friction_log.md 积压数量
- 结果发到 Discord 提醒
- 现在不做原因：系统才3个项目，过度工程化；根本问题是习惯（说收工），不是扫描频率

[2026-04-16] **Stop Hook 自动写 friction_log** | 触发条件：出现重复性"忘清理token"或"漏写日志"问题时
- 方案：Stop Hook 检查 /tmp/task_approved 是否遗留 → 自动写 friction_log
- 实现：~20行 bash，加到 settings.json Stop 区块
- 当时不做原因：task_approved 遗忘率极低，日志提醒已有 UserPromptSubmit 双重覆盖，ROI 不够
- 主公决策：先记录，有真实重复性问题再实现

[讨论于2026-04-16对话] **mini LLM 文档对齐扫描** | 触发条件：收工规则改了但文档遗漏问题仍频繁出现（>2次/周）
- 背景：主公反映文档经常有遗漏（ARCHITECTURE.md Hook系统缺失是当次案例）；先用收工规则触发映射解决；如果还不够再升级
- 方案：GPT-4o-mini每周定时扫描 CLAUDE.md + ARCHITECTURE.md + context.md + playbooks/，输出不一致清单发Discord
- 需要：OpenAI API key（主公已有）；开发约半天
- 现在不做原因：收工规则加了具体触发映射（改Hook→更新ARCHITECTURE.md等），先观察是否够用
- 主公决策：先改收工规则，问题持续再做mini LLM方案

[讨论于2026-04-16对话] **CLAUDE.md 拆分为 @import 结构** | 触发条件：CLAUDE.md 超过 180 行
→ [决定 2026-05-02]：不做。@import只是重组文件，不减少token负担，也不降低规则数量。真正的复杂度降级靠删除冗余规则（已于2026-05-02完成，161行→145行）。

[讨论于2026-04-19] **第三方项目安全沙箱（Docker + 监控）** | 触发条件：使用第三方GitHub项目时
- Docker 隔离：文件系统隔离，不挂载敏感目录，防止读取主机数据
- 网络监控：记录容器所有出站请求，陌生域名发 Discord/Email 告警（~20行 Python）
- 文件监控：inotifywait 监控指定目录，有异常读取发告警
- 能防住 ~80% 常见威胁（偷文件/偷数据/持久化后门）
- 典型场景：career-ops 等开源求职/自动化工具
- 开发难度：半天，比量化系统简单

### [公开前] 安全与可移植性闭环（Codex审核发现，2026-04-17）
- 触发：准备公开repo或多人使用时
- 内容：
  1. git untrack cowork_log.md / flightscripts/flight_prices.db（`git rm --cached`）
  2. 更新flightscripts/README.md：SerpAPI key描述改为"从环境变量读取"
  3. 补 requirements.txt / .env.example
  4. 去掉cron里每次pip install
  5. 路径硬编码（/mnt/c/Users/zhi89/...）配置化
  6. flight_monitor.py失败原因日志细化
- 现状：私人仓库，暂不处理；到时候搜索 SERPAPI_KEY/hardcoded/mnt/c/Users/zhi89 快速定位

## 治理壳（加壳方向①②，2026-04-21讨论，③已完成）
- [2026-04-21] **① 环境变量统一（env层）** | 触发条件：迁移Mac mini前，或有脚本路径问题时
  - 新建 `config/system.env`，存WSL路径/时区/Discord频道等系统级变量
  - 各脚本 `source` 此文件，改路径只改一处
  - 现在不做原因：系统运行正常，改动有引入bug风险；Mac mini时一次性做更合理
- [2026-04-21] **② 路径标准化（路径层）** | 触发条件：迁移Mac mini前
  - `COWORK_ROOT=/mnt/c/Users/zhi89/Desktop/cowork` 统一变量，所有路径用变量拼接
  - 迁移时只改一行
  - 现在不做原因：和①同步做，等Mac mini到手

## 🧠 Personal AI 助理（2026-04-25 讨论）

> 背景：主公下载了 gbrain（YC总裁Garry Tan自用的agent记忆系统）和 llm_wiki（Karpathy模式文档wiki），研究后决定把这套思路融入 cowork，把 cowork 升级成真正的个人AI助理。

**[2026-04-25] P10 个人文件库 MVP** | 触发条件：主公说"开始做P10"
- 目标：把个人文件（简历/租约/税表等）内容索引化，实现"发我简历"类自然语言查询
- 为什么现在值得做：P8求职进行中，简历/求职信立即有实际使用价值
- 范围：MVP只做 `资料/个人文档/简历/` 下的文件（AI_agent_Resume.docx / Tommy_Zou_AI_Resume.docx / coverletter.docx），验收标准是说"发我简历"能拿到文件
- 技术方案：python-docx 提取文本 → 存入 cowork.db 新表 `personal_files`（含内容+路径+分类）→ 检索时关键词+向量双路
- 放在 cowork/personal/ 子文件夹，CURRENT_SESSION.md 加 P10 块管理
- 决策原因：属于 cowork 系统升级，不是独立创业项目，共用同一套框架

**[2026-04-26] P2 cowork搜索数据质量清理** | 触发条件：搜索噪音影响日常使用时，或主公有空
- 现状：message_embeddings 9700条，重复率70%（distinct内容只2902条）；boilerplate噪音："正在退出"x11/"No response requested"x38/"配额限制"x18等漏过过滤
- 方案（简化版）：① 频率统计SQL找boilerplate（出现≥5次且长度<100字）→ 人工确认后DELETE；② SQL去重保留最早一条；③ embed_messages.py加应用层内容去重（写入前查已有则跳过）
- 预期效果：9700条→2000-3000条有效内容，搜索信噪比从50→85+分
- 参考：2026-04-26讨论（Codex建议完整版加content_hash，简化版应用层判重效果等同，单进程场景够用）
- 不急原因：搜索目前够用，等噪音真正影响体验时再做

**[2026-04-25] P2 cowork搜索升级 A+D** | 触发条件：session 数量 > 60 条，或主公有空
- A（查询意图分类）：20-30行Python，搜索前判断时间/实体/语义类型再路由；独立可随时加
- D（两步CoT结构化摄入）：改收工Skill，收工时额外生成知识摘要（决策/新知识点），单独存储和embed
- 现在不做原因：25个session感知不明显；D的价值是复利型，越晚开始损失越多（酌情考虑早做D）

**[2026-04-25] 知识图谱 B+C（等规模）** | 触发条件：session > 100 条
- B（实体关系自动织网）：embed时提取实体引用，建entity_links表，零LLM调用
- C（backlink引用频次加权）：被多个session引用的内容排名加分，依赖B完成
- 现在不做原因：25 session数据量不够，图稀疏，backlink无法产生有意义密度
- 来源参考：gbrain `src/core/link-extraction.ts` / `src/core/search/`

---

## P9 量化交易系统扩展
- [2026-04-20] P9月报/季报/年报 | 触发：跑满4周后加月报，跑满3个月后加季报；代码改weekly_report.py日期范围即可，30分钟内可完成
- [2026-04-24, 代码审查发现] **strategy.yaml 阈值未被读取** | 背景：evaluate_rules()里阈值全部硬编码，改yaml不影响代码行为；触发条件：有50条数据准备第一次调阈值时，届时改成从yaml动态读取 | 决定不急修：数值目前一致，调阈值前改更有意义
- [2026-04-24, 代码审查发现] **买入规则第3条漏洞** | 背景：第3条"SPY跌幅≥-1.5%"几乎永远为真，min_conditions:2实际上等于只需满足RSI<35或MACD多头之一；触发条件：stats_engine出数据后看买入命中率，若偏低则收紧 | 决定不急修：纸账号阶段宽松=积累更多买入案例，等数据说话
