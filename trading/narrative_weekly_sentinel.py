#!/usr/bin/env python3
"""
公司叙事追踪系统 · 周记哨兵
================================================================
是什么：
  每周一自动跑，给每个在追踪的公司：抓本周新闻 → 调 claude CLI 让 AI
  筛新闻/绑假设/提信心建议 → 生成一份"周记草稿" → 自动 Discord 推送主公。
  主公被动接收（像财报哨兵），看完想讨论就回，不想就放着。

为什么这样设计（红线，不可破）：
  ⚠️ 本脚本**只出草稿、只读不写判断**：
     - 不改 narrative_hypotheses 的信心/状态
     - 不插 narrative_evidence
     草稿里 AI 的判断和信心都标「建议」。真正落库改信心，等主公与 CC
     讨论后**人手动**做（narrative_dossier.py）。AI 自动报信+出草稿，账本由人把关。
  为什么：MVP 阶段验证的就是"AI 草稿靠不靠谱"，让 AI 自动改信心=最易制造
     漂亮废话/把噪音当信号（Codex 反复警告）。头几周是"考核 AI 草稿"不是"享受自动化"。

数据驱动：
  追踪对象从 narrative_hypotheses 表解析（不硬编码 ticker），增删公司本脚本不用改。

成绩单关系：
  AI 草稿里每条建议，主公采纳/驳回记进 narrative_evidence.adoption 字段（人手动），
  攒几周即第③层成绩单(AI 草稿采纳率)的原料。成绩单本身=到 8/6 的一条查询，不在此脚本。

用法：
  python3 narrative_weekly_sentinel.py          # 正常跑(cron 周一)
  python3 narrative_weekly_sentinel.py --dry    # 生成草稿只打印不发 Discord
"""
import json
import subprocess
import sqlite3
import sys
import urllib.request
from datetime import datetime, timedelta

import requests

from tide_utils import load_env, run_with_alert

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API_BASE = "https://discord.com/api/v10"
NEWS_LOOKBACK_DAYS = 7


def tracked_tickers(c):
    rows = c.execute(
        """SELECT DISTINCT ticker FROM narrative_hypotheses
           WHERE status NOT IN ('已失效','已移交持仓监控') ORDER BY ticker"""
    ).fetchall()
    return [r[0] for r in rows]


def active_hypotheses(c, ticker):
    return c.execute(
        """SELECT id,statement,trigger_condition,invalidation_condition,confidence,status,importance
           FROM narrative_hypotheses
           WHERE ticker=? AND status NOT IN ('已失效','已移交持仓监控') ORDER BY id""",
        (ticker,),
    ).fetchall()


def fetch_news(ticker, env):
    key = env.get("FINNHUB_API_KEY") or env.get("FINNHUB_KEY")
    if not key:
        return []
    to = datetime.now().strftime("%Y-%m-%d")
    frm = (datetime.now() - timedelta(days=NEWS_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    url = (f"https://finnhub.io/api/v1/company-news?symbol={ticker}"
           f"&from={frm}&to={to}&token={key}")
    try:
        data = json.load(urllib.request.urlopen(url, timeout=25))
        seen, out = set(), []
        for n in data:
            h = n.get("headline", "").strip()
            if h and h not in seen:
                seen.add(h)
                out.append(h)
        return out[:40]
    except Exception:
        return []


def build_prompt(ticker, hypos, headlines):
    hlines = "\n".join(f"- {h}" for h in headlines) or "（本周无抓到新闻）"
    hypo_lines = "\n".join(
        f"  假设id={h[0]}[{h[6]}] 信心{h[4]} 状态{h[5]}: {h[1]}\n"
        f"    触发:{h[2]}\n    失效:{h[3]}"
        for h in hypos
    )
    return f"""你是投资叙事追踪助手。核心铁律：**新闻不是资产，假设才是资产。绑不到任何假设的新闻=噪音，丢弃。**

【追踪对象】{ticker}
【当前活跃假设】
{hypo_lines}

【本周新闻标题（近{NEWS_LOOKBACK_DAYS}天）】
{hlines}

请只输出一份「周记草稿」，严格按下面格式，简洁，全部用中文：

== {ticker} 周记草稿 ==
操作倾向：买/持/加/减/避/等（选一个）
本周假设变化（建议，非终稿）：
- 对每条被新闻推动的假设，写：假设id / 这条新闻是支持还是反对 / 信心建议从X→Y（只建议） / 一句依据
- 没有任何新闻能绑上某假设，就明说"无新增证据，信心维持"
丢弃噪音：列2-3条被判为噪音丢弃的新闻标题
理由：一句话说清现在为什么是这个操作倾向
改主意的条件：什么事发生会让判断变

⚠️ 要求：
1. 信心变化只能写"建议"，宁可不动也不要为凑数硬提信心
2. 泛行业宏观叙事(非公司层硬证据)最多算弱支持、不提信心
3. 分析师评级是滞后指标，别当硬证据
4. 别编新闻里没有的事实"""


def call_claude(prompt):
    try:
        r = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True, text=True, timeout=180,
        )
        out = (r.stdout or "").strip()
        return out or "（AI 未返回内容）"
    except Exception as e:
        return f"（AI 调用失败：{e}）"


def send_discord(env, message):
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        print("⚠️ 缺 DISCORD_BOT_TOKEN/CHANNEL_ID，跳过发送")
        return
    # Discord 单条 2000 字符上限，超了分段
    for i in range(0, len(message), 1900):
        chunk = message[i:i + 1900]
        try:
            requests.post(
                f"{DISCORD_API_BASE}/channels/{channel_id}/messages",
                headers={"Authorization": f"Bot {token}",
                         "Content-Type": "application/json"},
                json={"content": chunk}, timeout=15,
            )
        except Exception as e:
            print(f"⚠️ Discord 发送失败：{e}")


def _main():
    dry = "--dry" in sys.argv
    env = load_env()
    c = sqlite3.connect(DB_PATH)
    tickers = tracked_tickers(c)
    print(f"[narrative_weekly_sentinel] 追踪 {len(tickers)} 票: {tickers}")
    if not tickers:
        print("无追踪对象，结束。")
        c.close()
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today = datetime.now().strftime("%Y-%m-%d")
    for t in tickers:
        hypos = active_hypotheses(c, t)
        if not hypos:
            continue
        headlines = fetch_news(t, env)
        print(f"  {t}: 抓到 {len(headlines)} 条新闻，调 AI 生成草稿…")
        draft = call_claude(build_prompt(t, hypos, headlines))

        # 🟢 纯留痕：草稿存档（不碰判断账本——不改信心/不插 evidence）
        if not dry:
            c.execute(
                """INSERT INTO narrative_draft_archive
                   (ticker,draft_date,draft_text,news_count,created_at)
                   VALUES (?,?,?,?,?)""",
                (t, today, draft, len(headlines), now),
            )
            c.commit()

        # 记录状态行（三级透明：明确声明这次只留痕、没动账本）
        archived = "草稿已存档✅" if not dry else "草稿未存档(dry-run)"
        status = (
            f"\n\n📌 **记录状态**："
            f"{archived} | 本周抓 {len(headlines)} 条新闻仅作原始留痕，"
            f"**未入证据库、未改任何假设**（信心/假设变更 = 0，需你确认才动账本）"
        )
        header = (f"📓 **{t} 周记草稿** · {today}\n"
                  f"_(AI 自动生成的草稿，判断/信心均为**建议**；要落库改信心请和我讨论后定)_\n\n")
        msg = header + draft + status
        if dry:
            print("\n" + "=" * 50 + "\n" + msg + "\n" + "=" * 50)
        else:
            send_discord(env, msg)
            print(f"  ✅ {t} 草稿已发送+存档")
    c.close()


def main():
    run_with_alert("narrative_weekly_sentinel", _main)


if __name__ == "__main__":
    main()
