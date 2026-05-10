#!/usr/bin/env python3
"""
认知滞后扫描器 - 第一步：筛选候选股票
宇宙：S&P 400+600（过滤金融/医疗）+ 手动补充目标行业中小盘股
过滤：yfinance - 市值$5亿-$150亿 + 收入增速>15% + 分析师<15 + 6个月涨幅<25%
"""
import io, json, os, time, urllib.request
import pandas as pd
import yfinance as yf

OUTPUT_PATH = "/home/cowork/cowork/trading/screener_output.json"
MARKET_CAP_MIN = 500_000_000
MARKET_CAP_MAX = 15_000_000_000
REVENUE_GROWTH_MIN = 0.15
SIX_MONTH_RETURN_MAX = 25.0
ANALYST_COUNT_MAX = 15

SP400_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies"
SP600_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies"

# 过滤掉这些行业（增速逻辑与认知滞后thesis不匹配）
EXCLUDED_SECTORS = {"Financial Services", "Healthcare", "Real Estate"}

# 手动补充：目标行业中小盘股（AI/半导体/存储/国防软件/电力基建）
SUPPLEMENTARY_TICKERS = [
    # 半导体设备
    "ONTO", "FORM", "ACLS", "COHU", "UCTT", "CAMT",
    # AI基础设施/数据中心
    "SMCI", "IREN", "APLD", "CORZ", "BIT", "BTBT",
    # 存储/内存周边
    "VIAV", "IIVI", "IPGP",
    # 国防软件/技术
    "KTOS", "BWXT", "SPSC", "CACI", "DRS", "RCAT",
    # 电力/数据中心基建
    "POWL", "WATT", "NOVA", "ARRY", "SHLS",
    # 配电设备/变压器（AI电网主题）
    "VRT", "AMSC", "ERII", "HUBB", "NVT", "WIRE",
    # 电网自动化/测量
    "ITRI", "AMPS", "REZI",
    # 热管理/冷却
    "AEHR", "GTLS",
    # 电力转型/地热/水务
    "ORA", "WTRG",
    # AI软件/平台（中小盘）
    "BBAI", "GFAI", "SOUN", "AAOI", "SANG",
    # 网络安全
    "QLYS", "RDWR", "EGIS",
    # 工业自动化/机器人
    "BRNS", "ARIS", "ACMR",
]


def fetch_wiki_symbols(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=15).read()
        df = pd.read_html(io.BytesIO(html))[0]
        col = next((c for c in df.columns if "symbol" in c.lower() or "ticker" in c.lower()), df.columns[0])
        return df[col].dropna().astype(str).tolist()
    except Exception as e:
        print(f"  ⚠️ 拉取失败 {url}: {e}")
        return []


def yf_filter(symbol):
    """yfinance过滤：市值/行业/收入增速/分析师数量/6个月涨幅"""
    try:
        tk = yf.Ticker(symbol)
        info = tk.info

        mc = info.get("marketCap")
        if not mc or mc < MARKET_CAP_MIN or mc > MARKET_CAP_MAX:
            return None

        sector = info.get("sector", "")
        if sector in EXCLUDED_SECTORS:
            return None

        growth = info.get("revenueGrowth")
        if growth is None or growth < REVENUE_GROWTH_MIN:
            return None

        analyst_count = info.get("numberOfAnalystOpinions")
        if analyst_count is None or analyst_count > ANALYST_COUNT_MAX:
            return None

        hist = tk.history(period="6mo", auto_adjust=True)
        if hist.empty or len(hist) < 10:
            return None
        six_month_return = round((hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100, 2)
        if six_month_return > SIX_MONTH_RETURN_MAX:
            return None

        return {
            "symbol": symbol,
            "market_cap": mc,
            "sector": sector,
            "industry": info.get("industry", ""),
            "revenue_growth": round(growth * 100, 1),
            "gross_margins": round((info.get("grossMargins") or 0) * 100, 1),
            "analyst_count": analyst_count,
            "6m_return": six_month_return,
        }
    except Exception:
        return None


def run_screener(output_path=OUTPUT_PATH):
    print("Step 1: 拉取S&P 400+600成分股...")
    syms400 = fetch_wiki_symbols(SP400_URL)
    syms600 = fetch_wiki_symbols(SP600_URL)
    wiki_symbols = list(dict.fromkeys(syms400 + syms600))
    print(f"  S&P宇宙：{len(wiki_symbols)}家")

    all_symbols = list(dict.fromkeys(wiki_symbols + SUPPLEMENTARY_TICKERS))
    print(f"  + 手动补充{len(SUPPLEMENTARY_TICKERS)}家 → 总计{len(all_symbols)}家待扫描")
    print(f"  过滤行业：{EXCLUDED_SECTORS}")

    print("\nStep 2: yfinance逐一过滤...")
    results = []
    for i, sym in enumerate(all_symbols, 1):
        row = yf_filter(sym)
        if row:
            results.append(row)
            print(f"  ✅ [{i}/{len(all_symbols)}] {sym} | 增速{row['revenue_growth']}% | 分析师{row['analyst_count']} | 6m{row['6m_return']}% | {row['sector']}")
        elif i % 100 == 0:
            print(f"  ... [{i}/{len(all_symbols)}] 扫描中")
        time.sleep(0.2)

    results.sort(key=lambda x: (x["analyst_count"], x["6m_return"]))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成：{len(results)}家候选写入 {output_path}")
    return results


if __name__ == "__main__":
    run_screener()
