---
name: 搜索
description: 搜索 cowork 历史对话记录（cowork.db FTS5全文索引）。当主公说"搜索 XXX"、"帮我搜 XXX"、"查一下 XXX"、"搜一下关于 XXX 的对话"、"X月份关于XXX"时立刻触发此 Skill。不需要主公记命令语法，直接解析意图执行搜索并返回结果。
allowed-tools: Bash
---

# 历史对话搜索

> 主公通过自然语言表达搜索意图，你来解析参数、执行搜索、格式化输出。
> 这样主公不需要记命令语法，直接说想找什么就行。

---

## 第一步：解析搜索意图

从主公的消息里提取以下参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `keyword` | 核心搜索词（必填） | "langfuse" / "eval" / "streaming" |
| `project` | 项目过滤（可选，格式 P2/P3/P4/P5/P6） | "P3" / 无 |
| `date` | 日期前缀过滤（可选，格式 YYYY-MM） | "2026-04" / 无 |
| `limit` | 最多显示条数（默认10，Discord上不要太多） | 10 |

**解析示例：**
- "搜索 langfuse" → keyword=langfuse
- "搜索 P3 streaming" → keyword=streaming, project=P3
- "帮我查4月份关于eval的对话" → keyword=eval, date=2026-04
- "搜一下机票监控的配置" → keyword="机票监控 配置"（可拆成两次搜索）

---

## 第二步：执行搜索

```bash
python3 /home/cowork/cowork/scripts/search_conversations.py \
  "keyword" \
  [--project P3] \
  [--date 2026-04] \
  --limit 10
```

捕获输出结果。

---

## 第三步：格式化并回复

**如果在 Discord 频道**（消息来自 `<channel source="plugin:discord:discord">`）：
用 Discord reply 工具回复，格式简洁：

```
🔍 搜索「keyword」结果：

📅 2026-04-12 | P3 | 🤖 Claude
"...匹配片段..."

📅 2026-04-10 | 未标记 | 🙋 主公
"...匹配片段..."

（共找到 N 条）
```

**如果在终端**：
直接输出，格式同上。

---

## 注意事项

- 若搜索无结果，说明该词在历史对话中未出现（或用了不同表达），建议尝试英文/同义词
- `--project` 过滤只对有 /收工 记录的对话有效；历史对话无项目标签时显示"未标记"
- 每条结果保持简短（2-3行），不要把整段对话都粘出来

---

## 示例输出

用户说「搜索 langfuse」时：

```
🔍 搜索「langfuse」— 找到 3 条

📅 2026-04-12 | 未标记 | 🤖 Claude
"...env 里已经有 LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY，只差两步..."

📅 2026-04-12 | 未标记 | 🤖 Claude  
"测试通过，去 Langfuse 控制台确认 trace 出现就搞定了。"

📅 2026-04-12 | 未标记 | 🙋 主公
"Added Langfuse HOST alignment..."
```
