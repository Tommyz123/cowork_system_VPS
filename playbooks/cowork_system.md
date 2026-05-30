---
name: cowork_system
description: Cowork AI 系统维护：规则优化、文件管理、架构升级、收工流程
triggers: [cowork, 系统维护, 系统优化, CLAUDE.md, 规则, 架构, 收工, cowork_system]
working_dir: C:\Users\zhi89\Desktop\cowork\
status: active
---

# Playbook: Cowork 系统维护

> 工作目录：`C:\Users\zhi89\Desktop\cowork\`
> 规则文件（不重复）：`CLAUDE.md`、`ARCHITECTURE.md`

---

## 启动序列（维护 Cowork 系统时必做）

1. 读 `ARCHITECTURE.md` — 理解系统结构
2. 读 `context.md` — 了解当前文件布局和项目状态
3. 明确本次维护任务

---

## 典型工作流：新增授权文件夹

```
1. 主公授权新文件夹
2. 扫描文件夹内容，了解用途
3. 在 context.md 新增文件夹区块（含标签、用途、状态、关键文件）
4. 在 ARCHITECTURE.md 相关区块更新
5. 在 CURRENT_SESSION.md 新增项目进度块
6. 在 playbooks/ 新建对应 playbook 文件（必须，不可省略）
7. 写入 cowork_log.md
```

---

## 典型工作流：系统规则优化

```
1. 读 friction_log.md，了解积压问题
2. 分析问题根因（规则模糊/冲突/缺失）
3. 提出修改方案（改哪个文件、改哪段）
4. 等主公确认
5. 执行修改
6. 在 friction_log.md 追加处理结果
```

---

## 典型工作流：会话收工

```
1. 保存进度：对本次涉及的所有活跃项目更新 CURRENT_SESSION.md + 记日志
2. 主动记忆：判断有无值得写入 memory/ 的内容，有则写入并更新 MEMORY.md 索引
   （若本次已执行"整理记忆"则跳过此步）
3. 文档对齐：检查 context.md 和 ARCHITECTURE.md 是否需要同步，有变动则更新
4. 审计：cowork_log.md 有无漏记，输出 ✅ 无漏项 / ⚠️ 发现漏项
5. 检查本次 friction_log.md 新增记录
6. 在 cowork_log.md 追加：--- 📋 会话总结 --- 本次完成/文件变动/本次摩擦/下次继续 ---
7. commit：将本次更新的系统文件 commit 到 cowork_system repo
```

---

## 典型工作流：调用归档 Skill

主公说出归档 Skill 触发关键词时（项目规划 / 任务清单 / 审核架构 / 系统复盘 等）：

1. 读 `cowork/skill_archives/INDEX.md` 找到匹配的 Skill 名 + 关键词映射
2. 读对应 `cowork/skill_archives/<skill-name>/SKILL.md` 完整流程
3. 按 SKILL.md 步骤执行（跟在用 Skill 同样的执行方式，归档不影响功能）
4. 完成后正常记 cowork_log.md（注明走的是归档 Skill 路径）

规则源头：cowork/CLAUDE.md 「🔧 Skill 快速路由」一行指针；本节是该指针的展开操作步骤。

---

## 格式标准

| 项目 | 标准 |
|------|------|
| cowork_log 时间格式 | `[YYYY-MM-DD HH:MM]` |
| friction_log 状态 | `需主公确认` / `已自行修复` |
| context.md 文件夹区块 | 含标签/用途/状态/规则文件/关键文件 |
| CURRENT_SESSION 存档 | [PX] 名称 / 状态 / 停在 / 下一步 / 路径 |
| playbook 文件命名 | 项目简称小写（marketing / legal_library / ai_skill） |

---

## 核心文件速查

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` | AI 行为规则（每次自动加载） |
| `ARCHITECTURE.md` | 系统结构说明 |
| `context.md` | 全局文件索引 + 项目状态 |
| `CURRENT_SESSION.md` | 项目进度存档 |
| `cowork_log.md` | 操作流水账 |
| `friction_log.md` | 规则摩擦记录 |
| `playbooks/` | 各项目操作手册 |


## 子Agent 协作层

| 项目 | 说明 |
|------|------|
| 角色 | Claude 策划+验收，子Agent 执行 |
| 路由 | ①读多文件+改+验证→`general-purpose`；②只读型→`Explore`；③长耗时→`general-purpose`；④其他→Claude直接做 |
| 判据 | 「验收能写死」+「无需中途对话」两个都满足才派 |

---

## 历史对话搜索
搜索此项目相关历史对话：
```bash
python3 /home/cowork/cowork/scripts/search_conversations.py "关键词"
```
