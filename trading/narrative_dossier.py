#!/usr/bin/env python3
"""
公司叙事追踪系统 · 档案核心（建表 + 手动录入接口）
================================================================
是什么：
  P9「主题累积研究 Loop」的公司粒度分支 MVP。给"还没建仓 / 观察期"的公司
  建一组活的"假设"，新闻只能去推动假设变化，定期对答案。
  方案定稿见 trading/notes/新闻追踪方案_2026-06-27.md。

为什么做：
  现有 thesis_monitor / scanner_picks / dossier_autowrite 全围绕"已建仓持仓票"，
  缺"建仓前研究跟踪"这一环。主公 2026-06-27 提出"新闻追踪"需求。

为什么这样设计（核心哲学，不可动）：
  「新闻不是资产，假设才是资产。绑不到任何假设的信息不准进档案。」
  这是防止系统沦为"勤奋新闻笔记库"的根。判断是否笔记库的唯一标准=改变过决策没有。

边界铁律（防与现有系统打架）：
  对象一旦真建仓 → 假设追踪移交 thesis_monitor/scanner_picks，本档案归档
  （status 置 '已移交持仓监控'）。本系统只管建仓前观察期。

演进：
  MVP=3表(假设/证据/周记)+1闸(绑不到假设就丢)+人肉录入，先 VST 1只跑 6-8 周。
  通过后再铺 3 只 + 按需加 Codex 那些零件(冷缓存/档案预算/自动 agent)。

用法：
  python3 narrative_dossier.py init                # 建表（幂等）
  python3 narrative_dossier.py add-hypo <ticker>   # 交互录一条假设
  python3 narrative_dossier.py add-evi             # 交互录一条证据（必须绑假设）
  python3 narrative_dossier.py checkin <ticker>    # 交互填一行周记
  python3 narrative_dossier.py show <ticker>       # 看某票当前档案全貌
"""
import sqlite3
import sys
from datetime import datetime

DB_PATH = "/home/cowork/cowork/trading/trading.db"

# ── 状态/枚举词表（防自由发挥乱填）─────────────────────────
HYPO_STATUS = ["成立中", "被强化", "被削弱", "已失效", "已移交持仓监控"]
HYPO_IMPORTANCE = ["核心", "次要", "仅观察"]
EVI_DIRECTION = ["支持", "反对"]
ACTION_VIEW = ["买", "持", "加", "减", "避", "等"]


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today():
    return datetime.now().strftime("%Y-%m-%d")


def conn():
    return sqlite3.connect(DB_PATH)


# ── 第1步：建表 ───────────────────────────────────────────
def init_tables():
    c = conn()
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS narrative_hypotheses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            statement TEXT NOT NULL,
            trigger_condition TEXT,
            invalidation_condition TEXT,
            confidence INTEGER DEFAULT 3,        -- 1-5
            status TEXT DEFAULT '成立中',
            importance TEXT DEFAULT '核心',       -- 核心/次要/仅观察
            next_review_date TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS narrative_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hypothesis_id INTEGER NOT NULL,       -- 绑不到假设就别建
            direction TEXT,                       -- 支持/反对
            confidence_before INTEGER,
            confidence_after INTEGER,
            summary TEXT,                         -- 客观事实摘要，零主观
            source TEXT,
            source_type TEXT,                     -- SEC/PR/媒体/分析师...
            event_date TEXT,
            logged_at TEXT,
            FOREIGN KEY (hypothesis_id) REFERENCES narrative_hypotheses(id)
        );

        CREATE TABLE IF NOT EXISTS narrative_weekly_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            checkin_date TEXT,
            top_hypothesis_change TEXT,
            action_view TEXT,                     -- 买/持/加/减/避/等
            reason TEXT,
            what_changes_my_mind TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS narrative_discard_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            title TEXT,
            discard_date TEXT
        );
        """
    )
    c.commit()
    c.close()
    print("✅ 建表完成（幂等）：narrative_hypotheses / _evidence / _weekly_checkins / _discard_log")


# ── 交互辅助 ──────────────────────────────────────────────
def ask(prompt, choices=None, default=None):
    hint = f" {choices}" if choices else ""
    dh = f"（默认 {default}）" if default else ""
    while True:
        v = input(f"{prompt}{hint}{dh}: ").strip()
        if not v and default is not None:
            return default
        if choices and v not in choices:
            print(f"  ⚠️ 只能填 {choices}")
            continue
        if v:
            return v


def add_hypo(ticker):
    print(f"\n── 录入假设 [{ticker}] ──")
    statement = ask("假设内容(为什么能赚钱,用 may/could 语气)")
    trigger = ask("触发条件(带指标+阈值,如 Q3 backlog 同比+15%→加仓预警)")
    invalid = ask("失效条件(什么情况认错放弃)")
    conf = int(ask("当前信心 1-5", default="3"))
    importance = ask("重要性", HYPO_IMPORTANCE, default="核心")
    review = ask("下次必须复看日期 YYYY-MM-DD(如财报日)", default="")
    c = conn()
    cur = c.execute(
        """INSERT INTO narrative_hypotheses
           (ticker,statement,trigger_condition,invalidation_condition,
            confidence,status,importance,next_review_date,created_at,updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (ticker, statement, trigger, invalid, conf, "成立中",
         importance, review or None, now(), now()),
    )
    c.commit()
    hid = cur.lastrowid
    c.close()
    print(f"✅ 假设已入库 id={hid}")


def add_evi():
    print("\n── 录入证据（必须绑到某条假设，绑不到=不该存）──")
    list_open_hypos()
    hid = ask("绑哪条假设 id（绑不到任何假设就 Ctrl-C 退出、别硬塞）")
    c = conn()
    row = c.execute(
        "SELECT ticker,statement,confidence FROM narrative_hypotheses WHERE id=?",
        (hid,),
    ).fetchone()
    if not row:
        print("  ⚠️ 没有这条假设 id")
        c.close()
        return
    print(f"  → 绑定：[{row[0]}] {row[1]}（当前信心 {row[2]}）")
    direction = ask("方向", EVI_DIRECTION)
    cb = int(row[2])
    ca = int(ask(f"把信心从 {cb} 推到几", default=str(cb)))
    summary = ask("客观事实摘要(零主观,如'营收X 同比+Y%')")
    source = ask("来源(链接/出处)", default="")
    stype = ask("来源类型(SEC/PR/媒体/分析师/transcript)", default="媒体")
    edate = ask("事件日 YYYY-MM-DD", default=today())
    c.execute(
        """INSERT INTO narrative_evidence
           (hypothesis_id,direction,confidence_before,confidence_after,
            summary,source,source_type,event_date,logged_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (hid, direction, cb, ca, summary, source or None, stype, edate, now()),
    )
    # 同步更新假设信心 + 状态
    new_status = "被强化" if ca > cb else ("被削弱" if ca < cb else "成立中")
    c.execute(
        "UPDATE narrative_hypotheses SET confidence=?,status=?,updated_at=? WHERE id=?",
        (ca, new_status, now(), hid),
    )
    c.commit()
    c.close()
    print(f"✅ 证据已入库，假设信心 {cb}→{ca}，状态={new_status}")


def checkin(ticker):
    print(f"\n── 周记 [{ticker}] ──")
    change = ask("这周最大假设变化")
    action = ask("当前操作倾向", ACTION_VIEW)
    reason = ask("一句理由")
    mind = ask("下次什么会让我改主意")
    c = conn()
    c.execute(
        """INSERT INTO narrative_weekly_checkins
           (ticker,checkin_date,top_hypothesis_change,action_view,
            reason,what_changes_my_mind,created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (ticker, today(), change, action, reason, mind, now()),
    )
    c.commit()
    c.close()
    print(f"✅ 周记已记：[{ticker}] {today()} 操作倾向={action}")


def list_open_hypos():
    c = conn()
    rows = c.execute(
        """SELECT id,ticker,confidence,status,importance,statement
           FROM narrative_hypotheses
           WHERE status NOT IN ('已失效','已移交持仓监控')
           ORDER BY ticker,id"""
    ).fetchall()
    c.close()
    if not rows:
        print("  （暂无活跃假设）")
        return
    print("  活跃假设：")
    for r in rows:
        print(f"   id={r[0]} [{r[1]}] 信心{r[2]} {r[3]}/{r[4]} | {r[5][:50]}")


def show(ticker):
    c = conn()
    print(f"\n========== {ticker} 档案 ==========")
    hypos = c.execute(
        "SELECT * FROM narrative_hypotheses WHERE ticker=? ORDER BY id", (ticker,)
    ).fetchall()
    for h in hypos:
        print(f"\n【假设 id={h[0]}】信心{h[5]} 状态={h[6]} 重要性={h[7]} 复看={h[8]}")
        print(f"  内容: {h[2]}")
        print(f"  触发: {h[3]}")
        print(f"  失效: {h[4]}")
        evis = c.execute(
            "SELECT direction,confidence_before,confidence_after,summary,source_type,event_date "
            "FROM narrative_evidence WHERE hypothesis_id=? ORDER BY event_date", (h[0],)
        ).fetchall()
        for e in evis:
            print(f"   · [{e[5]}] {e[0]} 信心{e[1]}→{e[2]} ({e[4]}) {e[3]}")
    print("\n--- 最近周记 ---")
    cks = c.execute(
        "SELECT checkin_date,action_view,top_hypothesis_change,reason "
        "FROM narrative_weekly_checkins WHERE ticker=? ORDER BY checkin_date DESC LIMIT 5",
        (ticker,),
    ).fetchall()
    for ck in cks:
        print(f"  {ck[0]} 操作={ck[1]} | {ck[2]} | {ck[3]}")
    c.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "init":
        init_tables()
    elif cmd == "add-hypo":
        init_tables()
        add_hypo(sys.argv[2] if len(sys.argv) > 2 else ask("ticker"))
    elif cmd == "add-evi":
        add_evi()
    elif cmd == "checkin":
        checkin(sys.argv[2] if len(sys.argv) > 2 else ask("ticker"))
    elif cmd == "show":
        show(sys.argv[2] if len(sys.argv) > 2 else ask("ticker"))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
