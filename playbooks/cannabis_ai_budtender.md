---
name: cannabis_ai_budtender
description: Cannabis AI 对话顾问系统开发、Eval 测试和多轮对话优化
triggers: [budtender, cannabis AI, 大麻AI, 对话顾问, budtender测试, eval, cannabis_AI_BUDTENDER]
working_dir: C:\Users\zhi89\Desktop\cannabis_AI_BUDTENDER\
status: active
---

# Playbook: Cannabis AI Budtender

> 代码规范、prompt 规则、模块说明详见项目内 `CLAUDE.md` / `agents.md`
> 本文件只做快速入口，不重复项目内规则

---

## 快速启动（摘自项目 CLAUDE.md，命令改动以项目为准）

**路径**
- Windows：`C:\Users\zhi89\Desktop\cannabis_AI_BUDTENDER\`
- WSL：`/mnt/c/Users/zhi89/Desktop/cannabis_AI_BUDTENDER/`

**启动后端**（Windows CMD）
```
cd C:\Users\zhi89\Desktop\cannabis_AI_BUDTENDER
venv\Scripts\activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**跑 Eval**（WSL bash）
```bash
# 全量 25 TC
"/mnt/c/Users/zhi89/Desktop/cannabis_AI_BUDTENDER/venv/Scripts/python.exe" eval/run_eval.py

# 单 TC
"/mnt/c/Users/zhi89/Desktop/cannabis_AI_BUDTENDER/venv/Scripts/python.exe" eval/run_eval.py --tc tc_C4
```

⚠️ **禁止在 WSL 里写内联 `-c "..."` 测试脚本**，路径混用会出错，调试统一走 eval runner。

---

## 当前进度

→ 见 `CURRENT_SESSION.md` [P3]

---

## 协作习惯（此项目专属）

- **报错/bug 类**：先说原因 + 方案 → 等主公确认 → 再动手
- **Eval 修复流程**：分析失败原因 → 汇报方案 → 确认 → 执行 → 单 TC 测 2-3 次稳定 → 全量回归
- **Prompt 修改**：每个规则必须是独立模块（命名 `FEATURE_NAME_PROMPT`），禁止直接往现有 prompt 追加
- **每次只改 1 个 TC**，修好验证后再推进下一个

---

## 核心文件速查

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` / `agents.md` | AI 行为规则（两者内容同步） |
| `backend/prompts.py` | 所有 prompt 模块 |
| `backend/llm_service.py` | Agent loop + streaming |
| `backend/router.py` | 查询分类 + FastPath |
| `golden_dataset_v2.json` | Eval 数据集（当前版本，25 TC） |
| `planning/context.md` | 架构、模块状态、关键接口 |
| `.env` | API keys（OpenAI / Langfuse / DeepSeek） |


## 历史对话搜索
搜索此项目相关历史对话：
```bash
python3 /mnt/c/Users/zhi89/Desktop/cowork/scripts/search_conversations.py "关键词"
```
