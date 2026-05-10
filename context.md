# Context — Tom 电脑全局文件索引

> 最后更新：2026-05-07（AI量化交易系统行改为TIDE描述）
> 维护方式：由 Cowork AI 自动更新，每次文件变动后同步修改

> ⚠️ **给 Cowork AI 的指引：**
> - 读取此文件后即可了解 Tom 电脑全局状态，无需再扫描文件夹
> - 每次授权新文件夹后，必须扫描并更新本文件对应区块
> - 此文件需要桌面授权才能修改：`request_cowork_directory("~/Desktop")`
> - `cowork/friction_log.md` = 系统摩擦日志，记录规则问题和优化建议，说"系统复盘"时读取

---

## 电脑基本信息

- 用户名：zhi89
- 系统：Windows
- 桌面路径：`C:\Users\zhi89\Desktop`
- 主要工作区：桌面

---

## 📁 文件夹索引

### 🗂️ Desktop/资料  ← 主文件库
- **标签：** #文件库 #全局归档 #语义索引
- **用途：** Tom 电脑所有文件的统一归档库，含专属索引和整理规则
- **状态：** 持续更新
- **规则文件：** `资料/RULES.md`（含收件箱工作流、重命名规则、整理规范）
- **索引文件：** `资料/INDEX.md`（详细语义索引，找文件时优先读这里）

- **主要文件夹：**

  | 文件夹 | 用途 |
  |--------|------|
  | `cannabis/` | 大麻零售创业全套（商业计划/法规/数据/合同） |
  | `药房计划/` | 药房运营规划与 SOP |
  | `c_project/` | AI 技术开发与学习（含 cc_skill、多智能体、各类项目） |
  | `数据分析/` | 数据科学项目集（Python/Jupyter） |
  | `app/` | 应用程序开发 |
  | `JCcrab文件/` | 螃蟹餐厅历史档案 |
  | `Hair Ave/` | 理发店投资周报 |
  | `出租lease/` | 出租房产管理（162-22、法拉盛） |
  | `个人文档/` | 简历、证件、账号 |
  | `个人财务税务/` | 税表与财务记录 |
  | `证书/` | 学习证书收藏 |
  | `老人公寓/` | 父亲养老申请材料 |
  | `牙科/` | 父亲牙科纠纷文书 |
  | `_待整理/` | 新文件收件箱 |

---

### 🗂️ Desktop/legal_library
- **标签：** #法律 #大麻法规 #知识库 #本地检索
- **用途：** 大麻法律助手知识库，供 Claude Code 本地检索问答
- **状态：** ✅ 建立完成（2026-03-23）
- **规则文件：** `legal_library/RULE.md`（检索流程、文件读取策略）
- **索引文件：** `legal_library/INDEX.md`（19个单主题索引 + 12条高频复合问题路径）

---

### 🗂️ Desktop/cc_skill
- **标签：** #AI框架 #Claude Code #Skill #多智能体 #评估框架 #context框架
- **用途：** 自主开发的 Claude Code AI 控制框架集合（从 资料/c_project/ 移出独立管理）
- **状态：** 🔄 持续更新

- **关键内容：**

  | 文件夹 | 用途 |
  |--------|------|
  | `skill/skills_v5/` | V5 技能包，7个技能，最新版本 |
  | `context/V6/` | Context 控制框架**最新版**（含进度管理/收工流程/5步验证） |
  | `context/V5/` | Context 控制框架 V5（含TODOLIST规则，较轻量） |
  | `mutl-agent-poco/` | 多智能体协作框架 |
  | `inspect_eval_framework/` | 技能评估框架 |
  | `llm_eval_framework/` | LLM 评估框架 |
  | `claude_code/` | Claude Code 工具与配置 |

---

### 🗂️ Desktop/marketing
- **标签：** #大麻项目 #纽约 #weedmaps #SQLite数据库 #爬虫 #AI顾问
- **用途：** 纽约大麻 AI 顾问项目，构建全州大麻产品数据库
- **状态：** ⏸️ 暂停中（2026-04-06）
- **规则文件：** `CLAUDE.md`（含操作规范，任务执行前必须读取）

- **关键文件：**

  | 文件/文件夹 | 标签 | 用途 |
  |------------|------|------|
  | `CLAUDE.md` | #项目规则 #操作规范 | 项目规则，Claude Code 启动必读 |
  | `PROJECT_INDEX.md` | #项目索引 #数据状态 | 项目结构和数据状态总览 |
  | `session_progress.txt` | #当前进度 #数据库状态 #待做事项 | **最新进度文件，必读** |
  | `weedmaps-listings-scraper/` | #爬虫代码 #Python #SQLite | 爬虫主代码目录 |
  | `weedmaps-listings-scraper/dumps/market.db` | #数据库 #SQLite | **主数据库文件** |
  | `archived/` | #归档 #旧数据 | 旧版数据和草稿归档 |

- **技术栈：** Python + SQLite + curl_cffi + pdfplumber
- **数据库详情：** 见 `marketing/PROJECT_INDEX.md`（数据量/完成率等细节在那里维护）

---

### 🗂️ Desktop/cowork/scraper
- **标签：** #爬虫 #Dutchie #大麻零售 #产品数据
- **用途：** Dutchie POS 平台菜单爬取原型代码，Playwright 响应拦截方案已验证
- **状态：** ⏸️ 暂停（逻辑验证完成，未正式建项目）
- **对应playbook：** `cowork/playbooks/dutchie_scraper.md`

  | 文件 | 用途 |
  |------|------|
  | `sage_seeds_probe.py` | Playwright 抓取主代码（验证通过，388个唯一产品） |
  | `captured_requests.json` | 抓取到的原始请求数据 |

---

### 🗂️ Desktop/cowork/research
- **标签：** #研究笔记 #技术探索 #系统分析
- **用途：** 技术研究笔记、系统架构分析、工具探索记录，供 AI 下次对话直接复用
- **状态：** 持续更新

  | 文件 | 用途 |
  |------|------|
  | `cc_source_insights.md` | Claude Code 源码架构研究（Hook/权限/多智能体/压缩等8模块+实施建议） |

---

### 🗂️ Desktop/cowork/scripts
- **标签：** #自动化 #SQLite #对话搜索 #收工系统
- **用途：** cowork.db 对话搜索系统的 Python 脚本集
- **状态：** ✅ 上线（2026-04-17）

  | 文件 | 用途 |
  |------|------|
  | `setup_db.py` | 初始化 cowork.db（建表），安全重跑 |
  | `index_conversations.py` | 解析 JSONL 对话历史 → FTS5索引（支持 --rebuild）|
  | `search_conversations.py` | CLI搜索：`python search_conversations.py "关键词" [--project P3] [--date 2026-04]` |
  | `log_session.py` | 收工时写入 sessions 表 + 触发增量索引 |

- **数据库：** `cowork/cowork.db`（已索引101个历史session，2710条消息）
- **数据库分层原则：** cowork.db=对话历史 / personal.db=个人文件 / trading.db=交易 / market.db=大麻市场；不同数据类型分库，避免职责模糊

---

### 🗂️ Desktop/cowork/flightscripts
- **标签：** #自动化 #机票 #Discord #定时任务 #SerpAPI
- **用途：** 机票价格监控 Agent，每日查 NYC→港/穗/深航线价格，AI分析走势，Discord推送日报
- **状态：** ✅ 运行中（本地 cron，每天 13:30 EDT）

  | 文件 | 用途 |
  |------|------|
  | `run_flight.sh` | 主入口：查价→claude分析→发Discord |
  | `flight_monitor.py` | 查SerpAPI+存SQLite+输出JSON |
  | `flight_prices.db` | 历史价格数据库（SQLite） |

- **监控路线：** JFK/EWR→HKG/CAN/SZX（商务转机）+ JFK→HKG/CAN（经济直飞）
- **数据来源：** SerpAPI Google Flights

---

### 🗂️ Desktop/cowork/newscripts
- **标签：** #自动化 #新闻 #Discord #定时任务
- **用途：** 每日精华日报脚本，自动抓取 RSS + 通过 Discord DM 推送
- **状态：** ✅ 运行中（本地 cron，每天 13:00 EDT），GitHub Action 已删除（2026-04-01）
- **Git repo：** github.com/Tommyz123/cowork-scripts

  | 文件 | 用途 |
  |------|------|
  | `run_daily_news.sh` | 主入口：抓 RSS → claude 生成摘要 → 发 Discord |
  | `daily_news.py` | 抓取 RSS 新闻（政治/股市/虚拟币/AI/大麻NY），含 published 时间 |
  | `send_discord_dm.py` | 发送消息到 Discord channel 1485128242808619079 |
  | `news_agent_instructions.md` | Agent 完整操作指令（格式/来源/过滤逻辑） |

---

## 🛠️ 工作规则（适用于 Cowork AI）

1. **执行前确认**：任何操作必须先重复理解，等主公确认后才执行
2. **读取此文件**：新对话开始时，如需了解文件位置，直接读取本文件
3. **自动维护**：每次文件新增/修改/项目状态变化后，自动更新本文件对应条目和"最后更新"时间
4. **授权提醒**：新文件夹需要主公授权后，才能扫描写入
5. **任务守卫机制**（2026-04-15 上线）：非白名单文件改动前，必须先 Discord 报计划，主公确认后执行 `touch /tmp/task_approved`，任务完成后 `rm -f /tmp/task_approved`。白名单文件（cowork_log.md / CURRENT_SESSION.md 等）直接放行，无需 token。Hook 脚本：`~/.claude/system_file_guard.sh`

---

## 🔄 活跃项目状态

> 项目当前进度统一记录在 `CURRENT_SESSION.md`，不在此重复维护。
> 需要了解项目进度时，读取：`Desktop/cowork/CURRENT_SESSION.md`

---

## 📌 快速查找指引

| 我需要... | 去哪找 |
|----------|--------|
| 任意文件/文档 | 先读 `资料/INDEX.md`，语义搜索定位 |
| 大麻项目数据库 | `marketing/weedmaps-listings-scraper/dumps/market.db` |
| 大麻项目当前进度 | `marketing/session_progress.txt` |
| 大麻项目爬虫代码 | `marketing/weedmaps-listings-scraper/` |
| 大麻创业文件 | `资料/cannabis/`（读 INDEX.md 精确定位） |
| 大麻法律问答知识库 | `legal_library/`（读 INDEX.md 检索） |
| 每日新闻脚本 | `cowork/newscripts/`（改配置读 news_agent_instructions.md） |
| 机票监控脚本 | `cowork/flightscripts/`（run_flight.sh 主入口） |
| AI量化交易系统 | `cowork/trading/`（TIDE系统：cognitive_scanner.py 建仓 / signal_collector.py 日报 / bash run_scanner.sh 手动触发） |
| Mac mini价格监控 | `cowork/scripts/mac_monitor.py`（低于$450发Email） |
| AI 控制框架最新版 | `Desktop/cc_skill/context/V6/` |
| Skill 最新版本 | `Desktop/cc_skill/skill/skills_v5/` |
| 多智能体研究 | `Desktop/cc_skill/mutl-agent-poco/` |
| Eval 评估框架 | `Desktop/cc_skill/inspect_eval_framework/` |
| 个人简历 | `资料/个人文档/简历/` |
| 出租房文件 | `资料/出租lease/` |
