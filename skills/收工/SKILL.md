---
name: 收工
description: 执行 cowork 系统的会话结束流程（保存进度、文档同步、备份提交、DB写入、深度审核）。主公说"收工"/"结束"/"今天到这里"/"停"时触发。
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

# 收工流程

> 收工是一次"系统快照 + 深度整合"——确保本次对话的所有成果被正确保存、记录、提交，同时对今天所有对话进行深度审核，整理草稿等主公次日决策。
> 按顺序执行以下6步，每步完成后报告结果，不要跳步。
> ⚠️ 收工期间忽略所有 hook 提示（包括 `⏳ [待审记忆]` / `🧠 [记忆捕获]`），不中断流程；待审记忆留在 auto_pending.md，下次对话开始时处理。

---

## 步骤1：保存进度 + 日志总结

更新 `/home/cowork/cowork/CURRENT_SESSION.md` 中本次涉及的所有活跃项目块。

每个项目块格式：
```
### [PX] 项目名
状态：（描述当前状态）
last_updated: YYYY-MM-DD
停在：（具体停在哪里）
本次完成（YYYY-MM-DD）：
- 条目1
- 条目2
下一步：
- 重点下一步
路径：（项目路径）
```

完成后在 `cowork_log.md` 末尾追加会话总结：

```
--- 📋 会话总结 ---
本次完成：[简述]
文件变动：[列出核心文件]
下次继续：[下一步重点]
---
```

**BACKLOG 决策检查：**
回顾本次对话，有没有明确决定了某条 BACKLOG 条目的走向（做/不做/改触发条件/改策略）？
- 有 → 在 BACKLOG.md 对应条目下追加一行：`→ [决定 YYYY-MM-DD]：结论一句话`
- 无 → 跳过，不输出任何内容

**"暂不做"二选一强制规则（2026-05-12）：**
任何"暂不做"决策必须当场追问主公归类，禁止留在"🔜 下次对话做"区块：
- 🟡 **缓做**（明确触发条件下会做）→ 移到 "⏳ 等触发条件" 区块，必须写明触发条件
- 🔴 **砍掉**（不会再做）→ 直接从 BACKLOG.md 删除（git history 可追溯）

依据：`memory/feedback_backlog_format.md` "暂不做必须二选一规则"
违规反例：Discord Webhook 配置条目（2026-05-02 决定暂不做但留在"下次对话做"区块7天，2026-05-12 处理）

完成后报告：✅ 进度已保存 + 日志已追加（列出更新了哪些项目）

---

## 步骤2：文档同步检查（静默）

```bash
grep "\[需同步:" /home/cowork/cowork/cowork_log.md | tail -50
```

- **有标记** → 逐一处理，完成后报告：✅ 文档同步完成（N条）
- **无标记** → 静默跳过，不输出任何内容

```bash
python3 /home/cowork/cowork/scripts/check_doc_sync.py
```

- **有不匹配** → 列出问题文件，提醒主公更新 ARCHITECTURE.md / context.md
- **全部通过** → 静默跳过

---

## 步骤3：同步备份 + Git Commit

**先同步备份（自动，无需等确认）：**

同步 skills 备份：
```bash
for skill in 收工 审核架构 搜索 整理记忆 系统复盘; do
  cp "/home/cowork/.claude/skills/${skill}/SKILL.md" "/home/cowork/cowork/skills/${skill}/SKILL.md" 2>/dev/null
done
```

同步 memory 备份：
```bash
cp /home/cowork/.claude/projects/-home-cowork-cowork/memory/*.md \
   /home/cowork/cowork/memory/ 2>/dev/null
```

**备份 trading DB（SQL dump）：**
```bash
python3 -c "
import sqlite3, os
db = '/home/cowork/cowork/trading/trading.db'
out = '/home/cowork/cowork/trading/trading_backup.sql'
if os.path.exists(db):
    conn = sqlite3.connect(db)
    with open(out, 'w') as f:
        for line in conn.iterdump(): f.write(line + '\n')
    conn.close()
"
```

**再 Git Commit（包含 skills/ 和 memory/ 和 trading backup）：**
> ⚠️ 收工例外：此 commit 无需向主公确认，直接执行（CLAUDE.md 明确豁免：「收工流程中的 commit 由收工 Skill 统一处理，无需额外确认」）

```bash
git -C /home/cowork/cowork add <本次涉及的系统文件列表> skills/ memory/ trading/trading_backup.sql reference/review_drafts.md reference/deep_reviewed_sessions.json
git -C /home/cowork/cowork commit -m "收工：[本次完成摘要]"
```

不要用 `git add -A`，只添加本次涉及的系统文件 + skills/ + memory/ + trading/trading_backup.sql + reference/ 草稿文件。

**最后 Push 到 GitHub：**
> ⚠️ 收工例外：push 前自动预授权，无需手动 touch
```bash
touch /tmp/git_approved
git -C /home/cowork/cowork push
rm -f /tmp/git_approved
```

完成后报告：✅ 已 commit + push（显示 commit hash 前8位）

---

## 步骤4：写入 cowork.db

这一步记录本次会话到结构化数据库，供以后趋势分析和历史查询用。

1. 列出本次涉及的项目ID（如 P2, P3）
2. 自动统计本次被纠正次数：
   ```bash
   LAST_COMMIT=$(git -C /home/cowork/cowork log -1 --format="%ci")
   grep "⚠️" /home/cowork/cowork/friction_log.md | awk -v since="$LAST_COMMIT" '$0 > since' | wc -l
   ```
3. 生成会话摘要并写入数据库：

```bash
TODAY=$(date +%Y-%m-%d)
COMPLETED=$(grep -A 25 "本次完成（${TODAY}" /home/cowork/cowork/CURRENT_SESSION.md 2>/dev/null | head -20)
AUTO_SUMMARY=$(cd /tmp && claude --print --model haiku "用1-2句话总结以下cowork对话核心产出（说清楚改了什么/决定了什么，不废话）：

${COMPLETED}")
```

```bash
python3 /home/cowork/cowork/scripts/log_session.py \
  --project-ids "P2,P3" \
  --summary "$AUTO_SUMMARY" \
  --next-steps "下一步重点" \
  --corrections <本次被纠正次数> \
  --files "CLAUDE.md,CURRENT_SESSION.md"
```

完成后报告：✅ cowork.db 会话记录已写入

---

## 步骤5：深度审核（生成草稿）

这一步审核今天所有未处理的对话，把发现整理成草稿，**不直接写入正式文件**，存入 `reference/review_drafts.md` 等主公次日决策。

### 5.1 找今天未审核的 session

读取已处理列表：
```bash
python3 -c "
import json
try:
    data = json.load(open('/home/cowork/cowork/reference/deep_reviewed_sessions.json'))
    reviewed = [d['session_id'] for d in data]
    print('\n'.join(reviewed))
except: print('')
"
```

查询今天所有 session：
```bash
TODAY=$(date +%Y-%m-%d)
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/cowork/cowork/cowork.db')
rows = conn.execute(\"SELECT DISTINCT session_id FROM conversations WHERE date=?\", ('$TODAY',)).fetchall()
for r in rows: print(r[0])
conn.close()
"
```

排除已审核的 session_id，得到待审核列表。若列表为空 → 报告"今天无新 session 待审核"，跳至步骤5.5。

### 5.2 逐 session 读取并分析

对每个待审核 session，分批读取对话内容：
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/cowork/cowork/cowork.db')
rows = conn.execute('SELECT role, content FROM conversations WHERE session_id=? ORDER BY timestamp', ('<SESSION_ID>',)).fetchall()
for role, content in rows:
    print(f'[{role}] {content[:800]}')
    print('---')
conn.close()
"
```

读取后，**in-context 分析**（我自己判断，不靠脚本）：

**A. INSIGHTS 提炼**
- 先读现有 `/home/cowork/cowork/INSIGHTS.md`，检查是否已有 `[src:<session_id>]` 标记
- 新发现值得记的内容 → 草拟条目，加 `[src:<session_id>]`
- 内容够写成完整参考/操作文档的 → 加 `[ref-worthy]`

**B. 操作记录判断**
该 session 是否涉及：多步骤操作 + 踩过坑 + 有明确完成状态？
→ 是 → 草拟操作记录标题 + 结构大纲（不起草全文）

**C. Friction 检查**
有没有被纠正/踩坑未记录在 `friction_log.md` 的？→ 记录摘要

**D. Playbook 更新检查**
这次工作影响了 `playbooks/` 里的命令/路径/流程？→ 列出建议更新点

**E. 文档对齐检查**
有影响 ARCHITECTURE.md / context.md 的改动？→ 列出具体同步点

**F. MEMORY.md 废弃检查**
读 `/home/cowork/.claude/projects/-home-cowork-cowork/memory/MEMORY.md`，逐条扫描：
- 有无已标注"废弃/停用"的条目（如某 reference_*.md 标注了"已废弃/停用"）
- 有无项目已从 CURRENT_SESSION.md 活跃列表完全退出但 memory 条目仍留着的冗余项
→ 有发现 → 列入 review_drafts.md 草稿「建议清理」，主公确认后才删
→ 无发现 → 静默跳过

### 5.2.1 重要性评分（2026-05-26 上线 · 抗堆积机制）

对 A/B/C/D/E/F 每项候选，按以下 5 分制打分。**根据分数自动路由**——避免低价值草稿堆积浪费主公审核精力。

| 分数 | 标准 | 路由 |
|---|---|---|
| **5** | 跨项目通用 + 有真实痛点数据（friction_log / bug 实测 / 反复触发）+ 完整规则可写 | ✅ **自动写入正式文件** |
| **4** | 跨项目通用 + 有具体场景（≥2 次类似事件 或 主公明确说过）| ✅ **自动写入正式文件** |
| 3 | 单项目 specific + 有价值 + 第一次发现 | 📝 进 review_drafts 送审 |
| 2 | 低 confidence 但可能有用 | 📝 进 review_drafts 送审 |
| 1 | 可有可无 / AI 自己觉得"好像"值得但没具体场景 | 🗑️ **直接丢，不写** |

**打分原则**：
- **宁低勿高** → 错放低=多 1 条送审；错放高=污染正式文件，污染信任
- 不确定时**取低**
- 跨项目通用判断标准：换成另一个项目（如 P12 替换 P9）规则还能直接用 → 跨项目；不能 → 单项目
- 完整规则可写标准：能写出 "Why + How to apply + 适用场景" 三段 → 完整；只有现象描述 → 不完整

**冷启动期保守**：
- 上线第 1-2 周，**门槛设高**：只 5 分自动写，4 分也送审
- 收集 1-2 周主公审核反馈后，**评估是否放宽到 4 分自动写**

### 5.3 路由：分数决定走向

**4-5 分（自动写入正式文件）**：
| 类型 | 写入位置 |
|---|---|
| INSIGHTS（[ref-worthy]）| `reference/knowledge_base.md` 对应章节 |
| INSIGHTS（普通）| `INSIGHTS.md` |
| Friction（已闭环）| `friction_log_archive.md` 新批次 |
| Friction（未闭环）| `friction_log.md` |
| Playbook 更新 | 直接修改对应 `playbooks/<name>.md` |
| 文档对齐 | 直接修改 `ARCHITECTURE.md` / `context.md` |

写入后必须在 `cowork_log.md` 单独记一行：
`[YYYY-MM-DD HH:MM] 🤖自动写入 | [评分:5] 类型 | 内容摘要 | 写入位置`

**2-3 分（送审）**：
进 review_drafts.md，沿用现有逻辑（见 5.3 原格式）。**每条标注分数**让主公一眼看 AI 怎么判断。

**1 分（丢弃）**：
不写。在 cowork_log.md 注明：`[YYYY-MM-DD HH:MM] 🗑️丢弃 | N 条候选被 AI 自判 1 分丢弃`（不展开内容，省 token）

### 5.3 写入 review_drafts.md（仅 2-3 分候选）

把所有发现整理，追加到 `/home/cowork/cowork/reference/review_drafts.md`：

格式（**每条必须标分数**）：
```markdown
## [草稿] YYYY-MM-DD 深度审核

### INSIGHTS 建议写入（N条）
1. **[评分:3]** [标题] → 内容 [src:session_xxx]
2. **[评分:2]** [标题] → 内容 [src:session_xxx]

### 操作记录 建议起草（N份）
- **[评分:2]** 主题：XXX / 背景：... / 建议文件名：reference/xxx_log.md

### Friction 建议补记（N条）
- **[评分:3]** ...

### Playbook 建议更新（N处）
- **[评分:3]** playbooks/XXX.md：具体改什么

### 文档对齐待处理（N处）
- **[评分:3]** ARCHITECTURE.md：...

### MEMORY.md 建议清理（N条）
- **[评分:3]** 建议删除：xxx.md（原因：项目已废弃/条目冗余/已内化）

---

### 🤖 本次自动写入摘要（4-5 分，已直接写入正式文件）
- **[评分:5]** [类型] [标题] → 已写入 [位置]
- **[评分:4]** [类型] [标题] → 已写入 [位置]

### 🗑️ 本次自动丢弃摘要（1 分，未保留）
- 共 N 条 1 分候选被 AI 自判低价值丢弃（详细内容不展开，省 token）
```

若某类别无内容 → 该小节不写，保持草稿简洁。

**摘要的关键作用**：让主公一眼看到「自动写了什么 / 自动丢了多少」，发现 AI 打分不合理可立即在 Discord 反馈，触发回滚 + 调整评分标准。

### 5.4 更新 deep_reviewed_sessions.json

所有分析和草稿写入完成后，再更新标记文件（失败就不更新，下次重新审核）：

```bash
python3 -c "
import json, datetime
path = '/home/cowork/cowork/reference/deep_reviewed_sessions.json'
try: data = json.load(open(path))
except: data = []
new_sessions = ['SESSION_ID_1', 'SESSION_ID_2']
today = '$(date +%Y-%m-%d)'
for sid in new_sessions:
    if not any(d['session_id'] == sid for d in data):
        data.append({'session_id': sid, 'reviewed_at': datetime.datetime.now().isoformat(), 'date': today})
json.dump(data, open(path, 'w'), ensure_ascii=False, indent=2)
print(f'已标记 {len(new_sessions)} 个 session 为已审核')
"
```

### 5.5 发 Discord 通知 + 写入 ops_log

无论有无草稿，收工完成时通过 mcp__plugin_discord_discord__reply 发送：

```
✅ 深度审核完成 | YYYY-MM-DD
- 审核 session：N个
- 🤖 自动写入（4-5 分）：N 条 → 已直接写入正式文件
- 📝 送审草稿（2-3 分）：N 条 → 存 review_drafts.md
- 🗑️ 自动丢弃（1 分）：N 条
→ 草稿存入 reference/review_drafts.md，明天第一件事展示给你决策
→ 自动写入的 N 条详见 cowork_log.md "🤖自动写入" 行；觉得有错立即说，我回滚
```

写入 ops_log：
```bash
NOW=$(TZ="America/New_York" date "+%Y-%m-%d %H:%M EDT")
PROJECTS="[本次涉及项目列表]"
echo "[$NOW] SKILL[SYS] | 收工 | ✅ | 项目:$PROJECTS commit:[hash前8位] 草稿:[N条]" >> /home/cowork/cowork/ops_log.md
```

完成后报告：✅ 深度审核完成 + 草稿已存

---

## 步骤6：更新索引（最后跑）

所有写入完成后，更新搜索索引：

```bash
cd /tmp && python3 /home/cowork/cowork/scripts/index_conversations.py 2>&1 | tail -3
cd /tmp && python3 /home/cowork/cowork/scripts/embed_sessions.py 2>&1 | tail -3
cd /tmp && python3 /home/cowork/cowork/scripts/embed_messages.py 2>&1 | tail -3
```

完成后报告：✅ 索引已更新（显示新增消息数）

---

## 完成

所有6步完成后，输出一行总结：

```
✅ 收工完成 | 涉及项目：[列表] | 完成：[条数]项 | 草稿：[N条等待明日决策] | 下次：[重点]
```
