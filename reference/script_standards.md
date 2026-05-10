# 脚本标准（所有新建/修改脚本必须包含）

> 写任何新脚本或修改脚本前读此文件。

## 崩溃告警
每个 bash 脚本必须有 `set -e` + `trap '...' ERR`，失败时发邮件到 GMAIL_TO，主题格式 `⚠️ [项目名]运行失败 YYYY-MM-DD`

## ERR trap 写法
trap 内 Python f-string 禁止用 `f'...'`/`f"...strftime(\"...\")"`，一律用字符串拼接：
```python
"prefix" + datetime.now().strftime("%Y-%m-%d") + "suffix"
```

## 邮件格式
- 有视觉输出（表格/链接/排版）的邮件 → HTML
- 纯文字告警 → plain text
- **HTML 邮件预览规则**：修改邮件格式前先生成样本发 Discord，主公确认后才执行

## `claude --print` cwd 规则
从 cowork/ 运行会自动加载 CLAUDE.md+MEMORY.md（~5000 token 无效 overhead）。
- 默认用 `/tmp`：`(cd /tmp && claude --print ...)`
- Python subprocess：加 `cwd='/tmp'` 参数
- ⚠️ `--bare` 不可用（断 keychain 认证）

## 模型选择
- 摘要/格式化任务 → `--model haiku`（省 80% 成本）
- 多维度 JSON 分析/复杂推理 → 默认 Sonnet
