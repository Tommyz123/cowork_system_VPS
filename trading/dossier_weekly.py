#!/usr/bin/env python3
"""
趋势追踪档案 · 周报（趋势主线第2层 · AI自动分析）

流程：
  1. 读 趋势追踪档案.md 全文
  2. 用 claude CLI（订阅，不调 API）分析：每个进池对象逻辑状态(强化/松动/瓦解) + 整体提示
  3. 报告双写：① 存归档 trading/reports/weekly/YYYY-MM-DD.md ② 发邮件(Brevo)
  4. （阶段1）轨迹追加由人工/半自动做，本脚本只做"读+分析+发+存"，不自动改档案
     —— 早期"逻辑还成不成立"的模糊判断需主公校准，不让脚本自动写死轨迹

护栏（铁律）：
  - 只输出 事实+分析+反思，绝不输出"该买/该卖"
  - 进池/出池决策权在主公；本脚本是辅助记忆与盯防，不替决策
  - 用 claude CLI 订阅（claude --print），不调 Anthropic API（主公原则）

创建：2026-06-20（趋势追踪档案系统 阶段2-A：AI自动读档案+周报email）
调用：python3 dossier_weekly.py   （cron 每周一 10:00 EDT）
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path("/home/cowork/cowork")
DOSSIER = BASE / "trading/notes/趋势追踪档案.md"
REPORT_DIR = BASE / "trading/reports/weekly"
LOG_PATH = BASE / "trading/dossier_weekly.log"
SCRIPTS_DIR = BASE / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
from send_email import send_email  # noqa: E402

NOW = datetime.now()
DATE_STR = NOW.strftime("%Y-%m-%d")


def log(msg: str) -> None:
    line = f"[{NOW.strftime('%Y-%m-%d %H:%M')} EDT] {msg}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


ANALYSIS_PROMPT = """你在为一套「趋势追踪档案」生成每周分析报告。下面是档案全文。

你的任务（严格遵守）：
1. 逐个对象（4趋势 + 6个股）给一句话「逻辑状态」判断：强化 / 成立稳定 / 松动 / 瓦解 —— 依据是档案里记录的进池理由和最新轨迹。
2. 指出本周最值得注意的 1-3 个点（哪个对象逻辑在变、离触发闸门近了吗）。
3. 用一句话给整体盯防结论。

铁律（违反即失败）：
- 绝对不要输出「该买/该卖/建议买入/可以加仓」这类决策语言。你只做事实陈述 + 逻辑状态分析 + 反思。
- 如果档案里某对象只有基线一行、还没有后续轨迹，就如实说「暂无新轨迹，待数据更新」，不要编造价格变化。
- 不确定的地方标「待人工确认」，不要硬编数字。

输出格式（简洁，控制在一屏内）：
## 一句话总览
（整体盯防结论）

## 趋势层（4条）
- [趋势名]：[状态] — [一句依据]
...

## 个股层（6只）
- [代码]：[状态] — [一句依据]
...

## 本周关注
1. ...

档案全文如下：
---
{dossier}
"""


def run_claude_analysis(dossier_text: str) -> str:
    prompt = ANALYSIS_PROMPT.format(dossier=dossier_text)
    try:
        result = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            log(f"❌ claude CLI 返回非0: {result.stderr[:200]}")
            return ""
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        log("❌ claude CLI 超时(300s)")
        return ""
    except Exception as e:
        log(f"❌ claude CLI 异常: {e}")
        return ""


def main():
    if not DOSSIER.exists():
        log(f"❌ 档案不存在: {DOSSIER}")
        sys.exit(1)

    dossier_text = DOSSIER.read_text(encoding="utf-8")
    log(f"读档案 {len(dossier_text)} 字符，开始 AI 分析…")

    analysis = run_claude_analysis(dossier_text)
    if not analysis:
        # 分析失败也要告警，不能静默
        send_email(
            f"⚠️ 趋势档案周报生成失败 {DATE_STR}",
            f"claude CLI 分析未返回内容，请人工检查 dossier_weekly.log。\n时间: {NOW}",
        )
        log("❌ 分析为空，已发失败告警邮件")
        sys.exit(1)

    # 报告正文
    report = (
        f"# 趋势档案周报 {DATE_STR}\n\n"
        f"> 自动生成 by dossier_weekly.py（AI读档案分析）\n"
        f"> 护栏：只做事实+逻辑状态+反思，不构成买卖建议；决策权在主公。\n\n"
        f"{analysis}\n\n"
        f"---\n"
        f"_数据来源：趋势追踪档案.md；本报告已归档至 trading/reports/weekly/{DATE_STR}.md_\n"
    )

    # ① 存归档
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{DATE_STR}.md"
    report_path.write_text(report, encoding="utf-8")
    log(f"✅ 报告已归档: {report_path}")

    # ② 发邮件（HTML，把 markdown 简单转一下换行）
    html_body = report.replace("\n", "<br>\n")
    send_email(f"📊 趋势档案周报 {DATE_STR}", html_body, html=True)
    log("✅ 周报邮件已发送")


if __name__ == "__main__":
    main()
