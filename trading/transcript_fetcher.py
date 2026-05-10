#!/usr/bin/env python3
"""
认知滞后扫描器 - 第二步：抓取新闻数据 + SEC 10-Q 全文
数据来源：
- 新闻：Finnhub（FMP 旧接口保留作 fallback）
- 10-Q：SEC EDGAR（按需调用：python3 transcript_fetcher.py --10q SYMBOL）
"""
import json, os, time
import requests
from bs4 import BeautifulSoup

ENV_PATH = "/home/cowork/cowork/config/api_keys.env"
SCREEN_OUTPUT_PATH = "/home/cowork/cowork/trading/screener_output.json"
TRANSCRIPTS_DIR = "/home/cowork/cowork/trading/transcripts"
BASE_URL = "https://financialmodelingprep.com/stable"
NEWS_LIMIT = 30
SEC_USER_AGENT = "Tom Zhi (zhitao776@gmail.com)"
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
CIK_CACHE_PATH = os.path.join(TRANSCRIPTS_DIR, "_sec_tickers_cache.json")
CIK_CACHE_TTL_DAYS = 7


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def fmp_get(path, api_key, params=None):
    query = dict(params or {})
    query["apikey"] = api_key
    try:
        r = requests.get(f"{BASE_URL}{path}", params=query, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def load_symbols(input_path=SCREEN_OUTPUT_PATH):
    if not os.path.exists(input_path):
        return []
    try:
        with open(input_path, encoding="utf-8") as f:
            rows = json.load(f)
    except Exception:
        return []
    return [row.get("symbol") for row in rows if isinstance(row, dict) and row.get("symbol")]


def fetch_news(symbol, api_key):
    data = fmp_get("/news/stock", api_key, params={"symbols": symbol, "limit": NEWS_LIMIT})
    if not isinstance(data, list):
        return []
    return [
        {
            "date": item.get("publishedDate", ""),
            "title": item.get("title", ""),
            "text": item.get("text", "") or item.get("description", ""),
            "publisher": item.get("publisher", ""),
        }
        for item in data
    ]


def fetch_news_finnhub(symbol, api_key, from_date, to_date):
    """Fetch company news from Finnhub free API (replaces FMP news/stock)."""
    from datetime import datetime as _dt
    try:
        r = requests.get(
            "https://finnhub.io/api/v1/company-news",
            params={"symbol": symbol, "from": from_date.isoformat(), "to": to_date.isoformat(), "token": api_key},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    results = []
    for item in data:
        try:
            pub_date = _dt.fromtimestamp(item.get("datetime", 0)).strftime("%Y-%m-%d")
        except Exception:
            continue
        headline = (item.get("headline") or "").strip()
        if not headline:
            continue
        results.append({
            "date": pub_date,
            "title": headline,
            "text": (item.get("summary") or "")[:800],
            "publisher": (item.get("source") or "").strip(),
        })
    return results


def fetch_for_symbols(symbols=None, output_dir=TRANSCRIPTS_DIR):
    os.makedirs(output_dir, exist_ok=True)
    env = load_env()
    api_key = env.get("FMP_API_KEY", "")
    target = list(symbols or load_symbols())
    saved, skipped = [], []

    for sym in target:
        news = fetch_news(sym, api_key)
        if not news:
            skipped.append(sym)
            print(f"  ⚠️ {sym} 无新闻，跳过")
        else:
            out = {"symbol": sym, "news": news}
            with open(os.path.join(output_dir, f"{sym}.json"), "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            saved.append(sym)
            print(f"  ✅ {sym} {len(news)}条新闻")
        time.sleep(0.3)

    return {"saved": saved, "skipped": skipped}


def extract_10q_text(html):
    """从 10-Q HTML 提取纯文本，去掉 head/script/style 噪音。"""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "head", "meta", "link"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


def _load_cik_cache():
    """加载本地 SEC tickers 缓存，过期/缺失时返回 None。"""
    if not os.path.exists(CIK_CACHE_PATH):
        return None
    age_days = (time.time() - os.path.getmtime(CIK_CACHE_PATH)) / 86400
    if age_days > CIK_CACHE_TTL_DAYS:
        return None
    try:
        with open(CIK_CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def lookup_cik(symbol):
    """ticker → CIK（10位补零），SEC tickers JSON 本地缓存 7 天。"""
    headers = {"User-Agent": SEC_USER_AGENT}
    tickers = _load_cik_cache()
    if tickers is None:
        try:
            r = requests.get(SEC_TICKERS_URL, headers=headers, timeout=30)
            r.raise_for_status()
            tickers = r.json()
            os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
            with open(CIK_CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(tickers, f)
        except Exception as e:
            print(f"[ERROR] SEC ticker 列表抓取失败: {e}", flush=True)
            return None
    for entry in tickers.values():
        if entry.get("ticker", "").upper() == symbol.upper():
            return str(entry.get("cik_str")).zfill(10)
    return None


def fetch_sec_10q(symbol, output_dir=TRANSCRIPTS_DIR, skip_if_exists=True):
    """
    从 SEC EDGAR 抓最新 10-Q 全文，提取纯文本存到本地。
    skip_if_exists=True 时，若本地已有同 filing_date 的 10-Q 就跳过下载直接返回。
    返回 dict {symbol, filing_date, accession, path, size_kb, cached} 或 None
    """
    headers = {"User-Agent": SEC_USER_AGENT}
    cik = lookup_cik(symbol)
    if not cik:
        print(f"[ERROR] SEC 找不到 ticker={symbol} 的 CIK", flush=True)
        return None

    time.sleep(0.15)
    try:
        r = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=headers, timeout=30)
        r.raise_for_status()
        sub = r.json()
    except Exception as e:
        print(f"[ERROR] SEC submissions 抓取失败 ({symbol}): {e}", flush=True)
        return None

    recent = sub.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accessions = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])
    dates = recent.get("filingDate", [])

    latest = None
    for i, form in enumerate(forms):
        if form == "10-Q":
            latest = {"accession": accessions[i], "doc": docs[i], "date": dates[i]}
            break

    if not latest:
        print(f"[ERROR] SEC 找不到 {symbol} 的 10-Q filing", flush=True)
        return None

    output_path = os.path.join(output_dir, f"{symbol}_10Q_{latest['date']}.txt")
    if skip_if_exists and os.path.exists(output_path):
        return {
            "symbol": symbol,
            "filing_date": latest["date"],
            "accession": latest["accession"],
            "path": output_path,
            "size_kb": os.path.getsize(output_path) // 1024,
            "cached": True,
        }

    time.sleep(0.15)
    accession_clean = latest["accession"].replace("-", "")
    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_clean}/{latest['doc']}"
    try:
        r = requests.get(doc_url, headers=headers, timeout=60)
        r.raise_for_status()
        html = r.text
    except Exception as e:
        print(f"[ERROR] SEC 10-Q 文档抓取失败 ({symbol}, {doc_url}): {e}", flush=True)
        return None

    text = extract_10q_text(html)
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {symbol} 10-Q\n")
        f.write(f"# Filing Date: {latest['date']}\n")
        f.write(f"# Accession: {latest['accession']}\n")
        f.write(f"# Source: {doc_url}\n\n")
        f.write(text)

    return {
        "symbol": symbol,
        "filing_date": latest["date"],
        "accession": latest["accession"],
        "path": output_path,
        "size_kb": len(text) // 1024,
        "cached": False,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--10q", dest="ten_q", metavar="SYMBOL", help="抓取指定 ticker 的最新 10-Q 全文")
    args = parser.parse_args()

    if args.ten_q:
        result = fetch_sec_10q(args.ten_q.upper())
        if result:
            print(f"✅ {result['symbol']} 10-Q 已保存")
            print(f"   filing_date: {result['filing_date']}")
            print(f"   accession:   {result['accession']}")
            print(f"   path:        {result['path']}")
            print(f"   size:        {result['size_kb']} KB")
        else:
            print(f"❌ {args.ten_q} 10-Q 抓取失败")
        return

    fetch_for_symbols()


if __name__ == "__main__":
    main()
