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

---

## WSL 启动 Windows 程序
- ❌ 错误：`cmd.exe /c start "程序路径"` → WSL 找不到 cmd.exe
- ✅ 正确：`/mnt/c/Windows/System32/cmd.exe /c start "" "C:\Program Files\程序名\程序.exe"`
- 适用：TeamViewer、任何 Windows 原生程序
