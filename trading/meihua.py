#!/usr/bin/env python3
"""
梅花玄学分 —— 隔离观察模块。

用途: P9 建仓时给候选股算一个"玄学分", 只记录、不参与任何选股/下单决策。
攒满 1-2 季度样本后, 用真实平仓收益验证玄学分是否有预测力, 再决定是否纳入。

100% 可复现: 同一只票、同一建仓时刻, 跑一万遍分数一样。无任何临场解读。

规则(v4, 含动爻位置+互卦微调):
  本命 = 上市日(首个交易日)的 月、日
  当下 = 建仓时刻的 日、时辰(地支1-12; 历史无时分用午时=7占位)
  上数 = L月 + L日 + T时辰;  下数 = 上数 + T日
  上卦 = 上数 mod8(0->8); 下卦 = 下数 mod8; 动爻 = 下数 mod6(0->6)
  动爻在下卦(1-3)->下卦为用; 在上卦(4-6)->上卦为用; 另一卦为体
  主分: 用生体+25 比和+15 体克用+10 体生用-10 用克体-25; base=50
  互卦: 本卦六爻取2-3-4爻为互下卦、3-4-5爻为互上卦
  微调①动爻位置: 1-2->-3  3-4->0  5-6->+3
  微调②互卦: 互卦生体或比和+3; 互卦克体-3; 其他0
  玄学分 = 50 + 主分delta + 动爻微调 + 互卦微调  (约 19~81)
  对照分 = hash(symbol+scan_date) 映射 25~75 (验证用随机基准)
"""
import hashlib
from datetime import datetime

GUA = {1: "乾", 2: "兑", 3: "离", 4: "震", 5: "巽", 6: "坎", 7: "艮", 8: "坤"}
# 三爻(从下到上, 1=阳爻 0=阴爻) -> 卦名
LINES = {
    "乾": (1, 1, 1), "兑": (1, 1, 0), "离": (1, 0, 1), "震": (1, 0, 0),
    "巽": (0, 1, 1), "坎": (0, 1, 0), "艮": (0, 0, 1), "坤": (0, 0, 0),
}
LINES_INV = {v: k for k, v in LINES.items()}
WUXING = {"乾": "金", "兑": "金", "震": "木", "巽": "木",
          "坎": "水", "离": "火", "坤": "土", "艮": "土"}
SHENG = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
KE = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}

DEFAULT_SHICHEN = 7  # 历史数据无时分 -> 午时(正午)占位


def hour_to_shichen(hour):
    """纽约本地钟点(0-23) -> 地支时辰序号(1-12, 子时=1)。"""
    return ((hour + 1) // 2) % 12 + 1


def qi_gua(L_month, L_day, T_day, T_shichen):
    up_num = L_month + L_day + T_shichen
    dn_num = L_month + L_day + T_shichen + T_day
    up = up_num % 8 or 8
    dn = dn_num % 8 or 8
    dong = dn_num % 6 or 6
    up_g, dn_g = GUA[up], GUA[dn]
    if dong <= 3:
        yong, ti = dn_g, up_g
    else:
        yong, ti = up_g, dn_g
    # 本卦六爻(从下到上): 下卦三爻 + 上卦三爻
    lines = list(LINES[dn_g]) + list(LINES[up_g])
    hu_dn = LINES_INV[tuple(lines[1:4])]  # 2-3-4 爻
    hu_up = LINES_INV[tuple(lines[2:5])]  # 3-4-5 爻
    return up_g, dn_g, dong, ti, yong, hu_up, hu_dn


def score_tiyong(ti, yong):
    wt, wy = WUXING[ti], WUXING[yong]
    if wt == wy:
        return 15, "比和"
    if SHENG.get(wy) == wt:
        return 25, "用生体"
    if SHENG.get(wt) == wy:
        return -10, "体生用"
    if KE.get(wt) == wy:
        return 10, "体克用"
    if KE.get(wy) == wt:
        return -25, "用克体"
    return 0, "?"


def adj_dong(dong):
    if dong <= 2:
        return -3
    if dong <= 4:
        return 0
    return 3


def adj_hugua(ti, hu_up, hu_dn):
    wt = WUXING[ti]
    for hg in (hu_up, hu_dn):
        if SHENG.get(WUXING[hg]) == wt:
            return 3
    if WUXING[hu_up] == wt or WUXING[hu_dn] == wt:
        return 3
    for hg in (hu_up, hu_dn):
        if KE.get(WUXING[hg]) == wt:
            return -3
    return 0


def random_score(symbol, scan_date):
    h = int(hashlib.md5(f"{symbol}|{scan_date}".encode()).hexdigest(), 16)
    return 25 + (h % 51)  # 25~75


def get_listing_date(symbol, cache={}):
    """首个交易日作为上市日近似。失败返回 None。"""
    if symbol in cache:
        return cache[symbol]
    d = None
    try:
        import yfinance as yf
        hist = yf.Ticker(symbol).history(period="max")
        d = hist.index[0].date() if len(hist) else None
    except Exception:
        d = None
    cache[symbol] = d
    return d


def compute(symbol, scan_date, build_dt=None, listing_date=None):
    """
    返回 dict 或 None(上市日拿不到时)。
      symbol      : 股票代码
      scan_date   : 建仓日期字符串 'YYYY-MM-DD'
      build_dt    : 可选, 真实建仓 datetime(带纽约时分)。给了就用真实时辰, 否则午时占位
      listing_date: 可选, 已知上市日(date)。不给则 yfinance 查
    """
    ld = listing_date or get_listing_date(symbol)
    if ld is None:
        return None
    sd = datetime.strptime(scan_date, "%Y-%m-%d")
    if build_dt is not None:
        shichen = hour_to_shichen(build_dt.hour)
    else:
        shichen = DEFAULT_SHICHEN
    up_g, dn_g, dong, ti, yong, hu_up, hu_dn = qi_gua(ld.month, ld.day, sd.day, shichen)
    delta, rel = score_tiyong(ti, yong)
    score = 50 + delta + adj_dong(dong) + adj_hugua(ti, hu_up, hu_dn)
    return {
        "meihua_score": score,
        "meihua_hexagram": f"{up_g}/{dn_g}",
        "meihua_relation": rel,
        "meihua_random": random_score(symbol, scan_date),
        "listing_date": str(ld),
    }


if __name__ == "__main__":
    # 自测: AAPL
    r = compute("AAPL", "2026-06-01", listing_date=datetime(1980, 12, 12).date())
    print("AAPL 自测:", r)
