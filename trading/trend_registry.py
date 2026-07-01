"""
第2层趋势实验·登记 CLI（判断冻结层 + 扫描长名单）

【是什么】trend_judgments（判断冻结）与 trend_scan_longlist（供给留痕）的唯一写入口。
【为什么做】方案规则4：每笔判断建仓前先冻结登记；防污染闸④：扫描长名单留痕。
【为什么这样设计】
- 登记走 JSON 文件而非命令行参数：六维打分快照（含出处）字段多且长，JSON 便于
  BB 认真准备+主公抽查；文件本身留在 trading/judgments/ 作为二次留痕。
- 本脚本只写冻结层和长名单，不下单不判定——下单在 trend_paper_trade.py，
  判定在 trend_verdict_check.py（机械落库，BB 无权改判）。
- 冻结层由 SQLite trigger 禁 UPDATE/DELETE（trend_db_schema.py），写错了只能
  INSERT 新记录并在 notes 里注明作废原因（复盘留痕，不抹历史）。
【用法】
  python3 trend_registry.py add <judgment.json>       # 登记一笔判断（返回 judgment_id）
  python3 trend_registry.py longlist <date> <候选> <理由> [--advanced]
  python3 trend_registry.py list [cohort]             # 查看已登记判断
【演进】2026-07-01 v0.2 首版。方案：notes/第2层提速攒样本方案_20260701.md
"""
import json
import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading.db")

REQUIRED = ["judgment_date", "trend_name", "proxy_symbol", "proxy_type",
            "manual_version", "cohort", "risk_cluster", "trigger_source"]
COHORTS = ("passed", "borderline", "rejected")
TRIGGERS = ("showdown", "w7", "heatmap", "quota_scan", "user", "backfill")
DIRECTIONS = (None, "long", "short", "neutral")


def add_judgment(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        j = json.load(f)
    for k in REQUIRED:
        if not j.get(k):
            raise ValueError(f"缺必填字段: {k}")
    if j["cohort"] not in COHORTS:
        raise ValueError(f"cohort 必须是 {COHORTS}")
    if j["trigger_source"] not in TRIGGERS:
        raise ValueError(f"trigger_source 必须是 {TRIGGERS}")
    if j.get("direction") not in DIRECTIONS:
        raise ValueError(f"direction 必须是 {DIRECTIONS}")
    # 防污染自检：rejected 组不设下车信号（方案规则4）
    if j["cohort"] == "rejected" and j.get("exit_signals"):
        raise ValueError("rejected 组不设下车信号（方案规则4）")
    # 方向留空必须显式声明 no_direction_frozen，防"忘了填"与"刻意留空"混淆
    if not j.get("direction") and not j.get("no_direction_frozen"):
        raise ValueError("direction 为空时必须显式 no_direction_frozen=1（刻意留空防事后诸葛亮）")
    cols = ["judgment_date", "trend_name", "proxy_symbol", "proxy_type", "proxy_reason",
            "proxy_chosen_date", "sector_benchmark", "score_json", "score_display",
            "score_pct", "veto_hit", "manual_version", "cohort", "risk_cluster",
            "trigger_source", "direction", "no_direction_frozen", "direction_basis",
            "verification_points", "exit_signals", "notes"]
    vals = []
    for c in cols:
        v = j.get(c)
        if c == "score_json" and isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)
        vals.append(v)
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(
            f"INSERT INTO trend_judgments ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
            vals)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def add_longlist(scan_date: str, candidate: str, reason: str, advanced: bool) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO trend_scan_longlist (scan_date, candidate, drop_reason, advanced)"
            " VALUES (?,?,?,?)",
            (scan_date, candidate, reason, 1 if advanced else 0))
        conn.commit()
    finally:
        conn.close()


def list_judgments(cohort: str | None = None) -> None:
    conn = sqlite3.connect(DB_PATH)
    q = ("SELECT id, judgment_date, trend_name, proxy_symbol, score_display, cohort,"
         " risk_cluster, trigger_source, COALESCE(direction,'—') FROM trend_judgments")
    args = ()
    if cohort:
        q += " WHERE cohort=?"
        args = (cohort,)
    q += " ORDER BY judgment_date, id"
    for r in conn.execute(q, args):
        print(" | ".join(str(x) for x in r))
    conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "add":
        jid = add_judgment(sys.argv[2])
        print(f"✅ judgment_id={jid} 已冻结登记")
    elif cmd == "longlist":
        add_longlist(sys.argv[2], sys.argv[3], sys.argv[4], "--advanced" in sys.argv)
        print("✅ 长名单已留痕")
    elif cmd == "list":
        list_judgments(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print(__doc__)
        sys.exit(1)
