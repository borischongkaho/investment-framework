#!/usr/bin/env python3
"""
V4.4 Mandatory Pre-Flight Inputs Check.
Includes Operating Leases (ASC 842) + SBC adjustment + Adjusted FCF/OE.

Usage:
    python valuation_inputs.py NVDA
    → outputs all V4.4 adjusted inputs needed for DCF
    python valuation_inputs.py DECK --source yf   # force yfinance (default auto: FMP → yfinance)
    FMP key: FMP_API_KEY env var, or FMP_API_KEY=... in $BT_CONFIG_DIR/fmp.env (yfinance path needs no key)
    Exit code 2 + "error" in JSON when no source has financials for the ticker.

V4.4 changes from V4.3:
- Adjusted Net Debt = Total Debt + Operating Leases - Cash
  (2026-10-07: leases counted ONCE — FMP Total Debt already includes them; see leases_in_total_debt)
- Adjusted FCF = FCF - SBC (true economic FCF)
- Adjusted Owner Earnings = Manual OE - SBC
- Tax rate explicit from financials
- All inputs flagged with source
"""

import sys, json, subprocess, argparse, math
from pathlib import Path

from fmp_client import load_api_key

# endpoint -> why FMP returned nothing (so a blocked ticker is reported, not silently empty)
FMP_UNAVAILABLE = {}


def get_fmp_raw(endpoint, ticker, **params):
    """Direct FMP curl wrapper - tolerates blocked tickers."""
    api_key = load_api_key()  # FMP_API_KEY env var or $BT_CONFIG_DIR/fmp.env (see fmp_client.py)
    base = "https://financialmodelingprep.com/stable"
    qs_parts = [f"symbol={ticker.upper()}"]
    for k, v in params.items():
        qs_parts.append(f"{k}={v}")
    qs_parts.append(f"apikey={api_key}")
    url = f"{base}/{endpoint}?{'&'.join(qs_parts)}"
    result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=15)
    body = result.stdout
    if "Premium" in body[:200] or "Restricted" in body[:200] or "Legacy" in body[:200]:
        FMP_UNAVAILABLE[endpoint] = "blocked on current FMP plan (premium ticker/endpoint)"
        return None
    try:
        data = json.loads(body)
    except Exception:
        FMP_UNAVAILABLE[endpoint] = f"non-JSON response: {body[:80].strip()!r}"
        return None
    if isinstance(data, dict) and "Error Message" in data:
        FMP_UNAVAILABLE[endpoint] = f"FMP error: {str(data['Error Message'])[:80]}"
        return None
    if not data:
        FMP_UNAVAILABLE[endpoint] = "empty response (unknown ticker?)"
    return data


# ---------- yfinance fallback ----------
# Returns records under FMP field names so the V4.4 derivations below run unchanged.
# Semantics mirror FMP: totalDebt INCLUDES lease liabilities (yfinance "Total Debt" does too),
# capitalLeaseObligations = lease liabilities, missing balance-sheet items -> absent (→ 0 via .get default).
YF_FIELDS = {
    "balance-sheet-statement": {
        "cashAndCashEquivalents": ["Cash And Cash Equivalents"],
        "shortTermInvestments": ["Other Short Term Investments"],
        "totalDebt": ["Total Debt"],
        "longTermDebt": ["Long Term Debt"],
        "shortTermDebt": ["Current Debt"],
        "capitalLeaseObligations": ["Capital Lease Obligations"],
        "totalStockholdersEquity": ["Stockholders Equity"],
    },
    "income-statement": {
        "revenue": ["Total Revenue"],
        "operatingIncome": ["Operating Income"],
        "netIncome": ["Net Income"],
        "eps": ["Basic EPS"],
        "weightedAverageShsOutDil": ["Diluted Average Shares"],
        "incomeBeforeTax": ["Pretax Income"],
        "incomeTaxExpense": ["Tax Provision"],
    },
    "cash-flow-statement": {
        "operatingCashFlow": ["Operating Cash Flow"],
        "capitalExpenditure": ["Capital Expenditure"],  # negative, same as FMP
        "freeCashFlow": ["Free Cash Flow"],
        "depreciationAndAmortization": ["Depreciation And Amortization", "Depreciation Amortization Depletion"],
        "stockBasedCompensation": ["Stock Based Compensation"],
    },
}
YF_SOURCE_NOTES = ("yfinance annual statements (latest fiscal year, max 4-5 yrs → revenue_5yr_cagr usually absent); "
                   "lease liabilities only where Yahoo reports them (if absent, net debt excludes leases — check 10-K); "
                   "EV / EV÷EBITDA / EV÷Sales from Yahoo quote; ROIC, invested capital, tax/interest burden, "
                   "FCF yield, net debt÷EBITDA, FMP owner earnings and FMP DCF not available from this source")
_YF_TICKERS = {}


def _num(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


def get_yf_raw(endpoint, ticker, **params):
    """yfinance stand-in for get_fmp_raw (same signature, FMP-shaped output)."""
    import yfinance as yf
    t = _YF_TICKERS.setdefault(ticker.upper(), yf.Ticker(ticker.upper()))
    if endpoint == "quote":
        i = t.info or {}
        price = _num(i.get("currentPrice")) or _num(i.get("regularMarketPrice"))
        if not price:
            return None
        return [{"price": price, "marketCap": _num(i.get("marketCap")),
                 "yearHigh": _num(i.get("fiftyTwoWeekHigh")), "yearLow": _num(i.get("fiftyTwoWeekLow"))}]
    if endpoint == "key-metrics-ttm":
        i = t.info or {}
        return [{"enterpriseValueTTM": _num(i.get("enterpriseValue")),
                 "evToEBITDATTM": _num(i.get("enterpriseToEbitda")),
                 "evToSalesTTM": _num(i.get("enterpriseToRevenue"))}]
    if endpoint not in YF_FIELDS:
        return None  # owner-earnings, discounted-cash-flow: FMP-only
    df = {"balance-sheet-statement": t.balance_sheet, "income-statement": t.income_stmt,
          "cash-flow-statement": t.cashflow}[endpoint]
    if df is None or df.empty:
        return None
    records = []
    for col in df.columns:  # newest first, like FMP
        rec = {}
        for fmp_key, rows in YF_FIELDS[endpoint].items():
            for r in rows:
                if r in df.index and (v := _num(df.loc[r, col])) is not None:
                    rec[fmp_key] = v
                    break
        if rec:  # skip all-NaN years
            rec["date"] = str(col)[:10]
            records.append(rec)
    return records[: int(params.get("limit", 1))] or None


def has_core_data(inputs):
    return any(k in inputs for k in ("total_debt", "latest_revenue", "latest_ocf"))


def mandatory_inputs_v44(ticker, source="auto"):
    """V4.4 mandatory pre-flight inputs with op leases + SBC adjustments."""
    print(f"=== V4.4 Pre-Flight Inputs: {ticker} ===\n")

    inputs = {}
    if source in ("auto", "fmp"):
        inputs = collect_inputs(ticker, get_fmp_raw)
        inputs["data_source"] = "FMP"
    if source == "yf" or (source == "auto" and not has_core_data(inputs)):
        if source == "auto":
            print(f"⚠️  FMP has no financials for {ticker.upper()} "
                  f"({len(FMP_UNAVAILABLE)} endpoints unavailable) → falling back to yfinance\n")
        try:
            inputs = collect_inputs(ticker, get_yf_raw)
            inputs["data_source"] = "yfinance" + (" (fallback: FMP unavailable)" if source == "auto" else "")
            if has_core_data(inputs):
                inputs["source_notes"] = YF_SOURCE_NOTES
        except Exception as e:
            inputs = {"ticker": ticker.upper(), "version": "v4.4", "yfinance_error": f"{type(e).__name__}: {str(e)[:120]}"}
    if FMP_UNAVAILABLE:
        inputs["fmp_unavailable"] = dict(FMP_UNAVAILABLE)

    if not has_core_data(inputs):
        inputs["error"] = (f"No financial statements for {ticker.upper()} from "
                           f"{'FMP or yfinance' if source == 'auto' else source} — "
                           f"check ticker / FMP plan, or pass inputs manually")
        print(json.dumps(inputs, indent=2, ensure_ascii=False))
        print(f"\n❌ {inputs['error']}", file=sys.stderr)
        return inputs

    # Print
    print(json.dumps(inputs, indent=2, ensure_ascii=False))
    sanity_checks(inputs)
    return inputs


def collect_inputs(ticker, fetch):
    """Sections 1-7: pull raw data via `fetch` (get_fmp_raw or get_yf_raw) and derive V4.4 inputs."""
    inputs = {"ticker": ticker.upper(), "version": "v4.4"}

    # 1. Quote
    quote = fetch("quote", ticker)
    if quote:
        q = quote[0] if isinstance(quote, list) else quote
        inputs["current_price"] = q.get("price")
        inputs["market_cap"] = q.get("marketCap")
        inputs["yearHigh"] = q.get("yearHigh")
        inputs["yearLow"] = q.get("yearLow")

    # 2. Key Metrics TTM
    km = fetch("key-metrics-ttm", ticker)
    if km:
        d = km[0] if isinstance(km, list) else km
        inputs["enterprise_value"] = d.get("enterpriseValueTTM")
        inputs["roic"] = d.get("returnOnInvestedCapitalTTM")
        inputs["net_debt_ebitda"] = d.get("netDebtToEBITDATTM")
        inputs["ev_ebitda"] = d.get("evToEBITDATTM")
        inputs["ev_sales"] = d.get("evToSalesTTM")
        inputs["fcf_yield"] = d.get("freeCashFlowYieldTTM")
        inputs["invested_capital"] = d.get("investedCapitalTTM")
        inputs["tax_burden"] = d.get("taxBurdenTTM")  # NEW v4.4
        inputs["interest_burden"] = d.get("interestBurdenTTM")  # NEW v4.4
        if inputs.get("enterprise_value") and inputs.get("market_cap"):
            inputs["net_debt_simple"] = inputs["enterprise_value"] - inputs["market_cap"]

    # 3. Balance Sheet (CRITICAL for v4.4 op leases)
    bs = fetch("balance-sheet-statement", ticker, limit=2)
    if bs:
        latest = bs[0]
        inputs["cash_and_equiv"] = latest.get("cashAndCashEquivalents", 0)
        inputs["st_investments"] = latest.get("shortTermInvestments", 0)
        inputs["total_debt"] = latest.get("totalDebt", 0)
        inputs["lt_debt"] = latest.get("longTermDebt", 0)
        inputs["st_debt"] = latest.get("shortTermDebt", 0)
        # NEW v4.4: Operating Leases
        inputs["operating_leases"] = latest.get("capitalLeaseObligations", 0)
        # NEW v4.4: Adjusted Net Debt (includes op leases per ASC 842)
        # 2026-10-07 fix: FMP totalDebt already = short + long debt + capitalLeaseObligations
        # (verified AAPL/MSFT/NVDA/GOOGL/COST/AMZN) → add leases only if they are evidently NOT in totalDebt
        cash_total = inputs["cash_and_equiv"] + inputs["st_investments"]
        funded = inputs["st_debt"] + inputs["lt_debt"]
        inputs["leases_in_total_debt"] = (
            abs(inputs["total_debt"] - (funded + inputs["operating_leases"]))
            < abs(inputs["total_debt"] - funded)
        )
        inputs["net_debt_adjusted_v44"] = (
            inputs["total_debt"]
            + (0 if inputs["leases_in_total_debt"] else inputs["operating_leases"])
            - cash_total
        )
        inputs["total_equity"] = latest.get("totalStockholdersEquity", 0)

    # 4. Income Statement (5-year)
    is_data = fetch("income-statement", ticker, limit=5)
    if is_data:
        latest = is_data[0]
        inputs["latest_revenue"] = latest.get("revenue")
        inputs["latest_ebit"] = latest.get("operatingIncome")
        inputs["latest_net_income"] = latest.get("netIncome")
        inputs["latest_eps"] = latest.get("eps")
        inputs["weighted_shares_diluted"] = latest.get("weightedAverageShsOutDil")
        # NEW v4.4: explicit tax rate from financials
        if latest.get("incomeBeforeTax") and latest.get("incomeTaxExpense"):
            inputs["effective_tax_rate"] = latest["incomeTaxExpense"] / latest["incomeBeforeTax"]
        if len(is_data) >= 5:
            new_rev = is_data[0].get("revenue", 0)
            old_rev = is_data[4].get("revenue", 0)
            if old_rev > 0:
                inputs["revenue_5yr_cagr"] = round((new_rev / old_rev) ** (1/4) - 1, 4)

    # 5. Cash Flow Statement (5-year)
    cf = fetch("cash-flow-statement", ticker, limit=5)
    if cf:
        latest = cf[0]
        inputs["latest_ocf"] = latest.get("operatingCashFlow")
        inputs["latest_capex"] = latest.get("capitalExpenditure")  # negative number
        inputs["latest_fcf"] = latest.get("freeCashFlow")
        inputs["latest_da"] = latest.get("depreciationAndAmortization")
        # NEW v4.4: SBC extraction
        inputs["latest_sbc"] = latest.get("stockBasedCompensation", 0)
        # NEW v4.4: Manual Owner Earnings (D&A as maintenance capex proxy)
        if inputs["latest_ocf"] and inputs["latest_da"]:
            inputs["manual_owner_earnings"] = inputs["latest_ocf"] - inputs["latest_da"]
        # NEW v4.4: Adjusted FCF (deduct SBC = true economic FCF)
        if inputs["latest_fcf"] and inputs.get("latest_sbc"):
            inputs["adjusted_fcf_v44"] = inputs["latest_fcf"] - inputs["latest_sbc"]
        # NEW v4.4: Adjusted Owner Earnings (deduct SBC)
        if inputs.get("manual_owner_earnings") and inputs.get("latest_sbc"):
            inputs["adjusted_owner_earnings_v44"] = inputs["manual_owner_earnings"] - inputs["latest_sbc"]

    # 6. FMP Owner Earnings
    oe = fetch("owner-earnings", ticker)
    if oe:
        latest_oe = oe[0] if isinstance(oe, list) else oe
        inputs["fmp_owner_earnings_q1"] = latest_oe.get("ownersEarnings")
        inputs["fmp_oe_per_share_q1"] = latest_oe.get("ownersEarningsPerShare")
        inputs["fmp_maintenance_capex_q1"] = latest_oe.get("maintenanceCapex")
        inputs["fmp_growth_capex_q1"] = latest_oe.get("growthCapex")

    # 7. FMP DCF
    dcf = fetch("discounted-cash-flow", ticker)
    if dcf:
        d = dcf[0] if isinstance(dcf, list) else dcf
        inputs["fmp_dcf"] = d.get("dcf")
        inputs["fmp_dcf_stockprice"] = d.get("Stock Price", d.get("stockPrice"))

    return inputs


def sanity_checks(inputs):
    # V4.4 Sanity Checks
    print("\n=== V4.4 Sanity Checks ===")

    # Op Leases impact
    if inputs.get("operating_leases") and inputs.get("net_debt_simple"):
        op_lease_pct = inputs["operating_leases"] / (inputs["net_debt_simple"] + 1e-6) * 100
        if op_lease_pct > 5:
            print(f"⚠️  Op Leases material: ${inputs['operating_leases']/1e9:.1f}B ({op_lease_pct:.0f}% of net debt)")
            print(f"   ASC 842 adjustment NEEDED")
            print(f"   Adjusted Net Debt (V4.4): ${inputs['net_debt_adjusted_v44']/1e9:.1f}B (vs simple ${inputs['net_debt_simple']/1e9:.1f}B)")

    # SBC impact
    if inputs.get("latest_sbc") and inputs.get("latest_fcf"):
        sbc_pct = inputs["latest_sbc"] / inputs["latest_fcf"] * 100
        if sbc_pct > 3:
            print(f"⚠️  SBC material: ${inputs['latest_sbc']/1e9:.1f}B ({sbc_pct:.1f}% of FCF)")
            print(f"   Adjusted FCF (V4.4): ${inputs['adjusted_fcf_v44']/1e9:.1f}B")

    # Tax rate sanity
    if inputs.get("effective_tax_rate"):
        rate = inputs["effective_tax_rate"]
        if rate < 0.05:
            print(f"⚠️  Effective tax rate {rate*100:.1f}% — unusually low, investigate")
        elif rate > 0.35:
            print(f"⚠️  Effective tax rate {rate*100:.1f}% — unusually high, investigate")
        else:
            print(f"✓  Effective tax rate: {rate*100:.1f}%")

    # DCF gap check
    if inputs.get("fmp_dcf") and inputs.get("current_price"):
        gap = (inputs["fmp_dcf"] - inputs["current_price"]) / inputs["current_price"] * 100
        if abs(gap) > 30:
            print(f"⚠️  FMP DCF vs price: {gap:+.1f}% — significant divergence")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="V4.4 pre-flight valuation inputs (op leases + SBC adjusted)")
    ap.add_argument("ticker")
    ap.add_argument("--source", choices=["auto", "fmp", "yf"], default="auto",
                    help="auto (default) = FMP, fall back to yfinance when FMP has no financials for the ticker")
    a = ap.parse_args()
    if "error" in mandatory_inputs_v44(a.ticker, a.source):
        sys.exit(2)
