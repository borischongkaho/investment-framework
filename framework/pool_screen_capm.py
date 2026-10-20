#!/usr/bin/env python3
"""
pool_screen_capm.py — 一次過 quick-screen 成個 pool(V4.4 CAPM WACC + Owner-FCF 兩段 DCF)
用法:
    python3 pool_screen_capm.py                       # rf 5.2%, ERP 5.5%,source auto(FMP → 429 就轉 yfinance)
    python3 pool_screen_capm.py --source yf           # 直接用 yfinance(唔使 FMP key)
    python3 pool_screen_capm.py --rf 0.043            # 對照舊 rf
    python3 pool_screen_capm.py --no-cache            # 強制重新拉數
    python3 pool_screen_capm.py --pool my_pool.json   # 自己嘅 pool(格式見 pool_example.json)
    python3 pool_screen_capm.py --tickers DECK:6,LULU:5 --source yf   # 臨時 screen 幾隻(唔使改 pool)
    python3 pool_screen_capm.py --tickers DECK,ONON --g 6 --with-pool # 冇 :g 就用 --g;--with-pool = 連埋成個 pool
    cache:$BT_CACHE_DIR/fmp_cache(default ~/.cache/boris-investment/fmp_cache),超過 12 個鐘自動重拉
    FMP key:FMP_API_KEY env var 或 $BT_CONFIG_DIR/fmp.env(見 fmp_client.py)
方法(framework V4.4):
    Re = rf + β×ERP;WACC = E/V×Re + D/V×Rd×(1−T),Rd = rf+1.5%,D = max(淨債,0)
    Owner FCF = OCF − |capex| − SBC(TTM = 最近 4 季,冇就用最近年度 ⚠️)
    留存率 = g ÷ ROIC(ROIC 攞唔到/≤2% 用 15% ⚠️;cap 85%)
    可分派 = Owner FCF × (1−留存);兩段 DCF:10 年 g → terminal 3%(terminal 留存 = 3%/ROIC)
    Equity = PV − 淨債(債[已包 lease,只計一次]−現金−短投);IV/股 = Equity ÷ (市值/價)  ← 自動處理 ADR 比率/幣種
    MoS = 1 − 價/IV
pool JSON 格式(見 pool_example.json;除 growth_pct 外全部可選):
    {"growth_pct": {"AAPL": 6, ...},            # 每隻可持續 10 年 g(%)
     "groups": {"mega_cap": ["AAPL", ...]},     # 輸出表「組」欄;冇就 "WL"
     "fin_flag": ["CB", ...],                   # 金融/保險(FCF 法唔準,出 ⚠️)
     "old_iv": {"AAPL": 190},                   # 上次 IV 對照
     "dream": [["AAPL", 190, 142], ...]}        # [ticker, 舊 quick IV, 舊★價(IV×0.75)] → 出「夢幻名單」表
"""
import json, sys, argparse, time, re, os, statistics as st
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor

from fmp_client import load_api_key

CACHE_DIR = Path(os.environ.get("BT_CACHE_DIR") or (Path.home() / ".cache" / "boris-investment")).expanduser() / "fmp_cache"
CACHE_MAX_AGE_H = 12   # 永久位置 → 要有過期,唔係會靜靜雞用舊價
BASE = "https://financialmodelingprep.com/stable"
DEFAULT_POOL_PATH = Path(__file__).resolve().parent / "pool_example.json"
def api_key():
    return load_api_key()

# ---------- Pool + 可持續 10 年 g(%) — 由 JSON 載入(load_pool) ----------
POOL = {}        # ticker -> g (percent)
GROUP = {}       # ticker -> group label
FIN_FLAG = set() # financials / insurers: FCF method unreliable
OLD_IV = {}      # ticker -> previous IV (optional, for comparison column)
DREAM = []       # [(ticker, old_quick_iv, old_star_price), ...] (optional)

def load_pool(path):
    spec = json.loads(Path(path).expanduser().read_text())
    POOL.clear(); POOL.update({k.upper(): float(v) for k, v in spec.get("growth_pct", {}).items()})
    GROUP.clear()
    for name, tickers in spec.get("groups", {}).items():
        for t in tickers: GROUP[t.upper()] = name
    for t in POOL: GROUP.setdefault(t, "WL")
    FIN_FLAG.clear(); FIN_FLAG.update(t.upper() for t in spec.get("fin_flag", []))
    OLD_IV.clear(); OLD_IV.update({k.upper(): v for k, v in spec.get("old_iv", {}).items()})
    DREAM[:] = [tuple(x) for x in spec.get("dream", [])]
    if not POOL: sys.exit(f"pool {path} 冇 growth_pct 條目")

# ---------- cache ----------
def cget(key):
    f = CACHE_DIR / (re.sub(r"[^A-Za-z0-9_.-]", "_", key) + ".json")
    fresh = f.exists() and time.time() - f.stat().st_mtime < CACHE_MAX_AGE_H * 3600
    return json.loads(f.read_text()) if fresh else None
def cput(key, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / (re.sub(r"[^A-Za-z0-9_.-]", "_", key) + ".json")).write_text(json.dumps(data, default=str))

# ---------- FMP ----------
class FMPLimit(Exception): pass
def fmp(endpoint, use_cache=True, **params):
    key = endpoint + "_" + "_".join(f"{k}-{v}" for k, v in sorted(params.items()))
    if use_cache and (c := cget(key)) is not None: return c
    params = dict(params); params["apikey"] = api_key()
    try:
        body = urlopen(f"{BASE}/{endpoint}?{urlencode(params)}", timeout=20).read().decode()
    except Exception as e:
        if "429" in str(e): raise FMPLimit("FMP 429 Limit Reach")
        return None
    if "Limit Reach" in body[:200]: raise FMPLimit("FMP Limit Reach")
    if "Premium" in body[:200] or "Restricted" in body[:200]: return None
    data = json.loads(body); cput(key, data); return data
def first(x):
    if isinstance(x, list): return x[0] if x else None
    return x if isinstance(x, dict) else None

def fetch_fmp(t, use_cache=True):
    p = first(fmp("profile", use_cache, symbol=t)); q = first(fmp("quote", use_cache, symbol=t))
    if not q or not q.get("price"): return None
    cfq = fmp("cash-flow-statement", use_cache, symbol=t, period="quarter", limit=4) or []
    cfa = first(fmp("cash-flow-statement", use_cache, symbol=t, period="annual", limit=1))
    bs = first(fmp("balance-sheet-statement", use_cache, symbol=t, limit=1))
    inc = first(fmp("income-statement", use_cache, symbol=t, limit=1))
    km = first(fmp("key-metrics-ttm", use_cache, symbol=t))
    if not bs: return None
    if len(cfq) >= 4:
        ocf = sum(x.get("operatingCashFlow") or 0 for x in cfq[:4]); capex = sum(abs(x.get("capitalExpenditure") or 0) for x in cfq[:4])
        sbc = sum(x.get("stockBasedCompensation") or 0 for x in cfq[:4]); src = "TTM"; rep = cfq[0].get("reportedCurrency")
    elif cfa:
        ocf = cfa.get("operatingCashFlow") or 0; capex = abs(cfa.get("capitalExpenditure") or 0); sbc = cfa.get("stockBasedCompensation") or 0
        src = f"FY{str(cfa.get('date',''))[:4]}"; rep = cfa.get("reportedCurrency")
    else: return None
    return {"price": q["price"], "mcap": q.get("marketCap") or (p or {}).get("marketCap"), "beta": (p or {}).get("beta"),
            "quote_cur": (p or {}).get("currency") or "USD", "rep_cur": rep, "ocf": ocf, "capex": capex, "sbc": sbc, "src": src,
            "debt": bs.get("totalDebt") or 0, "lease": bs.get("capitalLeaseObligations") or 0,
            "funded": (bs.get("shortTermDebt") or 0) + (bs.get("longTermDebt") or 0),
            "cash": (bs.get("cashAndCashEquivalents") or 0) + (bs.get("shortTermInvestments") or 0),
            "pretax": (inc or {}).get("incomeBeforeTax"), "tax_exp": (inc or {}).get("incomeTaxExpense"),
            "roic": (km or {}).get("returnOnInvestedCapitalTTM"), "provider": "FMP"}

# ---------- yfinance fallback ----------
def fetch_yf(t, use_cache=True):
    key = "yf_" + t
    if use_cache and (c := cget(key)) is not None: return c
    import yfinance as yf
    tk = yf.Ticker(t); info = tk.info or {}
    price = info.get("currentPrice") or info.get("regularMarketPrice"); mcap = info.get("marketCap")
    if not price or not mcap: return None
    def row(df, *names):
        for n in names:
            if n in df.index: return df.loc[n]
        return None
    def latest(s):
        if s is None: return None
        s = s.dropna(); return float(s.iloc[0]) if len(s) else None
    q = tk.quarterly_cashflow; a = tk.cashflow; bs = tk.balance_sheet; inc = tk.income_stmt
    ocf_q = row(q, "Operating Cash Flow"); cap_q = row(q, "Capital Expenditure"); sbc_q = row(q, "Stock Based Compensation")
    if ocf_q is not None and ocf_q.dropna().shape[0] >= 4:
        ocf = float(ocf_q.dropna().iloc[:4].sum()); capex = abs(float(cap_q.dropna().iloc[:4].sum())) if cap_q is not None else 0.0
        sbc = float(sbc_q.dropna().iloc[:4].sum()) if sbc_q is not None else 0.0; src = "TTM"
    else:
        ocf = latest(row(a, "Operating Cash Flow")); capex = abs(latest(row(a, "Capital Expenditure")) or 0); sbc = latest(row(a, "Stock Based Compensation")) or 0
        if ocf is None: return None
        src = "FY" + str(a.columns[0])[:4]
    debt = latest(row(bs, "Total Debt")) or 0.0   # yfinance Total Debt 已包 lease
    cash = latest(row(bs, "Cash Cash Equivalents And Short Term Investments"))
    if cash is None: cash = (latest(row(bs, "Cash And Cash Equivalents")) or 0) + (latest(row(bs, "Other Short Term Investments")) or 0)
    pretax = latest(row(inc, "Pretax Income")); tax_exp = latest(row(inc, "Tax Provision")); ebit = latest(row(inc, "EBIT"))
    ic = latest(row(bs, "Invested Capital"))
    if ic is None: ic = (latest(row(bs, "Stockholders Equity")) or 0) + debt
    roic = None
    if ebit and ic and ic > 0:
        tr = min(max((tax_exp or 0) / pretax, 0), 0.35) if pretax and pretax > 0 else 0.21
        roic = ebit * (1 - tr) / (ic - min(cash, ic * 0.5))   # 扣現金(最多扣 IC 一半)
    d = {"price": price, "mcap": mcap, "beta": info.get("beta"), "quote_cur": info.get("currency") or "USD",
         "rep_cur": info.get("financialCurrency") or info.get("currency"), "ocf": ocf, "capex": capex, "sbc": sbc, "src": src,
         "debt": debt, "lease": 0.0, "cash": cash, "pretax": pretax, "tax_exp": tax_exp, "roic": roic, "provider": "yf"}
    cput(key, d); return d

FX = {}
def fx_to(cf, ct, provider, use_cache=True):
    if not cf or cf == ct: return 1.0
    k = f"{cf}{ct}"
    if k in FX: return FX[k]
    if (c := cget("fx_" + k)) is not None: FX[k] = c; return c
    r = None
    try:
        if provider == "FMP":
            q = first(fmp("quote", use_cache, symbol=k)); r = q and q.get("price")
            if not r:
                q = first(fmp("quote", use_cache, symbol=f"{ct}{cf}")); r = q and q.get("price") and 1 / q["price"]
        else:
            import yfinance as yf
            for sym, inv in ((f"{cf}{ct}=X", False), (f"{ct}{cf}=X", True)):
                p = (yf.Ticker(sym).info or {}).get("regularMarketPrice")
                if p: r = 1 / p if inv else p; break
    except Exception: r = None
    if r: FX[k] = r; cput("fx_" + k, r)
    return r

# ---------- 估值 ----------
def value(t, d, rf, erp, debt_prem=0.015):
    g = POOL[t] / 100; notes = []
    if not d: return {"ticker": t, "error": "冇數"}
    price, mcap = d["price"], d["mcap"]; shares = mcap / price
    beta = d.get("beta")
    if not beta or beta <= 0: beta = 1.0; notes.append("β⚠️=1.0")
    if d["src"] != "TTM": notes.append(f"CF 用{d['src']}⚠️")
    owner_fcf = d["ocf"] - d["capex"] - d["sbc"]
    # 2026-10-07 修正:FMP totalDebt 已包 lease → 只有 lease 明顯唔喺 debt 入面先加(yf 路徑 lease=0,唔受影響)
    funded = d.get("funded", 0)
    lease_in_debt = abs(d["debt"] - (funded + d["lease"])) < abs(d["debt"] - funded)
    net_debt = d["debt"] + (0 if lease_in_debt else d["lease"]) - d["cash"]
    rate = fx_to(d["rep_cur"], d["quote_cur"], d["provider"])
    if rate is None: rate = 1.0; notes.append(f"FX {d['rep_cur']}→{d['quote_cur']} 攞唔到⚠️")
    elif d["rep_cur"] != d["quote_cur"]: notes.append(f"{d['rep_cur']}→{d['quote_cur']}@{rate:.3f}")
    tax = 0.21
    if d.get("pretax") and d["pretax"] > 0 and d.get("tax_exp") is not None:
        tax = min(max(d["tax_exp"] / d["pretax"], 0.0), 0.35)
    roic = d.get("roic")
    if roic is None or roic <= 0.02: roic = 0.15; notes.append("ROIC⚠️15%")
    D = max(net_debt * rate, 0); E = mcap; V = E + D
    re_ = rf + beta * erp; rd = (rf + debt_prem) * (1 - tax)
    wacc = E / V * re_ + D / V * rd
    ret1 = min(g / roic, 0.85) if g > 0 else 0.0
    if g > 0 and g / roic > 0.85: notes.append("留存 cap 85%⚠️")
    ret_t = min(0.03 / roic, 0.85)
    pv = 0.0; f = owner_fcf
    for yr in range(1, 11):
        f *= (1 + g); pv += f * (1 - ret1) / (1 + wacc) ** yr
    tv = f * 1.03 * (1 - ret_t) / (wacc - 0.03)
    pv += tv / (1 + wacc) ** 10
    equity = (pv - net_debt) * rate
    iv = equity / shares
    mos = 1 - price / iv if iv > 0 else None
    if owner_fcf <= 0: notes.append("Owner FCF≤0⚠️")
    if t in FIN_FLAG: notes.append("金融/保險 FCF 法唔準⚠️")
    return {"ticker": t, "group": GROUP.get(t, "WL"), "price": price, "cur": d["quote_cur"], "beta": beta, "wacc": wacc, "g": g,
            "roic": roic, "ret": ret1, "owner_fcf": owner_fcf * rate, "ocf": d["ocf"]*rate, "capex": d["capex"]*rate, "sbc": d["sbc"]*rate,
            "net_debt": net_debt * rate, "shares": shares, "iv": iv, "mos": mos, "src": d["src"], "tax": tax,
            "old_iv": OLD_IV.get(t), "notes": " ".join(notes), "provider": d["provider"]}

def main():
    ap = argparse.ArgumentParser(description="V4.4 CAPM pool screen (Owner-FCF two-stage DCF)")
    ap.add_argument("--rf", type=float, default=0.052); ap.add_argument("--erp", type=float, default=0.055)
    ap.add_argument("--source", choices=["auto", "fmp", "yf"], default="auto")
    ap.add_argument("--no-cache", action="store_true"); ap.add_argument("--json", default=None)
    ap.add_argument("--pool", default=str(DEFAULT_POOL_PATH), help="pool JSON (default: bundled pool_example.json)")
    ap.add_argument("--tickers", default=None, help="ad-hoc tickers, comma-separated, optional :g per ticker in percent (e.g. DECK:6,LULU:5); screens only these unless --with-pool")
    ap.add_argument("--g", type=float, default=None, help="10-yr growth in percent for --tickers given without :g")
    ap.add_argument("--with-pool", action="store_true", help="screen --tickers on top of the pool file")
    a = ap.parse_args(); use_cache = not a.no_cache
    load_pool(a.pool)
    if a.tickers:
        adhoc = {}
        for tok in filter(None, (x.strip() for x in a.tickers.split(","))):
            t, _, g = tok.partition(":"); t = t.upper()
            if g: adhoc[t] = float(g)
            elif a.g is not None: adhoc[t] = a.g
            elif t in POOL: adhoc[t] = POOL[t]
            else: ap.error(f"{t} 冇 g:用 {t}:<g> 或者 --g")
        if not a.with_pool: POOL.clear()
        POOL.update(adhoc)
        for t in adhoc: GROUP.setdefault(t, "臨時")
    src = a.source
    if src == "auto":
        probe = next(iter(POOL))
        try: fetch_fmp(probe, use_cache); src = "fmp"
        except FMPLimit: src = "yf"; print("⚠️ FMP 429 Limit Reach → 轉用 yfinance", file=sys.stderr)
    def get(t):
        for attempt in range(3):
            try: return t, (fetch_fmp(t, use_cache) if src == "fmp" else fetch_yf(t, use_cache))
            except FMPLimit: return t, fetch_yf(t, use_cache)
            except Exception as e:
                print(f"{t} 第{attempt+1}次: {str(e)[:80]}", file=sys.stderr); time.sleep(5 * (attempt + 1))
        return t, None
    with ThreadPoolExecutor(max_workers=3) as ex: raw = dict(ex.map(get, POOL))
    rows = [value(t, raw[t], a.rf, a.erp) for t in POOL]
    rows_old = {r["ticker"]: r for r in (value(t, raw[t], 0.043, a.erp) for t in POOL) if "error" not in r}
    ok = [r for r in rows if "error" not in r]; bad = [r for r in rows if "error" in r]
    ok.sort(key=lambda r: (r["mos"] if r["mos"] is not None else -9), reverse=True)
    B = lambda x: f"{x/1e9:.2f}B"
    prov = ",".join(sorted({r["provider"] for r in ok}))
    print(f"# Pool screen {time.strftime('%Y-%m-%d')} — rf {a.rf*100:.1f}% / ERP {a.erp*100:.1f}% / 數據源 {prov}({len(ok)} 隻有數,{len(bad)} 隻冇數)\n")
    print("| # | Ticker | 組 | 價 | β | WACC | g | ROIC | 留存 | Owner FCF | 淨債 | IV/股 | **MoS** | 舊 IV | 備註 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(ok, 1):
        mos = f"**{r['mos']*100:+.0f}%**" if r["mos"] is not None else "n/a(IV<0)"
        print(f"| {i} | {r['ticker']} | {r['group']} | {r['price']:.2f} | {r['beta']:.2f} | {r['wacc']*100:.1f}% | {r['g']*100:.0f}% | {r['roic']*100:.0f}% | {r['ret']*100:.0f}% | {B(r['owner_fcf'])} | {B(r['net_debt'])} | {r['iv']:.0f} | {mos} | {r['old_iv'] or '—'} | {r['notes']} |")
    dream = [d for d in DREAM if d[0] in POOL]   # --tickers 臨時 screen 冇包嘅就唔出
    if dream:
        print("\n## 夢幻名單:新 WACC 新 IV / 新★價 vs 舊★價\n")
        print("| Ticker | 舊 Quick IV | 舊★價 | 新 IV | 新★價(×0.75) | ★變化 | 現價 | 現價 vs 新★ | WACC | 備註 |")
        print("|---|---|---|---|---|---|---|---|---|---|")
    m = {r["ticker"]: r for r in ok}
    for t, oiv, ostar in dream:
        r = m.get(t)
        if not r: print(f"| {t} | {oiv} | {ostar} | 冇數 | | | | | | |"); continue
        ns = r["iv"] * 0.75; chg = ns / ostar - 1
        print(f"| {t} | {oiv} | {ostar} | {r['iv']:.0f} | **{ns:.0f}** | {chg*100:+.0f}% | {r['price']:.2f} | {(r['price']/ns-1)*100:+.0f}% | {r['wacc']*100:.1f}% | {r['notes']} |")
    dw = [r["wacc"] - rows_old[r["ticker"]]["wacc"] for r in ok]
    div = [r["iv"] / rows_old[r["ticker"]]["iv"] - 1 for r in ok if rows_old[r["ticker"]]["iv"] > 0 and r["iv"] > 0]
    if dw and div:   # 臨時 screen 全部冇數時 statistics 會 crash
        print(f"\n## 方法論:rf 4.3%→{a.rf*100:.1f}%:WACC 平均 +{st.mean(dw)*100:.2f}pp(中位 +{st.median(dw)*100:.2f}pp);IV 平均 {st.mean(div)*100:+.1f}%(中位 {st.median(div)*100:+.1f}%,n={len(div)})")
    print("\n## 攞唔到數:", ", ".join(f"{r['ticker']}({r['error']})" for r in bad) or "無")
    if a.json: Path(a.json).write_text(json.dumps({"rows": ok, "bad": bad, "rows_rf43": rows_old}, indent=1, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
