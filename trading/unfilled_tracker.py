#!/usr/bin/env python3
"""
未成交票纸面跟踪器（unfilled paper tracker）—— P9 「过期单也对答案」的数据层。

【是什么】
  P9 盘后自动下 OPG 单，开盘未撮合即过期（status='expired'，filled_qty=0）。
  这些票"选了但没买到"，过去无人回头看它后续涨跌 → 选股眼光准不准无从验证。
  本脚本对每只过期票，从「信号日价格」起持续跟踪后续股价，算出涨跌 %，写回 DB。

【为什么做】
  买没买到 ≠ 选得准不准。没买到的票照样能"对答案"：信号日看好它、记下当时价，
  事后看它涨了还是跌了，就能验证选股逻辑。这批"押了题没对答案"的样本本不该浪费。
  （2026-06-27 主公 + CC 对话定案；起因=查清 10 笔 OPG 过期单后发现选股样本流失。）

【为什么这样设计——分层铁律（主公硬要求：数据与判断分开，AI 不混乱）】
  本脚本 = 「数据员」角色，**纯客观数据层，零判断**：
    - 只读价格、只写"客观涨跌数字"（信号价→当前价的 return、峰值、价格序列、更新时间）
    - 写入独立字段 unfilled_track_*（与"卖出后跟踪"post_exit_* 物理隔离，语义不打架）
    - **绝不写任何判断字段**（verdict / mistake_type / real_reason / score 等）——
      "这次选股对不对"的对错打分留给将来的【审计员 agent】（loop 的 B 步），不在此脚本。
  依据 memory [[feedback_tracking_facts_only]] + [[feedback_docs_for_ai]]
  + notes/主题累积研究loop设计.md（三角色：数据员/分析师/审计员职责分离）。

【演进】
  v1 (2026-06-27)：数据层 only——跟踪过期票信号日起涨跌，写 unfilled_track_* 4 字段。
  下一步 (B)：把本数据层接入主题累积研究 Loop 的审计环（回看"高分押题 vs 实际涨跌"打对/错/待定）。
  仿 post_exit_tracker.py（已稳跑），复用其 fetch_series 取价逻辑；不碰选股/下单/对账。

用法：python3 unfilled_tracker.py
"""
import importlib.util
import json
import sqlite3
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from tide_utils import load_env, run_with_alert
# 复用 post_exit_tracker 已验证的取价 + 日期解析逻辑（同一套数据源，避免重复实现）
from post_exit_tracker import fetch_series, parse_iso_date, yfinance_available

DB_PATH = Path("/home/cowork/cowork/trading/trading.db")
LOG_PATH = Path("/home/cowork/cowork/trading/unfilled_tracker.log")
TRACK_DAYS = 90  # 信号日后跟踪窗口（天），与 post_exit_tracker 对齐


def log(message: str) -> None:
    from datetime import datetime
    timestamped = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    print(timestamped)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(timestamped + "\n")


def get_unfilled_picks() -> List[Tuple[int, str, float, str]]:
    """取所有过期票 (id, symbol, signal_entry_price, signal_date)。
    数据层：只挑 status='expired' 且有信号价+信号日的票。"""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT id, symbol, signal_entry_price,
                   COALESCE(signal_date, scan_date) AS sig_date
            FROM scanner_picks
            WHERE status = 'expired'
              AND COALESCE(TRIM(symbol), '') != ''
              AND signal_entry_price IS NOT NULL
              AND COALESCE(TRIM(COALESCE(signal_date, scan_date)), '') != ''
            ORDER BY id
            """
        ).fetchall()
    finally:
        conn.close()
    return [(r[0], r[1].strip().upper(), float(r[2]), r[3][:10]) for r in rows]


def track(env: Dict[str, str]) -> None:
    from datetime import datetime
    picks = get_unfilled_picks()
    log(f"{len(picks)} unfilled (expired) picks to track")

    conn = sqlite3.connect(DB_PATH)
    try:
        for pick_id, symbol, signal_price, signal_date in picks:
            start = parse_iso_date(signal_date).date().isoformat()
            end = (parse_iso_date(signal_date) + timedelta(days=TRACK_DAYS + 5)).date().isoformat()
            series = fetch_series(symbol, start, end, env)
            # 只保留信号日之后的价格点（信号日当天不算，对齐"事后表现"口径）
            post = {d: p for d, p in series.items() if d > signal_date}
            if not post:
                log(f"{symbol}: no post-signal prices yet (signal {signal_date})")
                continue

            peak = max(post.values())
            ordered = sorted(post.items())
            last_date, last_price = ordered[-1]
            # 纯客观：信号价 → 最新价 的涨跌 %（不解读、不判断对错）
            sig_return = round((last_price - signal_price) / signal_price * 100.0, 2) if signal_price else None

            conn.execute(
                """
                UPDATE scanner_picks
                SET unfilled_track_prices = ?,
                    unfilled_track_peak = ?,
                    unfilled_signal_return = ?,
                    unfilled_track_updated = ?
                WHERE id = ?
                """,
                (
                    json.dumps(post, sort_keys=True),
                    round(peak, 4),
                    sig_return,
                    datetime.now().date().isoformat(),
                    pick_id,
                ),
            )
            log(
                f"{symbol}: signal({signal_date})=${signal_price:.2f} "
                f"peak=${peak:.2f} last({last_date})=${last_price:.2f} "
                f"signal_return={sig_return}% pts={len(post)}"
            )
        conn.commit()
    finally:
        conn.close()


# ───────────────────────────────────────────────────────────────────────────
# 审计层（loop 三层档案的第3层 · 审计员角色）—— B-轻量版 (2026-06-27)
# ───────────────────────────────────────────────────────────────────────────
# 【与数据层的分层铁律】审计层只读"数据层已算好的客观涨跌"(unfilled_signal_return)，
#   用一条**确定性规则**(纯数学,零 AI 判断,零幻觉)打"对/错/待定"，写独立 audit_* 字段。
#   不重新取价、不下主观判断、不碰数据层字段，更不碰 verdict(历史污染字段,主动避开)。
# 【为什么是确定性规则而非 agent】loop 设计当前在阶段0/排雷期，阶段1(审计员 agent 化)须
#   等 2026-08-24 地基验收通过才做。本轻量版不跳阶段、不建 agent，且产出正是将来 agent 审计的原料。
#   依据 notes/主题累积研究loop设计.md + memory [[feedback_p9_strategy_discipline]]。
# 【规则】信号收益 >+2%=选对 / <-2%=选错 / 中间=待定(±2% 噪音带,过滤接近零的抖动)。
AUDIT_RULE = "signal_return >+2%=correct / <-2%=wrong / else=tentative (data-layer only, deterministic)"
AUDIT_THRESHOLD = 2.0


def audit() -> None:
    """审计员：读数据层 unfilled_signal_return → 确定性规则打 audit_pick_verdict。"""
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().date().isoformat()
    try:
        rows = conn.execute(
            """SELECT id, symbol, unfilled_signal_return FROM scanner_picks
               WHERE status='expired' AND unfilled_signal_return IS NOT NULL"""
        ).fetchall()
        counts = {"correct": 0, "wrong": 0, "tentative": 0}
        for pick_id, symbol, ret in rows:
            if ret > AUDIT_THRESHOLD:
                verdict = "correct"
            elif ret < -AUDIT_THRESHOLD:
                verdict = "wrong"
            else:
                verdict = "tentative"
            counts[verdict] += 1
            conn.execute(
                """UPDATE scanner_picks
                   SET audit_pick_verdict=?, audit_rule=?, audit_updated=?
                   WHERE id=?""",
                (verdict, AUDIT_RULE, today, pick_id),
            )
        conn.commit()
        total = sum(counts.values())
        hit = counts["correct"] / (counts["correct"] + counts["wrong"]) * 100 if (counts["correct"] + counts["wrong"]) else 0
        log(f"audit: {total} picks → 对{counts['correct']}/错{counts['wrong']}/待定{counts['tentative']} | 选对率={hit:.0f}%（剔除待定）")
    finally:
        conn.close()


def main() -> None:
    env = load_env()
    log(f"startup: yfinance_available={yfinance_available()} fmp_key={bool(env.get('FMP_API_KEY'))}")
    track(env)   # 数据层：取价 + 算客观涨跌
    audit()      # 审计层：确定性规则打对/错/待定
    log("unfilled tracker complete")


if __name__ == "__main__":
    run_with_alert("unfilled_tracker", main)
