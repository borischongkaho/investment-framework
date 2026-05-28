#!/usr/bin/env python3
"""
V4.4 Mandatory Pre-Flight Inputs Check.
Includes Operating Leases (ASC 842) + SBC adjustment + Adjusted FCF/OE.

Usage:
    python valuation_inputs.py NVDA
    → outputs all V4.4 adjusted inputs needed for DCF

V4.4 changes from V4.3:
- Adjusted Net Debt = Total Debt + Operating Leases - Cash
- Adjusted FCF = FCF - SBC (true economic FCF)
- Adjusted Owner Earnings = Manual OE - SBC
- Tax rate explicit from financials
- All inputs flagged with source
"""

import sys, json, subprocess
from pathlib import Path


def get_fmp_raw(endpoint, ticker, **params):
    """Direct FMP curl wrapper - tolerates blocked tickers."""
    api_key = open(Path.home() / ".config" / "boris-investment" / "fmp.env").read().split("=", 1)[1].strip()
    base = "https://financialmodelingprep.com/stable"
    qs_parts = [f"symbol={ticker.upper()}"]
    for k, v in params.items():
        qs_parts.append(f"{k}={v}")
    qs_parts.append(f"apikey={api_key}")
    url = f"{base}/{endpoint}?{'&'.join(qs_parts)}"
    result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=15)
    body = result.stdout
    if "Premium" in body[:200] or "Restricted" in body[:200] or "Legacy" in body[:200]:
        return None
    try:
        return json.loads(body)
    except Exception:
        return None


def mandatory_inputs_v44(ticker):
    """V4.4 mandatory pre-flight inputs with op leases + SBC adjustments."""
    print(f"=== V4.4 Pre-Flight Inputs: {ticker} ===\n")

    inputs = {"ticker": ticker.upper(), "version": "v4.4"}

    # 1. Quote
    quote = get_fmp_raw("quote", ticker)
    if quote:
        q = quote[0] if isinstance(quote, list) else quote
        inputs["current_price"] = q.get("price")
        inputs["market_cap"] = q.get("marketCap")
        inputs["yearHigh"] = q.get("yearHigh")
        inputs["yearLow"] = q.get("yearLow")

    # 2. Key Metrics TTM
    km = get_fmp_raw("key-metrics-ttm", ticker)
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
    bs = get_fmp_raw("balance-sheet-statement", ticker, limit=2)
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
        cash_total = inputs["cash_and_equiv"] + inputs["st_investments"]
        inputs["net_debt_adjusted_v44"] = (
            inputs["total_debt"]
            + inputs["operating_leases"]
            - cash_total
        )
        inputs["total_equity"] = latest.get("totalStockholdersEquity", 0)

    # 4. Income Statement (5-year)
    is_data = get_fmp_raw("income-statement", ticker, limit=5)
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
    cf = get_fmp_raw("cash-flow-statement", ticker, limit=5)
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
    oe = get_fmp_raw("owner-earnings", ticker)
    if oe:
        latest_oe = oe[0] if isinstance(oe, list) else oe
        inputs["fmp_owner_earnings_q1"] = latest_oe.get("ownersEarnings")
        inputs["fmp_oe_per_share_q1"] = latest_oe.get("ownersEarningsPerShare")
        inputs["fmp_maintenance_capex_q1"] = latest_oe.get("maintenanceCapex")
        inputs["fmp_growth_capex_q1"] = latest_oe.get("growthCapex")

    # 7. FMP DCF
    dcf = get_fmp_raw("discounted-cash-flow", ticker)
    if dcf:
        d = dcf[0] if isinstance(dcf, list) else dcf
        inputs["fmp_dcf"] = d.get("dcf")
        inputs["fmp_dcf_stockprice"] = d.get("Stock Price", d.get("stockPrice"))

    # Print
    print(json.dumps(inputs, indent=2, ensure_ascii=False))

    # V4.4 Sanity Checks
    print("\n=== V4.4 Sanity Checks ===")

    # Op Leases impact
    if inputs.get("operating_leases") and inputs.get("net_debt_simple"):
        op_lease_pct = inputs["operating_leases"] / (inputs["net_debt_simple"] + 1e-6) * 100
        if op_lease_pct > 5:
            print(f"⚠️  Op Leases material: \${inputs['operating_leases']/1e9:.1f}B ({op_lease_pct:.0f}% of net debt)")
            print(f"   ASC 842 adjustment NEEDED")
            print(f"   Adjusted Net Debt (V4.4): \${inputs['net_debt_adjusted_v44']/1e9:.1f}B (vs simple \${inputs['net_debt_simple']/1e9:.1f}B)")

    # SBC impact
    if inputs.get("latest_sbc") and inputs.get("latest_fcf"):
        sbc_pct = inputs["latest_sbc"] / inputs["latest_fcf"] * 100
        if sbc_pct > 3:
            print(f"⚠️  SBC material: \${inputs['latest_sbc']/1e9:.1f}B ({sbc_pct:.1f}% of FCF)")
            print(f"   Adjusted FCF (V4.4): \${inputs['adjusted_fcf_v44']/1e9:.1f}B")

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

    return inputs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python valuation_inputs.py TICKER")
        sys.exit(1)
    mandatory_inputs_v44(sys.argv[1])
