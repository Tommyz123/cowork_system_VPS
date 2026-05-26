---
triggers: ["求职", "找工作", "career-ops", "投简历", "面试", "职位", "JD"]
---

# Playbook: 求职 (career-ops) [P8]

## 快速启动

```bash
# 进入项目目录（在 Claude Code 中打开此目录）
C:\Users\zhi89\Desktop\job\career-ops\
```

## 核心信息（2026-05-24 策略大重定向）

> 旧策略「作品敲门 / AI Agent Developer / 兼职优先」已弃用。新策略要点如下。

**策略核心：跳板策略**
- 6-12 月在一家公司积累 AI 履历 → 跳到下一家，或 P12 大麻牌照下来后全职转 P12
- 看履历"下游兼容性"——第一份选 YC 早期 AI 履历远胜 Cannabis Tech 履历（详见本 playbook 后面「履历下游兼容性」段）

**甜区岗位（5 类，必须 JD 含技术关键词）**：
1. Solutions Engineer / Customer Engineer
2. Implementation Engineer
3. Founding Engineer（早期创业）
4. Applied AI Engineer
5. AI Automation / Agent Engineer

**不投清单（6 类）**：
- FDE（Forward Deployed Engineer，门槛高 + 英语 B1 不够）
- Tier 1 Lab（OpenAI / Anthropic 等顶级 lab，水平/英语都不够）
- CSM（Customer Success Manager，不写代码）
- Sales / Marketing / Operations（非技术岗）

**主公真实约束**：
- 英文水平：B1（限制了部分外企/客户密集岗位）
- 当前在职：Sage Seeds budtender，时间灵活但需顾忌
- NY 大麻牌照申请中（P12），最终目标是牌照下来全职转大麻零售

**与 P12 主线协同**：跳板期获得 AI 履历 → 牌照下来后将 AI 能力嵌入 P12（自营 AI 顾问 / kiosk / 合规过滤）

**30+ 家公司清单 + 4 优先级** → 详见 `career-ops/` 项目（cowork 是战略层，作战细节在那边）

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

---

## 岗位筛选方法：Title 不等于工作内容（2026-05-24）[ref-worthy]

**核心原则**：岗位 title 看似相同但内涵差很大，**绝对不能只看 title 投**。

**典型例子**：
- "Customer Success Manager" vs "Customer Engineer" — 一个是客服，一个是技术岗
- "Solutions Engineer" vs "Sales Engineer" — 一个写代码做 POC，一个是销售
- "Implementation Specialist" 在不同公司可能是技术 / 也可能是项目经理

**JD 关键词扫描法**（投前必做）：
看 JD 里有没有这些**技术信号词**：
- ✅ `write code` / `build` / `deploy` / `integrate`
- ✅ `Python` / `SQL` / `API` / `LLM` / `agent`
- ✅ `technical implementation` / `prototype` / `POC`

**判断**：
- 有 ≥ 2 个技术信号词 → 技术岗（可投，主公能学到+用上）
- 0-1 个 → 客服/销售/PM 岗（**淘汰**，违反主公 hard requirement"能学到+用上 cowork 经验"）

**适用**：30+ 家公司清单筛选 / 任何"看起来对"但要二次确认的岗位。

**为什么这条重要**：跳板策略下，投错岗位 = 学不到 + 用不上 = 6-12 月白干。Blast radius 大于"投错被拒"。

---

## 履历下游兼容性：跳板策略的第三维度（2026-05-24）[ref-worthy]

**核心原则**：评估"敲门砖"工作时，**除了薪资+学习，还要看"6-12 月后能跳到哪里"**——履历的下游兼容性。

**例子**：
- **YC 早期 AI 履历** → 跳任何 AI 公司都易（同圈互认 / 标签清晰 / 圈内推荐链路畅）
- **Cannabis Tech 履历** → 跳到 AI 公司难（AI 公司可能不认这个标签 / 行业跨度大）
- **传统大厂 PM/Sales 履历** → 跳到早期 AI 创业难（标签错位）

**评估三维度**（投每个岗位前都过一遍）：
1. 薪资 / 工作环境
2. 学习曲线 + 能用上 cowork 经验吗
3. **6-12 月后这段履历能跳到哪些公司**（**容易被忽略，但最重要**）

**适用场景**：
- 30+ 家公司清单优先级排序——同等条件下选"下游兼容性"高的
- 决定"先干 Cannabis Tech 还是 AI 创业"等方向判断
- 避免选了"看起来好但跳不出去"的死胡同岗位（即使薪资高、学得到，但下游路径死了 = 跳板策略失败）

**为什么这条重要**：跳板策略不是单点最优，是**两步最优**——第一份工作 + 第二份能跳到哪。只算第一份 = 短视。
