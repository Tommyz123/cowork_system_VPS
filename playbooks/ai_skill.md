---
name: ai_skill
description: AI Skill V5 框架研究：技能开发、多智能体、评估框架
triggers: [ai skill, cc_skill, V5框架, skill框架, 多智能体, 评估框架, inspect_eval, cc_skill]
working_dir: C:\Users\zhi89\Desktop\cc_skill\
status: active
---

# Playbook: AI Skill 框架研究

> 工作目录：`C:\Users\zhi89\Desktop\cc_skill\`

---

## 启动序列（每次进入项目必做）

1. 确认本次任务方向（skill 开发 / context 框架 / 评估 / 多智能体）
2. 根据方向进入对应子目录
3. 读当前目录下的 README 或说明文件

---

## 目录结构与对应任务

| 目录 | 任务类型 |
|------|---------|
| `skill/skills_v5/` | 开发或优化 V5 技能包 |
| `context/V5/` | 修改 Context 控制框架 |
| `mutl-agent-poco/` | 多智能体协作研究 |
| `inspect_eval_framework/` | 技能评估（使用 Inspect 框架） |
| `llm_eval_framework/` | LLM 能力评估 |
| `claude_code/` | Claude Code 工具与配置研究 |

---

## 典型工作流：新建/修改 Skill

```
1. 进入 skill/skills_v5/
2. 读现有 skill 结构了解规范
3. 新建或修改目标 skill 文件
4. 在评估框架（inspect_eval_framework/）里写测试用例
5. 运行评估，记录结果
6. 更新 skill 版本号和说明
```

---

## 典型工作流：Context 框架调整

```
1. 进入 context/V5/
2. 读框架说明文件，理解当前设计
3. 明确修改目标（性能/token/准确性）
4. 修改框架文件
5. 用实际场景验证效果
```

---

## 格式标准

| 项目 | 标准 |
|------|------|
| Skill 文件命名 | 功能描述，小写下划线 |
| 版本管理 | 文件内标注版本号（如 v5.1） |
| 测试记录 | 写入 eval 结果文件，注明日期和场景 |
| 代码注释 | 英文 |
| 文档说明 | 中文 |
