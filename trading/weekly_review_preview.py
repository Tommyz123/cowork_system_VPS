#!/usr/bin/env python3
"""
P9 TIDE 周报 - 中文友好版预览（理财顾问对客户口吻）
- 用于发给主公看预览
- 主公确认后会替代 weekly_review.py 进生产

输出渠道：Discord（主公在手机能看）+ 控制台
"""
import json
import sqlite3
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, "/home/cowork/cowork/trading")
import yfinance as yf
from tide_utils import load_env

DB_PATH = "/home/cowork/cowork/trading/trading.db"
DISCORD_API = "https://discord.com/api/v10"
NOW = datetime.now()


def fetch_open_positions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT symbol, entry_price, scan_date, score, theme, secondary_themes,
                   spy_entry, catalyst_date, explosion_catalyst
            FROM scanner_picks
            WHERE status = 'open'
            ORDER BY scan_date, symbol
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def fetch_live_prices(symbols):
    """批量拉当前价"""
    prices = {}
    for sym in symbols + ["IWM"]:
        try:
            h = yf.Ticker(sym).history(period="5d")
            if not h.empty:
                prices[sym] = float(h["Close"].iloc[-1])
        except Exception:
            prices[sym] = None
    return prices


def calc_alpha(positions, prices):
    """每只算 alpha vs IWM"""
    enriched = []
    iwm_now = prices.get("IWM")
    for p in positions:
        sym = p["symbol"]
        now = prices.get(sym)
        if now is None or p["entry_price"] is None:
            continue
        ret_pct = (now - p["entry_price"]) / p["entry_price"] * 100
        iwm_pct = None
        alpha = None
        if iwm_now and p["spy_entry"]:
            iwm_pct = (iwm_now - p["spy_entry"]) / p["spy_entry"] * 100
            alpha = ret_pct - iwm_pct
        days_held = (NOW - datetime.strptime(p["scan_date"], "%Y-%m-%d")).days
        enriched.append({
            **p,
            "current_price": now,
            "return_pct": ret_pct,
            "iwm_pct": iwm_pct,
            "alpha": alpha,
            "days_held": days_held,
        })
    return enriched


def theme_distribution(positions):
    counts = {}
    for p in positions:
        t = p.get("theme") or "未标"
        counts[t] = counts.get(t, 0) + 1
    return counts


def find_catalysts_this_week(positions):
    """本周内的 catalyst_date"""
    week_end = NOW + timedelta(days=7)
    upcoming = []
    for p in positions:
        cd_str = p.get("catalyst_date")
        if not cd_str:
            continue
        try:
            cd = datetime.strptime(cd_str, "%Y-%m-%d")
        except ValueError:
            continue
        if NOW.date() <= cd.date() <= week_end.date():
            upcoming.append((cd_str, p["symbol"], p.get("explosion_catalyst", "")[:80]))
    return sorted(upcoming)


PLAIN_LANG_TEMPLATES = {
    # 每只股的"通俗一句话"模板，根据 symbol 定制（来自 bear_thesis 摘要 + theme）
    "ORA": "地热 + 储能双轮叙事兑现，是本周**唯一绝对正收益**。但 red team 揭示 5 个结构性 bear 风险（地热衰减资本化掩盖/Puna 集中度/Kenya FX/储能估值 mismatch/IRA 政策回滚）。**建议 trim 30-60%** 锁定一半已有 alpha。完整分析：`case_studies/ORA_2026_05_18.md`",
    "SOUN": "AI 语音平台。比小盘指数多赚 2.2%，但绝对值微跌。竞争隐忧：OpenAI Realtime / Gemini Live / ElevenLabs 三面挤压。等下季客户合同披露观察。",
    "WTRG": "水务并购预期。比小盘指数多赚 1.3%，但反垄断 + 州 PUC 审批风险大。'全国水务平台'估值溢价可能已部分 priced in。",
    "MIR": "SMR 配套（辐射监测）。比小盘指数多赚 1.1%。但单 SMR 合同 dollar content 通常有限，story 已被 OKLO/NNE 等纯 pure play 透支一轮。",
    "CPK": "公用事业转型故事。比小盘指数多赚 0.8%。但州 PUC 决定的 ROE 才是真锚，转型故事历史上少改变 PE 中枢。",
    "LZ": "在线公司注册 + AI 集成。比小盘指数多赚 0.5%。**AI 是双刃剑**——通用 LLM 可能 commoditize 文档生成业务，从'AI 受益者'变'AI 被颠覆者'。",
    "HCC": "冶金煤 + 分析师上调。比小盘指数多赚 0.4%。但冶金煤可能是结构性衰退资产（CBAM/中国压减/印度自给三重夹击）。'Hold→Buy'升级在周期股里**有时**是顶部信号。",
    "AGYS": "酒店 PMS + AI 模块（5/18 财报）。比小盘指数多赚 0.2%。Forward P/E 较高水位，需要 Q4 财报 AI ARR 数据撑住估值。**明天就出**。",
    "FSS": "市政基建（街道清扫/吸污车）。比小盘指数少赚 2.4%。已 rerate 过一轮，ARPA 资金耗尽后市政 capex 或回落。",
    "CSW": "建筑/HVAC 渠道（5/21 财报）。比小盘指数少赚 3.4%。已 rerate 到 30x+ 高位，'buy the rumor sell the news' 风险存在。",
    "VRRM": "自动化交通执法。比小盘指数少赚 5.7%。NYC 大合同政治风险 + PE 大股东历史减持记录。",
    "ARLO": "智能家居硬件 → SaaS 转型。比小盘指数少赚 6.6%。硬件 ASP 下滑拖累订阅故事；Amazon Ring 在 Alexa+ AI 时代有原生优势。",
    "LIF": "工业 → SaaS+硬件重分类。比小盘指数少赚 8.3%。小盘股narrative trade 的 tail risk 在流动性——一旦初期买盘耗尽容易 air pocket 回调。",
    "VSEC": "航空售后市场重分类（5/20 B. Riley 大会）。比小盘指数少赚 8.5%。可比标的（HEI/TDG/AAR）估值已在历史高位，rerate 上行空间有限。",
}


def plain_language_for(p):
    sym = p["symbol"]
    return PLAIN_LANG_TEMPLATES.get(sym, f"持仓 {p['days_held']} 天，等 catalyst 兑现观察。")


def build_discord_chunks(positions):
    avg_alpha = (
        sum(p["alpha"] for p in positions if p["alpha"] is not None)
        / max(1, sum(1 for p in positions if p["alpha"] is not None))
    )
    alpha_positive = sum(1 for p in positions if p["alpha"] is not None and p["alpha"] > 0)
    total = len(positions)

    # 排序：按 alpha 降序，所有 14 只都展示
    by_alpha = sorted(
        [p for p in positions if p["alpha"] is not None],
        key=lambda x: -x["alpha"],
    )

    themes = theme_distribution(positions)
    theme_lines = " / ".join(f"{t}({c})" for t, c in sorted(themes.items(), key=lambda x: -x[1]))

    catalysts = find_catalysts_this_week(positions)

    # ===== Chunk 1: 开场 + 数据快照（含术语翻译）=====
    chunk1 = f"""📋 **P9 TIDE 周报 - {NOW.strftime('%Y-%m-%d')}**

主公早，本周给您汇报一下纸账号 ($1M paper trading，模拟交易、不是真钱) 的运行情况。

---

📊 **本周关键数字**（专业指标）
- **在场仓位**：**{total} 只**（持有中，未平仓）
- **整体 alpha**：**{avg_alpha:+.2f}% vs IWM**（也就是比罗素 2000 小盘指数{'少赚' if avg_alpha < 0 else '多赚'} **{abs(avg_alpha):.2f}%**）
- **跑赢基准的**：**{alpha_positive}/{total} 只**（{alpha_positive/total*100:.0f}%，意思是 14 只里有 {alpha_positive} 只比小盘指数表现好）

📂 **主题分布**（每只股票背后的"故事类型"）：
{theme_lines}

---

💬 **通俗解读**（顾问视角）

简单说，**本周组合整体微微跑输小盘指数**（差距约 {abs(avg_alpha):.1f}%）。但要注意——这只是入场 12 天的早期数据，**统计意义为零**，30 天后才有第一批可分析的 outcome（结果验证）。

有一只股票（ORA）扛起了大旗，独自实现 +6.3% 绝对收益；另外几只跌幅较深的票（VSEC/LIF/ARLO）拖了后腿。

更深的判断需要等到 6 月初第一批 30 天 outcome 数据出来。当前**应该继续观察，不应该急于操作**——除非个别股票出现 thesis 失效信号（投资逻辑被现实否定）。
"""

    # ===== Chunk 2: 全 14 只持仓（按 alpha 排序，每只带通俗一句话）=====
    chunk2_lines = ["\n---\n\n📋 **14 只持仓全览**（按 alpha 从高到低，每只附通俗解读）\n"]
    for p in by_alpha:
        chunk2_lines.append(
            f"**{p['symbol']}** | 主题: {p.get('theme','-')} | "
            f"alpha **{p['alpha']:+.2f}%** | 持仓 {p['days_held']} 天 | "
            f"绝对 {p['return_pct']:+.2f}%"
        )
        chunk2_lines.append(f"  💬 *{plain_language_for(p)}*")
        chunk2_lines.append("")  # 空行分隔

    chunk2 = "\n".join(chunk2_lines)

    # ===== Chunk 3: catalyst 时间线 + 待决策 =====
    chunk3_lines = ["\n---\n\n🗓️ **本周关键 catalyst**\n"]
    if catalysts:
        for cd, sym, brief in catalysts:
            chunk3_lines.append(f"- **{cd}** {sym}: {brief}")
    else:
        chunk3_lines.append("- 本周无标注 catalyst（详见 scanner_picks.catalyst_date 字段）")

    chunk3_lines.append("\n---\n\n🎯 **待主公人工决策**\n")
    chunk3_lines.append("1. **ORA trim 百分比**（明日 09:00 EDT pre-market 提醒会自动推送）")
    chunk3_lines.append("2. **CSW 5/21 财报**：FY27 Q1 → verdict 更新")
    chunk3_lines.append("3. **VSEC 5/20 B. Riley 大会**：行业重分类 catalyst")
    chunk3_lines.append("4. **AGYS 5/18 财报**（明天）：AI ARR 数据披露")

    chunk3_lines.append("\n---\n\n📂 **深度文档**\n")
    chunk3_lines.append("- ORA 完整 case study: `trading/case_studies/ORA_2026_05_18.md`")
    chunk3_lines.append("- 14 只 bear thesis 库: `trading/case_studies/backfill/14_positions_2026_05_18.md`")
    chunk3_lines.append("- P9 方法论 (GPT 二次纠偏): 已存 `memory/feedback_thesis_normalization.md`")
    chunk3_lines.append("- 数据库 SQL 直查：`scanner_picks` 表新增 7 个 attribution 字段（theme/bear_thesis/hidden_risk/verdict 等）")

    chunk3_lines.append(
        "\n---\n\n_本周报由 P9 TIDE 系统自动生成。"
        "每周日 16:00 EDT 自动发送。"
        "下一份完整 outcome 数据：6 月 5 日（第一批 30 天 outcome 入库）。_"
    )
    chunk3 = "\n".join(chunk3_lines)

    return [chunk1, chunk2, chunk3]


def send_discord(token, channel_id, content):
    url = f"{DISCORD_API}/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
    data = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Discord error: {e}")
        return False


def main():
    env = load_env()
    token = env.get("DISCORD_BOT_TOKEN")
    channel_id = env.get("DISCORD_CHANNEL_ID")
    if not token or not channel_id:
        print("ERROR: 缺少 Discord token / channel")
        sys.exit(1)

    positions = fetch_open_positions()
    if not positions:
        print("无 open 持仓")
        return

    symbols = [p["symbol"] for p in positions]
    print(f"拉 {len(symbols)} 只股票 + IWM 实时价...")
    prices = fetch_live_prices(symbols)

    enriched = calc_alpha(positions, prices)
    chunks = build_discord_chunks(enriched)

    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ({len(chunk)} chars) ---")
        print(chunk)
        send_discord(token, channel_id, chunk)


if __name__ == "__main__":
    main()
