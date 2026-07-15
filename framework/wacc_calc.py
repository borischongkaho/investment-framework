#!/usr/bin/env python3
"""
V4.4 Standardized WACC Calculation (CAPM-based).
Replaces ad hoc WACC choices across memos.

WACC = (E/V × Re) + (D/V × Rd × (1-T))

Where:
  E = Market Cap (equity value)
  D = Adjusted Net Debt (incl. operating leases)
  V = E + D
  Re = Cost of Equity = Rf + Beta × ERP
  Rd = Cost of Debt
  T = Effective Tax Rate

Risk-Free Rate (Rf):
  Use 10-year US Treasury yield (currently ~4.3%)

Equity Risk Premium (ERP):
  Standard: 5.5% (Damodaran historical)
  Emerging Markets: +2-3% additional country risk premium

Beta:
  Pull from FMP profile endpoint

Usage:
    python wacc_calc.py NVDA
    python wacc_calc.py --rf 4.5 --erp 5.5 NVDA  # custom Rf, ERP
"""

import sys, json, subprocess, argparse
from pathlib import Path


def get_fmp_raw(endpoint, ticker, **params):
    """Direct FMP curl wrapper."""
    api_key = open(Path.home() / ".config" / "boris-investment" / "fmp.env").read().split("=", 1)[1].strip()
    base = "https://financialmodelingprep.com/stable"
    qs_parts = [f"symbol={ticker.upper()}"]
    for k, v in params.items():
        qs_parts.append(f"{k}={v}")
    qs_parts.append(f"apikey={api_key}")
    url = f"{base}/{endpoint}?{'&'.join(qs_parts)}"
    result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=15)
    body = result.stdout
    if "Premium" in body[:200] or "Restricted" in body[:200]:
        return None
    try:
        return json.loads(body)
    except Exception:
        return None


def calc_wacc(ticker, rf=0.043, erp=0.055, country_premium=0.0, debt_premium=0.015):
    """Calculate WACC via CAPM.

    Args:
        rf: Risk-free rate (default 4.3% = 10Y UST current)
        erp: Equity risk premium (default 5.5%)
        country_premium: Additional for EM (e.g. Brazil +3%)
        debt_premium: Spread over risk-free for corporate debt (default 1.5%)
    """
    print(f"=== V4.4 WACC Calculation: {ticker} ===\n")

    # Pull data
    profile = get_fmp_raw("profile", ticker)
    km = get_fmp_raw("key-metrics-ttm", ticker)
    bs = get_fmp_raw("balance-sheet-statement", ticker, limit=1)
    is_data = get_fmp_raw("income-statement", ticker, limit=1)

    # If blocked, use placeholders
    if not profile or not km or not bs or not is_data:
        print(f"⚠️  FMP free tier blocked - need manual inputs")
        return {"wacc": None, "error": "FMP blocked"}

    p = profile[0] if isinstance(profile, list) else profile
    k = km[0] if isinstance(km, list) else km
    b = bs[0] if isinstance(bs, list) else bs
    i = is_data[0] if isinstance(is_data, list) else is_data

    # Extract inputs
    beta = p.get("beta", 1.0)
    market_cap = p.get("marketCap", 0)
    total_debt = b.get("totalDebt", 0)
    op_leases = b.get("capitalLeaseObligations", 0)
    cash_st = b.get("cashAndCashEquivalents", 0) + b.get("shortTermInvestments", 0)
    # V4.4: Adjusted Net Debt incl op leases
    adj_net_debt = total_debt + op_leases - cash_st

    # Effective tax rate
    tax_burden = k.get("taxBurdenTTM", 0.79)  # default 21%
    effective_tax = 1 - tax_burden  # tax burden is post-tax / pre-tax
    if i.get("incomeBeforeTax") and i.get("incomeTaxExpense"):
        effective_tax = i["incomeTaxExpense"] / i["incomeBeforeTax"]

    # Cost of equity (CAPM)
    cost_equity = rf + beta * erp + country_premium

    # Cost of debt (rf + corporate spread)
    cost_debt = rf + debt_premium
    after_tax_cost_debt = cost_debt * (1 - effective_tax)

    # Capital structure weights
    total_capital = market_cap + max(adj_net_debt, 0)  # if net cash, weight = 0
    weight_equity = market_cap / total_capital if total_capital > 0 else 1.0
    weight_debt = max(adj_net_debt, 0) / total_capital if total_capital > 0 else 0.0

    # WACC
    wacc = (weight_equity * cost_equity) + (weight_debt * after_tax_cost_debt)

    output = {
        "ticker": ticker.upper(),
        "version": "v4.4",
        "inputs": {
            "risk_free_rate": rf,
            "equity_risk_premium": erp,
            "country_premium": country_premium,
            "debt_premium": debt_premium,
            "beta": beta,
            "market_cap": market_cap,
            "total_debt": total_debt,
            "operating_leases": op_leases,
            "cash_and_st_investments": cash_st,
            "adjusted_net_debt": adj_net_debt,
            "effective_tax_rate": effective_tax,
        },
        "calculations": {
            "cost_of_equity_capm": cost_equity,
            "cost_of_debt_pretax": cost_debt,
            "cost_of_debt_aftertax": after_tax_cost_debt,
            "weight_equity": weight_equity,
            "weight_debt": weight_debt,
        },
        "wacc": wacc,
    }

    # Print
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n→ WACC = {wacc*100:.2f}%")

    return output


def main():
    parser = argparse.ArgumentParser(description="V4.4 WACC Calculator (CAPM)")
    parser.add_argument("ticker")
    parser.add_argument("--rf", type=float, default=0.043, help="Risk-free rate (default 4.3%)")
    parser.add_argument("--erp", type=float, default=0.055, help="Equity risk premium (default 5.5%)")
    parser.add_argument("--country-premium", type=float, default=0.0, help="Country risk premium for EM (e.g. 0.03 for Brazil)")
    parser.add_argument("--debt-premium", type=float, default=0.015, help="Corporate debt spread over Rf (default 1.5%)")
    args = parser.parse_args()
    calc_wacc(args.ticker, args.rf, args.erp, args.country_premium, args.debt_premium)


if __name__ == "__main__":
    main()
