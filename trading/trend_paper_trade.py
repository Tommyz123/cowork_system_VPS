"""
第2层趋势实验·纸仓下单 CLI（intraday 纸账户专用，物理锁死）

【是什么】trend_paper_trades 执行层的唯一写入口——在 Alpaca intraday 纸账户上
按统一金额 $25,000/笔 建仓/平仓，并把客观成交事实写入 DB。
【为什么做】方案规则1/2/5：passed/borderline 建纸仓；下车信号触发纸面卖出。
【为什么这样设计】
- 账号锁死 intraday（TREND_ACCOUNT + assert_trend_account）：镜像第1层
  config.assert_p9_account 的硬闸手法、方向相反——第1层锁 swing 防写 intraday，
  本实验锁 intraday 防污染第1层 swing。两套账本物理隔离。
- 市价 day 单：执行细节不进主统计（主统计用信号层次日开盘价，见
  trend_signal_prices），成交价只如实记录在执行层。
- 只对 cohort in (passed, borderline) 且 direction != short 的 judgment 放行
  （rejected 只信号层记账；看空不做纸面做空——方案规则2）。
【用法】
  python3 trend_paper_trade.py buy <judgment_id>            # 建仓 $25,000 市价
  python3 trend_paper_trade.py sell <judgment_id> <原因>     # 平仓（下车信号|保命线|12m终判到期）
  python3 trend_paper_trade.py sync                         # 回填成交价（下单后次日跑）
  python3 trend_paper_trade.py positions                    # 看 intraday 实时持仓
【演进】2026-07-01 v0.2 首版。方案：notes/第2层提速攒样本方案_20260701.md
"""
import json
import sqlite3
import sys
import os
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tide_utils import load_env  # 铁律：不本地复制 load_env

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading.db")
NOTIONAL = 25000.0  # 统一金额（2026-07-01 主公确认：权益$1,006,475÷40 取整）
TREND_ACCOUNT = "intraday"
ALLOWED_TREND_ACCOUNTS = ("intraday",)
EXPECTED_ACCOUNT_NUMBER = "PA3HOPG4XQ0O"  # intraday 账户身份号（key 可轮换，账户号不变；2026-07-01 实测核对）


def assert_trend_account(account: str) -> None:
    """第2层实验所有写操作必须先过这道闸——只许 intraday，绝不许碰第1层的 swing。"""
    if account not in ALLOWED_TREND_ACCOUNTS:
        raise ValueError(
            f"第2层账号路由违规：尝试在 '{account}' 执行写操作，只允许 {ALLOWED_TREND_ACCOUNTS}。"
            f"swing 是第1层 TIDE 专用账本，两层物理隔离（方案规则1）。")


def _api(env, path, payload=None, method="GET"):
    base = env["ALPACA_ENDPOINT"].rstrip("/")
    headers = {"APCA-API-KEY-ID": env["ALPACA_API_KEY"],
               "APCA-API-SECRET-KEY": env["ALPACA_SECRET_KEY"],
               "Content-Type": "application/json"}
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def verify_account(env) -> None:
    """下单前运行时核对：ALPACA_* 默认 key 必须指向 intraday 账户本尊。
    assert_trend_account 只校验脚本内常量（约定层）；这道才是物理闸——
    key 轮换/env 被改指向时在此被拦（2026-07-01 审核项🟡1）。"""
    acct = _api(env, "/account")
    if acct.get("account_number") != EXPECTED_ACCOUNT_NUMBER:
        raise ValueError(
            f"账户核对失败：当前 key 指向 {acct.get('account_number')}，"
            f"预期 intraday={EXPECTED_ACCOUNT_NUMBER}。拒绝下单，请检查 ALPACA_* env 指向。")


def buy(judgment_id: int) -> None:
    assert_trend_account(TREND_ACCOUNT)
    conn = sqlite3.connect(DB_PATH)
    j = conn.execute(
        "SELECT proxy_symbol, cohort, direction, trend_name FROM trend_judgments WHERE id=?",
        (judgment_id,)).fetchone()
    if not j:
        raise ValueError(f"judgment_id={judgment_id} 不存在")
    symbol, cohort, direction, trend_name = j
    if cohort not in ("passed", "borderline"):
        raise ValueError(f"cohort={cohort} 不建纸仓（rejected 只信号层记账，方案规则2）")
    if direction == "short":
        raise ValueError("看空样本不做纸面做空（方案规则2），只信号层记账")
    if direction == "neutral":
        raise ValueError("观望(neutral)样本不建纸仓（v0.2.2 预注册：观望=不出手），只信号层记账")
    dup = conn.execute(
        "SELECT id FROM trend_paper_trades WHERE judgment_id=? AND status='open'",
        (judgment_id,)).fetchone()
    if dup:
        raise ValueError(f"judgment_id={judgment_id} 已有 open 纸仓 trade_id={dup[0]}")
    env = load_env()
    verify_account(env)
    order = _api(env, "/orders", {
        "symbol": symbol, "notional": str(NOTIONAL), "side": "buy",
        "type": "market", "time_in_force": "day"}, "POST")
    conn.execute(
        "INSERT INTO trend_paper_trades (judgment_id, symbol, account, entry_order_id,"
        " entry_date, notional, status) VALUES (?,?,?,?,date('now'),?, 'open')",
        (judgment_id, symbol, TREND_ACCOUNT, order["id"], NOTIONAL))
    conn.commit()
    conn.close()
    print(f"✅ 建仓单已提交：{trend_name} → {symbol} ${NOTIONAL:,.0f} 市价 "
          f"order_id={order['id']}（成交价明日 sync 回填）")


def sell(judgment_id: int, reason: str) -> None:
    assert_trend_account(TREND_ACCOUNT)
    valid = ("下车信号", "保命线", "12m终判到期")
    if not any(reason.startswith(v) for v in valid):
        raise ValueError(f"平仓原因必须以 {valid} 之一开头（方案规则5），收到: {reason}")
    conn = sqlite3.connect(DB_PATH)
    t = conn.execute(
        "SELECT id, symbol, qty FROM trend_paper_trades"
        " WHERE judgment_id=? AND status='open'", (judgment_id,)).fetchone()
    if not t:
        raise ValueError(f"judgment_id={judgment_id} 无 open 纸仓")
    trade_id, symbol, qty = t
    if not qty:
        raise ValueError(
            f"trade {trade_id} 的 qty 未回填（先跑 sync，下单次日）——"
            f"必须按本笔 qty 平仓，禁止按 symbol 全平（两条趋势共用代理时会误平别人的仓，v0.2.2 审计重要-6）")
    env = load_env()
    verify_account(env)
    order = _api(env, "/orders", {
        "symbol": symbol, "qty": str(qty), "side": "sell",
        "type": "market", "time_in_force": "day"}, "POST")  # 按本笔 qty 反向市价，只平自己的份额
    conn.execute(
        "UPDATE trend_paper_trades SET exit_order_id=?, exit_date=date('now'),"
        " exit_reason=?, status='closed' WHERE id=?",
        (order["id"], reason, trade_id))
    conn.commit()
    conn.close()
    print(f"✅ 平仓单已提交：{symbol} 原因={reason}（成交价明日 sync 回填）")


def sync() -> None:
    """回填成交价（幂等）：查 Alpaca 订单终态，把 fill 价/数量写回执行层。"""
    env = load_env()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, entry_order_id, exit_order_id FROM trend_paper_trades"
        " WHERE (entry_fill_price IS NULL AND entry_order_id IS NOT NULL)"
        " OR (status='closed' AND exit_fill_price IS NULL AND exit_order_id != '')").fetchall()
    for trade_id, eid, xid in rows:
        if eid:
            cur = conn.execute("SELECT entry_fill_price FROM trend_paper_trades WHERE id=?",
                               (trade_id,)).fetchone()
            if cur[0] is None:
                o = _api(env, f"/orders/{eid}")
                if o.get("filled_avg_price"):
                    conn.execute(
                        "UPDATE trend_paper_trades SET entry_fill_price=?, qty=? WHERE id=?",
                        (float(o["filled_avg_price"]), float(o["filled_qty"]), trade_id))
                    print(f"trade {trade_id} entry fill {o['filled_avg_price']} x {o['filled_qty']}")
        if xid:
            o = _api(env, f"/orders/{xid}")
            if o.get("filled_avg_price"):
                conn.execute("UPDATE trend_paper_trades SET exit_fill_price=? WHERE id=?",
                             (float(o["filled_avg_price"]), trade_id))
                print(f"trade {trade_id} exit fill {o['filled_avg_price']}")
    conn.commit()
    conn.close()
    print("✅ sync 完成")


def positions() -> None:
    env = load_env()
    verify_account(env)  # 只读，但看错账户的持仓会误导人工下车决策
    for p in _api(env, "/positions"):
        print(p["symbol"], p["qty"], "@", p["avg_entry_price"],
              "pnl%:", round(float(p["unrealized_plpc"]) * 100, 2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "buy":
        buy(int(sys.argv[2]))
    elif cmd == "sell":
        sell(int(sys.argv[2]), sys.argv[3])
    elif cmd == "sync":
        sync()
    elif cmd == "positions":
        positions()
    else:
        print(__doc__)
        sys.exit(1)
