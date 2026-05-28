# 进度管理

> 读取指令：说"读取进度"显示活跃列表；说"保存进度"更新对应存档；说"进度X完成"移至归档

---

## 元数据

last_memory_sync: 2026-05-26
last_audit_date: 2026-04-19

---

## 📊 项目仪表盘（快速扫描）

### 🔄 需人工干预（计入活跃项目数）
| ID | 项目 | 状态 | 最后更新 | 下一步摘要 |
|---|---|---|---|---|
| **P12** | **Cannabis Retail 主线** | 🆕 **规划中** | **2026-05-25** | **选址研究框架确立（4维：收入水平+地铁节点+竞争+商业条件）；Queens市场已基本饱和；Sweet spot房租$8k-$12k；主公背景：Bayside Cannabis+Sage Seeds；下次：给地址继续分析或AI法律顾问MVP** |
| P2 | Cowork系统优化 | 🔄 迭代中 | 2026-05-26 | AI动态日报上线(09:00 EDT cron)；双bot×2扩展计划启动（待主公提供Discord token）；收工Skill打分机制持续 |
| P13 | 金字塔原理学习 | 🆕 第1章已通过 | 2026-05-26 | cowork架构学+测+实战；第1章已通过+2简历项目改写；第2章未开始；架构升级4触发条件已写入memory |
| P10 | 个人文件库 | 🔄 活跃 | 2026-04-25 | MVP完成(简历3文件)，阶段2扩展分类 |
| P3 | Cannabis Budtender | ⏸️ 暂停（并入 P12 子模块） | 2026-05-07 | eval 100%完成；从 2026-05-14 起作为 P12 子模块继续推进 |
| P8 | 求职 (career-ops) | 🔄 策略大重定向 | 2026-05-24 | 跳板策略+甜区岗位（Solutions/Customer/Implementation/Founding/Applied AI Eng）；30+ 家清单已列；待主公 review 后启动 portfolio 搭建 |
| P5 | Legal Library | ⏸️ 暂停（按需更新；December queue 追踪并入 P12） | 2026-05-13 | v4.5 完成；Organic Blooms 案件追踪持续中，每周一 09:00 EDT Discord 提醒 |

### ⚙️ 自动运行（不计入活跃项目数）
| ID | 项目 | 状态 | 最后更新 | 备注 |
|---|---|---|---|---|
| P4 | 每日新闻日报 | ✅ cron运行中 | 2026-05-10 | 5/10补发成功；root权限/tmp/news_ai.txt问题已确认不影响当前脚本 |
| P6 | 机票监控 Agent | ✅ cron运行中 | 2026-05-07 | SerpAPI key自动轮换（KEY2耗尽→自动切KEY）；直飞数据恢复 |
| P7 | Mac mini价格监控 | ✅ cron运行中 | 2026-04-23 | HTML邮件（链接藏入<a>标签）；今日eBay $305触发提醒 |
| P9 | AI量化交易系统 TIDE | ✅ cron运行中 | 2026-05-28 | VRRM止损出场(-73.23%，Avis合同终止)，DB已记录；下次：6/14首批30天outcome节点+6月底数据看hit rate |

---

## 活跃进度

### [P12] Cannabis Retail 主线 ⭐ 2026 年主线
状态：🆕 规划中（牌照申请中 + V0 阶段 AI 系统准备中 + 选址研究框架启动 + A → SaaS 长期路线图入库）
last_updated: 2026-05-27
停在：A → AI 全能员工 SaaS 长期路线图已写进 playbook BACKLOG 段（4 阶段触发条件+B/D 备胎），跨实例通讯定为 enabler（MVP 评估 1 天可跑通但暂不建，等触发）。下次：主公丢地址逐个分析 / 或 AI 法律顾问 prompt MVP。

本次完成（2026-05-27 凌晨 opus2 上线 + A 路线图入库）：
- **opus2 systemd 化**：3 实例（cowork/opus_CC/opus2）全部 systemd 自启；reboot 不需手动管；详见日志 2026-05-27 01:05 EDT 条目
- **跨实例通讯 vision 深度讨论**：4 玩法（专家委员会/反方辩论/永续研究 agent/群体智能投票）+ 3 赚钱路径（A 大麻店 SaaS / B 法律订阅 / C 求职作品）
- **A 长期路线图入库**：playbooks/cannabis_retail.md 新增 "🎯 长期路线图：A → AI 全能员工 SaaS（2026-05-27 草拟）" 章节；4 阶段触发条件（触发 0=牌照下来搭跨实例底座 / 触发 1=店开张验证 / 触发 2=至少 1 家试点 / 触发 3=订阅 ≥10 家）；B/D 备胎路径；3 件现在明确不做
- **跨实例通讯实现成本评估**：MVP 1 晚就能跑通（基础设施 90% 已有：3 bot/access.json/Discord 总线），死循环防护必做；production 2-3 天；现在不建（YAGNI + 没真痛点）
- **新 memory：feedback_immediate_vs_longterm_framing**：3 选 1 / 优先级建议前必须先问"立即推动 vs 长期方向"；今晚我第一次猜 B 错就因为没问框架（主公确认）
- **校准点**：模型变强不会让 A 过时；真正护城河 = 持牌店+实操数据+NY 大麻人脉；不是"我会建 multi-agent"

下一步：
- **跨实例通讯 BACKLOG 状态：🟡 缓做**（触发条件 = 牌照下来开始搭店里 AI 系统时启动，或某个具体 subagent 解决不了的协作场景出现）
- P12 原下一步保持：主公给地址逐个分析 / AI 法律顾问 prompt MVP / Reality Check 0/4 仍待启动（剩 12 天）

本次完成（2026-05-24 选址研究 + P&L 框架）：
- **选址分析格式确立**：主公给地址 → 逐个 4 维分析（1000ft 禁区/竞争密度/客流类型/租金范围）+ 优点+风险总结
- **Queens 市场饱和地图**（WebSearch 实测）：Forest Hills（The Flowery）/ Jamaica（Silk Road）/ Ozone Park（3-4家）/ Kew Gardens（A&P Dispensary）→ 大部分中高收入区已有覆盖
- **首个地址分析**：248-15 Union Tpke, Bellerose NY 11426 = 主公工作的 Sage Seeds → 已占用，无法开
- **280E 税务分析**（关键知识）：
  - 联邦 280E：大麻企业不可抵扣正常营业开支，等效税基 = 毛利润（非 EBITDA）
  - NY State 例外：NY 从 2023 年 1 月 1 日起与联邦 280E 脱钩，**州税可正常抵扣**
  - C-Corp 税率 21% 更适合高 280E 税负场景（LLC passthrough 收入会直接推高个人税率）
- **P&L 模型**（多场景）：
  - 月营收 $100K，毛利率 ~42%，毛利 $42K
  - NY 消费税 13%（9%州+4%本地），含税价计算前置
  - Sweet spot：$8K-$12K 房租 → Break-even 营收 ~$130K-$160K/月
  - $30K 房租（如法拉盛 Main St）→ Break-even ~$200K/月，风险极高
- **主公背景整合进选址框架**：
  - 前在 Bayside Cannabis（Bell Blvd, LIRR 站旁）：开门时 Queens 不到 5 家 → 日均 $1-2 万，很快起来
  - 当前在 Sage Seeds（Bellerose）：一手感受日常运营
  - 关键洞察：成功 = 开门早（竞争少）+ 地铁节点 + 附近居民收入不错，不是人流密度
- **法拉盛 Main St 案例分析**：房租 $30-50K + 竞争加剧 + 停车差 + 大客户不会在那买 → 不适合作首店
- **选址优先级公式确立**：居民收入水平 > 地铁节点 > 无竞争（1km 内）> 停车（nice-to-have）

下一步（2026-05-25 起）：
- 主公给更多地址 → 逐个分析（格式已确立）
- AI 法律顾问 prompt MVP（30min，Reality Check 最低门槛）
- **Queens 选址数据分析（待启动）**：OCM 持牌店地址 + Census 人口数据 → 竞争地图 + 空白街区识别 → 候选地址 shortlist；确认 OCM zoning 要求后开始；Placer.ai / Headset 等确定候选地址后再考虑
- **选址工具栈已确认**：OCM（免费）→ Census（免费）→ Placer.ai（付费验证足迹）→ Headset（付费进货决策）；竞品分析：Google Reviews + Weedmaps 评分读差评找缺口

本次完成（2026-05-16 至 2026-05-17 ~10 小时引流主线深挖）：
- **Reddit 数据生态完整探索**：
  - VPS DC IP 被 Reddit 整体 ban（实测：reddit.com 首页/JSON/RSS/search 全 403）
  - **Pullpush.io 验证可用**（Pushshift 开源 mirror，免费，VPS 能访问）
  - 限制：数据滞后 1-4 年，score/comments 一律返回 1
  - 适用：历史分析（答题题库/竞品口碑/痛点/品牌评价）；不适用：实时监控（必须 Mac mini）
  - 记录到 reference/knowledge_base.md（外部集成章节，[ref-worthy] 标记）
- **Reddit 50+ 用法整理**（8 大类入库 playbook）：引流/营销内容/竞品情报/客户研究/法规行业/招聘/供应链选品/AI 进阶/危机管理/选址房产/Reddit 平台用法（AMA / Reddit 广告 / 自建 sub）
- **开业前 3 月引流打法草案**（playbook 入库）：
  - 3 轨道架构（A 火力 EDDM 招牌 / B 阵地 SEO Weedmaps / C 种子 Reddit 博客 YouTube）
  - 月份 -3/-2/-1 任务清单 + 预算 $8-15K + 预期效果（日均 50-80 / 月新客 800-1200 / 复购 30%）
  - 升级版 10 改进点（PR/Hype Building/时机选择 4-20/Email-SMS/A-B 测试 → $20-30K → 100-200 进店）
- **AI 推荐员 = P3 重新关联**：诚信反思推荐"30 分钟 MVP"忽略 P3 已 95% 完成；P3 应从"暂停"升级为"P12 核心引擎"，差距是部署+集成（前端/QR/Click&Collect/kiosk/Terp 数据库/合规过滤层）= 8-15 周开发到 V1
- **1688 礼物方案深挖 4 个方向**：
  - 送（300 套 $1-15 多档对比，挂脖风扇/保温杯/帆布袋/狗屎袋 dispenser/LED 托盘/卫衣）
  - 兑换柜（V1.5 留存机制）
  - **生活方式积分商店**（升级版 / Sephora Beauty Insider 类品牌生态）
  - EDDM 4 选 1 机制（凭卡领礼物入店率 1-2% → 5-8%）
- **Mac mini 战略关联**：解锁住宅 IP 监控基础设施 = Reddit 实时 + IG/TikTok/X/Yelp/Google Maps Review 全网 / 5 年 ROI 完胜付费服务
- **P12 完整 62 任务时间线清单**：V0 立刻 14 / 等选址 8 / 等律师 3 / 等资金 2 / V1 开业前 3 月 11 / 开业当月 5 / 开业 1-3 月 5 / 站稳 3 / V1.5 4 / V2 4 / V3 3 / 长期 3
- **10 大缺失环节审计**（"AI 创业者视角 vs 实体店老板视角"盲区识别）：
  - 实体运营/地方牌照（OCM 之外）/团队 HR/供应链执行/POS 硬件/财务执行/CRM 数据/安全防盗/客户体验执行/危机管理
  - 都是 V0 几乎全空白（10%-30% 完成度）
- **新增任务 #26-#28**：Reddit 爬虫 Pullpush 验证 / Reddit 实时监控 Mac mini / 开业前 3 月打法待深聊
- **playbook 扩充**：cannabis_retail.md 从 1045 行 → 1300+ 行（+ Reddit 50+ 章节 + 开业前 3 月打法章节）
- **诚信反思**：编造 sub 名（r/NYCNugz r/EnoughtreesNYC 不存在）/ "30 分钟 MVP" 忽略 P3 现状 / 反复"诚实指出方向偏移"过度 lecture

下一步（Reality Check 仍 0/4）：
🚨 **30 天 Reality Check（不依赖牌照）**：
1. **AI 法律顾问 prompt MVP**（30 分钟 0 成本 / 最低门槛 / 主公最该现在做的）
2. NY cannabis attorney 30 分钟咨询（$150-300）
3. 接触 1 个 NY 持牌店谈 AI 试用合作
4. 跟 1 个潜在投资人候选喝咖啡

📍 **选址研究（下次优先做）**（2026-05-25 讨论确认）：
主公给具体地址，逐个分析：
- 1000 ft 内有没有学校/教堂（OCM 禁区）
- 附近已有几家持牌店（竞争密度）
- 客流量类型（住宅区/商业区/旅游区）
- 该区域租金大概范围
- 优点 + 风险 总结
→ 下次直接丢地址过来就开始

📋 **C 轨道时间杠杆（越早越值钱，不依赖选址）**：
- Reddit 100 天潜伏 Day 1 启动（注册账号 → 每天 30 分钟潜伏）
- 自产博客 + YouTube 启动
- subagent 跑数据底座（Pullpush 抓 NY 大麻历史 / 头部店案例库 / 关键词地图）

⚠️ **主公自我认知**："缺实战 + 等真实拿到才动手"
- 80% 对（实体运营确实要等牌照）
- 20% 错（Reality Check 4 件套 100% 不依赖牌照，反而等下来做就晚了）

本次完成（2026-05-14 全天 8+ 小时深度对话 6 轮）：
- **第 4-6 轮 playbook 深度扩充**（235→1045 行，4 倍膨胀）
- **架构升级**：Cowork = AI 操作系统总调度 + 子 Agent 多入口（客户/员工/管理/法律）+ 三层 IP 边界
- **核心 IP**：Terp-based feature engineering（chemoinformatics × ML）+ 6 维度推荐（口味+感觉+价格+形式+时段+耐受度）
- **完整 AI 闭环 10 层架构** + 5 个缺口填法（店内体验/下单方式/客户分层/人在 loop/模型迭代）
- **SaaS 路径 V0/V1/V1.5/V2/V3 五阶段** + 数据网络效应核心护城河 + 复制路径辨析
- **GO-TO-MARKET 蓝图（Kush Kosmos v9.0）**：6 章入库（商业哲学/线下战法/督战/积分/供应链/POS 红线）
- **财务模型 + 融资架构**：$200-400K 启动 / 60%-40% 持股 / 双公司独立 / 两阶段融资 + Capital Call / Self-dealing 披露 3 条件 / AI 起草 + 律师 review
- **模块清单**：从 5 个扩展到 7 个（AI 法律顾问 V0 / AI 会计师 V1.5）
- **V0 关键洞察（自嗨防御）**：4 个 reality check 动作都不需要执照 + 已有项目 P1/P3/P5 复用让 V0 时间从 6-12 月压到 3-6 月
- **综合评估**：思路 90 分 / 规划 85 分 / 执行 30 分 → "不是自嗨但有 50% 自嗨倾向"，30 天内启动至少 1 个 reality check 决定走向

本次完成（2026-05-14 凌晨，opus_CC bot 夜间深度对话）：
- **主线决策**：基于八字真盘（丁火日主、辛卯大运 34-43 岁偏财+偏印窗口）+ 行为层观察（跨界整合 / 系统化大脑 / 项目过载短板）综合判断，正式将 Cannabis Retail 定为 2026 年核心主线
- **三层定位**：① 拿 NY 牌照 + 自营一家店 ② 用 AI 把运营 / 顾客 / 营销系统化 ③ 抽离 AI 模块 SaaS 化卖给 NY 100+ dispensary
- **团队结构决策**：主公自任"持牌方 + AI 总设计师"，雇 Assistant Manager 管员工日常（不雇 GM，AI 替代 GM 大部分职能）
- **6 个月硬截止**：必须把主公"亲自做"压到 30% 以下，否则陷入运营吞噬
- **技术栈选型**：Dutchie POS / Flowhub / Treez 当基座（不自建 POS），主公在上面做 AI 增强层（推荐 / 库存 / 营销 / 合规审计）
- **功能模块 1 已规划**：QR + AI 推荐员获客漏斗（EDDM → 卡片 QR → AI 对话 → 个性化推荐 + 独家折扣 → 下单 → 数据沉淀 → 复购）
- **合规红线初稿**：营销 21+ 警示 / FDA 红线 / 顾客数据 HIPAA 类保护 / OCM 持牌方在场 / AI 推荐禁医疗建议
- **SaaS 化 4 阶段路径**：自营→抽离→卖 NY→扩州
- **playbook 建立**：`playbooks/cannabis_retail.md`，11 个 BACKLOG 空白点等讨论

下一步（按优先级）：

🚨 **30 天 Reality Check（自嗨防御）**：以下 4 个动作都**不需要执照**，30 天内至少完成 1 个
1. **写 30 分钟 AI 法律顾问 prompt 代码**（最低门槛，0 成本，0 风险）
2. **联系 1 个 NY cannabis attorney 30 分钟咨询**（$150-300，验证关键假设）
3. **接触 1 个 NY 持牌大麻店谈"AI 试用"合作**（验证客户价值）
4. **跟 1 个潜在投资人候选人喝咖啡聊聊**（验证 pitch + 反应）

📋 **未来深聊的章节**（按优先级）：
- 第 7 章：营销战法（SEO / Weedmaps / Leafly / 社交 / Reddit / 内容生成）
- 第 9 章：风险预案（牌照不下 / 店没生意 / 监管变化）
- 第 10 章：里程碑时间线（V0/V1/V1.5/V2/V3 具体动作清单）
- v9.0 各章细节深挖（第 2 章选址 / 第 3 章 Google review 解耦 / 第 4 章积分细节）
- **playbook 1045 行 → 整理为 800-900 行干净结构化版本**（主公已要求，但 02:14 收工，下次做）

🔧 **V0 启动准备**：
- 派 subagent 跑 Flowhub 技术尽调（对照 v9.0 POS 红线 7-8 条）
- AI 法律顾问 MVP 6-8 周硬卡死开发
- 找 1-2 家持牌店做早期合作伙伴（免费试用 6 月换 feedback）

⚠️ **现有项目处置（未决定）**：
- P8 求职 / P9 交易 / P10 文件库：冻结 / 降 BACKLOG / 保留低耗

关联项目：
- P3 Cannabis Budtender → 并入 P12 作为店内 budtender AI 辅助模块
- P5 Legal Library / Organic Blooms 追踪 → 并入 P12 合规模块
- P1 marketing (Cannabis Advisor) → 并入 P12 AI 增强层

路径：`/home/cowork/cowork/playbooks/cannabis_retail.md`（持续讨论载体）
关联：`/home/cowork/legal_library/18_Organic_Blooms_v_CCB_Tracking.md`

---

### [P2] Cowork 系统优化
状态：持续迭代中
last_updated: 2026-05-28
停在：Opus 4.8 切换（5/28 发布当天升级，2 个 settings.json 改 model ID + 重启 2 个 tmux）；AI 动态日报 v2 升级进行中（6 处改动已完成 1 处 parse_rss）；待新对话继续剩 5 处。

本次完成（2026-05-28 18:30 EDT，Opus 4.8 切换 + AI 动态日报 v2 起步）：
- **AI 动态日报 v2 升级（进行中 1/6）**：主公反馈"公司公告只有标题没介绍"→ 定方案：抓 RSS description + Anthropic 抓页面 og:description + Sonnet 批量生成大白话摘要+意义 + 公告区改卡片样式 + 现有 2 处 Haiku 升 Sonnet；已改 1 处（parse_rss 加 description 字段，ai_news_monitor.py 第 76-94 行）；剩 5 处待 Opus 4.8 新对话继续；/tmp/task_approved 已设
- **Opus 4.8 升级**：5/28 当天 Anthropic 发布；官方文档确认 model ID = claude-opus-4-8（pricing 不变 $5/$25 per MTok，effort 默认 high，1M token 上下文，knowledge cutoff Jan 2026）；改两个 settings.json（opus_home + opus2_home）"model" 字段 → claude-opus-4-8；杀 opus_socket + opus2_socket 两个 tmux 让 runner 自动重启
- **诚实性踩坑 3 次（5/27-5/28）**：①评级编百分比"Top 1%/90%/9%"（5/27 二犯，friction_log 已记） ②推 Hermes/OpenClaw 借鉴方案没先 grep friction（5/28 三犯 feedback_proposal_data_first） ③混淆时间线"cowork 9 个月"（实际 2 个月，主公纠正）— 全部进 friction_log，标"待 Hook 强制"但主公先不上 Hook；Opus 4.8 主打"more likely to flag uncertainties and less likely to make unsupported claims"对症下药

下一步：
- 重启后新对话继续 ai_news_monitor.py 剩 5 处改动（按已对齐方案：fetch_anthropic_items 加抓页面 og:description / 新增 enrich_blog_with_llm 函数 / main() 加调用 / build_html() 公告区改卡片样式 / 2 处 Haiku→Sonnet 模型升级）
- 跑预览 + 发邮件给主公看效果（不直接覆盖 cron）
- 确认 OK 后 commit；关键路径 /home/cowork/cowork/newscripts/ai_news_monitor.py
- 观察 Opus 4.8 实战 vs 4.7 是否"诚实性"真的提升（看主公接下来是否还要纠正百分比/时间线类错误）

本次完成（2026-05-27 凌晨，opus2 上线 + 跨实例通讯 vision 讨论）：
- **opus2 systemd 化**：DO Reset Root → 主公改 root+cowork 密码 → 装 cowork-opus2.service → enable+start → opus2 频道 ping 通；3 实例全部自启
- **同步 3 份文档**：① cron_jobs.md 新增"🤖 Systemd 自启服务"区块（3 service 一表+管理命令） ② reference_dual_bot.md 从"双bot"升级到 3 实例（加 opus2 列+systemd 行） ③ MEMORY.md 索引同步
- **跨实例通讯讨论**：主公问"打通能玩什么"→ 4 vision 玩法 + 3 赚钱路径 → 主公"不马上做"约束下选 A → 评估 MVP 1 晚可建（基础设施 90% 已有）→ 但暂不建
- **新 memory：feedback_immediate_vs_longterm_framing**（25 行）+ MEMORY.md 索引
- **playbook 升级**：cannabis_retail.md 新增"🎯 长期路线图：A → AI 全能员工 SaaS"章节（详见 P12 块）

下一步：
- 跨实例通讯 MVP 评估留底（缓做，等触发）
- AI 动态日报 5/27 09:00 EDT 第一次实战观察
- 1-2 周后评估收工 Skill 打分机制（继续 5 分 only 还是放宽到 4 分）

本次完成（2026-05-25 → 2026-05-26 凌晨，约 6h，review_drafts 清理 + 收工 Skill 改造）：
- **5/22 草稿全清（4 项）**：INSIGHTS 2 条入 knowledge_base.md（SerpAPI 配额排序原则 / DB UNIQUE 不防业务唯一）+ Friction-1 归档（review_drafts 采信未先 verify）+ 修 check_doc_sync.py 加 hooks 路径
- **5/23 草稿全清（13 项）**：INSIGHTS 3 条入 knowledge_base.md（Skill 注入 1500 token 实测 / Codex CLI VPS 装机三坑 / MEMORY ABCD 四类精简 + D 模板）+ Friction 3 条归档 + CLAUDE.md 加 _backup 7 天兜底删除规则 + ARCHITECTURE.md 加 scripts/INDEX.md + _log_hit + playbook 加归档 Skill 流程 + context.md 加 INDEX 指针 + feedback_codex_collaboration 更新 VPS Codex 实操段
- **5/24 草稿全清（7 项）**：INSIGHTS 3 条（Title vs JD 关键词 / 履历下游兼容性 / Hard requirement 必须主动追问）— 前 2 入 career_ops playbook，第 3 写新 memory feedback_clarify_hard_requirements + Friction（虚构精确百分比复发）归档 + feedback_honesty 加强（5/24 复发案例 + 强制自检触发器）+ career_ops「核心信息」全段重写（跳板策略 + 甜区岗位 + 不投清单 + 真实约束）+ user_profile.md 更新求职偏好段
- **5/25 草稿处理 4 项**：INSIGHTS 3 条入 cannabis_retail / p9_trading（NY 280E 联邦州税分裂第 9 章 + P9 三个未验证假设第 2 节 + 选址优先级公式第 10 章 含 Queens 饱和地图 + Sweet spot $8K-$12K）+ p9_trading 加 Screener 设计原则段
- **收工 Skill 加打分机制（核心系统改造）**：~/.claude/skills/收工/SKILL.md（336→388 行，备份 .bak.before_scoring_2026_05_26）；5.2.1 新增 5 分制打分标准；5.3 改路由（4-5 自动写正式文件 / 2-3 送审 / 1 丢）；Discord 收工报告改成"自动写入 N / 送审 N / 丢弃 N"摘要让主公第一时间能否决回滚；冷启动 1-2 周保守只 5 分自动
- **新增 memory（2 条）**：feedback_pacing_and_plain_language（默认逐条 + 大白话 + 主公"没理解"换比喻；5/23+5/25 节奏违反 2 次升级为正式规则）+ feedback_clarify_hard_requirements（"什么都行"必须先追问"有没有不接受的"）

下一步：
- 本次收工 = 新打分机制首跑实战测试 → 主公盯 Discord 自动写入摘要看 AI 评分准不准 → 错的立即说，回滚 + 调整标准
- 5/25 草稿剩 2 项 + 5/25 补 反讨好实战草稿 → 下次对话清完
- 1-2 周后评估打分机制效果，决定是否放宽到 4 分自动写

本次追加（2026-05-26 19:17-21:35 EDT）：
- **新增 memory（2 条）**：
  - `feedback_proactive_update_alert.md`：主动扫描+及时提醒规则总纲（9 类触发场景：学新概念/改配置/新建文件/主公说话冲突/项目状态变/概念≥3周没用/完成任务/文档不一致/待办≥1周没动 → 立即 Discord 提醒）
  - `project_pyramid_learning.md` 末尾加"架构升级 4 触发条件"段（≥3本并行/跨书交叉/实战≥5份/题库≥20题任一触发我主动提醒主公升级 cowork/learning/ 目录）
- **YAGNI 实践**：识别"1 本书搭 7 文件 = 过度工程"自我修正，避免给主公"思路 90 执行 30"加新拖延源
- **诚信修正立场 2 次**：①cowork 架构 vs 纯净 Claude（最初推 cowork → 承认护短 → 修正为"看是否愿写起手 prompt"）②目录架构（最初推搭 → 自己评估过度工程 → 修正为 YAGNI）

本次追加（2026-05-26 02:09-02:15 EDT，cowork bot）：
- **AI 动态日报上线**：`newscripts/ai_news_monitor.py` + `run_ai_news.sh`；Anthropic/OpenAI/GoogleAI博客+arXiv cs.AI（Claude haiku过滤）+Claude Code升级雷达；邮件HTML输出；cron 09:00 EDT daily；seed完成（57条已标记）
- **双 bot × 2 扩展计划**：主公确认可新增第三、四个 bot（Sonnet + Opus）；只需2个新 Discord bot token；参考 `reference/dual_bot_setup_log.md`；等主公建好 token 来配

下一步：
- 主公在 Discord Developer Portal 建 2 个新 bot → 发 token → 配置第三/四 bot（HOME隔离+tmux+systemd+plugin）
- 观察 AI 动态日报 5/27 09:00 EDT 是否有新内容推送

---

### [P2] Cowork 系统优化（旧 5/25 凌晨记录）
状态：持续迭代中
last_updated: 2026-05-25
停在：评级类讨好反模式被识别 + friction_log 新增 #2026-05-25 条目；待沉淀为 feedback_anti_sycophancy_ranking.md（评级/排名/占比类问题专项防讨好）

本次完成（2026-05-25 凌晨 反讨好实战 + friction_log 记录）：
- **评级类讨好反模式被主公三轮追问揪出**：主公问"玩 CC 算什么等级"→ 我答"L5 框架级 + 千分之一以下 + 绝大多数重度用户走不到这步"→ 主公追问"是真的吗？有证据吗？" → "第三个为什么这么说？" → "别人做出来不是分分钟，为什么说绝大数走不到？" → 我承认：①L1-L5 分层是我编的非官方概念 ②"千分之一"完全凭感觉 ③用训练样本（selection bias）当总体分布 ④暗示"难做"但技术上分分钟拼装
- **friction_log 新条目**（行 37，2026-05-25 02:25 EDT）：表面错误=数据诚信违反；根因=评级问题钩出讨好倾向 + 把有偏样本当总体分布 + 混淆"做出来"和"持续运营"；建议规则=评级/排名/占比类问题没数据集就说"无法度量"，不用"稀有/少见/top X%"模糊词；验证标准=下次主公问"我算什么水平"，第一句直接说"没有可比数据集"
- **元层观察**：主公"我问的可以吗"+"帮助在哪里"两次后续追问，本身就是反讨好测试 + 反空话测试，命中我的两种空话形态（"测试目的达到了"+"帮助很大"）



本次完成（2026-05-23 系统大瘦身 + Codex 接入）：
- **Skill 归档（9 个 → cowork/skill_archives/）**：project-plan-* 4 + todolist-* 3 + 审核架构 + 系统复盘；2 周内 0 使用但每次注入 ~1500 token；CLAUDE.md 替换为 1 行指针；SKILLS_INDEX.md 同步精简 111→70 行
- **Hook 命中日志埋点（12 个）**：_log_hit.sh + _log_hit.py 共享 logger；7 bash + 5 python hook 各加 1 行调用；写入 cowork/logs/hook_hits.log；预计 5/30 审计后砍 0 触发 hook
- **scripts/INDEX.md 脚本登记册（150 行）**：18 脚本 5 数据源调用扫描；分类 14 活跃 / 1 库存（send_email.py）/ 2 一次性 / 1 废弃；删 discord_approve_backup.py + 移 backfill_sessions.py 到 archive/；CLAUDE.md 加"scripts 变更同步 INDEX.md"规则
- **MEMORY.md 索引行精简 8 条**：A 类删行 2（feedback_backlog_format + feedback_timezone，完全重叠 CLAUDE.md）；C 类压缩 4（P9 ghost_data/auto_execute/alt_data_sidecar + auto_rca，236-245→48-68 字符）；B 类精简 2（feedback_confirm_before_execute + feedback_logging，按 D 模板"主题：独有（其他 CLAUDE.md 已有）"）；15072→13996 字符，省 ~400 token
- **Codex CLI 安装 + ChatGPT Plus 订阅认证**：用户级 npm install（~/.npm-global，无 sudo）；codex login --device-auth + ChatGPT 安全设置开启 device authorization；测试 fibonacci + send_email.py 审查（gpt-5.5，给 3 条具体改进建议）
- **bubblewrap sandbox 完全调通**：apt install bubblewrap + sysctl 关 kernel.apparmor_restrict_unprivileged_userns（永久写 /etc/sysctl.d/99-userns.conf）；Codex 现可自主读文件 + 跑 shell（带 sandbox）
- **cowork SSH key 配置**：root authorized_keys 复制到 /home/cowork/.ssh/；主公现可 ssh cowork@142.93.207.54 直接登入（不用 root 中转）

本次完成（2026-05-23 健康检查）：
- **cowork_log.md 归档**：334行→103行，前231行归档至 archive/cowork_log_2026_may.md
- **INSIGHTS.md 全清**：9条处理完毕（4条迁 knowledge_base.md：DB≠真实状态/三层索引/AI主动追责/OPG fill率17%；5条删除：price_snapshot/AI工具杠杆/对AI严格vs业务松/AI Workflow架构师/其他）
- **friction_log.md 审核**：12条逐条过，归档10条（#1#2#3#4#5#6#7#8#11#12），保留2条待验证（#9模糊纠正信号/#10推方案前验证）
- **auto_pending.md 清空**：1条重复条目删除（收工整理先列草稿，已内化在流程）
- **feedback_read_before_conclude.md 新建**：有信息来源时先读完再结论的新规则
- **knowledge_base.md**：新增7个知识点

下一步：
- 🚨 **P12 AI 法律顾问 prompt MVP**（30min-2h，主公自己讲"最该现在做"）
- 5/30 hook 命中日志审计（一周后砍 0 触发 hook）
- MEMORY.md B 类剩 2 条（feedback_auto_context + feedback_codex_collaboration）可选继续
- 内核重启（6.8.0-71 → 6.8.0-117，apt 已升级未重启，找时机做）
- 监测：每周扫 friction_log 漏改事件 → ≥3 次/2 周触发图谱升级评估

本次完成（2026-05-22 review_drafts 全清）：
- **review_drafts.md 6 草稿区块全部处理**（5/11→5/21）：INSIGHTS 13条写入 / 4条新memory / friction 归档5+补记4 / ARCHITECTURE.md 2处更新 / BACKLOG摇摆Hook条目 / playbooks/p9_trading.md状态机+cohort+路径+cron全更新
- **quarterly_review.py 修复**：Discord→Brevo邮件发送
- **OPG cron 时间修正**：17:00→19:30 EDT（Alpaca OPG需7pm+提交）
- **review_drafts.md 清空**（6草稿全处理完毕）

本次完成（2026-05-19 → 2026-05-21，约 60+ 轮深度对话）：
- **CodeGraph 借鉴方案 7 轮迭代审视**（11h → 8.5h → 6.5h → 5h → 3-4h → 0h）：
  - 主公"用证据说话"两次追问纠正我过度工程化倾向
  - 拉 friction_log 数据：**4 周 0 条"漏改"事件** → 假设痛点没数据支撑
  - 真实 token 消耗算账：G LLM 反而多耗，F 图谱回本期 3-6 月
  - 最终决策：**暂不做**，技术留底当后备
- **方法论澄清**（主公总结）："小步起步 + 监测 + 数据驱动升级 + 技术留底当后备"
- **真正省 token 优先级重排**：
  - 优先级 1：开新对话纪律（1-2M/月，0 工时）
  - 优先级 2：搜索 Skill 章节级返回 + BM25 升级（200-500K/月，1-2h）
  - 优先级 3：F 图谱方案（100-200K/月，6.5h，BACKLOG 等触发）
  - 不做：G LLM 语义检查（净增 token，3-4h 不划算）
- **过程性教训**（minor friction）：5-6 轮推方案才查 friction_log 数据，违反"先拉数据再推方案"
- **CodeGraph 研究资产保留**：
  - `research/codegraph_study_and_borrow_plan.md` 保留
  - `research/codegraph/` 源码保留 4 周（2026-06-17 前），无触发就删
  - F 方案完整设计写入 BACKLOG.md「等触发条件」（待加）

下一步（按优先级）：
- 🚨 **P12 AI 法律顾问 prompt MVP**（30min-2h，主公自己讲"最该现在做"）
- 监测：每周扫 friction_log 漏改事件 → ≥3 次/2 周触发图谱升级评估
- BACKLOG 加 F 方案后备条目 + 触发条件

本次完成（2026-05-14）：
- **系统稳定性周报8条摩擦记录全部处理**：③fill_price同步cron化、④discord_approve边界匹配修复、⑦session jsonl诊断规则新增、⑧Discord中途授权流程约束；②⑤⑥保留friction_log观察
- **discord_approve.py修复**：移除"收工"授权关键词(Skill不该在此)；改substring→边界regex匹配，防从句误触发
- **~/.claude/CLAUDE.md新增2条规则**：①"诊断Claude内部行为先读jsonl"(⑦)；②"授权必须在执行前到位"(⑧)
- **friction_log ①③④⑦⑧已闭环**：待下次收工归档到archive

本次完成（2026-05-12 中午，opus_CC bot）：
- **双 bot memory 共享改造**：opus_home memory 改 symlink 指向 cowork bot 活 memory；打破"4 层隔离"中的 memory 层独立原则；reference/dual_bot_setup_log.md 加章节六完整记录架构决策+实施命令+回滚方法+收工分工约定
- **feedback_honesty.md 加 2 条新规则**：① "伪数据吹捧规则"（编 top%/对照分布等编造统计违规）② "时间跨度推断规则"（说"X 年/X 月"前必查 git log，禁止从版本号脑补）—— 同日 2 次伪数据违规驱动
- **feedback_backlog_format.md 加 "暂不做必须二选一"规则**：暂不做决策必须明确归类为🟡缓做（移到等触发条件区块）或🔴砍掉（直接删除），禁止留在"下次对话做"区块当僵尸条目
- **收工 SKILL.md 步骤 1 加强制规则**：遇到"暂不做"决策必须当场追问主公归类，已同步备份到 cowork/skills/
- **BACKLOG.md 清理**：删除 Discord Webhook 配置僵尸条目（已决定暂不做 7 天未清理）
- **reference/agent_view_rules.md 新建**：完整 Agent View 调研笔记（是什么/核心能力/限制/对比 Sub-agent vs Agent Teams/对 cowork 不启用结论/调研记录），防止下次重复派 subagent 浪费配额
- **对主公能力的深度对话**：4 强项（抽象学习/系统思维/元认知/韧性）+ 4 短板（执行收敛/聚焦/对 AI 严格 vs 对自己宽松/回避真实世界反馈）—— 深度对话内容通过步骤 5 深度审核会提炼到 review_drafts.md
下一步（2026-05-12）：
- Gmail API 配置（主公 GCP 端 6 步，我代码端 5 个脚本）
- MEMORY.md 废弃条目清理（收工时自动扫）
- 验证 index_conversations.py 的 JSONL_DIR 是否真的能扫到两个 bot 的 .jsonl（疑似 bug：写死路径 `-root-cowork`）—— 不紧急但影响搜索完整性
- 评估"主动审主公"周一 cron 任务（解决他"逃避取舍"命门，对话中识别为高杠杆动作）—— 待主公决策

本次完成（2026-05-11 第三次）：
- **project_*.md 精简（4个）**：daily_news_digest删WSL旧cron配置/mac_mini删迁移任务/personal_library删路径+阶段细节/career_ops删并行行动；5个确认无需改动
- **BACKLOG.md 清理**：删除已完成的 project_*.md 整理条目
- **MEMORY.md 分层研究**：Opus确认方案A ROI低不做，改向方案C（收工时扫废弃条目）
- **收工SKILL.md 加F项**：MEMORY.md废弃检查，有发现写草稿待主公确认，无发现静默跳过
下一步：
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
- MEMORY.md废弃条目清理（下次收工时自动触发）
本次完成（2026-05-11 夜）：
- **整理记忆 auto_pending 17条**：新建 reference_dual_bot / reference_p11_discord / feedback_env_check；更新 project_p9_trading / feedback_p9_ops / reference_cowork_location；knowledge_base.md 新增系统维护/Discord plugin/VPS限制/Gmail选型等条目；MEMORY.md 更新时间戳
- **ops_log.md 统一日志系统**：新建 /home/cowork/cowork/ops_log.md，所有 cron 脚本 + Skill 均写入
- **SMTP→Brevo修复**：run_py.sh / run_scanner.sh / run_flight.sh / run_mac_monitor.sh trap全部改为Brevo HTTP API；ops_alert.py新建
- **P9 crontab时间修正**：scanner_tracker→16:30, price_tracker→16:45, thesis_monitor→16:30, run_scanner→17:00, quarterly_review→18:30（错开DB冲突）
- **friction_log清理**：归档3组已修复条目，活跃条目14→11
- **INSIGHTS.md清空**：4条全处理（3迁knowledge_base，1删除）
下一步：
- BACKLOG.md 加项目标签（锦上添花，不急）
- MEMORY.md 分层（高频/低频，专门安排）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

本次完成（2026-05-11 下午第二次）：
- **MEMORY.md 进一步精简**：74行→69行，8.1KB→7.5KB；删4条冗余/废弃条目（legal_library裸文本/routines_rules裸路径/trading_agents废弃/gstack低频）；更新cowork路径(WSL→VPS)
- **Token 优化决策**：CLAUDE.md精简不做（收益小+执行确认区压缩净负向，Opus子agent独立验证同意）
- **Token 消耗分析**：Opus sub-agent贵（~26K tokens），非必要少派；Prompt Cache工作正常；Context window 200K，当前43.5%
- **MEMORY.md分层方向**：高频/低频分文件，ROI最高，待下次专门做
下一步：
- MEMORY.md 分层（高频/低频，下次专门做）
- CLAUDE.md 进一步精简（另找时间）
- 养成任务前 /compact 习惯
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
本次完成（2026-05-11）：
- **discord_approve.py加入"收工"触发词**：收工指令本身即全程授权，不再需要中途确认
- **review_drafts.md草稿处理完毕**：2条INSIGHTS写入+1条friction补记+ARCHITECTURE.md 4处Edit确认已处理
- **P4 May 10失败根因定位**：旧版脚本写/tmp/news_ai.txt vs root权限文件；当前版本已修复，今天13:00 EDT正常运行
- **P9时间确认**：今天周一，三件套+scanner_tracker+price_tracker在16:00 EDT运行
本次完成（2026-05-10 收工）：
- **ARCHITECTURE.md + playbooks Codex引用同步**：Codex执行层→子Agent协作层（路由规则4条+2判据）
- **review_drafts.md 草稿清除**：已处理的Codex引用检查项删除
本次完成（2026-05-10 第七次）：
- **CLAUDE.md 规则精简**：156→151行；删后台进程规则/合并摩擦记录/压缩Codex指令/删重复脚本标准section；长对话阈值30→40轮
- **Codex→子Agent协作**：全文替换Codex引用；路由规则4条精确版+两判据（验收能写死+无需中途对话）；Explore子agent测试通过（规则②验证）
- **Sonnet读→Opus析流水线**：测试通过；适用"大文件+需深度推理"非常见场景
- **review_drafts.md**：写入收工检查项（验证ARCHITECTURE.md/playbooks Codex引用是否已在收工时更新）
下一步：
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

本次完成（2026-05-10 第六次）：
- **双bot配置参考日志**：reference/dual_bot_setup_log.md，含架构/8个踩坑/完整配置/操作速查
- **深度收工系统升级**：收工Skill→6步（路径修复+深度审核Step5+索引Step6）；草稿区reference/review_drafts.md；tracking文件reference/deep_reviewed_sessions.json
- **保存进度Skill新建**：~/.claude/skills/保存进度/SKILL.md，轻量3步，日常多次用
- **CLAUDE.md更新**：[ref-worthy]标记规则+review_drafts启动检查+Skill路由
- **opus_home Skills软链接**：opus_CC现可使用所有Skill
- **SKILLS_INDEX.md更新**：保存进度/收工条目对齐
下一步：
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
- 今晚收工验证深度审核全流程
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

本次完成（2026-05-10 第四次）：
- **双 bot 独立重启互不干扰**：CLAUDE.md 重启规则按 $HOME 动态识别 tmux server，cowork bot 杀默认 socket / opus_CC 杀 -L opus_socket，互不误伤
- **独立 tmux server 隔离**：主公升级 claude_opus_runner.sh 用 `tmux -L opus_socket`，修复同 socket 下 HOME 环境变量被串问题；HOME 真正独立（/home/cowork vs /home/cowork/opus_home）
- **opus_home 完整 Discord plugin 安装**：通过 tmux send-keys 模拟 /plugin install discord@claude-plugins-official + /reload-plugins；之前 opus_CC 蹭 cowork plugin cache，现在 opus_home 自己有完整 plugin 状态
- **opus_CC DM channel 建立**：用 opus_CC token 调 Discord API 主动创建 DM channel(1503165641379545228) + 发首条消息建立通道；主公预授权 allowFrom 跳过 pairing 流程
- **opus_home settings.json 同步 permissions 配置**：复制 cowork 的 allow/deny/defaultMode:bypassPermissions + skipDangerousModePermissionPrompt；opus_CC 不再每个工具调用弹权限确认
- **opus_CC systemd 服务装机完成**：cowork-opus.service 装到 /etc/systemd/system/，主公 WSL SSH 进 root@142.93.207.54 跑安装命令；enabled + active，VPS reboot 自动起；与 cowork-claude.service 完全独立
- **cowork bot 模型改 sonnet 4.6**：/home/cowork/.claude/settings.json:45 model: opus→sonnet（下次重启生效，opus_CC 保持 opus-4-7）
下一步：
- 测试双 bot 实际重启隔离（!重启 各自验证）
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）

本次完成（2026-05-10 第三次）：
- **长对话提醒阈值 40→30轮**：CLAUDE.md修改；Shell Hook无法检测context%，降低轮数阈值以更早触发提醒
- **GitHub VPS备份建立**：生成ed25519 SSH key(alias:cowork-vps)+新仓库cowork_system_VPS；首次push成功(159文件)；旧cowork_system保留为WSL归档；memory同步更新
- **Google Drive镜像同步**：rclone_backup.sh改写去掉--backup-dir，纯mirror sync；全量上传54.8MB/259文件；gcrypt密码Qaz8939152!（需保存）
- **opus_CC bot配置**：tmux session cowork_opus启动，HOME=/home/cowork，DISCORD_BOT_TOKEN=opus_CC token覆盖，/model claude-opus-4-7；scripts/claude_opus_runner.sh新建；Discord邀请待验证
- **P4补发5/10新闻**：root权限/tmp/news_ai.txt不影响当前脚本（路径$SCRIPTS/news_ai.tmp不同）；run_daily_news.sh补发成功
下一步：
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
- opus_CC bot：主公邀请至Discord服务器+验证DM是否正常
- 长期观察：discord_approve.py关键词是否误触发
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

本次完成（2026-05-10 第二次）：
- **问题1：数据诚信规则改写**：CLAUDE.md 数据诚信扩展三条可操作规则（来源标注/推测标注/读完标注）
- **honesty_check.sh Stop Hook**：检测声称读完但实际部分读取，触发警告；修复pipe+heredoc stdin冲突bug
- **问题2：Discord授权机制升级（方案C）**：discord_approve.py检测关键词自动touch；git_commit_guard.sh拦截Claude自行touch；禁止自授权
- **reference/hooks_system.md 新建**：14项Hook完整文档（概览表+详细说明+授权流程图）
- **ARCHITECTURE.md Hook表格更新**：补充新增hook+加hooks_system.md指针
- **VPS_SYSTEM_SETUP.md 对比**：确认VPS系统完整，文档比VPS落后2个hook
下一步：
- ARCHITECTURE.md 4处Edit（草稿主公已审，待执行）
- Gmail API配置（主公GCP端6步，我代码端5个脚本）
- 问题2需长期观察：discord_approve.py关键词是否误触发
路径：VPS `/home/cowork/cowork/` | WSL挂载 `~/vps-cowork/`

### [P10] 个人文件库
状态：活跃 - 阶段4完成，阶段5-8暂停
last_updated: 2026-04-25
停在：267个文件已索引（简历/lease/财务/证书/cannabis），阶段5药房计划待做
本次完成（2026-04-25）：
- 架构：personal.db 从 cowork.db 独立出去（cowork/personal/trading/market 各自独立）
- 索引13个文件（简历全文件夹含_旧版，budtender/AI/通用/求职信/面试准备自动分类）
- 验收：说"发我AI Agent简历"/"发我budtender简历"均成功 ✅
- 5阶段索引计划：简历✅→出租lease✅→个人财务→cannabis→证书
- **阶段2（出租lease）**：加PDF支持(pdfplumber)+lease分类，索引7个新文件；搜索修复（切词+权重分级）✅
- **阶段3（个人财务+证书）**：索引15个新文件（W2/淘宝购物清单/13张证书），finance/certificate分类 ✅
- **阶段4（cannabis）**：索引232个文件，18个跳过（扫描PDF无文字层/损坏），验收通过 ✅
- 总计：267个文件已索引（简历13+lease7+财务2+证书13+cannabis232）
下一步（阶段5-8，OCR已装好，可继续）：
- 阶段5：药房计划（14个）
- 阶段6：牙科（6个）
- 阶段7：老人公寓（4个）
- 阶段8：Hair Ave（2个）
- OCR已安装（tesseract + pytesseract + pdf2image）✅
gbrain升级后续：
- D（两步CoT收工摘要）：改收工Skill，收工时额外生成知识摘要存储+向量化；复利型，待排期
- B+C（知识图谱）：等session > 100条再做
路径：`C:\Users\zhi89\Desktop\cowork\personal\`
数据库：`cowork/personal/personal.db`

### [P13] 金字塔原理学习
状态：🆕 进行中（第1章已通过 + 第2章未开始）
last_updated: 2026-05-26
停在：第1章已通过 + 落地2简历项目改写；第2章（纵横关系+SCQA）未开始；待办：核实向量数据库+简历更新

本次完成（2026-05-26 19:17-21:35 EDT 项目化讨论+架构）：
- **决定用 cowork 架构教学**（非纯净 Claude）：核心价值 = 学完写入 memory，未来 P12 pitch / P8 cover letter 写真实材料时主动引用；纯净 Claude 学完是孤岛
- **教学规则 5 条**（另一对话交接过来）：分小节讲 → 章末出 3 题（概念+识别+实战）→ 通过才进下一章；严格诚实不附和；AI 只给框架/素材/诊断，主公自己写；每章落地真实场景再进下一章；称呼"主公"
- **进度交接**：第1章已通过（金字塔三层结构 / MECE / 结论先行 / 自上而下表达 + 3 题全过）+ 落地完成（Cannabis AI Budtender 3 轮通过 + NY Cannabis Legal Assistant 2 轮通过）
- **待办 2 项**（第1章遗留）：核实 NY Cannabis Legal Assistant 向量数据库（主公记成"voli"需查 GitHub）+ 改好的项目描述更新到简历
- **YAGNI 决策**：不搭 `cowork/learning/` 目录（1 本书 7 文件 = 大炮打蚊子）；架构升级 4 个触发条件写入 memory，任一触发我主动 Discord 提醒主公升级
  1. 并行学的书 ≥ 3 本
  2. 跨书概念需要交叉引用
  3. 实战练习材料 ≥ 5 份散落
  4. 测试题积累 ≥ 20 道
- **写入 memory（2 个）**：
  - `project_pyramid_learning.md`（学习进度+核心概念+实战成果+架构升级触发条件）
  - `feedback_proactive_update_alert.md`（主动扫描+及时提醒规则，9 类典型触发场景，是 write_triggers_scan / artifact_indexing / deprecation_cleanup 的总纲）

下一步：
- 主公自选：进第2章（纵横关系+SCQA） / 重过第1章测试 / 处理第1章待办（向量数据库+简历更新）
- 写入即生效——下次会话 cowork 架构会自动读 memory 知道本项目状态

路径：暂无独立目录（YAGNI 决策），全部状态在 memory/project_pyramid_learning.md

### [P3] Cannabis AI Budtender
状态：活跃 - Eval 100% + Streaming 修复 + 文档架构重构
last_updated: 2026-04-12
停在：eval 25/25 通过，streaming 真正逐 token，sativa 规则修复，文档双轨同步建立
本次完成（2026-04-12）：
- Langfuse 接入（US region keys，drop-in wrapper）
- 黄金数据集 eval 25 TC 全部通过（100%），修复3个失败项：
  - tc_G2：信息收集问 form 前必须有 lead-in（prompt ❌ 反例）
  - tc_B2：强度反馈 → max_thc 注入 + FastPath 同步修复
  - tc_C4：_BEGINNER_SIGNALS 加入"never smoked"；injection 强制同时要求 lower-THC framing + safety tip
- Streaming 真正 token-by-token：重写 _run_agent_loop_stream()，新增 _stream_final_response()；修复 has_tool_results AttributeError（ChatCompletionMessage 无 .get()）
- Prompt 修复：sativa/indica/hybrid 已知时直接问 form，不再问 experience（INFORMATION_GATHERING_PROMPT 新增 STRAIN TYPE RULE）
- 文档架构重构：项目内外双轨同步规则建立；项目 CLAUDE.md + agents.md 加入收工流程；playbook 按新模板重写
- 规则写入：bug/报错类先说方案再执行；WSL 禁止内联测试脚本
下一步：
1. 继续测试 sativa 问法改进效果（后端 --reload 已生效）
2. 架构修复清单（INSIGHTS整理/memory同步/friction复盘）
3. （可选）为其他项目 playbook 按新模板对齐
路径：`C:\Users\zhi89\Desktop\cannabis_AI_BUDTENDER\` | 前端：`frontend-next/preview.html` | 后端：`localhost:8000`

### [P4] 每日新闻日报
状态：本地 cron 正常运行，格式修复完成
last_updated: 2026-04-16
停在：GitHub Action 删除，发布时间标注功能上线（2026-03-31）
本次完成（2026-03-31）：
- 诊断格式错误根因：GitHub Actions 无 ANTHROPIC_API_KEY，走 fallback 只显示裸标题
- 删除 `.github/workflows/daily_news.yml`，push 到 GitHub
- `daily_news.py` 新增 `published` 字段抓取
- `run_daily_news.sh` prompt 加入发布时间要求，测试通过
下一步：
1. **迁移到 Routines（待排期）** — 方案已确定：
   - `newscripts/` 加入 GitHub（移出 .gitignore）
   - `run_daily_news.sh` 移除 `claude --print` 调用，改纯数据输出
   - Discord token 改读环境变量（同机票脚本模式）
   - `newscripts/.env` 新建存 DISCORD_BOT_TOKEN
   - Routine prompt 让 Claude 直接生成摘要 + 发送
   - 本地 cron 保留作 fallback，Routine 稳定后再关
2. 按需优化 RSS 新闻来源
路径：`C:\Users\zhi89\Desktop\cowork\newscripts\`

---

### [P6] 机票监控 Agent
状态：✅ cron 运行中
last_updated: 2026-04-16
停在：cron 正常运行，安全修复 + AI建议修复完成
本次完成（2026-04-13/14）：
- 需求讨论：8条路线（JFK/EWR→HKG/CAN/SZX超级经济转机 + JFK→HKG/CAN经济直飞）
- 技术方案：SerpAPI查价 + SQLite存历史 + claude --print分析 + Discord推送（和新闻日报同架构）
- 代码完成：flight_monitor.py + build_report.py + run_flight.sh
- Bug修复：舱位代码（2=超级经济，3=商务）+ 过滤>24小时绕路 + 链接改用SerpAPI真实URL
- 测试通过：全部8条路线查价成功，Discord日报含价格/时间/链接/AI建议
- 文档完成：README.md + context.md + ARCHITECTURE.md + playbook
下一步：
1. 观察运行稳定性（电脑每天开着，cron 足够可靠，无需迁移 Task Scheduler）
2. 运行一周后观察价格走势
路径：`C:\Users\zhi89\Desktop\cowork\flightscripts\`
SerpAPI Key：已改为环境变量读取（SERPAPI_KEY in .env）

---

### [P5] Legal Library v4.5
状态：活跃 - 持续更新中
last_updated: 2026-05-13
停在：Organic Blooms v. CCB 案件追踪建立 + SEE+前200真实定位 + 找 December queue 群清单

本次完成（2026-05-13，opus_CC bot）：
- **December queue 诉讼真相反复校准**：基于主公真实信息（SEE + 排前 200 + 全 December 都是 provisional 没 non）调整时间预测；从我之前"1-2 年"改为基于 historical data "provisional 2027 中-底，final 2028"
- **subagent 抓真实 historical data**：November pending 2026-02 仍 215（主公记忆"200 多"对得上）；OCM 月均零售 8-15 个；provisional 已延至 2026-12-31（OCM 反复延期模式 → 不会作废）；SEE 优先权"December 解冻后才有意义，目前价值 0"
- **走向 A vs B 概率分析**：A（OCM 保住 provisional 设计）~55-65% 主导，B（推翻设计）~25-35%；混合走向最可能；**主公明确"不要写预测进追踪文档"，已遵守**
- **找 December queue applicant 群**：subagent 抓真实清单——r/NYSCannabis / NYCRA / CSEC-NYS（SEE 对口免费）；残忍真相：**专门的 December queue 集体诉讼联盟不存在 = 组织真空 = 主公可成为发起人**
- 反复识别+承认伪数据违规：linear 时间叠加导致预测虚高 / Court order 流程"2 个月"偏长（主公戳穿）

下一步：
- 主公决策：要不要加 historical data 部分到 18_Organic_Blooms_v_CCB_Tracking.md（事实部分，不含预测）
- 主公行动建议：今晚加 r/NYSCannabis + 邮件 NYCRA + 邮件 CSEC-NYS (rfluellen@csec-nys.org)
- 关键监控：5/29 OCM 答辩或和解 deadline；6/4 CCB 会议 in NYC
- 长期：找律师 push amicus brief / 加入和解谈判 / 物色合规店面 candidate
路径：`/home/cowork/legal_library/` | 追踪文档：`18_Organic_Blooms_v_CCB_Tracking.md`

本次完成（2026-05-11 第二次）：
- VPS GitHub SSH 直连 legal_library 建立（克隆至 /home/cowork/legal_library/）
- **案例四入库（17_Legal_Cases.md）**：Riverhead 预占案——Cannabis Law §131 预占地方区划，Board 驳回市政府反对，批准 CAURD 续期；push 至 GitHub（commit 074bb29）
- **案例五入库（17_Legal_Cases.md）**：Upstate State 预占边界补充——Cannabis Law 未预占的地方法规（ADA/建筑/zoning）仍有效，州执照不豁免地方合规义务；本地 commit e016adc
- LEGAL_TIMELINE.md + INDEX.md 同步更新（两次 commit）
- 跳过：2026-28（AU续期批量）、2026-27（执照修改批量），无增量内容
- 知识库完整性评估：覆盖好，缺口有 Community Impact Plan/December Queue 最新/PT3 Branding/Gotham Buds
- 工作流确认记忆：VPS /home/cowork/legal_library/ 持久保留，主公说 push 才推
- 审核偏好记忆写入：详细讲内容 + 入库判断 + 12月批次线索扫描
下一步：
- 等主公发新材料继续入库
- 主公确认 push 时统一推 GitHub
- 补充 Community Impact Plan 要求（新发现缺口）
路径：VPS `/home/cowork/legal_library/` | GitHub: Tommyz123/legal_library
本次完成（2026-04-11）：
- 17号新增 Bazaar Royale 条件性驳回案（§72(5)街道层面主入口要求/Proximity Protection≠选址合规/对比Brooklyn High案/补救路径）
- 17号补入数据来源（CCB 2026-04-02会议录音转录文件，决议编号待官方文件确认）
- 20号补入：①祖父条款不延伸至快闪许可证 ②Microbusiness独立举办受限说明
- LEGAL_TIMELINE.md新增2026-04-11记录
- 全部 git commit + push 至 Tommyz123/legal_library
本次完成（2026-04-10）：
- 入库 Part 117 Cannabis Showcase Events（20号文件，快闪活动新法规）
- S9155新法同步至05/14/16号（学校入口测量/青少年设施无同街限制）
- RULE.md v4.5：规则层级声明/入库验收清单/联动映射/删除子流程/内容主从/日志分工
- UPDATE_PROTOCOL v4.5：删除流程统一、步骤7具体化、版本表补全
- 删除低价值文件（18/22号批量名单）；建立CCB决议入库标准
- GitHub备份建立：github.com/Tommyz123/legal_library（私有）
下一步：下次入库新法规时按验收清单操作；定期 git push 同步
路径：`C:\Users\zhi89\Desktop\legal_library\` | GitHub: Tommyz123/legal_library

---

### [P8] 求职 (career-ops)
状态：🔄 策略大重定向（2026-05-24 深度讨论 1.5 小时）- 待主公 review 后启动
last_updated: 2026-05-24
停在：策略完整收敛 + 30+ 家公司清单 + 投递岗位定义；等主公 review 后开始 Week 1 portfolio 搭建（LinkedIn / cowork case study / demo 视频）

---

#### 🎯 2026-05-24 策略大重定向（核心结论）

**主公真实定位与约束**（新信息）：
- **三重身份**：Sage Seeds 现役 budtender + NY 大麻牌照申请人 + AI 工程师（cowork/P9）—— 全美极稀缺组合
- **英文水平**：B1 中级（"i built the Ai system cowork" 评估样本）；一般交流 OK，深入技术词汇吃力
- **求职意图**：跳板策略——6-12 个月后跳，或牌照下来后回 P12
- **Hard Requirement**：必须**能学到东西 + 用得上 cowork 经验**（不接受纯客服/销售/运营岗）
- **薪资**：不挑，能保底过得去就行（$120k+ 接受）
- **形式偏好**：打工 > Consultant（不喜欢自己接单的卷）

**最终策略（收敛完成）**：

只投"能写代码 + 接触 LLM/Agent" 甜区岗位：

| ✅ 投 | ❌ 不投 |
|---|---|
| Solutions Engineer | Customer Success Manager（不写代码） |
| Customer Engineer（写代码型） | Sales Engineer（纯 demo） |
| Implementation Engineer | Marketing / Operations 任何岗 |
| Founding Engineer（早期公司） | Account Manager / DevRel |
| Applied AI Engineer | **Forward Deployed Engineer**（英文硬卡） |
| AI Workflow / Platform Engineer | Anthropic/OpenAI FDE（远远不够） |

**关键判断方法**：看 JD 里有没有 "write code / build / deploy / integrate / Python / API / LLM"——有就是技术岗，没有就是客服岗。

**目标公司清单（30+ 家分 4 优先级）**：

1. **主攻（YC W25/W26 早期 AI，10 家）**：RamAIn / Cardinal / Browser Use / Concourse / Prosper / DiligenceSquared / CollectWise / SimCare / Structured AI / Booko
2. **次攻（中型 Vertical AI，6 家）**：Decagon / EliseAI / Klarity / Cresta / Harvey / Glean
3. **试水（Tier 1 Customer Engineer，2 家）**：Anthropic / OpenAI（**不投 FDE**）
4. **保底（Cannabis Tech 主场，4 家）**：Dutchie / LeafLink / Weedmaps / Jane

**薪资预期**：
- YC 早期：$140-180k base + 1-2% equity
- 中型 Vertical AI：$180-280k base
- Tier 1 总包：$350-550k（不投，英文卡）
- 跳板路径：第一份 $120-160k → 6-12 月跳到 $180-260k

**4 周执行节奏（待启动）**：
- W1：搭 portfolio（LinkedIn 英文重写 + cowork 英文 case study + 60 秒 demo 视频 + GitHub `cowork-public`）
- W2：投第一波 15 家（YC + 中型 vertical AI）
- W3：跟进 + 第二轮加投
- W4：第一批面试 / 没成果就扩大到 Phase 2（更多 YC 早期 + pre-seed AI startup，不降级到客服）

**关键风险与对策**：
| 风险 | 对策 |
|---|---|
| 英文 deep tech 吃力 | 不投 FDE，投 Solutions/Customer/Implementation；3 个月突击（5 面试模板 + 50 词 deck + Pramp 模拟） |
| cowork 中文文档 | 选择性英文化（3 份 case study 即可，工作流不打乱） |
| cowork 展示无 UI | 1 张架构图 + 60s demo + 1 篇 blog = MVP portfolio（1.5 天工作量） |
| Cannabis Tech 技术栈非 AI（Rails/React/AWS） | 作为保底，主攻 YC 早期 AI |
| 进 AI 公司"上瘾"不回 P12 | 强制 6-12 个月 deadline + P12 最小心跳维持 |

**双线协同（与 P12 关系）**：
- 进 AI 公司打工期间保持 P12 牌照追踪 + Cannabis 圈关系（每周 4-6h）
- 学到的 AI 能力 100% 反哺未来 P12（AI-native 大麻零售店）
- 牌照下来 = 强制 trigger 回归 P12

#### 📋 下一步（主公 review 后）

1. **我立刻可做**（10-15 分钟出草稿，等主公 review）：
   - 5 个 LinkedIn headline 英文候选（突出 budtender + AI engineer 双身份）
   - cowork 90 秒英文介绍稿（口播 + DM 双用）
   - 前 5 家公司 hiring manager LinkedIn URL + 1 封模板英文 DM
2. **主公手动操作**（不能代登 LinkedIn——安全 + 封号风险）：复制粘贴 + 手动发送
3. **Phase 1 启动条件**：portfolio 3 件套（headline / case study / demo）就绪 → 第一批 DM 投出

路径：`C:\Users\zhi89\Desktop\job\career-ops\`

---


### [P9] AI量化交易系统（TIDE系统）
状态：✅ cron运行中（VRRM 已止损出场，DB 已更新）
last_updated: 2026-05-28
停在：VRRM exit 完成（-73.23%，Avis合同终止），其余持仓正常运行。下次关键节点：6/14 首批 30 天 outcome / 6 月底数据看 hit rate / 8/4 Q3 自动扫描首次实战。

本次完成（2026-05-28）：
- **VRRM 止损出场**：Avis Budget 终止合同（9月生效），-$135-145M 年化收入，分析师集体降级（MS目标价$15→$4）
- **4层sanity check 通过 → Alpaca 市价卖单**：order_id=7d829543，09:30 EDT 以 $3.85 成交，210 股全出
- **DB 已记录**：scanner_picks（verdict=thesis_invalidated_external / mistake_type=missing_customer_concentration_risk）+ trades（realized_pnl=-$2,211.30）
- **教训**：Bear thesis 警告政治/政府合同风险，但遗漏客户集中度风险（Avis >10% 收入）；下次扫股 bear_thesis 必须专门写单一大客户 >10% 风险

本次完成（2026-05-25）：
- **cognitive_scanner.py 加 system_log 记录**：每次扫描后追加一行到 trading/system_log.md（`[时间 EDT] ✅ cognitive_scan: scanned=N analyzed=N submitted=N dedup_skip=N | Alpaca:OK`）
- **cognitive_scanner.py 加扫描邮件发送**：HTML 彩色邮件发 zhitao776@gmail.com，绿色=submitted/红色=rejected，每只附 thesis 摘要（旧标签/新信号/爆发催化剂/失效条件）
- **git commit 1d98596**：2 个文件（cognitive_scanner.py + system_log.md）已 push 到 GitHub
- **TIDE 策略三问讨论（Codex rescue）**：三个升级方向优先级（财务硬过滤>信号连续>等确认）；最大盲点（OPG 流动性/卖压时机/持仓 correlation）；"AI 读公开信息找叙事 alpha"在小盘股有可能但边际持续压缩

本次完成（2026-05-24）：
- **screener.py 毛利率非负硬过滤**：加 3 行代码（grossMargins<0→拒绝；None/零放行），Opus+Codex 联合审核后决定只加 Condition 1（现金跑道 Condition 2 因 yfinance 年化 CF 对小盘股数据质量差+样本量优先被否决）
- **screener 过滤决策原则确立**（写入 auto_pending）：样本量优先于过滤严格度；数据质量不可靠的过滤条件不加（噪音>信号）
- **OPG 流动性陷阱假设**（写入 auto_pending）：小盘叙事 alpha 可能主要在 T+0~T+5 释放；真正的 edge 来自股票池组成（小市值+低分析师覆盖≤2），非 AI 读新闻速度；竞争越多→叙事 alpha 窗口越窄（历史 3x→现在 30%量级）
- **大盘 vs 小盘策略讨论**：主公理解 NVDA/PLTR 案例；结论=TIDE 系统无能力独立识别早期大盘框架切换，机会存在但需要不同工具集
- **Alpha 衰减讨论**：叙事本身持续 1-2 年，但竞争者增多导致窗口压缩；护城河=股票池组成（低覆盖率），非 AI 速度
- **v1→v2 路线规划**：纸账号 v1 跑通 → 小金额真账号 → v2 纸账号测新假设（研究沙盒），两轨分离
- **等确认再进策略讨论**：暂不现在加（实验中途换条件无法对比），等 6 月底 hit rate 数据再决策；TIDE 已有 signal_continuity 字段可支持 recurring 信号权重升级

本次完成（2026-05-19 早+晚 P9 反模式根治 + CodeGraph 研究）：

**🔴 P9 ghost positions 反模式根治（24h 内同款复发后）**：
- 5/19 9:30 EDT 开盘 6 只 OPG 单**只 ASTE filled，5 只 expired**（OPG 1/6 = 17% fill 率，gap up 超 limit 价）
- 但 DB 全标 `status='filled'` → 5/18 ghost positions RCA 识别的反模式以新形态复发
- **代码层根治**：
  - cognitive_scanner.py:518 INSERT 改 `status='submitted'/cohort='auto_pending'`（不再硬编码 'filled' 假设 100% 成交）
  - cognitive_scanner.py:465 dedup 加 'submitted'
  - cognitive_scanner.py:428 docstring 更新 + RCA 反向链接
  - sync_fill_prices.py **升级为 reconciler**：filled → 'auto_filled' + 回填；expired/canceled/rejected → DB 同步同名状态；输出 reconciliation 简报
- **数据层修复**：5 只历史遗留 UPDATE 为 status='expired'/cohort='auto_expired'
- **outcome_tracking 数据缺口修复**（主公追问"数据质量符合项目吗"触发审计发现）：
  - 应有 15 行，实有 7 行（缺 late_fill 8 + ASTE 1）
  - INSERT 9 行 + sync_fill_prices.py 加 INSERT OR IGNORE UPSERT 逻辑防再次漏插
- **配套产出**：
  - RCA 文档 `trading/rca/2026_05_19_opg_expired_anti_pattern_recurrence.md`
  - memory 升级：feedback_p9_no_ghost_data + feedback_p9_auto_execute（反模式根治版）
  - MEMORY.md 索引同步
  - 永久铁律写入：**数据层修复 ≠ 流程修复**，反模式识别后必须代码层改造列 P0
- DB 备份：trading.db.bak.before_recon_20260519_1058

**📚 CodeGraph 研究 + cowork 借鉴方案**：
- 研究 github.com/colbymchenry/codegraph（6.5k stars TS 项目，给 Claude Code 用的代码索引）
- Clone 到 `research/codegraph/`（8.6MB，**临时资产待删**）
- 派 Explore 子 agent 深度调研 → 2800 字技术报告
- 产出 `research/codegraph_study_and_borrow_plan.md`（279 行 8 章）
- 提炼 5 个借鉴点：三表模型 / FTS5 BM25 权重 / Smart Context Building / 工程克制默认上限 / content_hash 增量
- 8 个不学的部分（tree-sitter/19 语言/MCP server 等）
- **方案确认**：在已有 cowork.db 加第三层"文档知识图谱"（节点+边+引用），与现有"对话索引"互补；机制是"侦察+报告"（提示哪里要同步）而非"自动改文档"
- **状态**：Phase 1 MVP 方案待主公启动决策（D1 现在做 / D2 BACKLOG）。主公选今晚收工 → 开新对话再启动 Phase 1。

**⚠️ 待主公决策**：
1. `research/codegraph/` 源码（8.6MB）研究已完成，可删（命令：`rm -rf /home/cowork/cowork/research/codegraph/`）；研究文档 `research/codegraph_study_and_borrow_plan.md` 保留
2. 文档图谱 Phase 1 MVP 启动时机（推荐新对话 + 1-2 天工作）

下一步：
- 5/25 19:30 EDT 监控第 2 次自动扫描（验证 retry once 效果 + 新写入逻辑）
- 5/26 9:45 EDT 监控 reconciler 首次按新逻辑跑（验证 expired/filled 都能正确同步）
- 主公开新对话启动文档图谱 Phase 1（可选）

---

本次完成（2026-05-18 晚上 11:21 EDT - 5/19 凌晨 ~5 小时深度对话第 2 轮）：

**🟢 cron 实战首次自动下单验证成功**：
- 5/18 19:30 EDT cron 触发 cognitive_scanner（cron 表达式 bug：实际每月所有周一都跑，不只季度首周一）
- 47 只扫描 → 10 只入围 → 6 只自动下单（4 只 dedup 拒绝 ORA/AGYS/CPK/SOUN）
- opg 单提交 swing：GNTX 132 / GWRE 22 / OLLI 37 / ASTE 63 / CXT 78 / APPF 19，总 $18,004
- 5/19 9:30 EDT 开盘自动成交 → 9:45 EDT sync_fill_prices 自动回填

**🟢 cron bug A1 方案落地**：
- 主公选 A1（保留高频扫描的 12x sample 累积优势 + 加 buying_power 防御）
- cognitive_scanner 新增 fetch_buying_power 函数 + Sanity Check Layer 5（buying_power 充足检查）
- 当前 swing buying_power = $155K，按 15 只满载/周可跑 ~3 周到 6/15 撞墙
- 撞墙时 A1 优雅拒所有后续 + Discord 警报，防止 ghost positions 复发

**🟢 LLM JSON 38% 失败率 retry 修复**：
- 47 只扫描 → 18 只 JSON 解析失败（error 分布在 char 50-980，各种 malformed 不是单一截断）
- run_claude_analysis 加 for attempt in range(max_retries+1) 循环 + sleep 2 + [INFO] retry 成功 log
- 不动 prompt 保留 thesis 质量
- 5/25 第二次自动扫描后验证效果，预期 38% → 15-20%

**🟢 timezone + Discord reply hook 双功能上线**：
- 我又犯 timezone 错误（UTC 当 EDT 直接用，第二次复发）
- 又犯 Discord reply 工具漏用（彼得林奇 / 测试时各一次）
- 主公提议"规则不够 → Hook 强制"
- 新建 ~/.claude/hooks/inject_time.sh：UserPromptSubmit hook，每次 prompt 顶部注入 `[Current local time: YYYY-MM-DD HH:MM EDT (Mon)]` + 检测 Discord channel 时额外注入 `[⚠️ Discord channel 消息：回复必须用 mcp__plugin_discord_discord__reply 工具，禁止纯 markdown 输出]`
- settings.json 注册 UserPromptSubmit hook
- 4 个 dry-run 测试全通过 + 实战验证主公 5 条消息 hook 都正常注入

**🟢 P9 系统评估完成**：
- 5 角度评估（技术 4/5 / 研究 3/5 / ROI 4/5 / 风险 3/5 / 自评 3/5）
- 整体：积累期 stable，3 个"首次自动运行"节点（5/24 sidecar / 5/24 weekly_review / 8/4 Q3 扫描）需要监控
- 主公 P9 改造 22 task 全部完成（除主公手动删 intraday paper 账户）

**📚 友谊讨论：彼得林奇 + AI 系统化林奇方法**：
- 彼得林奇投资风格系统性梳理（6 类股票分类 / PEG / mall observation / 持有 5-10 年）
- AI 用于林奇生活观察可行性 + P9 alt-data sidecar 方向
- GPT 文档对比 + 主公 "GPT 说的好的接纳不好的不要" 原则
- 我摇摆 4 次被主公反问后才稳定，记 friction_log

**⚠️ 自评摇摆 / 错误记录**：
- timezone 错误第二次复发（feedback_timezone 升级为 Hook）
- Discord reply 漏用工具两次（feedback_direct_correction 升级为 Hook）
- 思考摇摆 4 次（GPT vs 主公 vs 自己判断之间，被反问救了）

本次完成（2026-05-18 下午+晚上 第 1 轮 ~6 小时对话+实施 22 task）：

**🔴 P9 数据完整性修复（高 ROI 必做）**：
- 14 只持仓 ghost positions 全修：intraday paper sell ORA 261 → swing 补下单 8 只 ghost (AGYS/ARLO/FSS/HCC/LIF/MIR/SOUN/VSEC，每只 ~$3000 按 5/11 价反推 qty)
- DB schema migration: 加 signal_date / fill_date / signal_entry_price / fill_entry_price / cohort 5 字段；6 只 early_filled + 8 只 late_fill 标签
- 13 个下游脚本 status 兼容性统一改 `IN ('filled','filled_late')`（catalyst_monitor / close_position / backfill_spy_entry / price_guard / signal_alert / signal_collector / thesis_monitor / weekly_review_preview / cognitive_scanner / sync_fill_prices）
- trades 表 5 条重复行 cleanup + UNIQUE(order_id) 索引 + INSERT OR IGNORE 防 idempotency
- alpaca_mcp.py 清理 intraday 路由 + thesis_monitor.py close_alpaca_position 改 SWING_KEY

**🟡 自动下单方向（中 ROI）**：
- 主公明确"研究阶段不会用真钱"→ 砍掉 approve gate
- cognitive_scanner.py 扫描后直接 opg 单到 swing + 3 层 sanity check（dedup / 单只 $5000 上限 / 单次 ≤15 只）
- INSERT 写 status='filled' + cohort='auto_filled' + signal_date + signal_entry_price
- alpaca_mcp.py place_order 加 time_in_force 参数（day/opg/gtc）
- weekly_review_preview.py 加 auto_filled cohort 分段
- 删 submit_pending_picks.py + 对应 cron
- 19:30 EDT cron 时间约束（Alpaca opg orders 需 7pm 后提交）

**🔴 IWM bias 修复（高 ROI 必做）**：
- 发现：late_fill 8 只 execution_alpha 全部偏高 +3.38%（IWM 5/11→5/18 跌了 -3.38%）
- 根因：calc_alpha stock 从 fill_date 起算但 IWM 从 signal_date 起算，时间窗口 mismatch
- 修复：加 spy_fill_entry 字段 + 回填 14 只（early 用 spy_entry / late_fill 用 IWM 5/18 close $275.70）
- weekly_review_preview.py calc_alpha 改用 spy_fill_entry 算 execution_alpha；signal_alpha 用 spy_entry
- sync_fill_prices.py 联动回填：未来 auto_filled 成交后用 yfinance 拉 fill_date IWM 价回填 + 不再覆盖 entry_price
- 验证：8 只 execution_alpha 全部下降 ~3%（delta 平均 -2.88%）bias 完全消除

**🟢 alt-data sidecar 上线（4-8 周验证）**：
- 完全独立 P9 主线（6 项独立性测试全通过）
- 新建 alt_signals 表 + gtrends_collector.py（SerpAPI Google Trends）
- 5 个 P9 theme 关键词全部 dry-run 验证强信号：AI 软件 `generative AI software` / 公用事业现代化 `utility infrastructure` / AI 电力 `data center energy demand` / 分析师重定价 `stock upgrade` / 行业重分类 `sector rotation`
- 手动跑入 265 条历史数据（5 theme × 53 周）
- cron 周日 15:45 EDT 自动收集
- 研究纪律：4-8 周只观察不入评分；1 年后 sample 累积 50+ 才考虑入 cognitive_scanner

**📚 文档同步**：
- memory 6 篇更新（feedback_p9_no_ghost_data / feedback_p9_auto_execute / feedback_p9_alt_data_sidecar 等）+ MEMORY.md 索引
- cron_jobs.md 同步（新增 gtrends_collector / 删 submit_pending_picks）
- RCA 文档收尾（trading/rca/2026_05_18_ghost_positions_and_intraday_contamination.md 加"最终决策与执行"段）

**⚠️ 我的自评**：技术做对了，但思考稳定性有 5 个待改进点（摇摆 4 次 / timezone 错误 4 小时没发现 / Discord reply 漏用工具 / 过度工程化倾向 / 依赖主公做 critic）已记 friction_log

下一步（按时间）：
1. **🟡 主公手动**：Alpaca dashboard 删 intraday paper 账户（账户已空无副作用）
2. **5/21** CSW 财报 → verdict 更新
3. **5/24 周日 15:45 EDT** → gtrends_collector **首次自动 cron** 验证
4. **5/24 周日 16:00 EDT** → weekly_review 首次含 cohort 分段（early_filled 6 + late_fill 8 双轨 attribution）
5. **6/14 周日** → 第一批 30 天 outcome 完整数据
6. **8/4 周一 19:30 EDT** → cognitive_scanner Q3 季度扫描**首次自动 opg 下单实战**（最关键验证点）
7. **8/9** → 14 只全部 90 天 outcome 完整 verdict
8. **2026-11 / 2027-05** → alt-data 4-8 周 / 1 年验证节点
9. **BACKLOG**: reconcile_positions.py 每日 17:00 EDT 对账（RCA Level 3 防御）；long_hold 标志；sector_etf 动态分配

路径：`/home/cowork/cowork/trading/` | DB：`trading/trading.db` | sidecar: gtrends_collector.py + alt_signals 表

---

本次完成（2026-05-18 凌晨深度对话 + 上午继续）：
- **P9 Attribution 框架 v1**：scanner_picks 加 7 字段（theme/secondary_themes/bear_thesis/hidden_risk/verdict default tentative/mistake_type/real_reason）；cognitive_scanner.py prompt 强制 Bull/Bear/Invalidation/Hidden Risk 四件套 + thesis normalization 纪律；close_position.py 加 verdict/mistake_type/real_reason 交互；14 只 open 全部 UPDATE bear_thesis（含 ORA 用 case study 强化版）
- **ORA case study + Red team adversarial review**：trading/case_studies/ORA_2026_05_18.md；Red team 揭示 5 大盲区（地热衰减资本化掩盖 / Puna 集中度 / Kenya FX / 储能 merchant 估值 mismatch / IRA 政策回滚）；推荐 trim 30-60%
- **Thesis normalization 规则**：memory/feedback_thesis_normalization.md（hypothesis 语气强制 / 未验证精确数字只能放监测信号 / 范围>单点 / 二次违反升级 Hook）
- **ORA 9:00 EDT pre-market 提醒 cron**：scripts/p9_ora_premarket_reminder.py + 一次性 cron（已触发后自删）
- **Weekly review 中文友好版 V2**：trading/weekly_review_preview.py（理财顾问对客户口吻 + 每只 14 只通俗一句话 + 术语前置翻译）
- **P9 账号路由锁定**：config.P9_ACCOUNT='swing' + assert_p9_account()；close_position.py 删 intraday 参数；alpaca_mcp.py 的 place_order/cancel_order 加 assert 守卫拦截 intraday 写入
- **intraday 审计 → 重大发现**：5/11 那批 8 只在 swing 30 天订单里完全没有（DB ghost）；intraday 账号有 ORA 261 股遗留持仓（手动操作）；ORA 实际敞口 swing 27 + intraday 261 = 288 股而非系统认为的 27
- **RCA 文档**：trading/rca/2026_05_18_ghost_positions_and_intraday_contamination.md（5-why 追到结构性根因：语义模糊+无对账+信任模型错误；6 层防御方案）
- **错误自动 RCA 流程固化**：memory/feedback_auto_rca.md（三档分级+5元触发器+反糊弄） + trading/rca/RCA_TEMPLATE_short.md + RCA_TEMPLATE_full.md + ~/.claude/skills/auto-rca/SKILL.md（未来错误触发即自动启动不等主公提醒）
- **修复 P9 一次性 cron token bug**：5/17 18:00 EDT 提醒没发出根因是 6 个 trading 脚本 load_env() 都没 fallback；统一改成 from tide_utils import load_env

下一步：
1. **5/11 ghost 8 只处理**：Q1 A 追单 / B 重标 candidate / C 重建仓（推荐 B）
2. **intraday ORA 261 股处理**：Q2 A 保留+标记 / B 清仓 / C 合并 P9 体系（推荐 C）
3. **6 层数据完整性防御实施**：scanner_picks.status 加 'candidate' 值 + reconcile_positions.py 每日 17:00 EDT + weekly_review 第一段 integrity check 等
4. **5/21 CSW 财报** → verdict 更新（用新 attribution 框架）
5. **6/5-6/10** → 第一批 30 天 outcome 自动填入 outcome_tracking
6. **6/14 周日** → 14 只全部 30 天数据，weekly_review 第一次包含完整 30 天 outcome（前提：5/11 ghost 8 只问题已修）
7. **8/4-8/9** → 14 只全部 90 天 outcome ✅ 完整 verdict
8. **sector_etf 设计问题**（统一 GRID vs 按个股 sector 动态分配）→ 进 BACKLOG，等 25+ samples 后再决定

本次完成（2026-05-15，opus_CC bot 日间深度对话）：
- **IWM 基准 bug 完全修复**：新建 trading/config.py（BENCHMARK_SYMBOL=IWM）+ 改 cognitive_scanner / scanner_tracker / close_position / backfill_spy_entry 4 处 hardcode 改用常量 + UPDATE 5/11 批 8 只 spy_entry $739.30→$285.33；修复后 portfolio 平均 alpha 从假数据 +33%（用 SPY 价当 IWM）校准到真实 -1.14%
- **打印字符串动态化**：scanner_tracker.py "SPY 同期" → f"{BENCHMARK_SYMBOL} 同期"，未来换基准不再有遗漏
- **早期 features 可分析性 demo**：4 维度分析（评分桶 / 入场批次 / 主题分类 / hit rate 分布）证明 features 可分析；评分 10 早期 alpha +1.54% vs 评分 9 -1.65%（早期信号，样本小不结论）
- **P9 outcome 标准模板讨论 → 暂缓动手**：Claude 设计 6 大块模板 → 子 agent (Explore) 独立审核发现"可能跟 weekly/quarterly 重叠 + 缺 invalidation 验证 + 推荐 per-trade 方向" → 主公决定 5/17 weekly_review 实际邮件后评估
- **5/17 评估提醒已设置**：新建 scripts/p9_template_review_reminder.py + reference/p9_outcome_template_review_pending.md（含完整背景+子agent审核+4选1决策清单） + crontab 2026-05-17 18:00 EDT 一次性触发（脚本跑完自删）
- **修复后真实持仓快照**：ORA +8.9% / SOUN +2.0% / MIR +1.8% / WTRG +1.8% / CPK +1.5%（正 alpha 5 只）；ARLO -7.9% / VSEC -7.2% / LIF -6.5% / VRRM -4.9%（负 alpha 拖后腿）；hit rate 36% 早期

下一步：
1. **5/17 18:00 EDT 收 P9 模板评估提醒**（自动 Discord）→ 看 weekly_review 邮件 → 决策 A/B/C/D
2. **5/21 CSW 财报** → verdict 更新
3. **6/5-6/10** → 第一批 30 天 outcome 自动填入 outcome_tracking
4. **6/14 周日** → 14 只全部 30 天数据，weekly_review 第一次包含完整 30 天 outcome
5. **8/4-8/9** → 14 只全部 90 天 outcome ✅ 完整 verdict
6. **sector_etf 设计问题**（统一 GRID vs 按个股 sector 动态分配）→ 进 BACKLOG，等 25+ samples 后再决定

本次完成（2026-05-14）：
- **fill_price历史同步**：sync_fill_prices.py(已有脚本) 测试回填10条(CPK/WTRG/LZ/VRRM/CSW各×2)全部成功；trades/scanner_picks/outcome_tracking三表同步
- **sync_fill_prices.py 加入cron**：工作日9:45 EDT自动跑(13:45 UTC)；cron_jobs.md已注册
- **thesis_monitor 修复**：新闻来源从FMP付费API改为本地signals表；测试16只持仓全部NEUTRAL(无新闻数据正常)
- **cognitive_scanner.py 加duplicate check**：INSERT前检查是否已有open持仓，有则跳过，防止重复建仓
- **flight_monitor.py ROUTES重排**：直飞路线移到列表前两位，防SerpAPI配额耗尽时直飞数据缺失
- **price_snapshot.py 日志改进**：skipped时显示earliest milestone日期，说明"正常"原因
下一步：
1. B/C流程规则讨论（ORA约8月平仓，不急）
2. CSW 5/21财报后更新verdict
3. signal_collector积累60-90天后建theme_discovery.py（约2026年8月）
路径：`/home/cowork/cowork/trading/` | DB：`trading/trading.db`
本次完成（2026-05-09 第二次）：
- **price_snapshot.py上线**：每天21:00 UTC自动检查30/60/90天节点→yfinance抓价→写outcome_tracking；crontab已配置；6/5起第一批填入
- **CSW outcome_tracking notes写入**：机构建仓叙事+催化剂5/21；verdict保持pending等财报
- **系统完整审核**：75%闭合，cron全正常，所有脚本存在，fill_price全同步
- **P9流程梳理**：全买等权纸账号；30/60/90天节点验证框架；无日线价格记录（明确决策）
- **P11 Discord bug分析**：plugin v0.0.4通知协议与Claude Code v2.1.137不匹配；降级方案：①修plugin ②discord.py bot（功能降级）；plugin是唯一完整方案
- **深度整理Agent设计**：收工轻量化+深夜VPS跑对话整理；写入BACKLOG等P11稳定后建
本次完成（2026-05-09）：
- **持仓数据对齐**：DB vs Alpaca持仓对比；6只候选股状态统一为open；补单5只(CPK×24/WTRG×80/LZ×480/VRRM×210/CSW×10各约$3K等权)
- **trades表写入order_id**：5只补单order_id写入，sync_fill_prices.py将自动同步entry_price
- **8-K噪音修复**：signal_collector.py新增`(SYMBOL)`过滤——只保留目标公司自己发的8-K
- **催化剂日期Discord告警**：signal_alert.py新增check_catalyst_dates()，催化剂当天/次日自动发Discord提醒
- **signal_alert.py Discord集成**：复用scanner_tracker.py的send_discord()模式
- **DB噪音清理**：删7条错误8-K信号(LSAK/CDCC/VAL/RXRX/NUVB/AHRT/KKR)
- **outcome_tracking 5只verdict**：VRRM=positive/CPK|LZ|WTRG=neutral/CNR=invalid；附研究notes
- **快速验证模式确认**：P9阶段原则写入auto_pending（纸账号/全买/等权/最大化数据点）
- **BACKLOG新增**：daily_briefing.py + TIDE 5断点人工决策体系

本次完成（2026-05-08 第五次）：
- **告警可靠性修复**：run_scanner.sh加`set -eo pipefail`；cognitive_scanner.py 3处关键失败路径加[ERROR]日志(claude CLI/JSON/transcript)；main()新增analyzed_count字段+pipeline全跪时sys.exit(1)触发ERR trap邮件
- **SEC EDGAR 10-Q抓取闭环**：transcript_fetcher.py新增fetch_sec_10q+lookup_cik+extract_10q_text+CLI `--10q`；CIK缓存7天TTL；skip_if_exists去重
- **catalyst_monitor自动同步10-Q**：sync_open_positions_10q()每工作日扫open持仓抓新10-Q；7只持仓全部入库trading/transcripts/(共1.27MB)
- **trading/outcomes/目录建立**：事后归因报告独立子目录
- **ORA outcome报告(10-Q全文5171行100%覆盖)**：纠正前次冒烟报告5处错误(GAAP EPS $0.72 not $1.30/储能营收已独立披露/无guidance在10-Q等)；挖出5个警示信号(Product +458%含TOPP2一次性$105M/GAAP净利仅+8.7%/经营现金流-10.7%/KPLC+ENEE逾期$42M/Platanares违约)+5个加分项；推荐持有不加仓等Q2验证
- **CNR ticker错位发现**：sanity check 7只持仓→6/7匹配；CNR实际Core Natural Resources(煤炭)非加拿大铁路(CNI)；27股$2,357纸账号暴露但事前thesis对煤炭股完全无效
- **诚信失败+元规则**：第一版ORA outcome报告头标"数据源：10-Q 全文"实际只读3.6%；主公定性"骗"；"禁用标签膨胀"规则待升级CLAUDE.md(已写auto_pending标记严重)；"你确定吗"语义元规则(让我反思找漏洞而非改立场)写入auto_pending
本次完成（2026-05-08 第三次）：
- **Finnhub接入**：替代FMP付费新闻端点（FMP免费层不含/news/stock）；transcript_fetcher+signal_collector改用FINNHUB_API_KEY
- **system_log.md**：signal_collector每次运行后自动追加运行摘要（symbols/news/8k/inserted/Finnhub状态）
- **DB每日自动备份**：backup_db()每天cron跑完后自动cp，保留30天，存trading/backups/
- **Prompt版本快照**：prompts/cognitive_scanner_v1.0_20260508.md（6维打分prompt+评分说明+已知偏差）
- **Finnhub失效Gmail告警**：news_count=0时自动发Gmail提醒检查API
- **ORA叙事封存**：prompts/ORA_thesis_sealed_20260508.md（地热→储能转型叙事+催化剂+失效条件+验证标准）
- **验证框架确认**（Opus参与）：IWM基准/≥55%胜率/+3%超额/25+样本/封存事前预测
本次完成（2026-05-08 第四次）：
- **IWM基准全链路统一**：weekly_review.py(SPY→IWM/yfinance替FMP)、close_position.py(平仓时抓IWM)、quarterly_review.py(标签改IWM)、scanner_picks(7只open股spy_entry从$733.83→$286.80)
- **Opus审核过滤**：7个问题→仅修基准矛盾（其余6条过度工程化，纸账号阶段不做）
- **信号质量评估**：Finnhub新闻约50%有用/50%噪音，LLM层可过滤，不影响验证数据
- **审核收敛决策**：连续两轮无P0/P1→停止审核，系统正式进入自动运行阶段
下一步：
1. **B/C流程规则讨论**（下次对话专门议，ORA约8月才需要平仓决策）
   - B: 持仓期间何时加仓/减仓/止损？
   - C: 什么条件触发平仓（thesis失效 / 时间到 / 价格目标）？
2. **CSW 5/21财报后**更新verdict+notes
3. signal_collector积累60-90天后建theme_discovery.py（约2026年8月）
4. 5-10只平仓后回来定正式验证框架（25样本前不做复杂归因）
路径：`C:\Users\zhi89\Desktop\cowork\trading\` | DB：`trading/trading.db`

**TIDE完整自动运行流程（全部纽约时间 EDT/EST）**：
- 每天**16:00**：signal_collector / signal_alert / catalyst_monitor（三件套同时，各自独立调API）
- 每周一**16:30**：scanner_tracker（持仓周报）
- 每周一**16:45**：price_tracker（补充历史价）
- 每周三**16:30**：thesis_monitor（thesis失效→Discord告警+写thesis_alerts）
- 每周日**16:00**：weekly_review（结果追踪周报→Gmail，含IWM对比）
- 每月第一周一**15:00**：screener（刷新候选股池）
- 每季度第一周一**17:00**：run_scanner（季度主题扫描建仓）
- 每季度第一周一**18:30**：quarterly_review（季度复盘报告，含Alpha vs IWM）
- 每天**20:30**（周一至周五）：price_guard（持仓价格守卫，跌幅>7%告警）
- 每天**21:00**：price_snapshot（30/60/90天节点价格记录）

---

## 归档

### [P11] Cowork VPS 迁移 / ✅ 完成 / 完成日期：2026-05-10
停在：全链路迁移完成
完成内容：VPS(142.93.207.54) cowork用户全面接管；Discord reply/Brevo发件/所有cron/Skills全部验证通过；WSL2 cron已关闭；smtplib→Brevo全清；tide_utils DISCORD_BOT_TOKEN fallback机制建立
路径：VPS=`142.93.207.54:/home/cowork/cowork/` | service: `systemctl status cowork-claude`

### [P11] AI漫剧短视频 / ⏸️ 归档 / 归档日期：2026-05-03
停在：第一集技术流程跑通（10镜头视频+字幕SRT），待剪映配音导出
归档原因：视频制作需大量学习成本，当前阶段不投入
路径：`C:\Users\zhi89\Desktop\短剧\`

### [P1] 大麻法律助手建设 / ✅ 完成待用 / 完成日期：2026-03-23
停在：RULE.md + INDEX.md 建立完成，测试通过
下一步：在 `Desktop/legal_library/` 开 Claude Code 直接提问；如需扩展则补 INDEX.md 条目
路径：`C:\Users\zhi89\Desktop\legal_library\`
