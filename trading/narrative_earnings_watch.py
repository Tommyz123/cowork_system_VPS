#!/usr/bin/env python3
"""
公司叙事追踪系统 · 财报日哨兵
================================================================
是什么：
  公司叙事追踪 MVP 的唯一自动化部分。每天扫一遍正在追踪的公司，
  yfinance 查它们下次财报日，临近(默认 ≤5 天)就 Discord 提醒主公"该对答案了"。
  方案见 trading/notes/新闻追踪方案_2026-06-27.md。

为什么这样设计：
  - 追踪对象**从 narrative_hypotheses 表解析**(数据驱动,不硬编码 ticker)；
    以后增删追踪公司,本脚本一行不用改(承袭 feedback_data_driven_no_hardcode)。
  - 财报日**只当提醒不当死排期**：yfinance 财报日会变/是预估,
    每次重查、记抓取时间,不写死(Codex 一审提醒)。
  - 失败走 tide_utils.run_with_alert 邮件告警(正式 cron 规范)。

为什么是哨兵不是全自动：
  财报日是"假设对答案"的关键节点。脚本只负责"到点叫人",
  真正的对答案(假设触发/失效判断)仍由 CC 人肉做(MVP 不上 agent 链)。

用法：
  python3 narrative_earnings_watch.py          # 正常跑(cron)
  python3 narrative_earnings_watch.py --dry    # 只打印不发 Discord
"""
import sqlite3
import sys
from datetime import datetime, date

import requests

from tide_utils import load_env, run_with_alert

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"
REMIND_WITHIN_DAYS = 5

try:
    import yfinance as yf
    YF_OK = True
except Exception:
    YF_OK = False


def tracked_tickers():
    """从假设表解析在追踪的公司（排除已失效/已移交持仓的）。"""
    c = sqlite3.connect(DB_PATH)
    rows = c.execute(
        """SELECT DISTINCT ticker FROM narrative_hypotheses
           WHERE status NOT IN ('已失效','已移交持仓监控')
           ORDER BY ticker"""
    ).fetchall()
    c.close()
    return [r[0] for r in rows]


def next_earnings(ticker):
    """查下次财报日。返回 date 或 None。财报日会变,每次重查。"""
    if not YF_OK:
        return None
    try:
        cal = yf.Ticker(ticker).calendar
        ed = cal.get("Earnings Date") if isinstance(cal, dict) else None
        if not ed:
            return None
        d = ed[0] if isinstance(ed, (list, tuple)) else ed
        if isinstance(d, datetime):
            return d.date()
        return d
    except Exception:
        return None


def send_discord(env, message):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        print("⚠️ 缺 DISCORD_BOT_TOKEN/CHANNEL_ID，跳过发送")
        return
    try:
        requests.post(
            f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
            headers={"Authorization": f"Bot {token}",
                     "Content-Type": "application/json"},
            json={"content": message},
            timeout=15,
        )
    except Exception as e:
        print(f"⚠️ Discord 发送失败：{e}")


def _main():
    dry = "--dry" in sys.argv
    env = load_env()
    tickers = tracked_tickers()
    fetched = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[narrative_earnings_watch] yf={YF_OK} 追踪 {len(tickers)} 票: {tickers}")
    if not tickers:
        print("无追踪对象，结束。")
        return

    today = date.today()
    due = []
    for t in tickers:
        ed = next_earnings(t)
        if ed is None:
            print(f"  {t}: 财报日查不到（跳过，不报错）")
            continue
        days = (ed - today).days
        print(f"  {t}: 下次财报 {ed}（{days} 天后, 抓取于 {fetched}）")
        if 0 <= days <= REMIND_WITHIN_DAYS:
            due.append((t, ed, days))

    if due:
        lines = ["📅 **叙事追踪 · 财报临近提醒**", ""]
        for t, ed, d in due:
            lines.append(f"• **{t}** 将于 {ed}（{d}天后）发财报 → 该对照假设触发/失效条件对答案了")
        lines.append("")
        lines.append(f"_（财报日为 yfinance 估算, 抓取于 {fetched}, 可能变动）_")
        msg = "\n".join(lines)
        if dry:
            print("\n[DRY RUN] 本应发送：\n" + msg)
        else:
            send_discord(env, msg)
            print(f"\n✅ 已提醒 {len(due)} 票财报临近")
    else:
        print("无财报临近，不打扰。")


def main():
    run_with_alert("narrative_earnings_watch", _main)


if __name__ == "__main__":
    main()
