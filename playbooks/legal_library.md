---
name: legal_library
description: 纽约大麻法律知识库：法规文件管理、索引维护、法律问答、新文件入库审核
triggers: [法律, legal, 法规, 大麻法律, 知识库, legal_library, RULE.md, 入库, 新文件, PDF法规]
working_dir: C:\Users\zhi89\Desktop\legal_library\
status: active
---

# Playbook: 大麻法律知识库

> 工作目录：`C:\Users\zhi89\Desktop\legal_library\`
> 规则文件（不重复）：`legal_library/RULE.md`

---

## 启动序列（每次进入项目必做）

1. 读 `RULE.md` — 了解检索规则、文件优先级、回答格式
2. 读 `INDEX.md` — 了解知识库索引结构
3. 等待主公提问，不要提前读内容文件

---

## 典型工作流：法律问答

```
1. 收到问题 → 读 INDEX.md，关键词匹配
2. 定位相关文件（可能多个）
3. 按优先级读取（核心🔴 → 专项🟡 → 参考🔵）
4. 文件 >500行 → 先 Grep 定位，再局部读取
5. 整合内容，按回答格式输出
```

---

## 典型工作流：新文件入库（主线）

主公发 PDF 或文件路径 → 我按以下步骤处理（完整流程见 `UPDATE_PROTOCOL.md` 第十节）：

```
1. 重复检测（INDEX.md关键词匹配）
2. 入库标准检查（相关性/来源/增量/有效性）
3. 大文件策略（<30页全读，30-100页grep，>100页摘要）
4. 判断 type（regulation/guidance/legal_case/compliance_case/discussion）
5. 提取核心要点 + 关键条款 + 实操启示
6. 新建 NN_Topic.md（按标准格式含 frontmatter）
7. 更新 INDEX.md（新条目 + 当前最大编号）
8. 数据库对齐（跨类别，检查冲突/superseded_by/交叉引用）
9. 更新 LEGAL_TIMELINE.md（regulation/legal_case 必须）
10. 将 PDF 移至 _archive/YYYY-MM/
11. git commit
12. 输出标准入库报告
```

## 典型工作流：知识库更新（现有文件）

```
1. 读取目标文件完整内容
2. 标注变更（加 [YYYY-MM-DD更新] 注释，过时内容加删除线）
3. 更新 frontmatter date 字段
4. 检查关联文件是否需要同步
5. 更新 LEGAL_TIMELINE.md
6. git commit
```

---

## 格式标准

> 详细格式见 `legal_library/RULE.md`，以下为快速参考：

| 项目 | 标准 |
|------|------|
| 回答结构 | 结论 → 依据（来源+条款）→ 注意事项 |
| 文件冲突 | 以 frontmatter date 字段较新的为准 |
| 不确定内容 | 明确说"知识库暂无此内容"，不猜测 |

**RULE.md 为权威来源，有冲突时以 RULE.md 为准。**

---

## 知识库文件结构

- 🔴 核心（01-05）：OCM 规定、选址距离、许可证要求等
- 🟡 专项（06-14 + 16）：广告、包装、员工培训、执照拒绝标准等
- 🔵 参考（17 + LEGAL_TIMELINE）：法律案例、时间线


## 历史对话搜索
搜索此项目相关历史对话：
```bash
python3 /mnt/c/Users/zhi89/Desktop/cowork/scripts/search_conversations.py "关键词"
```
