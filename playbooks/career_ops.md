---
triggers: ["求职", "找工作", "career-ops", "投简历", "面试", "职位", "JD"]
---

# Playbook: 求职 (career-ops) [P8]

## 快速启动

```bash
# 进入项目目录（在 Claude Code 中打开此目录）
C:\Users\zhi89\Desktop\job\career-ops\
```

## 核心信息

- **目标职位**：AI Agent Developer / AI Automation Engineer（主），Junior AI Engineer / Cannabis Tech（次）
- **薪资目标**：$70k–$90k，底线 $60k
- **偏好**：兼职/Contract/Freelance 优先，不考虑全职；Remote only，Hybrid NYC 可接受，On-site 拒绝
- **差异化**：行业背景（大麻零售运营）+ AI builder，竞争对手极少

## 常用命令

| 操作 | 说明 |
|------|------|
| 粘贴 JD URL | 自动评估（A-F打分）+ 生成报告 |
| `/career-ops scan` | 扫描预配置45+公司招聘页 |
| `/career-ops tracker` | 查看投递状态 |
| `/career-ops pdf` | 生成定制PDF简历 |
| `/career-ops patterns` | 分析拒绝规律 |

## 安全规则

- **禁止自动更新**：`update-guard.sh` Hook 已拦截，apply 前必须人工确认
- **提交前必须主公确认**：career-ops 不会自动点击 Submit
- **低于 4.0/5 分不投**：系统会提示，听建议

## 关键文件

| 文件 | 用途 |
|------|------|
| `cv.md` | 简历（唯一来源，勿硬编码数据） |
| `config/profile.yml` | 个人配置（薪资/偏好/职位） |
| `modes/_profile.md` | AI评估个性化规则（永不被更新覆盖） |
| `data/applications.md` | 投递追踪表 |
| `reports/` | 各职位评估报告 |

## 协作习惯

- 进入这个项目时，在 `C:\Users\zhi89\Desktop\job\career-ops\` 目录开 Claude Code
- cowork 系统负责进度追踪（CURRENT_SESSION P8），career-ops 负责执行
- 每次投递后更新 applications.md 状态
