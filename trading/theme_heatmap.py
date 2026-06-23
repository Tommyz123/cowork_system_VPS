#!/usr/bin/env python3
"""
信号升温榜（theme heatmap）——P9 第2层趋势主线 / theme_discovery 阶段0 排雷工具。

【是什么】每周一自动列一张表：最近哪些股票的新闻/信号突然变多了（升温），
         并标好坏消息（🟢利好扎堆/🔴利空扎堆）+ 板块 + 是否已持仓，发 Discord 给主公。

【为什么做】P9 现在天天采信号（trading.db signals 表）但只在"已选股"上用，
         132 只持仓外股票的 1376 条高质信号"堆在仓库没进选股视野"。本榜把这些
         升温异动捞出来，验证地基假设"信号聚集→能预示主题机会"是否成立。

【为什么这样设计】
  - 升温=近30天信号数 vs 前90天基线日均的倍数（突然冒头才是信号，不是绝对数量）
  - 好坏消息标记：避开"信号多但全是利空"的陷阱（VRRM 升温45x 实为暴跌-70%的坏消息扎堆）
  - 纯读 DB 出报告，不碰下单、不改任何现有 P9 逻辑（零风险，阶段0只观察）

【演进】阶段0=本脚本(人工看表+人肉判断打分,排雷)→ 阶段1=判断档案+审计员子agent自动打分
       → 阶段2=接进 theme_discovery 自动化。详见对话 2026-06-23 + loop_engineering 方法论。

用法：python3 trading/theme_heatmap.py
"""
import sqlite3
from datetime import datetime

import requests

from tide_utils import load_env

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"

# 升温判定参数
RECENT_DAYS = 30          # 近期窗口
BASE_DAYS = 90            # 基线窗口（紧挨着近期窗口之前的 90 天）
MIN_RECENT_SIGNALS = 3    # 近30天至少 N 条信号才上榜（噪音门槛）
TOP_N = 15                # 榜单最多列几只

# 好坏消息关键词（粗筛，阶段0够用；阶段1可换更准的情绪模型）
GOOD_WORDS = ['beat', 'surge', 'soar', 'record', 'raise', 'upgrade', 'win', 'award',
              'contract', 'growth', 'strong', 'expand', 'partnership', 'approval', 'launch']
BAD_WORDS = ['miss', 'fall', 'drop', 'plunge', 'cut', 'downgrade', 'lawsuit', 'investigation',
             'decline', 'weak', 'loss', 'terminate', 'recall', 'warning', 'probe', 'delay']


def classify_sentiment(conn, symbol):
    """扫近30天 headline 关键词，粗判好坏消息倾向。返回 (标签, 好数, 坏数)。"""
    rows = conn.execute(
        "SELECT headline FROM signals WHERE symbol=? AND date >= date('now',?)",
        (symbol, f"-{RECENT_DAYS} days"),
    ).fetchall()
    good = bad = 0
    for (h,) in rows:
        if not h:
            continue
        hl = h.lower()
        good += sum(1 for w in GOOD_WORDS if w in hl)
        bad += sum(1 for w in BAD_WORDS if w in hl)
    if good > bad * 1.5:
        return f"🟢偏好({good}好/{bad}坏)", good, bad
    if bad > good * 1.5:
        return f"🔴偏坏({good}好/{bad}坏)", good, bad
    return f"⚪中性({good}好/{bad}坏)", good, bad


def build_heatmap(conn):
    """算升温榜，返回排好序的行列表。"""
    recent = dict(conn.execute(
        "SELECT symbol, COUNT(*) FROM signals WHERE date >= date('now',?) GROUP BY symbol",
        (f"-{RECENT_DAYS} days",),
    ).fetchall())
    base = dict(conn.execute(
        "SELECT symbol, COUNT(*) FROM signals WHERE date >= date('now',?) AND date < date('now',?) GROUP BY symbol",
        (f"-{RECENT_DAYS + BASE_DAYS} days", f"-{RECENT_DAYS} days"),
    ).fetchall())
    held = {r[0] for r in conn.execute(
        "SELECT DISTINCT symbol FROM scanner_picks WHERE status IN ('filled','filled_late','auto_filled')"
    )}

    rows = []
    for sym, rc in recent.items():
        if rc < MIN_RECENT_SIGNALS:
            continue
        recent_daily = rc / RECENT_DAYS
        base_cnt = base.get(sym, 0)
        base_daily = base_cnt / BASE_DAYS if base_cnt else 0
        ratio = (recent_daily / base_daily) if base_daily > 0 else float('inf')
        sentiment, _, _ = classify_sentiment(conn, sym)
        rows.append({
            "symbol": sym, "recent": rc, "base": base_cnt,
            "ratio": ratio, "sentiment": sentiment, "held": sym in held,
        })
    rows.sort(key=lambda x: x["ratio"], reverse=True)
    return rows[:TOP_N]


def format_message(rows):
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"📊 **信号升温榜** {today}（近{RECENT_DAYS}天 vs 前{BASE_DAYS}天基线）",
        "",
        "升温=信号突然变多的倍数 | 🟢利好扎堆=可能有机会 | 🔴利空扎堆=是雷别碰 | ✅=已持仓",
        "```",
        f"{'股票':6}{'近30天':>6}{'升温':>8}  {'好坏消息':16}{'持仓':>4}",
        "-" * 46,
    ]
    for r in rows:
        ratio_s = "🆕新冒头" if r["ratio"] == float('inf') else f"{r['ratio']:.0f}x"
        flag = "✅" if r["held"] else ""
        lines.append(f"{r['symbol']:6}{r['recent']:>6}{ratio_s:>9}  {r['sentiment']:16}{flag:>4}")
    lines.append("```")
    lines.append("👉 看绿色🟢且升温猛的=值得盯的苗头；红色🔴=信号多但是雷，跳过。")
    return "\n".join(lines)


def send_discord(env, message):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        print("[heatmap] 缺 DISCORD_BOT_TOKEN/CHANNEL_ID，跳过发送")
        return
    chunks = []
    while message:
        if len(message) <= 1900:
            chunks.append(message)
            break
        split_at = message.rfind("\n", 0, 1900)
        if split_at == -1:
            split_at = 1900
        chunks.append(message[:split_at].strip())
        message = message[split_at:].strip()
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    for chunk in chunks:
        try:
            requests.post(
                f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
                headers=headers,
                json={"content": chunk},
                timeout=15,
            ).raise_for_status()
        except Exception as e:
            print(f"[heatmap] Discord 发送失败: {e}")


def main():
    env = load_env()
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = build_heatmap(conn)
    finally:
        conn.close()
    if not rows:
        print("[heatmap] 本周无升温股票（信号量不足）")
        return
    message = format_message(rows)
    print(message)
    send_discord(env, message)


if __name__ == "__main__":
    main()
