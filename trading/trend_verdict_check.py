"""
第2层趋势实验·对答案机械判定（cron 周一 17:15，幂等）

【是什么】trend_verdicts 判断层的唯一写入口——按方案预注册口径，对到期窗口的判断
样本自动拉价、机械判定、落库、Discord 报告。
【为什么做】方案防污染闸⑥（裁判自审）：verdict 必须由脚本按预注册口径机械判定
直接落库，BB（AI）无权改判——AI 只可另行 INSERT account_type='discrepancy' 的
标记行（附证据）报主公裁决。堵死"打分者推翻机械结果"的口子。
【为什么这样设计】
- 预注册口径（方案二节三本账 + v0.2.2 修订记录，2026-07-01 冻结）：
  A账排序力：全样本记连续相对收益（不判对错，只供组间分布比较）；
  B账方向：看多=6m相对SPY≥+5%对/≤−5%错/中间待定；看空反向；观望=|x|<5%对否则错；
  窗口 3m/6m/12m 全算（主口径=6m，其余辅助）；
  C账上下车：下车后 3 个月**相对 SPY** ≤−5%=躲跌 / ≥+5%=卖飞 / 中间=中性（仅判首次下车）。
- 收益口径（v0.2.2）：auto_adjust 复权总收益，p0/p1 取自**同一次拉取的同基准序列**
  （p0=冻结 entry_date 开盘、p1=窗口末最后可得收盘）；trend_signal_prices 的存价只作
  登记时点存证，不进收益计算——否则分红摊派会让新旧复权基准漂 1-2%，污染±5%阈值。
- 退市/长期停牌（v0.2.2 预注册）：以最后可得收盘价为终值计入窗口，禁止静默排除
  （退市多为极端亏损结局，漏掉会系统性扭曲组间比较）。
- 一律按"信号层买入持有"，不受中途下车影响（下车只进 C 账）。
- 幂等：同 (judgment, account, window) 已有 verdict 行则跳过；作废样本（void 留痕行）跳过。
- 顺手补缺的 trend_signal_prices（proxy+SPY 缺一不写，禁止残行）。
- 完整性哨兵：5 表行数+缺号+内容哈希追加写 notes/trend_integrity_log.txt（git 追踪），
  未登记缺号→Discord 告警（触发器防不了有 shell 的人，哨兵防"改了没人发现"）。
【演进】2026-07-01 v0.2 首版；同日 v0.2.2 二轮审计修复（同基准复算/C账相对SPY/退市规则/
void 排除/哨兵/无静默跳过）。方案：notes/第2层提速攒样本方案_20260701.md
"""
import sqlite3
import os
import sys
from datetime import datetime, timedelta

import requests
import yfinance as yf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tide_utils import load_env, run_with_alert

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trading.db")
DISCORD_API_BASE = "https://discord.com/api/v10"
WINDOWS = {"3m": 3, "6m": 6, "12m": 12}
THRESH = 5.0  # B/C 账判定阈值 %（预注册，2026-07-01 冻结）


def add_months(date_str: str, n: int) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    y, m = d.year + (d.month - 1 + n) // 12, (d.month - 1 + n) % 12 + 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return f"{y:04d}-{m:02d}-{day:02d}"


def first_open_after(symbol: str, date_str: str):
    """date_str 之后第一个交易日的开盘价 → (entry_date, open_price)"""
    start = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    end = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=10)).strftime("%Y-%m-%d")
    h = yf.Ticker(symbol).history(start=start, end=end)
    if h.empty:
        return None, None
    return h.index[0].strftime("%Y-%m-%d"), round(float(h["Open"].iloc[0]), 4)


def open_on(symbol: str, date_str: str):
    """date_str 当日开盘价——SPY/板块基线与 proxy 锚定同一 entry_date（防各自取'下一交易日'错位）"""
    end = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    h = yf.Ticker(symbol).history(start=date_str, end=end)
    if h.empty:
        return None
    return round(float(h["Open"].iloc[0]), 4)


def window_prices(symbol: str, start_date: str, window_end: str, p0_field: str = "Open",
                  anchor: str = "exact"):
    """v0.2.2 同基准复算：一次拉取的复权序列取 p0/p1；p1=窗口末（含）最后可得收盘
    ——序列提前断掉即退市/停牌，按预注册规则以最后可得收盘为终值。
    anchor='exact'：p0 必须正好是 start_date（A/B 账，入场日=次日开盘必为交易日）；
    anchor='on_or_before'（v0.2.3）：p0=start_date（含）之前最近交易日——C 账专用，
    下车日可能落在假日/周末（周检恰排周一，MLK/国殇日真实场景），exact 会永久卡重试。
    返回 (p0, p1, 终值日期, p0锚定日) 或 (None, None, 原因, None)。"""
    fetch_start = start_date
    if anchor == "on_or_before":
        fetch_start = (datetime.strptime(start_date, "%Y-%m-%d")
                       - timedelta(days=7)).strftime("%Y-%m-%d")
    end = (datetime.strptime(window_end, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    h = yf.Ticker(symbol).history(start=fetch_start, end=end)
    if h.empty:
        return None, None, "序列为空", None
    dates = [i.strftime("%Y-%m-%d") for i in h.index]
    if anchor == "exact":
        if dates[0] != start_date:
            return None, None, f"序列起点{dates[0]}≠锚定日{start_date}", None
        i0 = 0
    else:
        cands = [i for i, d in enumerate(dates) if d <= start_date]
        if not cands:
            return None, None, f"锚定日{start_date}前7天无交易日数据", None
        i0 = cands[-1]
    return (round(float(h[p0_field].iloc[i0]), 4), round(float(h["Close"].iloc[-1]), 4),
            dates[-1], dates[i0])


def fill_signal_prices(conn, report):
    rows = conn.execute(
        "SELECT j.id, j.judgment_date, j.proxy_symbol, j.sector_benchmark FROM trend_judgments j"
        " LEFT JOIN trend_signal_prices p ON p.judgment_id=j.id WHERE p.id IS NULL").fetchall()
    for jid, jdate, proxy, sector in rows:
        entry_date, proxy_open = first_open_after(proxy, jdate)
        if not entry_date:
            report.append(f"⚠️ j{jid} {proxy} 信号价未取到（可能还没到下一交易日）")
            continue
        spy_open = open_on("SPY", entry_date)  # 锚定 proxy 的 entry_date 同日
        if not spy_open:
            report.append(f"⚠️ j{jid} SPY 基线价未取到（{entry_date}），本行不写（proxy+SPY 缺一不写，禁止残行）")
            continue
        sector_open = None
        if sector and sector != "N/A":
            sector_open = open_on(sector, entry_date)
            if sector_open is None:
                report.append(f"⚠️ j{jid} 板块基线 {sector} 未取到（{entry_date}），行照写、rel_sector 永久缺失（辅助口径）")
        conn.execute(
            "INSERT INTO trend_signal_prices (judgment_id, entry_date, proxy_entry_price,"
            " spy_entry_price, sector_entry_price, source) VALUES (?,?,?,?,?,'yfinance')",
            (jid, entry_date, proxy_open, spy_open, sector_open))
        report.append(f"📌 j{jid} {proxy} 信号价冻结：{entry_date} 开盘 {proxy_open}")
    conn.commit()


def judge_b(direction: str, rel_spy: float) -> str:
    if direction == "long":
        return "对" if rel_spy >= THRESH else ("错" if rel_spy <= -THRESH else "待定")
    if direction == "short":
        return "对" if rel_spy <= -THRESH else ("错" if rel_spy >= THRESH else "待定")
    if direction == "neutral":
        return "对" if abs(rel_spy) < THRESH else "错"
    return "待定"


def check_windows(conn, report):
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT j.id, j.judgment_date, j.proxy_symbol, j.sector_benchmark, j.direction,"
        " p.entry_date, p.proxy_entry_price, p.spy_entry_price"
        " FROM trend_judgments j JOIN trend_signal_prices p ON p.judgment_id=j.id").fetchall()
    for jid, jdate, proxy, sector, direction, edate, p0_frozen, spy0_frozen in rows:
        if conn.execute("SELECT 1 FROM trend_verdicts WHERE judgment_id=?"
                        " AND account_type='void'", (jid,)).fetchone():
            report.append(f"⏭️ j{jid} {proxy} 已作废（void 留痕行），不进统计")
            continue
        for wname, months in WINDOWS.items():
            wend = add_months(jdate, months)
            if wend > today:
                continue
            done = conn.execute(
                "SELECT 1 FROM trend_verdicts WHERE judgment_id=? AND window=?"
                " AND account_type IN ('A_ranking','B_direction')", (jid, wname)).fetchone()
            if done:
                continue
            p0, p1, pend, _ = window_prices(proxy, edate, wend)
            if p0 is None:
                report.append(f"⚠️ j{jid} {proxy} {wname} 代理序列问题（{pend}），本窗口未判，下周重试")
                continue
            spy0, spy1, _, _ = window_prices("SPY", edate, wend)
            if spy0 is None:
                report.append(f"⚠️ j{jid} SPY {wname} 基准序列问题，本窗口未判，下周重试")
                continue
            raw = (p1 / p0 - 1) * 100
            rel_spy = raw - (spy1 / spy0 - 1) * 100
            rel_sector = None
            if sector and sector != "N/A":
                s0, s1, _, _ = window_prices(sector, edate, wend)
                if s0 is not None:
                    rel_sector = raw - (s1 / s0 - 1) * 100
            basis = (f"同基准复算(auto_adjust总收益): 入场{edate}开盘{p0}(登记存证{p0_frozen})"
                     f" 窗口末{pend}收盘{p1}; SPY {spy0}->{spy1}(存证{spy0_frozen}); yfinance"
                     f" 口径=信号层买入持有 阈值±{THRESH}% 退市规则=最后可得收盘为终值")
            conn.execute(
                "INSERT INTO trend_verdicts (judgment_id, account_type, window, raw_return,"
                " rel_spy, rel_sector, verdict, verdict_date, basis, mechanical)"
                " VALUES (?,?,?,?,?,?,?,?,?,1)",
                (jid, "A_ranking", wname, round(raw, 2), round(rel_spy, 2),
                 round(rel_sector, 2) if rel_sector is not None else None,
                 "记录", today, basis))
            line = f"j{jid} {proxy} {wname}: 原始{raw:+.1f}% 相对SPY{rel_spy:+.1f}%"
            if direction:  # B账只对冻结了方向的样本
                bv = judge_b(direction, rel_spy)
                conn.execute(
                    "INSERT INTO trend_verdicts (judgment_id, account_type, window, raw_return,"
                    " rel_spy, rel_sector, verdict, verdict_date, basis, mechanical)"
                    " VALUES (?,?,?,?,?,?,?,?,?,1)",
                    (jid, "B_direction", wname, round(raw, 2), round(rel_spy, 2),
                     round(rel_sector, 2) if rel_sector is not None else None,
                     bv, today, basis + f" 方向={direction}"))
                line += f" | B账[{direction}]→{bv}"
            report.append("📊 " + line)
    conn.commit()


def check_exits(conn, report):
    """C账（v0.2.2 预注册口径）：主动下车后 3 个月，按**相对 SPY** 判"躲跌/卖飞/中性"
    （大盘崩时下车躲的是市场的跌，躲掉超额下跌才证明下车信号有效——主公 2026-07-01 拍板）。
    p0=下车日（含）之前最近交易日收盘（v0.2.3：下车可能落在假日/周末）、
    p1=+3m 最后可得收盘，同一复权序列；成交价只作执行层存证。
    仅判首次下车（同 judgment 再买入再下车不进 C 账，预注册）。"""
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT t.id, t.judgment_id, t.symbol, t.exit_date, t.exit_fill_price, t.exit_reason"
        " FROM trend_paper_trades t WHERE t.status='closed' AND t.exit_date IS NOT NULL"
        " AND (t.exit_reason LIKE '下车信号%' OR t.exit_reason LIKE '保命线%')").fetchall()
    for tid, jid, symbol, xdate, xprice, reason in rows:
        wend = add_months(xdate, 3)
        if wend > today:
            continue
        done = conn.execute(
            "SELECT 1 FROM trend_verdicts WHERE judgment_id=? AND account_type='C_exit'"
            " AND window='post_exit_3m'", (jid,)).fetchone()
        if done:
            continue
        p0, p1, pend, p0d = window_prices(symbol, xdate, wend, p0_field="Close",
                                          anchor="on_or_before")
        if p0 is None:
            report.append(f"⚠️ C账 j{jid} {symbol} 序列问题（{pend}），未判，下周重试")
            continue
        spy0, spy1, _, _ = window_prices("SPY", xdate, wend, p0_field="Close",
                                         anchor="on_or_before")
        if spy0 is None:
            report.append(f"⚠️ C账 j{jid} SPY 基准序列问题，未判，下周重试")
            continue
        raw = (p1 / p0 - 1) * 100
        rel = raw - (spy1 / spy0 - 1) * 100
        verdict = "躲跌" if rel <= -THRESH else ("卖飞" if rel >= THRESH else "中性")
        conn.execute(
            "INSERT INTO trend_verdicts (judgment_id, account_type, window, raw_return,"
            " rel_spy, verdict, verdict_date, basis, mechanical) VALUES (?,?,?,?,?,?,?,?,1)",
            (jid, "C_exit", "post_exit_3m", round(raw, 2), round(rel, 2), verdict, today,
             f"C账v0.2.3(相对SPY判): 下车{xdate}锚定{p0d}收盘{p0}(成交存证{xprice}) 3月后{pend}收盘{p1};"
             f" SPY {spy0}->{spy1}; yfinance auto_adjust 阈值±{THRESH}% 原因={reason} 仅判首次下车"))
        report.append(f"🚪 C账 j{jid} {symbol} 下车后3月 原始{raw:+.1f}% 相对SPY{rel:+.1f}% → {verdict}")
    conn.commit()


INTEGRITY_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "notes", "trend_integrity_log.txt")
KNOWN_ID_GAPS = {"trend_judgments": {1}}  # id=1='__test__'建库冒烟测试行（方案v0.2.2修订记录有案）


def integrity_sentinel(conn, report):
    """完整性哨兵（v0.2.2 审计攻击面#1）：5 表行数+缺号+内容哈希追加写 git 追踪文件。
    触发器防不了有 shell 的人；哨兵防的是"改了没人发现"——未登记缺号→Discord 告警，
    内容哈希变化可与 git 历史/每日 rclone 备份比对定位篡改时点。"""
    import hashlib
    parts = []
    for t in ("trend_judgments", "trend_signal_prices", "trend_paper_trades",
              "trend_verdicts", "trend_scan_longlist"):
        rows = conn.execute(f"SELECT * FROM {t} ORDER BY 1").fetchall()
        seq_row = conn.execute("SELECT seq FROM sqlite_sequence WHERE name=?", (t,)).fetchone()
        seq = seq_row[0] if seq_row else 0
        unexplained = set(range(1, seq + 1)) - {r[0] for r in rows} - KNOWN_ID_GAPS.get(t, set())
        if unexplained:
            report.append(f"🚨 完整性哨兵：{t} 未登记缺号 {sorted(unexplained)}（seq={seq}）"
                          f"——冻结层可能被绕闸删行，须人工核查")
        parts.append(f"{t}:n={len(rows)},seq={seq},"
                     f"md5={hashlib.md5(repr(rows).encode()).hexdigest()[:12]}")
    with open(INTEGRITY_LOG, "a", encoding="utf-8") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M") + " | " + " | ".join(parts) + "\n")


def send_discord(env, message):
    token, channel_id = env.get("DISCORD_BOT_TOKEN"), env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        print("[trend_verdict] 缺 Discord 配置，跳过")
        return
    try:
        requests.post(f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
                      headers={"Authorization": f"Bot {token}",
                               "Content-Type": "application/json"},
                      json={"content": message[:1900]}, timeout=15).raise_for_status()
    except Exception as e:
        print(f"[trend_verdict] Discord 发送失败: {e}")


def main():
    env = load_env()
    conn = sqlite3.connect(DB_PATH)
    report = []
    try:
        fill_signal_prices(conn, report)
        check_windows(conn, report)
        check_exits(conn, report)
        integrity_sentinel(conn, report)
    finally:
        # 已 commit 的 verdict 必须报出去——中途 crash 也把已产出的部分发掉，
        # 否则幂等跳过会让判定永远静默（审计次要-6）
        conn.close()
        for line in report:
            print(line)
        noteworthy = [l for l in report if l.startswith(("📊", "🚪", "🚨"))]
        if noteworthy:
            send_discord(env, "📐 第2层对答案（机械判定，BB无权改判）：\n" + "\n".join(noteworthy))
        else:
            print("本轮无到期窗口")


if __name__ == "__main__":
    run_with_alert("trend_verdict_check", main)
