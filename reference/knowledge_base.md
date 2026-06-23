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

**permissions.deny 禁止特定 Claude Code 工具触发（2026-06-22 验证）**
场景：Claude 实例被配置了"禁止弹终端交互式菜单"的规则（CLAUDE.md），但 BB 实例连续三次触犯，违反了记忆规则。
根因：文字规则靠内化执行，模型可能忽略；`permissions.deny` 在配置层硬拦截，模型无法绕过。
解决：在共享层 `settings.json` 加 `"permissions": {"deny": ["AskUserQuestion"]}`，三实例统一继承，重启生效。
- JSON 写法：与 `hooks` 平级，同级加 `"permissions": {"deny": ["工具名"]}`
- 生效：重启实例后生效（不热加载）
- 适用：任何"规则文字写了但 Claude 反复忘"的工具行为，升级机制=deny 硬拦
- 延伸：可以 deny 多个工具，如 `["AskUserQuestion", "Bash"]`（极端隔离）

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
- **`cmd | tee` 管道吞退出码 → 必须 `set -o pipefail`**（2026-06-21 P9 run_py.sh 增强时发现）：bash 管道默认返回**最后一个命令**的退出码，`python3 x.py 2>&1 | tee log` 里 tee 几乎总成功 → 整条管道退出码=0，即使 python 失败也判成功。后果：依赖退出码的 `trap ... ERR` / `set -e` / `&& 告警` **全部漏触发 = 漏报**（比误报危险）。凡是「跑命令 + tee 留日志 + 失败要告警」的脚本，开头必加 `set -o pipefail`。验证：python 故意报错时 `echo $?` 应=1 而非 0。
- **问实例"你是什么模型"不可靠 → 查 `$HOME/.claude/settings.json` 的 model 字段**（2026-06-10）：旧 CLI 下实例会否认晚于自己的型号存在（实测 AA 答"没有 Fable 5 这个模型"）。判断实例真实模型以 settings.json 为准。注：现已加 `instance_identity.sh` hook 自动注入身份，此坑日常已规避，仅作机制备查。
- **`run_py.sh` 只服务正式 cron，调试/临时脚本直接 `python3 xxx.py` 跑**（2026-06-22）：run_py.sh 内置失败 trap 告警（为正式 cron 设计），拿来跑临时调试脚本时——调试中代码报错本属正常，但 trap 一律告警 = 误报。规则：调试/临时脚本走 `python3`，只有正式 cron 走 run_py.sh。同理 `cmd|tee` 也只用于正式 cron。
- **维基成分股表 ticker 点号 vs Yahoo 横杠 → 喂 yfinance 前必做 `.replace(".","-")`**（2026-06-22）：class A/B 股维基写 `CWEN.A` 但 yfinance 要 `CWEN-A`，不转换则每次 404 **静默漏选**（不报错不告警，悄悄漏数据，最阴险）。screener 等用维基 symbol 喂 yfinance 前必做点号转横杠。验证：转换后该 ticker 能查到价。

### Discord API限制
- **Discord Bot reply** → pairing 模式下 reply 工具正常；allowlist 模式导致"channel is not allowlisted"报错，不要切换到 allowlist 模式
- **Discord DM 发送** → 不要用 `/users/@me/channels` 创建新 DM channel（返回400）；直接往已知 channel ID 发消息（`POST /channels/{id}/messages`）
- **Discord plugin v0.0.4 bug（fetchAllowedChannel）** → `ch.recipientId ?? dmChannelUserMap.get(id)` 在 partial DM channel 状态下 `ch.recipientId` 错返 bot 自己 ID，`??` 短路不走 fallback，报 "channel is not allowlisted"。修复：反转为 `dmChannelUserMap.get(id) ?? ch.recipientId`（dmMap 是 inbound 验证过的可靠值）。**plugin 升级后需重新 patch**，备份：`/root/.claude/plugins/cache/.../discord/0.0.4/server.ts.bak_fix`
- **`??` 操作符盲区** → 只在 null/undefined 时 fallback，"错的非空值"会跳过 fallback；当主数据源不可靠时，应改为 `fallback ?? primary` 或加显式校验
- **Discord 机器人显示灰点（离线）≠ 没工作**（2026-06-11）：是插件预期行为，收发消息完全正常。根因：discord 插件 `server.ts` 的 `ready` 回调从未调用 `setPresence/setStatus`（全文件搜 presence/status/online 零命中），且插件用轻量连接不维持完整 gateway presence 心跳 → Discord 服务端判离线显灰点。改绿点：`ready` 回调加 `c.user.setPresence({status:'online'})`。⚠️ 三实例各用各的 server.ts，且 cache 目录已标 `.orphaned_at`，改了可能被插件更新覆盖（需重新 patch）。看到灰点别当掉线排查，先确认消息能否收发。

### Claude Code 诊断方法
- **诊断 plugin/工具执行问题必须先看 session jsonl** → `~/.claude/projects/<cwd>/<sid>.jsonl`，解析 `user/assistant/tool_use/tool_result` 事件流看 Claude 实际做了什么。只看 hook log/server stderr 不看 Claude 行为会反复误判（P11 4次诊断全错的根因，2026-05-09）
- **`--channels plugin:<name>@<marketplace>` 是 plugin channel 订阅开关** → 不带这个参数 host 不会订阅 plugin notification；部署 systemd/守护服务时容易漏（P11 VPS 真根因）。验证：TUI 启动后显示 "Listening for channel messages from: ..." 表示订阅生效

### Claude Code Hook 系统限制
- **Discord中途消息不触发UserPromptSubmit hook** → discord_approve.py 仅在 UserPromptSubmit 阶段扫描输入；Claude 处理过程中主公在 Discord 回复的消息以 system-reminder 形式到达，不触发 hook，task_approved 不会自动创建。解法：主公需在**新消息**里重发一次确认（如"可以执行"）才能让 hook 正常生效。（2026-05-10 收工中发现）

## 系统维护

**三实例 Claude 登录 401 掉线：根因=同账号 refreshToken 互挤**（2026-06-20）[ref-worthy]
- **现象**：某实例对 Discord 消息只回 `Please run /login · API Error: 401 Invalid authentication credentials`，看似卡死，实为登录失效被踢下线。
- **诊断路径**（按此顺序，别凭印象）：
  1. 抓该实例 tmux 末屏看是否反复回 401（AA=默认socket `tmux -S /tmp/tmux-1000/default capture-pane -t cowork -p`；BB=`-S .../opus_socket -t cowork_opus`；CC=opus2_socket/cowork_opus2）
  2. 查凭证文件 `<HOME>/.claude/.credentials.json` 的 `claudeAiOauth.refreshToken` 长度——**空(0 chars)=病根**：accessToken 过期后无法自动续 → 永久 401；正常实例 refreshToken 有 108 chars
- **根因（强推测，未坐实）**：三实例用**同一个 Claude 账号**登录（同 email + 同 accountUuid，`.claude.json` 的 `oauthAccount` 可查）。OAuth refreshToken 会轮换——同账号谁刷新一次就可能让其他实例的旧 refreshToken 作废 → 它们 accessToken 过期后掉线。解释了"只最近登录的活/其余先后掉/重启无效"全现象。**未抓到轮换直接日志**（旧凭证被新登录覆盖无法回溯）。
- **修复**：唯一解=该实例手动 `/login` 重授权（交互式 OAuth+涉凭证，AI 不代操）。步骤：SSH 上 VPS → `tmux [-L socket] attach -t <session>` → 输 `/login` → 复制链接到手机/电脑浏览器授权 → 贴回 code → `Ctrl+b` 再 `d` 安全 detach（别按 Ctrl+C/别直接关窗会杀进程）。
- **关键坑**：①**重启无效**——重启只重读那个残缺凭证文件，缺的 refreshToken 变不出来 ②**别凭欢迎页判断恢复**——启动屏的 "Claude Max" 是缓存账号名，凭证可能仍失效，必须实测一条消息能回才算恢复（见 friction 2026-06-21）。
- 关联：`claude --print`（P4 新闻/P9 脚本）的 401 与此同根，鉴权失效会在三实例间扩散。
- 防复发待评估：独立登录态 / refreshToken 变空·过期前主动告警（不等掉线）。
- [src: 8100a43c]

**"自动化静默失败"是同一类病，要主动堵**（2026-06-21）[ref-worthy]
- "档案断档 9 天没人发现"和"脚本失败无告警会静默坏掉"是**同一种风险根源**：自动化系统出问题时不主动喊，人就不知道
- 解法：每个自动脚本必带崩溃告警（`run_with_alert`）+ 关键流程加"全员失败主动抛异常"（dossier_autowrite.py 已补全）
- 思维要点：从一个断档**联想到所有静默失败**（识别同类病），不止修眼前这一个
- 与 script_standards "崩溃告警"规范同向；审核/复盘时可作检查项

**`#{pane_current_command}` 检测盲点：Claude idle 等待时仍返回 `claude`**（2026-06-22）
- runner watchdog 用 `#{pane_current_command}` 区分 Claude/bash，能处理"Claude 退出到 bash"，但 **Claude idle 等输入时仍返回 `claude`** → 无法区分"活跃处理"和"等待中"
- 已知盲点：**Claude 卡死但进程还活着时，watchdog 不触发**。根治需心跳机制（发探针消息看回复），YAGNI 暂不做
- 看到 watchdog "正常"别等同于"实例在干活"，可能只是进程活着

**评估"自建功能是否被原生取代"必须先抓官方文档**（2026-06-07）[ref-worthy]
- 不能凭印象判断原生功能的能力边界，必须 WebFetch 官方文档确认（是否跨对话/如何写入/有何限制），再与自建实现逐条硬对照。
- 本次教训：第一版凭印象的对照被主公纠正"看表面"，抓文档后多处判断被推翻——Plan模式≠idea持久文档/原生auto-memory三实例各自独立（非跨实例共享）。
- 适用场景：做 cowork 系统减法时、评估是否引入原生工具时、对比自建 vs 平台能力时。
- [src: 1a423ab7]

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

**Hook 减耦合：3 处以上脚本共用同一段逻辑时抽成 CLI 工具**（2026-06-07 实战，2026-06-09 入库）[ref-worthy]
- 案例：system_file_guard / git_commit_guard / discord_approve.py 各自维护"实例推导"逻辑（$HOME→AA/BB/CC），逻辑一变要改 N 处易漏改
- 方案：抽 `token_utils.sh` 暴露 CLI 接口（instance/path/write/check/clear），调用方全部改为 `bash token_utils.sh <action>`
- 效果：改一处=全部同步；新增实例只改一个文件
- 通用原则：hooks/ 下任何"多处共用逻辑"（token、实例推导、路径拼接）≥3 处即抽工具

**Hook 选型原则：提前警示型 > 事后留痕型**（2026-06-04 实战，2026-06-09 入库）
- 对"AI 回答时容易偏的问题类型"（如评级类讨好），用 UserPromptSubmit/PreToolUse 在回答**前**注入警告，比 Stop hook 事后记录有效（伤害已发生才记没意义）
- Stop hook 适合留痕/统计型场景（如推方案词检测）
- 设计新 Hook 第一问："提前防还是事后留痕？"再选类型

**AI 自动判断 + 主公审的二级路由：打分门槛宁低勿高 + 冷启动从严**（2026-05-26 实战，2026-06-09 入库）
- 错放低分=多 1 条送审（成本小）；错放高分=污染正式文件+污染信任（成本大）→ 拿不准就压低分
- 新上线任何 AI 自动决策机制，第 1-2 周阈值设高（如收工打分只 5 分自动写），让主公早期 100% 看到 AI 判断，攒数据后再放宽
- 适用：收工打分、auto_pending 捕获、未来任何"AI 自动写入"机制

**验证带外部副作用的脚本：不实跑**（2026-05-31 实战，2026-06-09 入库）[ref-worthy]
- 脚本最后一步有真实副作用（发 Discord/写外部系统/下单）且无 dry-run 开关时，**禁止为验证逻辑而实跑**
- 替代：`py_compile` 语法检查 + DB 查询模拟核心逻辑（如查询命中数变化）；真实运行留给定时任务自然触发或主公明确授权
- 案例：scanner_tracker 221 行无条件发周报，用模拟验证后等授权才手动触发

**opus 实例撞限额卡交互菜单 → tmux Esc 解锁**（2026-05-28 实战，2026-06-09 入库）
- 症状：systemd active 但 Discord 无回复；`tmux attach` 见 `/rate-limit-options` 菜单停在屏幕
- 修复：`tmux send-keys -t <session> Escape ''` → 菜单关闭，积压消息自动处理
- 根因：高 token 任务耗尽 5h 配额，限额重置后弹菜单等交互输入，无人值守永远卡死
- 诊断顺序：① systemctl status ② tmux attach 看屏幕 ③ .claude.json 时间戳确认进程活着

**Claude Max 配额机制：5 小时滚动窗口 + 全 session 共享**（2026-05-28/29 实测，2026-06-09 入库）
- 配额按 5h 滚动窗口算（非 RPM/TPM）；所有 session（含子 agent）共享同一池
- **开多 session 不增加配额**，只是更快耗光窗口——"加 session 解决配额"是误判
- 自动化/批量使用踩 ToS 边界；重要任务放新对话开头执行

**VPS 3-session 内存基线**（2026-05-28 实测，2026-06-09 入库）
- 每个 Claude Code 完整开销：进程 150-320MB + Discord plugin(bun) 60-75MB + tmux ~5MB ≈ 250-400MB/session
- 2GB VPS 跑 3 session 总 ~1GB，swap 已用 ~500MB；再加 session 上限约 1-2 个
- Mac mini 16GB 理论 25-35 个，真瓶颈是 API 配额非内存

**跨实例诊断/操作两条铁律**（2026-05-29 实战，2026-06-09 入库）[ref-worthy]
- ① 跨实例查/操作 tmux 必须先 `TMUX= ` 清空环境变量：session 内跑裸 tmux 会被 $TMUX 重定向到自己 socket，看不到别实例 → 误判"对方死了/无 pane"（两实例先后踩同坑，曾产出假 bug 报告）
- ② 下结论前先确认对方任务状态（spinner/最新输出/是否已回 Discord），别用中途快照判"在打转"——曾据中途画面发错纠偏消息，对方实际已自行得出更准结论

**hermes-agent 是 Agent 框架不是本地模型**（2026-06-02 实读 GitHub 纠正）
- github.com/NousResearch/hermes-agent = Nous Research 开源 AI Agent 框架（Python/MIT），**不是**旧记忆误记的"Nous Hermes 本地模型"
- cowork ≈ hermes 理念的手搓定制版（4 月借鉴而建）；区别=hermes 是模型无关通用框架，cowork 长在 Claude Code 里为主公定制
- 下次问 hermes 用此条，别再凭 4 月自相矛盾的旧记忆

**Claude Code CLI 无 sudo 升级方式**（2026-06-09）
- `npm install -g --prefix ~/.local @anthropic-ai/claude-code@latest` 装到用户目录（~/.local/bin/）
- 再把 runner 脚本 CLAUDE_BIN 指向新路径；用户目录 PATH 排在 /usr/bin 前所以优先生效

**加字段/改输出后必须实跑验证"字段真填上"**（2026-06-08 实战，2026-06-09 入库）
- "跑了没崩"≠"字段有值"：MBTI 字段加完不报错但全空(0/7)，因 parse_json 误抓内嵌数组
- 任何"加字段→跑→以为成功"场景，验证标准=抽查输出里新字段非空率，不是无报错

---

## AI 项目评估与验证方法

**AI 当杠杆 vs AI 自主：可行性第一问**（2026-05-26 入库 2026-06-09）[ref-worthy]
- "AI 无监督自主赚钱"做不到（①不能主动发起 ②长任务幻觉 ③收款/合规/客户关系需真人）；能赚钱的是"AI 当主公判断力的杠杆"
- 评估任何 AI 项目先问：是"无监督自主"还是"杠杆放大"？前者基本不可行
- 配套评估法：**输入侧 vs 输出侧分维打分**——输入侧（规划/系统化/自动化数量）vs 输出侧（PR/收入/Reality Check 完成度）；输入高+输出低=高级拖延。首次应用 5/28：输入 8/10 输出 3/10 → 暴露 P12 落地缺口

**可验证"玄学/直觉"信号的实验设计三件套**（2026-06-01 P9 梅花易数实战，commit e91d357）[ref-worthy]
- ① 杀掉随机性做到 100% 可复现（同输入永远同输出，禁临场解读）② 同时记一个随机对照分（hash 映射同区间），真信号必须跑赢随机对照 ③ 先隔离只记录不参与决策，攒 1-2 季度样本后用真实结果验证
- 验证别只看 hit rate：要看分组收益、IC、t 检验/bootstrap 置信区间；分数过于离散会削弱统计力 → 加正交维度拉散分布
- **隔离观察列代码模式**：算分逻辑独立模块 / 写入处 try-except 包住算不出留空不阻断主流程 / grep 验证新字段只出现在 import+写库两处不进决策逻辑 / playbook 写明"改决策逻辑别读这些列"
- 适用：任何"我觉得 X 可能有用但不确定"的因子，低风险验证而不是直接信或直接否

**预测引擎对外结果必带定位免责**（2026-06-08 实战，2026-06-09 入库）
- 每次用 prediction_engine 对外给结果时必带一句："这是机制推演沙盘，不是基于今日数据的实时预测；角色编的具体数字是 roleplay 非真数据"
- 目的：避免把模拟数字当真。详见 `reference/prediction_method.md` 铁律七

**检查清单/评分系统必须用 hard negative 测特异性**（2026-06-10 趋势手册实战，2026-06-12 入库）[ref-worthy]
- 验证打分清单不能只用"明显赢家+明显泡沫"做考题（太简单必然全对）；必须找"**信号全亮但结局崩盘**"的硬对照组实测拦截率——趋势手册 v1.0 实锤：ZIM/Zoom/Moderna 摊牌信号全亮、五维清单 0/3 拦截、事后 -75~90%，由此补出第⑥维"利润来源分解（量 vs 价）"
- 回测打分只准用"决策日当天可知的信息"（引用来源出版日期 ≤ 决策日），禁止后见数据——否则回测分数虚高=实盘亏损来源
- 自产方法论/规则文档发布前，派独立 agent 对抗性审核（作者自审有立场盲区；两轮审核比一轮多抓出保命线未压测/起点漂移/编造胜率三个问题）
- 适用：任何评分/筛选/清单系统（P9 评分、趋势清单、未来 agent 评审）

**LLM 评分维度所需数据必须在输入里，拿不到的维度禁止让 LLM"猜"**（2026-06-10 P9 实锤）[ref-worthy]
- 实锤：prompt 要求 LLM 按"分析师覆盖少"打 market_lag 分，但**没把覆盖数喂进输入** → 32 个标的全打 9-11 分（分是编的）；6/10 补真实数据后发现 15 只持仓覆盖 5-11 个、无一冷门 = 分数纯属臆造
- 病根：LLM 拿不到某维度数据时不会说"我不知道"，而是从字里行间脑补一个看似合理的分 → 评分系统被污染却无报错
- 规则：① 评分维度所需的硬数据必须出现在 LLM 输入里；② 拿不到数据的维度，改用程序算分或留空，**禁止让 LLM 从文本里猜**；③ 上线后抽查分数分布，全员同档（如全 9-11）是"在编分"的信号
- 适用：任何 LLM 评分/筛选/评审系统（P9、趋势主线、未来 agent）

**让 AI 定期读档案做复盘，绕开"人不回看"的惰性**（2026-06-20，主公明确认可）[ref-worthy]
- 任何"追踪/留痕"类系统的真实价值都在"回看复盘"，而人天然惰性不回看 → 档案堆着等于白记
- 解法：让 AI 定期（cron）自动读结构化档案 + 分析 + 推送，把"复盘"从"靠人自觉"变成"系统强制"（趋势追踪档案 dossier_weekly.py 即按此设计）
- 跨项目通用：法律追踪 / 客户开发 / 项目复盘都适用
- 与"写时扫描"（[[feedback_write_triggers_scan]]）互补但角度不同：那条是写时扫，这条是定期主动读

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

**SQLite 存向量做语义搜索：cosine 必须 numpy 批量，禁止 python 逐条循环**（2026-06-10）[ref-worthy]
- 教训源头：cowork.db 对话搜索 `search_conversations.py` 原用 python `for` 循环逐条算 cosine，10920 条消息向量耗时 **3 秒**且随数据量线性增长；换 numpy 矩阵运算后降到 **<0.1 秒**（约 30 倍）
- 改法：`np.frombuffer(b"".join(blobs), dtype=np.float32).reshape(n, -1)` 一次性读全部 blob → `mat @ q` 矩阵乘 + `np.linalg.norm(axis=1)` 批量算分母，避免逐条 python 浮点循环
- embedding 用 `struct.pack("{n}f")` 存的 float32 blob，与 `np.frombuffer(dtype=np.float32)` 完全兼容，无需改存储格式
- 验证方法（改算法必做）：同一 query 向量，新旧两套逐条对比相似度，最大差值 < 1e-4 即纯浮点误差 = 结果一致（本次实测 1.55e-07）
- **架构判断（防过度工程）**：1 万条量级用 **SQLite + numpy 手算**完全够（毫秒级），不需要上 Milvus/向量数据库——Milvus 是十万条以上才有价值，小规模上它只增加一个要维护的服务。工业级 RAG 图（Milvus+reranker+文档转MD+LLM生成）对"对话记忆检索"这种小规模场景多数是过度工程，唯一普适可借鉴的是"向量计算别用慢算法"
- 剩余瓶颈：query embedding 的 API 网络往返（Voyage ~10s）才是大头，本地计算优化后想再快得靠 query 向量缓存

---

## P9 TIDE 量化系统

**OPG 单实测 fill 率（2026-05-19 基准）**
Alpaca paper account OPG 单实测 fill 率约 17%（1/6，5/19 首次自动扫描）。Gap up 超 limit 价时 Alpaca 自动作废订单。
- 15 只满载 × 17% ≈ 每次扫描成交 2-3 只
- buying_power 长期闲置，sample 累积慢（一年约 8-12 个数据点）
- Q3（8/4）扫描预期 2-3 只成交，不要期待满载
适用：评估 P9 sample 累积速度、讨论是否调整 limit 价策略时参考此基准

**OPG 订单"expired"状态可能含部分成交 → 对账必查 filled_qty**（2026-06-10 P9 实锤）[ref-worthy]
- Alpaca OPG 单开盘竞价只成交一部分时，订单**终态仍是 expired 但 filled_qty>0、持仓真实存在**（实例：GNTX 97/132、WTS 9/10）
- 陷阱：对账逻辑只看 `order.status` 会判"未成交"→ 漏掉真实持仓 → 幽灵持仓家族复发根源之一
- 规则：① 任何订单级对账必须同时检查 `filled_qty`，不能只看 status；② 更稳的是**持仓级对账**——定期比对 Alpaca `/positions` vs DB 持仓清单（以 broker 为准）
- 适用：任何依赖订单状态判断成交的对账/同步逻辑

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

---

## Alpine IQ (AIQ) API 认证踩坑（2026-06-04 最终确认）

**正确认证方式（唯一有效）：**
```python
headers = {"x-apikey": API_KEY}  # 全小写，无连字符
```

**无效写法（全部返回 403）：**
- `Authorization: Bearer {key}`、`Authorization: {key}`
- `X-API-Key: {key}`、`x-api-key: {key}`
- query string `?api_key=` / `?key=` / `?apiKey=`

**端点格式：** `https://lab.alpineiq.com/api/v1.1/{endpoint}/{UID}`

**Sage Seeds 凭证：** UID=4757，env 在 `/home/cowork/sage_seeds/aiq/aiq.env`

**可用端点（实测 200）：**
- `GET /piis/{uid}` — 搜索客户
- `GET /stores/{uid}` — 门店列表
- `GET /audiences/{uid}` — 所有受众群体（含 audienceSize）
- `GET /conversions/{uid}` — 所有营销转化记录
- `GET /contact/orders/{uid}/{contactID}` — 单客户订单历史
- `GET /contact/loyaltyPoints/timeline/{uid}/{contactID}` — 积分时间线

**Sage Seeds 数据概览（2026-06-04）：** 1 家门店 / 8,516 会员 / 35 个受众群体 / 4,568 条转化记录

**踩坑历史：** 2026-05-29 两次诊断均错误，误以为是 Bearer 格式或账号权限问题。真正原因：AIQ header 名称非标准，用 `x-apikey` 而非 `Authorization`。

---

**yfinance 单 ticker `history['Close']` 返回 DataFrame 不是 Series（2026-06-03）**[ref-worthy]
- `yf.download('AAPL')` 后 `history['Close']` 是 DataFrame（列名=ticker），不是 Series
- 直接 `.items()` 遍历得到列名字符串，下游 `.strftime()` 报 `'str' has no attribute 'strftime'`
- 修法：取出后加守卫 `if hasattr(closes, "columns"): closes = closes.iloc[:, 0]` 还原 Series
- 适用所有 P9 单票取价脚本（post_exit_tracker / price_tracker），新写取价逻辑直接套此守卫
- [src: 332a722a]

---

**官方 knowledge-work-plugins 方法论参考库（2026-06-07）**[ref-worthy]
- Anthropic 官方开源职能插件（19.5k★）的 skill 方法论已扒成参考库：`reference/official_plugins/`（16插件/140 skill）
- **纯参考，未安装未配置**：官方连接器(HubSpot/Klaviyo等)我们没连，Alpine IQ 也不在其中 → 不能即插即用，只借方法论/输出模板
- 用法：主公做相关工作时主动提醒读对应 .md（触发点见 `official_plugins/INDEX.md`）；高相关=marketing/legal/data/sales/small-business
- 需 skill 完整 Body → 抓 `github.com/anthropics/knowledge-work-plugins/blob/main/<插件>/skills/<skill>/SKILL.md`
- **总入口**：`reference/methodology_index.md` 把官方(official)+自有 skill_archives(self)+外部(external)统一索引，一页看全所有按需调用方法论；新增方法论必带「来源+日期+类型」出处三字段

---

**VPS 三实例重启正确方式：杀 tmux session，不杀 runner（2026-06-09）**[ref-worthy]
- **错误做法**：`kill <runner_PID>`（SIGTERM）→ runner 干净退出 → systemd `Restart=on-failure` 不触发（只对非 TERM 信号）→ 服务变 `inactive (dead)`，需手动再起
- **正确做法**：`tmux -L <socket> kill-server`（或 `kill-session`）→ tmux session 消失 → runner while-true 循环探测 session 不在 → 自动起新 session（15秒内完成）→ runner 进程保持存活，systemd 层完全不感知
- **适用场景**：想让某实例加载新 settings.json（改了 model/plugin 后需重启）
- **实例对照**：
  - AA（cowork）：`tmux kill-session -t cowork`
  - BB（opus）：`tmux -L opus_socket kill-server`
  - CC（opus2）：`tmux -L opus2_socket kill-server`
- **runner 路径**：`cowork/scripts/claude_runner.sh` / `claude_opus_runner.sh` / `claude_opus2_runner.sh`
