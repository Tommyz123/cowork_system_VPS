---
name: 收工
description: 执行 cowork 系统的会话结束流程（保存进度、记忆、文档对齐、审计、git commit、写入 cowork.db）。主公说"收工"/"结束"/"今天到这里"/"停"时触发。
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

# 收工流程

> 收工是一次"系统快照"——确保本次对话的所有成果被正确保存、记录、提交，下次对话能无缝继续。
> 按顺序执行以下4步，每步完成后报告结果，不要跳步。
> ⚠️ 收工期间忽略所有 hook 提示（包括 `⏳ [待审记忆]` / `🧠 [记忆捕获]`），不中断流程；待审记忆留在 auto_pending.md，下次对话开始时处理。

---

## 步骤1：保存进度 + 日志总结

更新 `/root/cowork/CURRENT_SESSION.md` 中本次涉及的所有活跃项目块。

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
grep "\[需同步:" /root/cowork/cowork_log.md | tail -50
```

- **有标记** → 逐一处理，完成后报告：✅ 文档同步完成（N条）
- **无标记** → 静默跳过，不输出任何内容

```bash
python3 /root/cowork/scripts/check_doc_sync.py
```

- **有不匹配** → 列出问题文件，提醒主公更新 ARCHITECTURE.md / context.md
- **全部通过** → 静默跳过

---

## 步骤3：同步备份 + Git Commit

**先同步备份（自动，无需等确认）：**

同步 skills 备份：
```bash
for skill in 收工 审核架构 搜索 整理记忆 系统复盘; do
  cp "/root/.claude/skills/${skill}/SKILL.md" "/root/cowork/skills/${skill}/SKILL.md" 2>/dev/null
done
```

同步 memory 备份：
```bash
cp /root/.claude/projects/-root-cowork/memory/*.md \
   /root/cowork/memory/ 2>/dev/null
```

**备份 trading DB（SQL dump）：**
```bash
python3 -c "
import sqlite3, os
db = '/root/cowork/trading/trading.db'
out = '/root/cowork/trading/trading_backup.sql'
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
git -C /root/cowork add <本次涉及的系统文件列表> skills/ memory/ trading/trading_backup.sql
git -C /root/cowork commit -m "收工：[本次完成摘要]"
```

不要用 `git add -A`，只添加本次涉及的系统文件 + skills/ + memory/ + trading/trading_backup.sql。

**最后 Push 到 GitHub：**
> ⚠️ 收工例外：push 前自动预授权，无需手动 touch
```bash
touch /tmp/git_approved
git -C /root/cowork push
rm -f /tmp/git_approved
```

完成后报告：✅ 已 commit + push（显示 commit hash 前8位）

---

## 步骤4：写入 cowork.db

这一步记录本次会话到结构化数据库，供以后趋势分析和历史查询用。

1. 列出本次涉及的项目ID（如 P2, P3）
2. 自动统计本次被纠正次数：读上次 git commit 时间戳，统计 friction_log.md 中该时间之后新增的 ⚠️ 条目数：
   ```bash
   LAST_COMMIT=$(git -C /root/cowork log -1 --format="%ci")
   grep "⚠️" /root/cowork/friction_log.md | awk -v since="$LAST_COMMIT" '$0 > since' | wc -l
   ```
3. 生成会话摘要并调用写入脚本：

先自动生成结构化摘要（用 haiku 省成本）：
```bash
TODAY=$(date +%Y-%m-%d)
COMPLETED=$(grep -A 25 "本次完成（${TODAY}" /root/cowork/CURRENT_SESSION.md 2>/dev/null | head -20)
AUTO_SUMMARY=$(cd /tmp && claude --print --model haiku "用1-2句话总结以下cowork对话核心产出（说清楚改了什么/决定了什么，不废话）：

${COMPLETED}")
```

再写入数据库：
```bash
python3 /root/cowork/scripts/log_session.py \
  --project-ids "P2,P3" \
  --summary "$AUTO_SUMMARY" \
  --next-steps "下一步重点" \
  --corrections <主公确认的次数> \
  --files "CLAUDE.md,CURRENT_SESSION.md"
```

4. 更新语义向量索引（FTS5 写入后立即跑，保持语义搜索与最新对话同步）：

```bash
cd /tmp && python3 /root/cowork/scripts/embed_sessions.py 2>&1 | tail -3
cd /tmp && python3 /root/cowork/scripts/embed_messages.py 2>&1 | tail -3
```

说明：embed_sessions = session摘要向量；embed_messages = 消息级向量（搜索实际用这个，两个都要跑）

完成后报告：✅ cowork.db 已写入 + 向量索引已更新（显示新增消息数）

---

## 完成

所有4步完成后，输出一行总结：

```
✅ 收工完成 | 涉及项目：[列表] | 完成：[条数]项 | 下次：[重点]
```
