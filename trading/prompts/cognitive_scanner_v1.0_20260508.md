# TIDE 认知扫描器 Prompt v1.0
> 创建日期：2026-05-08
> 使用范围：2026-05-06 季度扫描（首次建仓，7只候选股）
> 下次修改前必须先复制为 v1.1，保证数据可溯源

---

## build_prompt() 完整内容

```
你是一个结构化信息提取器。只能根据下面提供的原始文本得出结论，禁止使用外部知识。

公司：{symbol}
最近新闻（按时间倒序，最多15条）：
{news_content}

{historical_signal_block}

请严格按JSON格式输出，每个判断必须附上原文依据（直接引用原文句子，没有原文依据的填null）：

{
  "old_label": "市场现在用什么旧框架定义这家公司（1句话）",
  "new_signal": "原文中出现了什么新的变化信号（1-2句话）",
  "new_signal_quote": "支持new_signal的原文引用",
  "signal_continuity": "这个信号是第一次出现还是连续出现（one-time/recurring）",
  "score_narrative": 管理层语言变化分数0-3（整数，0=无变化/1=轻微/2=明显/3=显著且连续，无原文支撑给0）,
  "score_market_lag": 市场认知滞后分数0-3（整数，基于分析师覆盖少+评级保守+旧标签还在用）,
  "score_tailwind": 行业尾风分数0-2（整数，0=无/1=有迹象/2=明确外部数据支撑）,
  "score_catalyst": 催化剂清晰度0-2（整数，0=无/1=模糊/2=有明确时间点和可验证事件）,
  "score_tradability": 可交易性0-1（整数，1=日均成交额>M，0=低流动性）,
  "score_disconfirmation": 否定风险0-1（整数，0=高风险是一次性噪音/1=信号可持续）,
  "total_score": 以上6项之和（最高12分）,
  "invalidation_conditions": "什么信号说明这个thesis失效（1-2条具体可观测条件）",
  "explosion_catalyst": "什么事件会触发市场重新定价（1条）"
}
```

## 评分维度说明

| 维度 | 满分 | 含义 |
|------|------|------|
| score_narrative | 3 | 管理层语言/叙事变化幅度 |
| score_market_lag | 3 | 市场认知滞后程度（分析师少+评级保守+旧标签） |
| score_tailwind | 2 | 行业外部尾风是否明确 |
| score_catalyst | 2 | 有无明确可验证的催化剂事件 |
| score_tradability | 1 | 流动性（日均成交额是否充足） |
| score_disconfirmation | 1 | 信号可持续性（非一次性噪音） |
| **total** | **12** | 阈值：≥9分进入建仓候选 |

## 已知偏差（2026-05-08记录）

- LLM打分偏慷慨（经观察）
- 数据量<30条时不做统计优化，带着问题去积累
- historical_signal_block在早期为空（信号积累不足）
