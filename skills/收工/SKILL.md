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

### 5.3 写入 review_drafts.md

把所有发现整理，追加到 `/home/cowork/cowork/reference/review_drafts.md`：

格式：
```markdown
## [草稿] YYYY-MM-DD 深度审核

### INSIGHTS 建议写入（N条）
1. [标题] → 内容 [src:session_xxx]
2. ...

### 操作记录 建议起草（N份）
- 主题：XXX
- 背景：...
- 建议文件名：reference/xxx_log.md

### Friction 建议补记（N条）
- ...

### Playbook 建议更新（N处）
- playbooks/XXX.md：具体改什么

### 文档对齐待处理（N处）
- ARCHITECTURE.md：...
```

若某类别无内容 → 该小节不写，保持草稿简洁。

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

### 5.5 发 Discord 通知

无论有无草稿，收工完成时通过 mcp__plugin_discord_discord__reply 发送：

```
✅ 深度审核完成 | YYYY-MM-DD
- 审核 session：N个
- INSIGHTS草稿：N条
- 操作记录建议：N份
- Playbook更新：N处
- 文档对齐：N处
→ 草稿存入 reference/review_drafts.md，明天来了第一件事展示给你决策
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
