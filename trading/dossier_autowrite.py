#!/usr/bin/env python3
"""
趋势追踪档案 · 轨迹自动写入（趋势主线第2层 · 阶段2-B）

做什么：
  每周一自动给档案里「每一个」进池对象追加一行最新轨迹（价格/估值/距52周高），
  对象清单**从档案自身解析**，不写死在代码里——以后档案增删对象、换股票，
  本脚本一行都不用改（主公 2026-06-21 要求：必须通用）。

通用机制（数据驱动）：
  扫描档案所有 `## [` 开头的对象标题，读其出生档案里的
  `- **追踪代码**：XXX` 字段拿到 ticker，自动纳入追踪。
  没有「追踪代码」字段的对象会被跳过并告警（提示补字段）。

边界（铁律，承袭 趋势追踪档案.md / dossier_weekly.py）：
  - 只写「事实数据」（机器能查准的：价格/估值/距高/涨跌）
  - 「逻辑状态」列机器不判断 → 一律写 `🔍待校准`，由主公/我看后补
    （"逻辑还成不成立" 是判断不是数据，不让脚本编「成立/瓦解」）
  - 绝不写「该买/该卖」
  - 出生档案、历史轨迹行 永不修改，只在各对象轨迹表末尾追加
  - 幂等：今天已写过该对象 → 跳过（可重复跑）

数据源：yfinance（与 6/11 基线、6/20 手动补轨迹同源）
调用：python3 dossier_autowrite.py [--dry-run]
      --dry-run 只打印将写入的行，不改文件
cron：每周一 09:30 EDT（趋势周检/周报前，让它们读到最新轨迹）
创建：2026-06-21
"""
import re
import sys
from datetime import datetime
from pathlib import Path

import yfinance as yf

sys.path.insert(0, "/home/cowork/cowork/scripts")
from tide_utils import run_with_alert  # noqa: E402  失败自动发邮件告警

BASE = Path("/home/cowork/cowork")
DOSSIER = BASE / "trading/notes/趋势追踪档案.md"
LOG_PATH = BASE / "trading/dossier_autowrite.log"

DRY_RUN = "--dry-run" in sys.argv
NOW = datetime.now()
DATE_STR = NOW.strftime("%Y-%m-%d")

PENDING = "🔍待校准"
# 个股标题含「个股」二字 → 写 PE 口径；其余（趋势）→ 写代理股价口径
STOCK_HINT = "个股"
CODE_RE = re.compile(r"\*\*追踪代码\*\*[：:]\s*([A-Za-z0-9.\-]+)")


def log(msg: str) -> None:
    line = f"[{NOW.strftime('%Y-%m-%d %H:%M')} EDT] {msg}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_objects(lines: list[str]) -> list[dict]:
    """从档案解析所有对象：标题行号 + 标题文本 + 追踪代码 + 类型。"""
    objs = []
    # 所有对象标题（## [ 开头），按出现顺序；段范围 = 本标题 ~ 下一个标题/章节
    heads = [i for i, ln in enumerate(lines)
             if ln.startswith("## [")]
    for idx, start in enumerate(heads):
        title = lines[start].strip()
        # 段的结束 = 下一个 ## / # 行
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## ") or lines[j].startswith("# "):
                end = j
                break
        # 在段内找追踪代码
        ticker = None
        for j in range(start, end):
            m = CODE_RE.search(lines[j])
            if m:
                ticker = m.group(1)
                break
        kind = "stock" if STOCK_HINT in title else "trend"
        objs.append({"title": title, "head": start, "end": end,
                     "ticker": ticker, "kind": kind})
    return objs


def fetch(ticker: str) -> dict | None:
    try:
        info = yf.Ticker(ticker).info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        hi = info.get("fiftyTwoWeekHigh")
        pe = info.get("forwardPE")
        chg = info.get("52WeekChange")
        from_hi = (price / hi - 1) * 100 if (price and hi) else None
        return {"price": price, "pe": pe, "from_hi": from_hi,
                "yr": (chg * 100) if chg is not None else None}
    except Exception as e:
        log(f"⚠️ {ticker} 查数失败: {e}")
        return None


def fmt(v, suffix="", nd=1):
    return f"{round(v, nd)}{suffix}" if v is not None else "N/A"


def build_row(obj: dict, d: dict) -> str:
    price, from_hi, pe, yr = d.get("price"), d.get("from_hi"), d.get("pe"), d.get("yr")
    if obj["kind"] == "stock":
        keynums = (f"PE {fmt(pe, 'x')}；1年{fmt(yr, '%')}；"
                   f"距高{fmt(from_hi, '%')}（${fmt(price, '', 2)}）")
    else:
        keynums = (f"{obj['ticker']} ${fmt(price, '', 2)}；"
                   f"距高{fmt(from_hi, '%')}；1年{fmt(yr, '%')}")
    return f"| {DATE_STR} | {keynums} | {PENDING} | 数据已更新，逻辑状态待人工校准 |"


def insert_row(lines: list[str], obj: dict, new_row: str) -> str:
    """在对象轨迹表末尾插入 new_row。返回 written/skipped/notable。"""
    start, end = obj["head"], obj["end"]
    # 幂等：今天已写过
    for i in range(start, min(end, len(lines))):
        if f"| {DATE_STR} |" in lines[i]:
            return "skipped"
    # 找轨迹表最后一行（| 开头结尾、非分隔行）
    last_row = None
    for i in range(start, min(end, len(lines))):
        s = lines[i].strip()
        if s.startswith("|") and s.endswith("|") and "---" not in s:
            last_row = i
    if last_row is None:
        return "notable"  # 没找到表
    lines.insert(last_row + 1, new_row)
    return "written"


def reparse_shift(objs: list[dict], inserted_at: int):
    """插入一行后，其后所有对象的 head/end 行号 +1（保持后续插入正确）。"""
    for o in objs:
        if o["head"] > inserted_at:
            o["head"] += 1
        if o["end"] > inserted_at:
            o["end"] += 1


def main():
    if not DOSSIER.exists():
        log(f"❌ 档案不存在: {DOSSIER}")
        sys.exit(1)

    lines = DOSSIER.read_text(encoding="utf-8").split("\n")
    objs = parse_objects(lines)
    log(f"档案解析到 {len(objs)} 个对象")

    written = skipped = failed = nocode = 0
    preview = []
    for obj in objs:
        if not obj["ticker"]:
            log(f"⚠️ 对象「{obj['title']}」缺『追踪代码』字段，跳过（请在出生档案补 - **追踪代码**：XXX）")
            nocode += 1
            continue
        d = fetch(obj["ticker"])
        if d is None or d.get("price") is None:
            log(f"⚠️ {obj['ticker']}（{obj['title']}）无价格，跳过不写空行")
            failed += 1
            continue
        row = build_row(obj, d)
        preview.append(f"{obj['ticker']:8} | {obj['title']}\n         {row}")
        if DRY_RUN:
            continue
        res = insert_row(lines, obj, row)
        if res == "written":
            written += 1
            reparse_shift(objs, obj["head"])  # 行号后移，保证后续对象定位准确
        elif res == "skipped":
            skipped += 1
            log(f"↩️ {obj['ticker']} 今日已存在，跳过")
        else:
            failed += 1
            log(f"❌ {obj['ticker']} 未找到轨迹表，跳过")

    if DRY_RUN:
        print(f"\n=== DRY RUN（不写文件）· 将追加 {len(preview)} 行 ===")
        for p in preview:
            print(p)
        log(f"DRY RUN 完成：{len(preview)} 行待写 / 缺代码 {nocode}")
        return

    if written:
        DOSSIER.write_text("\n".join(lines), encoding="utf-8")
    log(f"✅ 完成：写入 {written} / 跳过 {skipped} / 失败 {failed} / 缺代码 {nocode}（共 {len(objs)}）")
    if written:
        log(f"⚠️ 逻辑状态列均为 {PENDING}，等人工补判断")

    # 全员查数失败 = 异常（yfinance 全挂/网络断），抛出触发崩溃告警，不静默
    if objs and failed == len(objs):
        raise RuntimeError(f"全部 {len(objs)} 个对象查数失败，疑似 yfinance/网络故障")


if __name__ == "__main__":
    if DRY_RUN:
        main()  # dry-run 不需要告警包装
    else:
        run_with_alert("dossier_autowrite.py", main)
