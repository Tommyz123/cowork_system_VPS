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
1. 逐个对象（趋势层 + 个股层，对象数量以档案实际为准，不要硬编）给「逻辑状态」判断：强化 / 成立稳定 / 松动 / 瓦解 —— 依据是档案里记录的进池理由和最新轨迹。
2. 每个对象必须把「数据」和「判断」拆成两个独立字段（见下方格式）——数据字段只放客观事实（价格/估值/距高/百分比等可核实的数字），判断字段只放你的推断（逻辑是否成立、位置好坏、离触发远近）。两者绝不混写。
3. 指出本周最值得注意的 1-3 个点。
4. 用一句话给整体盯防结论。

铁律（违反即失败）：
- 绝对不要输出「该买/该卖/建议买入/可以加仓」这类决策语言。你只做事实陈述 + 逻辑状态分析 + 反思。
- 数据/判断分层：`数据:` 行只准放客观数字与事实，一个主观词都不要；主观推断全部放 `判断:` 行。这是硬性分区，违反即失败。
- 如果档案里某对象只有基线一行、还没有后续轨迹，数据行如实写「暂无新轨迹」，不要编造价格变化。
- 不确定的地方标「待人工确认」，不要硬编数字。
- 直接从「## 一句话总览」开始输出，不要写任何开场白、思考过程或「I'll generate...」之类的前言。

输出格式（严格照此，每个对象三行：名称行 + 数据行 + 判断行）：
## 一句话总览
（整体盯防结论，纯判断）

## 趋势层
- [趋势名(代码)]：[状态]
  数据: [只放客观数字/事实，用 / 分隔多项；无则写「暂无新轨迹」]
  判断: [只放主观推断：逻辑成立度、位置、离触发远近]
...

## 个股层
- [代码]：[状态]
  数据: [只放客观数字/事实]
  判断: [只放主观推断]
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
    # 兜底：裁掉 AI 可能写的开场白（保留从第一个 ## 起的正文）
    if analysis:
        idx = analysis.find("## ")
        if idx > 0:
            analysis = analysis[idx:]
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

    # ② 发邮件（HTML，结构化渲染：卡片 + 数据/判断分区）
    from render_dossier_html import render  # noqa: E402  本目录内
    html_body = render(report, DATE_STR)
    send_email(f"📊 趋势档案周报 {DATE_STR}", html_body, html=True)
    log("✅ 周报邮件已发送")


if __name__ == "__main__":
    main()
