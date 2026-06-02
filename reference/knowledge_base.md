# Knowledge Base — 已审核技术参考

> 从 INSIGHTS.md 审核后迁入的稳定参考知识
> 遇工具报错/环境问题 → 先查这里
> 更新：新条目经 INSIGHTS.md 审核后追加；过时条目直接删除

---

## WSL 环境

**Playwright MCP 在 WSL 下的启动方式**
需要用 cmd.exe 执行：`/mnt/c/Windows/System32/cmd.exe /c "npx @playwright/mcp@latest"`
直接在 WSL 里调 npx 会失败，因为 Node.js 装在 Windows 侧。

**WSL 环境 pip install 需加 --break-system-packages**
PEP 668 保护机制导致直接 pip install 报错。
解决：`pip install feedparser requests --break-system-packages`

**claude --print stdout/stderr 分流行为**
AI 回复走 stdout，hook 日志走 stderr。
用 $() 捕获时加 2>&1 会把 hook 输出混进去覆盖 AI 回复。
正确写法：`claude --print --output-format text -p "$PROMPT" < /dev/null > /tmp/out.txt`
< /dev/null 跳过 stdin 等待，去掉 2>&1 保持 stdout 干净。

**cron 脚本省 token：cwd 不能在 cowork/ 目录**
`claude --print` 从 cowork/ 目录运行时自动加载 CLAUDE.md（~2500 token）+ MEMORY.md（~2300 token），对分析类 cron 任务完全无用。
解决：cwd 不能在 cowork/，默认用 `/tmp`；有特定 context 需求时可用其他无 CLAUDE.md 的目录，认证走 keychain 不受影响。
- bash 脚本：`(cd /tmp && claude --print ... -p "$PROMPT")`
- Python subprocess：加 `cwd='/tmp'` 参数
⚠️ `--bare` 也能跳过 CLAUDE.md，但同时断 keychain 认证，订阅模式下直接"Not logged in"，不可用。
验证：从 /tmp 跑的 P9 分析输出结构、推理质量与带 CLAUDE.md 版本一致（2026-04-24）。

**cron 脚本模型选择：摘要类用 Haiku，复杂分析保留 Sonnet**
`--model haiku` 可直接加在 `claude --print` 命令里，省约 80% 模型成本。
适用：格式化/汇总类任务（新闻摘要、简单通知）。
不适用：多维度结构化 JSON 分析（如 P9 盘前，8 个数据维度 + 严格 JSON 格式，Haiku 错误率明显上升）。

---

## MCP 与系统设计

**"不加规则"也是决策，需要记录理由**
系统复盘时不要直接加规则——先问"已有规则为什么没执行"。原因可能是：规则已有但没内化 / 单次违规不够升级 / 场景被现有规则覆盖。
判断框架：不是所有摩擦都该变成规则。加规则前先确认：① 这个场景没有已有规则吗？② 已有规则为什么失效了？
适用：系统复盘时决定是否新增规则/Hook。

**Opus subagent 作为第二意见的正确用法**
- 复杂规则/架构决策 → 先问 Opus 独立分析，置信度更高
- 个人倾向/执行细节 → 直接做，不需要派 Opus
关键：Opus 给的是"有据可查的推理"，不是附和。派之前确保 prompt 不泄露自己的倾向（否则容易拿到合理化而非真正第二意见）。

**子 agent 任务设计三要素（高质量输出必备）**
Opus subagent 质量高的 prompt 共性：
(a) 输出格式严格固定（字段/结构明确）
(b) 反糊弄条款明确（"不许只是 inverse"/"至少 3 layer 5-why"/"不能附和"）
(c) Quality bar 说明（"读起来像 institutional analyst 而非 Twitter call"）
三点缺一不可。随手写 prompt 输出质量不稳定。

**红队对抗审核（adversarial review）暴露盲区**
让独立 subagent 不知情当前持仓/决策状态，独立写 bear case / 反驳论点。效果显著优于自己写 bear thesis。
P9 实测：Opus subagent 揭示 5 个 Claude 自写 bear thesis 完全没覆盖的角度（地热衰减资本化/Puna集中度/Kenya FX/储能merchant估值/IRA政策）。
适用：任何重要决策——投资 thesis、系统设计方案、商业方案。关键：subagent 不知情，才能真正独立。

**DB ≠ 真实状态，自动化系统必须有 reconciliation 机制**
任何 DB + 外部权威系统（broker/API/账号）的组合，DB 记录不等于外部真实状态。必须有定期对账机制。
- P9 教训：scanner_picks.status='open' 被下游误读为"已成交持仓"，实际 8 只是 DB-only 虚拟记录
- 原则：Alpaca = 持仓 SoT；DB = thesis SoT。两者语义不同，不能混用
- 落地：reconciler 每次 OPG 成交后自动跑（sync_fill_prices.py），weekly_review 第一段 integrity check
适用：任何有 DB + 外部账号/服务的自动化系统设计

**cowork 三层索引架构（2026-05-21 决策）**
Layer 1 = cowork.db（对话 FTS5+向量，找过程/历史）；Layer 2 = MEMORY.md/INDEX.md（人工指针，定位文件）；Layer 3 = 知识图谱（节点+边，找规则波及范围，**待建**）。三层互补不替代，用途不同。
Layer 3 触发条件：2 周内 ≥3 次漏更新关联文件 friction → 才重新评估。当前 4 周 0 条漏更新，暂不建。

**AI 主动追责比被动响应杠杆更高**
主公逃避项目取舍的根本原因是"承诺没有外部追责"。AI 主动发起审查（如每周一审 CURRENT_SESSION 老化项目）比写 5 个自动化 Hook 加起来更有效——Hook 只管代码行为，管不了决策节奏。
适用：设计 AI 工作流时，主动周期性追责 > 被动响应触发。把"主动汇报过期项目"做成 cron，不是做成 Hook。

**MCP 工具定义的 token 开销规律**
每条消息固定带入所有 MCP 工具定义，Playwright MCP 约增加 2000-4000 token。
不用的 MCP 就不要装，用不到时从 mcp.json 删掉。

**CLAUDE.md 瘦身不影响功能的原则**
删格式示例（代码块模板）不影响规则逻辑，只要逻辑保留即可。
145行→50行，减少51%，规则全部保留。

---

## 外部集成

**邮件服务选型：优先 Gmail API，不用 Resend 免费层**
Resend 免费层未验证自定义域名时发件人是 `onboarding@resend.dev`，高概率进 Spam/Promotions。Gmail API 发件人是 `zhitao776@gmail.com`，天然可信。有自己 Gmail 账号时优先 Gmail API，不值得为 Resend 额外配域名+SPF/DKIM。（2026-05-10）

**RemoteTrigger 传中文/emoji 复杂 JSON 的解决方案**
update/create 时传复杂嵌套 JSON + 中文/emoji 会报 "provided as string" 错误。
解决方案：把完整指令写入本地文件，trigger prompt 只写一行"读取文件并执行"。

**Discord DM 发送：直接用已知 channel ID**
通过 POST /users/@me/channels 创建新 DM channel 后发消息会返回 400。
正确做法：直接往已知 channel ID 发消息（POST /channels/{id}/messages）。

**Reddit 爬取：VPS IP 被 ban，用 Pullpush mirror 绕过**（2026-05-16）[ref-worthy]
- ❌ VPS（DigitalOcean / AWS / GCP / Azure 全部）直接访问 `reddit.com` 任意路径 = **403 Blocked**（首页 / hot.json / about.json / search.json / RSS 全失败，与 User-Agent 无关）
- ❌ Reddit 2023 年起对 Data Center IP 整体封锁，OAuth API 限速严格 + 申请门槛高
- ❌ Claude Code 自带 WebFetch 也无法访问 reddit.com
- ✅ **解决方案：Pullpush.io**（Pushshift 开源 community mirror）
  - 端点：`https://api.pullpush.io/reddit/search/submission?subreddit={sub}&q={kw}&size={n}&sort=score&sort_type=desc`
  - 免费 / 不要 API key / 直接 JSON / VPS 能访问
  - 测试通过 sub：r/queens / r/AskNYC / r/newyork / r/cannabis / r/trees / r/nyc / r/NYSCannabis / r/longisland
- ⚠️ **限制必知**：
  - 数据滞后 1-4 年（r/NYWeed 最新 2022-08 / r/queens 最新 dispensary 帖 2024-11）
  - score / num_comments 是创建时初始值（一律返回 1），**无法按热度排序**
  - 但 title / selftext / author / created_utc / permalink 全部真实可用
- ✅ **适用场景**：历史数据分析（答题题库 / sub 文化 / 竞品口碑 / 品牌评价 / 痛点提取）
- ❌ **不适用**：实时监控（开业后口碑 / 24h 负评告警 → 需付费住宅代理 / ScraperAPI / 主公本地住宅 IP 跑）
- 测试脚本：`/tmp/reddit_test.py`（临时未纳入 scripts/）

**SerpAPI 配额管理：列表排序 = 隐含优先级声明**（2026-05-22）[ref-worthy]
- 月度配额耗尽时，**列表末位的项最先被跳过**（P6 机票直飞路线 JFK→HKG/CAN 原排末位被掉 → 已移到最前面修复）
- 通用原则：写"轮询 API / 速率限制 / 配额分配 / 资源轮转"代码时，**集合的物理排序就是隐含的优先级声明**，必须显式设计排序而非随机/历史顺序
- 排查信号：发现"某些 X 总被跳过"先检查它在列表中的位置

**Codex CLI 在 VPS（无浏览器）装机三坑组合**（2026-05-23）[ref-worthy]
- **坑 1：必须走 device-auth flow**——VPS 没浏览器，`codex login` 默认走 browser callback 直接卡死；改用 `codex login --device-auth` 走 device code flow（pair code 显示在终端，主公到 ChatGPT 网站输入）
- **坑 2：ChatGPT 安全设置默认禁用 device authorization**——主公需到 ChatGPT 网站 → Settings → Security 主动打开 "Device Authorization" 开关，否则 device-auth flow 直接拒绝
- **坑 3：Ubuntu 24.04 bubblewrap 二段限制**——`apt install bubblewrap` 装完还不够，AppArmor 默认 `kernel.apparmor_restrict_unprivileged_userns=1` 拦截 user namespace 创建（Codex/Docker/snap 都依赖）；需 `sudo sysctl kernel.apparmor_restrict_unprivileged_userns=0` + 写 `/etc/sysctl.d/99-userns.conf` 永久生效
- **安装方式**：用户级 npm（`npm install -g @openai/codex --prefix ~/.npm-global`），无 sudo；`~/.npm-global/bin/codex` 是命令路径
- **订阅模式**：ChatGPT Plus $20/月可用 codex CLI，**不耗 OpenAI API**（符合主公"用订阅不调 API"原则，详见 `memory/feedback_claude_cli_vs_api.md`）
- **验证命令**：`codex login status` 看认证状态；`echo "..." | codex exec` 是非交互调用模式
- 完整安装日志（如已起草）：见 `reference/codex_setup_log.md`

---

## 技术踩坑库

> 外部工具/服务的客观限制。设计涉及外部连接/API/定时任务/推送通知时先查此区块。

### 网络/连接限制
- **Routines** → discord.com 在白名单外不可达，RSS 抓取和 Discord API 推送均失败。推送类定时任务改用 GitHub Actions（有完整出站网络权限）
- **RSS feeds** → 部分源有缓存，抓取可能返回旧文章（最旧可到1月份）。解法：加48小时日期过滤，用 `parsedate_to_datetime` 解析 `published` 字段后与 `datetime.now(timezone.utc) - timedelta(hours=48)` 对比
- **DigitalOcean VPS 封出站 SMTP** → 所有 SMTP 端口（25/465/587）全部封锁，smtplib 方式发邮件在 DO VPS 上必定失败（不报错，只是发不出去）。唯一可用：HTTP API（走443）。当前方案：Brevo REST API（`https://api.brevo.com/v3/smtp/email`），key 存 `config/api_keys.env`（BREVO_API_KEY）

### CLI工具行为
- **`claude --print`** → 回复内容只输出到 stdout；不要加 `2>&1`（会混入系统日志）；必须加 `< /dev/null` 防止挂起；用临时文件 `> /tmp/out.txt` 捕获输出
- **Codex 原生调用方式** → `codex-companion.mjs task --background "..."` → 轮询 status → 读 result（JSON）；比用 result.md 文件传递更简洁，适合后台执行后读取结果

### Discord API限制
- **Discord Bot reply** → pairing 模式下 reply 工具正常；allowlist 模式导致"channel is not allowlisted"报错，不要切换到 allowlist 模式
- **Discord DM 发送** → 不要用 `/users/@me/channels` 创建新 DM channel（返回400）；直接往已知 channel ID 发消息（`POST /channels/{id}/messages`）
- **Discord plugin v0.0.4 bug（fetchAllowedChannel）** → `ch.recipientId ?? dmChannelUserMap.get(id)` 在 partial DM channel 状态下 `ch.recipientId` 错返 bot 自己 ID，`??` 短路不走 fallback，报 "channel is not allowlisted"。修复：反转为 `dmChannelUserMap.get(id) ?? ch.recipientId`（dmMap 是 inbound 验证过的可靠值）。**plugin 升级后需重新 patch**，备份：`/root/.claude/plugins/cache/.../discord/0.0.4/server.ts.bak_fix`
- **`??` 操作符盲区** → 只在 null/undefined 时 fallback，"错的非空值"会跳过 fallback；当主数据源不可靠时，应改为 `fallback ?? primary` 或加显式校验

### Claude Code 诊断方法
- **诊断 plugin/工具执行问题必须先看 session jsonl** → `~/.claude/projects/<cwd>/<sid>.jsonl`，解析 `user/assistant/tool_use/tool_result` 事件流看 Claude 实际做了什么。只看 hook log/server stderr 不看 Claude 行为会反复误判（P11 4次诊断全错的根因，2026-05-09）
- **`--channels plugin:<name>@<marketplace>` 是 plugin channel 订阅开关** → 不带这个参数 host 不会订阅 plugin notification；部署 systemd/守护服务时容易漏（P11 VPS 真根因）。验证：TUI 启动后显示 "Listening for channel messages from: ..." 表示订阅生效

### Claude Code Hook 系统限制
- **Discord中途消息不触发UserPromptSubmit hook** → discord_approve.py 仅在 UserPromptSubmit 阶段扫描输入；Claude 处理过程中主公在 Discord 回复的消息以 system-reminder 形式到达，不触发 hook，task_approved 不会自动创建。解法：主公需在**新消息**里重发一次确认（如"可以执行"）才能让 hook 正常生效。（2026-05-10 收工中发现）

## 系统维护

**停用/改方向系统必须三层同时清理**
停用一个系统时，不能只停代码，必须同时清理三层，缺任何一层都会导致新系统数据混乱无法信任：
1. **DB旧记录**：DELETE 或 DROP 旧系统表，避免新系统误读
2. **账号旧持仓**：平掉旧系统建的仓位/数据（如 Alpaca 纸账号里旧策略的持仓）
3. **引用文件**：清理 playbook/memory 里的遗留描述，避免下次对话被误导

适用：任何有 DB + 外部账号 + 文档三层的系统停用场景（P9第一系统2026-05-06停用时验证）

**Skill 描述每次对话自动注入有真实 token 成本**（2026-05-23）[ref-worthy]
- 实测数据：9 个未使用 Skill 的 description 字段被 Claude Code 自动注入 system-reminder 的 "Available skills" 列表，**累计 1,238 字符 ≈ 1,500 token / 对话**
- 归档到 `cowork/skill_archives/<name>/` 后，Claude Code 不再扫描该目录 → 简介不再注入 → 立刻省 token
- 单 Skill 估算：description 平均约 100-200 token 注入成本（取决于描述长度）
- 归档后**功能不丢**：CLAUDE.md 写好路由规则（"归档 Skill → 查 skill_archives/INDEX.md → 读对应 SKILL.md 执行"），归档 Skill 依然能被关键词触发，只是从"自动注入"变成"按需读取"
- 决策依据：日常用频次 ≥ 1 次/月 → 留在 `~/.claude/skills/`；< 1 次/月 → 归档
- 用于：未来加/删/归档任何 Skill 时的量化决策依据

**MEMORY.md 索引行精简：ABCD 四类处理 + D 模板**（2026-05-23）[ref-worthy]
- MEMORY.md 每行每次对话开头自动注入，行长度 = 直接 token 成本
- **A 类**（内容与 CLAUDE.md 完全重复）→ **删整行**
- **B 类**（有独家信息 + 部分跟 CLAUDE.md 重叠）→ **只留独家，加`（其他 CLAUDE.md 已有）`后缀**
- **C 类**（长字符串没重复但啰嗦）→ **压缩到 ≤150 字符**
- **D 模板**（推荐新加 memory 时的标准格式）：`[主题]：[独家部分]（其他 CLAUDE.md 已有）`
  - 例：`日志纪律：大事记不记细节；收工 ⊃ 保存进度（其他 CLAUDE.md 已有）`
  - 优点：一眼看主题分类 + 显式标注"完整规则在 CLAUDE.md"，提示 Claude 不要在 MEMORY 重复存
- 实测节省：全量精简后总省 **~400 token / 对话**
- 用于：新建 memory 时写索引行 / 整理记忆 Skill 流程加一步"按 ABCD 类格式化"

**三实例重启加载新配置：杀 session 不杀 server，无需 sudo**（2026-06-02）[ref-worthy]
- 场景：改了共享层 settings.json（hook）后需重启实例让新配置生效；`sudo systemctl restart` 会卡密码
- **无需 sudo 的正确做法**：杀掉 tmux **session**（不是整个 server），runner 会自动重生 session 并加载新配置
- **AA 与 BB/CC 的 runner 机制不同**（实测 2026-06-02）：
  - **BB/CC**（opus_home/opus2_home）：runner 是 `while true` 内循环，每 5s 检查 session 是否存在，不在就自己重生 → 杀 session 后 ≤5s 自动回来
  - **AA**（默认 socket）：runner 在 session 死后 **exit 1** → 靠 systemd `Restart=on-failure` 重启（spawn 新 runner 创建新 session）
- **坑**：杀 AA session 后立即检查会看到 "no server running"，那是 systemd RestartSec 窗口内（约几秒），不是失败——等几秒 NRestarts 会 +1，session 回来
- **CC 杀自己 session = 终止当前会话**：先发 Discord 通知主公，再杀；`while true` runner ≤5s 用新配置重生
- 验证配置已生效：看每条 Discord 消息收到的 `⏰ Discord消息时间` system-reminder（= 共享层 discord_ts_convert.py 输出），出现即证明新 hook 已加载
- 用于：任何改共享层 settings.json / hook 后需重启实例的场景

---

## SQLite / 数据库

**FTS5 多字段搜索权重设计**
filename/category 命中比 content 命中权重高（×2分），避免文件名明确匹配时被内容分散排序。
适用：多类型字段的 FTS5 搜索，文件名/分类比内容更可靠时。

**PDF提取工具选择（WSL）**
- PyMuPDF(fitz) 比 pdfplumber 快10倍；WSL 大 PDF 必须用 PyMuPDF
- 扫描版PDF（无文字层）需 OCR（tesseract 已装）
```python
import fitz  # PyMuPDF（推荐，快）
doc = fitz.open(path)
text = "\n".join(page.get_text() for page in doc)
# pdfplumber（小文件可用）
with pdfplumber.open(path) as pdf:
    text = "\n".join(p.extract_text() or "" for p in pdf.pages)
```

**FMP API 踩坑（金融数据）**
- FMP v3 endpoints 全部 403 废弃 → 改用 stable endpoints（`/stable/` 前缀）
- `stable/company-screener` 市值上限过滤失效 → 改用 Wikipedia S&P 400+600 名单 + yfinance 补数据
- FMP 财报 transcript 需付费 → 改用 FMP 新闻全文（`text` 字段已有内容）
- screener 单次运行约30分钟，不能在 scanner 里重跑 → 必须读 `screener_output.json` 缓存

**DB UNIQUE 约束只能管字段重复，管不了"业务唯一"**（2026-05-22）[ref-worthy]
- 教训源头：P9 `scanner_picks` 表 `UNIQUE(symbol, scan_date)` 只防"同一只股票+同一天"重复，**不防跨日重复扫入同一活跃股票**（5/6 扫入 ORA → 5/13 又被扫入 → DB 无报错，结果两条 ORA picks）
- 根因：DB UNIQUE 只能约束"几个字段不重合"，无法表达"业务上同一活跃实体只能存在一条"
- 修复：在 INSERT 前应用层加检查 — 「该 symbol 是否已有 `status IN ('submitted','filled','open')` 的活跃记录？有则跳过」
- 通用原则：任何 append-only 表里，**"逻辑唯一"约束（同一活跃实体只能有一条）必须在应用层检查**，不能只靠 DB UNIQUE
- 类似场景预警：trades 表（同一订单不能重复）/ news_archive（同一新闻不能重复推送）/ outcome_tracking（同一 pick 只能有一条结果记录）
- 排查信号：发现"实体重复出现"时先查 INSERT 路径有没有应用层前置检查，不要只看 DB schema

---

## P9 TIDE 量化系统

**OPG 单实测 fill 率（2026-05-19 基准）**
Alpaca paper account OPG 单实测 fill 率约 17%（1/6，5/19 首次自动扫描）。Gap up 超 limit 价时 Alpaca 自动作废订单。
- 15 只满载 × 17% ≈ 每次扫描成交 2-3 只
- buying_power 长期闲置，sample 累积慢（一年约 8-12 个数据点）
- Q3（8/4）扫描预期 2-3 只成交，不要期待满载
适用：评估 P9 sample 累积速度、讨论是否调整 limit 价策略时参考此基准

---

## WSL 启动 Windows 程序
- ❌ 错误：`cmd.exe /c start "程序路径"` → WSL 找不到 cmd.exe
- ✅ 正确：`/mnt/c/Windows/System32/cmd.exe /c start "" "C:\Program Files\程序名\程序.exe"`
- 适用：TeamViewer、任何 Windows 原生程序

---

## 法律 / 合规 AI 设计原则

**法律 RAG 必须保留原始来源指针（硬要求 / 2026-05-26 上线）**

LLM × LLM 双验证 ≠ 法律权威性。LLM 会重写/总结/改写法律条文，哪怕看起来一致，最终引用必须能回溯到**官方原文 PDF / HTML 锚点**。

**强制要求：**
1. **保留原始 URL + 抓取日期**：`source_url: https://ocm.ny.gov/...` + `fetched_at: YYYY-MM-DD`（法律会改版，没这个以后追溯不了）
2. **原始 HTML/PDF 单独存一份**：整理版给 AI 用 / 原始版给律师审 → 两层不要混
3. **联邦 vs 州 分目录**：`federal/` 和 `ny_state/` 分开（同一条款在不同层级规则不同）
4. **每条法律 frontmatter 标 `source` + `regulation` 字段**（P5 v4.5 的做法是对的：`source: 9NYCRR_Parts118-125_Official.pdf（页7-34）` + `regulation: 9 NYCRR Part 118, § 118.1`）

**反模式：**
- 只存 LLM 整理过的版本 → 法律顾问 AI 用的时候没法拿原文给律师审 → 出大问题
- 用 LLM 改写/精简法律条文当作权威 → 律师 review 时发现条文不对，整套系统信任崩塌

**适用：**
- P5 Legal Library（已遵循）
- P12 AI 法律顾问（V0 阶段必须遵循）
- 主公本地爬法律条文（2026-05-26 提醒主公）
- 未来任何法律/合规 AI 项目

依据：`memory/feedback_p9_no_ghost_data` 同款原则（DB ≠ broker，必须有真实 source of truth）的法律领域版本
