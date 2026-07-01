"""
第2层趋势实验·对答案机械判定（cron 周一 17:15，幂等）

【是什么】trend_verdicts 判断层的唯一写入口——按方案预注册口径，对到期窗口的判断
样本自动拉价、机械判定、落库、Discord 报告。
【为什么做】方案防污染闸⑥（裁判自审）：verdict 必须由脚本按预注册口径机械判定
直接落库，BB（AI）无权改判——AI 只可另行 INSERT account_type='discrepancy' 的
标记行（附证据）报主公裁决。堵死"打分者推翻机械结果"的口子。
【为什么这样设计】
- 预注册口径（方案四节，2026-07-01 冻结）：
  A账排序力：全样本记连续相对收益（不判对错，organ=组间分布比较）；
  B账方向：看多=6m相对SPY≥+5%对/≤−5%错/中间待定；看空反之；观望=|x|<5%对；
  窗口 3m/6m/12m 全算（主口径=6m，其余辅助）；
  C账上下车：下车后 3 个月该标的 ≤−5%=躲跌 / ≥+5%=卖飞 / 中间=中性。
- 一律按"信号层买入持有"计算：入场=trend_signal_prices 的次日开盘价，
  窗口末=最后可得收盘价，不受中途下车影响（下车只进 C 账）。
- 幂等：同 (judgment, account, window) 已有 verdict 行则跳过；周频跑，到期即判。
- 顺手补缺的 trend_signal_prices（登记时次日开盘价还不存在，本脚本回填）。
【演进】2026-07-01 v0.2 首版。方案：notes/第2层提速攒样本方案_20260701.md
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


def last_close_before(symbol: str, date_str: str):
    """date_str（含）之前最后一个交易日收盘价 → (date, close)"""
    start = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=10)).strftime("%Y-%m-%d")
    end = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    h = yf.Ticker(symbol).history(start=start, end=end)
    if h.empty:
        return None, None
    return h.index[-1].strftime("%Y-%m-%d"), round(float(h["Close"].iloc[-1]), 4)


def fill_signal_prices(conn, report):
    rows = conn.execute(
        "SELECT j.id, j.judgment_date, j.proxy_symbol, j.sector_benchmark FROM trend_judgments j"
        " LEFT JOIN trend_signal_prices p ON p.judgment_id=j.id WHERE p.id IS NULL").fetchall()
    for jid, jdate, proxy, sector in rows:
        entry_date, proxy_open = first_open_after(proxy, jdate)
        if not entry_date:
            report.append(f"⚠️ j{jid} {proxy} 信号价未取到（可能还没到下一交易日）")
            continue
        _, spy_open = first_open_after("SPY", jdate)
        sector_open = None
        if sector and sector != "N/A":
            _, sector_open = first_open_after(sector, jdate)
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
        " p.entry_date, p.proxy_entry_price, p.spy_entry_price, p.sector_entry_price"
        " FROM trend_judgments j JOIN trend_signal_prices p ON p.judgment_id=j.id").fetchall()
    for jid, jdate, proxy, sector, direction, edate, p0, spy0, sec0 in rows:
        if not p0 or not spy0:
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
            d1, p1 = last_close_before(proxy, wend)
            _, spy1 = last_close_before("SPY", wend)
            if not p1 or not spy1:
                report.append(f"⚠️ j{jid} {proxy} {wname} 窗口末价格取不到，跳过")
                continue
            raw = (p1 / p0 - 1) * 100
            rel_spy = raw - (spy1 / spy0 - 1) * 100
            rel_sector = None
            if sector and sector != "N/A" and sec0:
                _, sec1 = last_close_before(sector, wend)
                if sec1:
                    rel_sector = raw - (sec1 / sec0 - 1) * 100
            basis = (f"入场{edate}@{p0}(SPY@{spy0}) 窗口末{d1}@{p1}(SPY@{spy1}) yfinance"
                     f" 口径=信号层买入持有 阈值±{THRESH}%")
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
    """C账：主动下车（下车信号/保命线）3 个月后回看——躲跌还是卖飞。"""
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
        p0 = xprice
        if not p0:
            _, p0 = last_close_before(symbol, xdate)
        d1, p1 = last_close_before(symbol, wend)
        _, spy0 = last_close_before("SPY", xdate)
        _, spy1 = last_close_before("SPY", wend)
        if not p0 or not p1:
            continue
        raw = (p1 / p0 - 1) * 100
        rel = raw - ((spy1 / spy0 - 1) * 100 if spy0 and spy1 else 0)
        verdict = "躲跌" if raw <= -THRESH else ("卖飞" if raw >= THRESH else "中性")
        conn.execute(
            "INSERT INTO trend_verdicts (judgment_id, account_type, window, raw_return,"
            " rel_spy, verdict, verdict_date, basis, mechanical) VALUES (?,?,?,?,?,?,?,?,1)",
            (jid, "C_exit", "post_exit_3m", round(raw, 2), round(rel, 2), verdict, today,
             f"下车{xdate}@{p0} 3月后{d1}@{p1} 原因={reason} 阈值±{THRESH}%"))
        report.append(f"🚪 C账 j{jid} {symbol} 下车后3月 {raw:+.1f}% → {verdict}")
    conn.commit()


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
    fill_signal_prices(conn, report)
    check_windows(conn, report)
    check_exits(conn, report)
    conn.close()
    for line in report:
        print(line)
    new_verdicts = [l for l in report if l.startswith(("📊", "🚪"))]
    if new_verdicts:
        send_discord(env, "📐 第2层对答案（机械判定，BB无权改判）：\n" + "\n".join(new_verdicts))
    else:
        print("本轮无到期窗口")


if __name__ == "__main__":
    run_with_alert("trend_verdict_check", main)
