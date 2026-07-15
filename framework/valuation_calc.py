#!/usr/bin/env python3
"""
Valuation Calculation Library
investment framework — Layer 1 of Calculation Safety Net.

Why this exists:
LLM 直接做 DCF / EPV multi-step arithmetic 會有 5-15% error rate.
所有 valuation numerical calc 都要由 Python 執行，唔可以 LLM inline 計.

Usage:
    python3 valuation_calc.py dcf2 '{"fcf_year1": 100, "growth_high": 0.15, ...}'   # 2-stage DCF
    python3 valuation_calc.py dcf3 '{"fcf_year1": 100, ...}'                          # 3-stage DCF
    python3 valuation_calc.py epv '{"normalized_earnings": 100, "wacc": 0.09, ...}'
    python3 valuation_calc.py wacc '{"risk_free_rate": 0.045, ...}'
    python3 valuation_calc.py sensitivity '{"base_inputs": {...}, "wacc_range": [...], "growth_terminal_range": [...]}'
    python3 valuation_calc.py sanity '{"wacc": 0.09, "iv_per_share": 150, "current_price": 100, ...}'

Or import as module:
    from valuation_calc import dcf_two_stage, epv, sanity_check
"""

import json
import math
import random
import statistics
import sys
from typing import Optional


# -----------------------------------------------------------------------------
# DCF — Two-Stage Growth Model
# -----------------------------------------------------------------------------
def dcf_two_stage(
    fcf_year1: float,
    growth_high: float,
    years_high: int,
    growth_terminal: float,
    wacc: float,
    shares_outstanding: float,
    net_debt: float = 0.0,
) -> dict:
    """
    Two-stage DCF: high-growth period + terminal Gordon growth.

    fcf_year1: Year 1 projected free cash flow (in millions)
    growth_high: high-growth rate (e.g. 0.15 for 15%)
    years_high: number of years of high growth
    growth_terminal: perpetual growth rate
    wacc: weighted average cost of capital
    shares_outstanding: diluted shares (in millions)
    net_debt: total debt - cash (in millions)
    """
    if wacc <= growth_terminal:
        raise ValueError(
            f"WACC ({wacc:.2%}) must be > terminal growth ({growth_terminal:.2%}). "
            "Otherwise terminal value diverges to infinity."
        )

    pv_fcf = []
    fcf = fcf_year1
    for year in range(1, years_high + 1):
        if year > 1:
            fcf = fcf * (1 + growth_high)
        discount_factor = (1 + wacc) ** year
        pv = fcf / discount_factor
        pv_fcf.append({"year": year, "fcf": fcf, "pv": pv})

    fcf_terminal_year = fcf * (1 + growth_terminal)
    terminal_value = fcf_terminal_year / (wacc - growth_terminal)
    pv_terminal = terminal_value / ((1 + wacc) ** years_high)

    enterprise_value = sum(p["pv"] for p in pv_fcf) + pv_terminal
    equity_value = enterprise_value - net_debt
    iv_per_share = equity_value / shares_outstanding

    return {
        "method": "DCF Two-Stage",
        "inputs": {
            "fcf_year1": fcf_year1,
            "growth_high": growth_high,
            "years_high": years_high,
            "growth_terminal": growth_terminal,
            "wacc": wacc,
            "shares_outstanding": shares_outstanding,
            "net_debt": net_debt,
        },
        "pv_fcf_explicit": pv_fcf,
        "sum_pv_fcf": sum(p["pv"] for p in pv_fcf),
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "iv_per_share": iv_per_share,
    }


# -----------------------------------------------------------------------------
# DCF — Three-Stage Growth Model
# -----------------------------------------------------------------------------
def dcf_three_stage(
    fcf_year1: float,
    growth_high: float,
    years_high: int,
    growth_mid: float,
    years_mid: int,
    growth_terminal: float,
    wacc: float,
    shares_outstanding: float,
    net_debt: float = 0.0,
) -> dict:
    """
    Three-stage DCF: high-growth + mid-growth + terminal.
    Use for younger companies that transition through phases.
    """
    if wacc <= growth_terminal:
        raise ValueError(
            f"WACC ({wacc:.2%}) must be > terminal growth ({growth_terminal:.2%})"
        )

    pv_fcf = []
    fcf = fcf_year1

    for year in range(1, years_high + 1):
        if year > 1:
            fcf = fcf * (1 + growth_high)
        discount_factor = (1 + wacc) ** year
        pv = fcf / discount_factor
        pv_fcf.append({"year": year, "stage": "high", "fcf": fcf, "pv": pv})

    for year in range(years_high + 1, years_high + years_mid + 1):
        fcf = fcf * (1 + growth_mid)
        discount_factor = (1 + wacc) ** year
        pv = fcf / discount_factor
        pv_fcf.append({"year": year, "stage": "mid", "fcf": fcf, "pv": pv})

    last_year = years_high + years_mid
    fcf_terminal_year = fcf * (1 + growth_terminal)
    terminal_value = fcf_terminal_year / (wacc - growth_terminal)
    pv_terminal = terminal_value / ((1 + wacc) ** last_year)

    enterprise_value = sum(p["pv"] for p in pv_fcf) + pv_terminal
    equity_value = enterprise_value - net_debt
    iv_per_share = equity_value / shares_outstanding

    return {
        "method": "DCF Three-Stage",
        "inputs": {
            "fcf_year1": fcf_year1,
            "growth_high": growth_high,
            "years_high": years_high,
            "growth_mid": growth_mid,
            "years_mid": years_mid,
            "growth_terminal": growth_terminal,
            "wacc": wacc,
            "shares_outstanding": shares_outstanding,
            "net_debt": net_debt,
        },
        "pv_fcf_explicit": pv_fcf,
        "sum_pv_fcf": sum(p["pv"] for p in pv_fcf),
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "iv_per_share": iv_per_share,
    }


# -----------------------------------------------------------------------------
# DCF Three-Stage — COURSE-STRICT (ACCT6111E Dr. Swaminathan)
# Terminal: NOPAT × (1 - g/ROI) / (WACC - g)
# -----------------------------------------------------------------------------
def dcf_three_stage_course_strict(
    nopat_year1: float,
    growth_high: float,
    years_high: int,
    growth_mid: float,
    years_mid: int,
    growth_terminal: float,
    wacc: float,
    terminal_roi: float,
    shares_outstanding: float,
    net_debt: float = 0.0,
    roi_stage1: float = None,
    roi_stage2: float = None,
) -> dict:
    """
    Three-stage DCF using ACCT6111E course-strict terminal formula.

    KEY DIFFERENCE FROM PLAIN GORDON:
        Plain Gordon:  TV = FCF × (1+g) / (WACC - g)
        Course-Strict: TV = NOPAT × (1 - g/ROI) / (WACC - g)

    Course version explicitly accounts for terminal reinvestment rate b = g/ROI.
    Required when modeling compounders where terminal ROI > WACC (sustained moat).

    Inputs:
        nopat_year1: NOPAT (gross of reinvestment), millions
        growth_high, years_high: Stage 1 growth rate + duration
        growth_mid, years_mid: Stage 2 transition rate + duration
        growth_terminal: perpetual growth rate
        wacc: discount rate
        terminal_roi: terminal Return On Invested Capital
                     (course default: ROI = WACC for conservative)
        shares_outstanding: diluted shares, millions
        net_debt: total debt - cash, millions
        roi_stage1: explicit period ROI for Stage 1 (default: terminal_roi + 5%)
        roi_stage2: ROI fading toward terminal (default: between Stage1 + terminal)

    Returns same dict structure as dcf_three_stage().
    """
    if wacc <= growth_terminal:
        raise ValueError(
            f"WACC ({wacc:.2%}) must be > terminal growth ({growth_terminal:.2%})"
        )
    if terminal_roi <= 0:
        raise ValueError("terminal_roi must be positive")
    if growth_terminal > terminal_roi:
        raise ValueError(
            f"terminal_growth ({growth_terminal:.2%}) cannot exceed terminal_roi ({terminal_roi:.2%}). "
            "Reinvestment b = g/ROI would exceed 100%."
        )

    # Default ROI assumptions if not provided
    if roi_stage1 is None:
        roi_stage1 = max(wacc + 0.05, terminal_roi + 0.05)
    if roi_stage2 is None:
        roi_stage2 = max(wacc + 0.02, terminal_roi)

    pv_fcf = []
    nopat = nopat_year1

    # Stage 1 — high growth
    for year in range(1, years_high + 1):
        if year > 1:
            nopat = nopat * (1 + growth_high)
        b_stage1 = growth_high / roi_stage1
        fcf = nopat * (1 - b_stage1)
        pv = fcf / ((1 + wacc) ** year)
        pv_fcf.append({
            "year": year, "stage": "high", "nopat": nopat,
            "b": b_stage1, "fcf": fcf, "pv": pv,
        })

    # Stage 2 — transition
    for year in range(years_high + 1, years_high + years_mid + 1):
        nopat = nopat * (1 + growth_mid)
        b_stage2 = growth_mid / roi_stage2
        fcf = nopat * (1 - b_stage2)
        pv = fcf / ((1 + wacc) ** year)
        pv_fcf.append({
            "year": year, "stage": "mid", "nopat": nopat,
            "b": b_stage2, "fcf": fcf, "pv": pv,
        })

    # Terminal — COURSE-STRICT formula
    # TV = NOPAT(t+1) × (1 - g/ROI_terminal) / (WACC - g)
    last_year = years_high + years_mid
    nopat_terminal = nopat * (1 + growth_terminal)
    b_terminal = growth_terminal / terminal_roi
    fcf_terminal = nopat_terminal * (1 - b_terminal)
    terminal_value = fcf_terminal / (wacc - growth_terminal)
    pv_terminal = terminal_value / ((1 + wacc) ** last_year)

    sum_pv_explicit = sum(p["pv"] for p in pv_fcf)
    enterprise_value = sum_pv_explicit + pv_terminal
    equity_value = enterprise_value - net_debt
    iv_per_share = equity_value / shares_outstanding

    return {
        "method": "DCF Three-Stage (Course-Strict ACCT6111E)",
        "formula": "TV = NOPAT × (1 - g/ROI) / (WACC - g)",
        "inputs": {
            "nopat_year1": nopat_year1,
            "growth_high": growth_high, "years_high": years_high,
            "growth_mid": growth_mid, "years_mid": years_mid,
            "growth_terminal": growth_terminal,
            "wacc": wacc, "terminal_roi": terminal_roi,
            "roi_stage1": roi_stage1, "roi_stage2": roi_stage2,
            "shares_outstanding": shares_outstanding,
            "net_debt": net_debt,
        },
        "pv_fcf_explicit": pv_fcf,
        "sum_pv_explicit": sum_pv_explicit,
        "nopat_terminal_year": nopat_terminal,
        "b_terminal": b_terminal,
        "fcf_terminal": fcf_terminal,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "tv_concentration": pv_terminal / enterprise_value,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "iv_per_share": iv_per_share,
    }


# -----------------------------------------------------------------------------
# EPV — Earnings Power Value (Bruce Greenwald / Dr. Swaminathan)
# -----------------------------------------------------------------------------
def epv(
    normalized_earnings: float,
    wacc: float,
    shares_outstanding: float,
    net_debt: float = 0.0,
    excess_assets: float = 0.0,
) -> dict:
    """
    EPV = Normalized Earnings / WACC, no growth assumed.
    Conservative floor — what biz worth if it never grew.

    normalized_earnings: cycle-adjusted FCF or owner earnings (in millions)
    wacc: cost of capital
    excess_assets: cash / non-operating assets to add back
    """
    if wacc <= 0:
        raise ValueError(f"WACC ({wacc:.2%}) must be > 0")

    epv_operations = normalized_earnings / wacc
    epv_total = epv_operations + excess_assets - net_debt
    iv_per_share = epv_total / shares_outstanding

    return {
        "method": "EPV (Earnings Power Value)",
        "inputs": {
            "normalized_earnings": normalized_earnings,
            "wacc": wacc,
            "shares_outstanding": shares_outstanding,
            "net_debt": net_debt,
            "excess_assets": excess_assets,
        },
        "epv_operations": epv_operations,
        "epv_total": epv_total,
        "iv_per_share": iv_per_share,
    }


# -----------------------------------------------------------------------------
# WACC Calculation
# -----------------------------------------------------------------------------
def wacc_calc(
    risk_free_rate: float,
    equity_risk_premium: float,
    beta: float,
    cost_of_debt_pretax: float,
    tax_rate: float,
    weight_equity: float,
    weight_debt: float,
    small_cap_premium: float = 0.0,
) -> dict:
    """
    WACC = (E/V) * Re + (D/V) * Rd * (1 - T)
    where Re = Rf + beta * ERP (+ small cap premium)
    """
    if abs(weight_equity + weight_debt - 1.0) > 0.001:
        raise ValueError(
            f"Weights must sum to 1.0, got {weight_equity + weight_debt}"
        )

    cost_of_equity = risk_free_rate + beta * equity_risk_premium + small_cap_premium
    cost_of_debt_aftertax = cost_of_debt_pretax * (1 - tax_rate)
    wacc = weight_equity * cost_of_equity + weight_debt * cost_of_debt_aftertax

    return {
        "method": "WACC",
        "inputs": {
            "risk_free_rate": risk_free_rate,
            "equity_risk_premium": equity_risk_premium,
            "beta": beta,
            "cost_of_debt_pretax": cost_of_debt_pretax,
            "tax_rate": tax_rate,
            "weight_equity": weight_equity,
            "weight_debt": weight_debt,
            "small_cap_premium": small_cap_premium,
        },
        "cost_of_equity": cost_of_equity,
        "cost_of_debt_aftertax": cost_of_debt_aftertax,
        "wacc": wacc,
    }


# -----------------------------------------------------------------------------
# Sensitivity Analysis — DCF intrinsic value across WACC × growth grid
# -----------------------------------------------------------------------------
def sensitivity_dcf(
    base_inputs: dict,
    wacc_range: list,
    growth_terminal_range: list,
) -> dict:
    """
    Generate sensitivity table: IV per share for each (wacc, terminal_growth) cell.
    base_inputs must match dcf_two_stage signature.
    """
    grid = []
    for wacc in wacc_range:
        row = []
        for g in growth_terminal_range:
            inputs = dict(base_inputs)
            inputs["wacc"] = wacc
            inputs["growth_terminal"] = g
            try:
                result = dcf_two_stage(**inputs)
                row.append(round(result["iv_per_share"], 2))
            except ValueError:
                row.append(None)
        grid.append(row)

    return {
        "method": "Sensitivity (WACC × Terminal Growth)",
        "wacc_range": wacc_range,
        "growth_range": growth_terminal_range,
        "grid": grid,
    }


# -----------------------------------------------------------------------------
# Layer 3: Sanity Bounds Check
# -----------------------------------------------------------------------------
SANITY_BOUNDS = {
    "wacc": (0.06, 0.15),  # 6% - 15% normal range
    "growth_high": (-0.20, 0.50),
    "growth_mid": (-0.10, 0.30),
    "growth_terminal": (0.01, 0.04),  # tied to long-run GDP
    "tax_rate": (0.15, 0.30),
    "iv_to_price_ratio": (0.3, 3.0),  # outside this is suspicious
    "beta": (0.3, 2.5),
}


def sanity_check(values: dict) -> dict:
    """
    Check valuation inputs / outputs against reasonable bounds.
    Flag anything out-of-range so user can investigate before trusting result.

    values dict can contain any of: wacc, growth_high, growth_mid, growth_terminal,
    tax_rate, iv_per_share, current_price, beta.

    Returns: list of flags (empty = all good).
    """
    flags = []

    for key, (lo, hi) in SANITY_BOUNDS.items():
        if key in values and values[key] is not None:
            v = values[key]
            if v < lo or v > hi:
                flags.append({
                    "metric": key,
                    "value": v,
                    "expected_range": [lo, hi],
                    "severity": "HIGH" if (v < lo * 0.5 or v > hi * 1.5) else "MEDIUM",
                    "message": f"{key}={v} outside expected [{lo}, {hi}]",
                })

    if "iv_per_share" in values and "current_price" in values:
        iv = values["iv_per_share"]
        price = values["current_price"]
        if price <= 0:
            flags.append({
                "metric": "current_price",
                "value": price,
                "expected_range": ["> 0"],
                "severity": "HIGH",
                "message": f"current_price={price} invalid — must be positive. Re-fetch from market.",
            })
        else:
            ratio = iv / price
            lo, hi = SANITY_BOUNDS["iv_to_price_ratio"]
            if ratio < lo or ratio > hi:
                flags.append({
                    "metric": "iv_to_price_ratio",
                    "value": round(ratio, 2),
                    "expected_range": [lo, hi],
                    "severity": "HIGH",
                    "message": (
                        f"IV/Price = {ratio:.2f}x — extreme. "
                        "Either market is wildly mispriced or your assumptions are off."
                    ),
                })

    if "iv_per_share" in values and values["iv_per_share"] is not None and values["iv_per_share"] <= 0:
        flags.append({
            "metric": "iv_per_share",
            "value": values["iv_per_share"],
            "expected_range": ["> 0"],
            "severity": "HIGH",
            "message": "IV per share <= 0 — likely calc error or distressed company; verify inputs.",
        })

    return {
        "passed": len(flags) == 0,
        "flag_count": len(flags),
        "flags": flags,
    }


# -----------------------------------------------------------------------------
# Quality / Forensic Helpers (V4.1 from FISV lessons)
# -----------------------------------------------------------------------------

def gaap_gap_check(gaap_eps: float, non_gaap_eps: float, threshold: float = 0.30) -> dict:
    """
    Detect quality concern when GAAP / Non-GAAP EPS gap is too wide.

    From FISV post-mortem (2026-05-05):
    - FISV Q1 GAAP $1.07 vs Non-GAAP $1.79 = 67% gap
    - Sustained gap > 30% = quality flag
    - Action: Haircut DCF intrinsic by 15% if flagged
    """
    if gaap_eps == 0:
        return {"flag": True, "reason": "GAAP EPS = 0 (extreme quality concern)", "gap_pct": None}

    gap_pct = (non_gaap_eps - gaap_eps) / abs(gaap_eps)
    flagged = gap_pct > threshold

    return {
        "flag": flagged,
        "gap_pct": gap_pct,
        "threshold": threshold,
        "gaap_eps": gaap_eps,
        "non_gaap_eps": non_gaap_eps,
        "recommendation": (
            f"⚠️ HAIRCUT INTRINSIC 15% — Non-GAAP excludes {gap_pct*100:.1f}% of real cost"
            if flagged else "✅ GAAP/Non-GAAP gap acceptable"
        ),
    }


def position_size_check(proposed_size_pct: float, conviction_tier: int = 2,
                         max_cap: float = 0.12) -> dict:
    """
    Hard cap on position size per V3.0 / FISV lesson.

    Tier 1 (highest conviction): max 12% (0.12)
    Tier 2: max 8% (0.08)
    Tier 3: max 5% (0.05)
    Tier 4: max 3% (0.03)
    """
    tier_caps = {1: 0.12, 2: 0.08, 3: 0.05, 4: 0.03}
    applicable_cap = tier_caps.get(conviction_tier, 0.05)
    auto_reject = proposed_size_pct > applicable_cap

    return {
        "auto_reject": auto_reject,
        "proposed_size_pct": proposed_size_pct,
        "tier": conviction_tier,
        "applicable_cap": applicable_cap,
        "absolute_max": max_cap,
        "recommendation": (
            f"❌ AUTO-REJECT: Size {proposed_size_pct*100:.1f}% > Tier {conviction_tier} cap {applicable_cap*100:.1f}%"
            if auto_reject else
            f"✅ Size {proposed_size_pct*100:.1f}% within Tier {conviction_tier} cap"
        ),
    }


def organic_revenue_check(organic_yoy_history: list, decline_threshold: float = 0,
                           consecutive_quarters: int = 2) -> dict:
    """
    Auto-AVOID flag when organic revenue YoY declined for N+ consecutive quarters.

    From FISV: Q4 2025 + Q1 2026 organic both negative → would have triggered AVOID.
    Override only if specific catalyst (new product, M&A close, regulatory).
    """
    consecutive_negative = 0
    max_streak = 0
    for q in reversed(organic_yoy_history):
        if q < decline_threshold:
            consecutive_negative += 1
            max_streak = max(max_streak, consecutive_negative)
        else:
            consecutive_negative = 0

    auto_avoid = max_streak >= consecutive_quarters

    return {
        "auto_avoid": auto_avoid,
        "max_consecutive_negative_quarters": max_streak,
        "trigger_threshold": consecutive_quarters,
        "history": organic_yoy_history,
        "recommendation": (
            f"❌ AUTO-AVOID: {max_streak} consecutive declining organic quarters (≥ {consecutive_quarters} threshold)"
            if auto_avoid else
            f"✅ Organic revenue trend acceptable (max streak {max_streak})"
        ),
    }


def reverse_dcf(current_market_cap: float, fcf_year1: float, wacc: float,
                growth_terminal: float, years_high: int = 5,
                tolerance: float = 0.001) -> dict:
    """
    Reverse DCF: solve for implied Stage 1 growth rate that matches current market cap.

    Use to assess whether market expectation is realistic vs Mauboussin base rates:
    - Implied growth > 15% × 5 years: only top 25% of S&P 1500 achieve
    - Implied growth > 20% × 5 years: only top 8%
    - Implied growth > 25% × 5 years: heroic (< 5%)

    Binary search method.
    """
    def dcf_at_growth(g_high):
        pv = 0
        for year in range(1, years_high + 1):
            fcf_y = fcf_year1 * ((1 + g_high) ** (year - 1))
            pv += fcf_y / ((1 + wacc) ** year)
        terminal_fcf = fcf_year1 * ((1 + g_high) ** (years_high - 1)) * (1 + growth_terminal)
        terminal_value = terminal_fcf / (wacc - growth_terminal)
        pv += terminal_value / ((1 + wacc) ** years_high)
        return pv

    low, high = -0.20, 0.50
    for _ in range(60):
        mid = (low + high) / 2
        ev = dcf_at_growth(mid)
        if abs(ev - current_market_cap) < tolerance * current_market_cap:
            return {
                "implied_growth_high": mid,
                "implied_growth_pct": mid * 100,
                "check_market_cap": ev,
                "target_market_cap": current_market_cap,
                "base_rate_assessment": _base_rate_label(mid),
            }
        if ev < current_market_cap:
            low = mid
        else:
            high = mid

    return {"error": "Binary search did not converge", "last_mid": mid}


def _base_rate_label(growth: float) -> str:
    """Mauboussin S&P 1500 (1950-2015) base rates."""
    g_pct = growth * 100
    if g_pct < 0:
        return "🟢 Pessimistic / Distressed (market priced for decline)"
    elif g_pct < 5:
        return "🟢 Conservative (50%+ base rate)"
    elif g_pct < 10:
        return "🟢 Realistic (40% base rate)"
    elif g_pct < 15:
        return "🟡 Optimistic (25% base rate)"
    elif g_pct < 20:
        return "🟠 Aggressive (15% base rate)"
    elif g_pct < 25:
        return "🟠 Top decile (8% base rate)"
    else:
        return "🔴 Heroic (< 5% base rate)"


def yield_velocity_check(historical_yields: list, lookback_months: int = 18) -> dict:
    """
    Detect yield trap pattern: sudden yield jump > 50% over 12-18 months
    on previously stable name.

    From GIS post-mortem 2026-05-06:
    - GIS yield 3.5% (2024) → 4.5% (2025) → 6.86% (2026 TTM)
    - 96% increase in 18 months = yield trap warning
    - Historical pattern: KHC 2017, IBM 2018, GE 2018

    historical_yields: list of yields in chronological order (oldest first)
                       e.g., [3.5, 4.5, 6.86] = 18-month progression
    """
    if len(historical_yields) < 2:
        return {"flag": False, "reason": "Need at least 2 yield data points"}

    earliest = historical_yields[0]
    latest = historical_yields[-1]
    if earliest == 0:
        return {"flag": True, "reason": "Earliest yield = 0 (data error or no dividend before)"}

    velocity_pct = (latest - earliest) / earliest * 100
    flag_warning = velocity_pct > 50  # 50% increase = trap warning

    return {
        "flag_yield_trap": flag_warning,
        "velocity_pct": round(velocity_pct, 1),
        "earliest_yield": earliest,
        "latest_yield": latest,
        "lookback_months": lookback_months,
        "history": historical_yields,
        "recommendation": (
            f"⚠️ YIELD TRAP WARNING: {velocity_pct:.0f}% velocity in {lookback_months}mo. "
            f"Market predicting cut/freeze. Verify dividend coverage + management commentary."
            if flag_warning else
            f"✅ Yield velocity {velocity_pct:.0f}% within normal range"
        ),
    }


def owner_earnings(net_income: float, da: float, maintenance_capex: float,
                    working_capital_change: float = 0) -> dict:
    """
    Buffett's Owner Earnings = NI + D&A - Maintenance CapEx ± Working Capital change.

    Maintenance CapEx ≈ D&A for asset-medium companies; rule of thumb:
    - Asset-light (Visa, Adyen): 30-50% of total capex
    - Asset-medium (GIS, retail): 60-70%
    - Asset-heavy (railroads, utilities): 80-90%
    """
    oe = net_income + da - maintenance_capex - working_capital_change
    return {
        "owner_earnings": oe,
        "components": {
            "net_income": net_income,
            "depreciation_amortization": da,
            "less_maintenance_capex": -maintenance_capex,
            "less_wc_change": -working_capital_change,
        },
        "per_share_if_known": "Divide by shares_outstanding to get OE/share",
    }


# -----------------------------------------------------------------------------
# Statistical Confidence Layer (V5 Foundation)
# -----------------------------------------------------------------------------
# Why this section exists:
# Without confidence intervals, single-point estimates ("IV = $185", "hit rate = 87.5%")
# overstate certainty. Critic 5/9 report flagged this as #1 credibility gap.
#
# wilson_ci    — binomial CI for backtest hit rates (small n, extreme p tolerant)
# monte_carlo_dcf — distribution-based IV instead of single-point estimate

_WILSON_Z_TABLE = {0.80: 1.2816, 0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}


def wilson_ci(successes: int, n: int, confidence: float = 0.95) -> dict:
    """
    Wilson score interval for a binomial proportion.

    Why Wilson over normal approximation:
    - Normal approx breaks for small n (< 30) — gives bounds outside [0,1].
    - Normal approx breaks for extreme p (near 0 or 1) — coverage drops.
    - Wilson stays well-calibrated across full p range, even at small n.

    Primary use: backtest hit rate reporting.
        "16 cases, 14 hit" → 87.5% [62.5%, 96.7%] (n=16)

    Args:
        successes: count of successful trials (0 <= successes <= n)
        n: total sample size (>= 1)
        confidence: confidence level in (0, 1); standard values are
                    0.80 / 0.90 / 0.95 / 0.99
    """
    if n < 1:
        raise ValueError(f"n ({n}) must be >= 1")
    if successes < 0 or successes > n:
        raise ValueError(f"successes ({successes}) must be in [0, {n}]")
    if not (0 < confidence < 1):
        raise ValueError(f"confidence ({confidence}) must be in (0, 1)")

    z = _WILSON_Z_TABLE.get(round(confidence, 2))
    if z is None:
        raise ValueError(
            f"confidence={confidence} not in standard table {sorted(_WILSON_Z_TABLE)}. "
            "Use one of these standard levels."
        )

    p = successes / n
    denom = 1 + (z ** 2) / n
    centre = (p + (z ** 2) / (2 * n)) / denom
    half_width = (z * math.sqrt(p * (1 - p) / n + (z ** 2) / (4 * (n ** 2)))) / denom

    lower = max(0.0, centre - half_width)
    upper = min(1.0, centre + half_width)
    width = upper - lower

    if width >= 0.50:
        interpretation = "TOO WIDE — sample too small for any confident claim"
    elif width >= 0.20:
        interpretation = "WIDE — directional signal only, need more samples"
    elif width >= 0.10:
        interpretation = "MODERATE — meaningful but not precise"
    else:
        interpretation = "TIGHT — high confidence in the rate"

    return {
        "method": "Wilson Score Interval",
        "successes": successes,
        "n": n,
        "point_estimate": p,
        "confidence": confidence,
        "lower": lower,
        "upper": upper,
        "ci_width": width,
        "interpretation": interpretation,
        "formatted": f"{p*100:.1f}% [{lower*100:.1f}%, {upper*100:.1f}%] (n={n}, {int(confidence*100)}% CI)",
    }


def monte_carlo_dcf(
    base_inputs: dict,
    num_simulations: int = 10000,
    uncertainty: str = "medium",
    seed: int = 42,
    method: str = "two_stage",
) -> dict:
    """
    Monte Carlo DCF: replace single-point IV estimate with a sampled distribution.

    Inputs (growth, WACC, terminal growth) are drawn from Gaussian distributions
    around the base assumptions, and a DCF is run for each draw. Output is a
    distribution of IV values, summarized by percentile (p5/25/50/75/95).

    Why this matters:
    - Single-point IV hides assumption sensitivity.
    - "IV = $185" feels solid; "IV most likely $148-$232 (90% CI)" is honest.

    Uncertainty presets (translated to Gaussian std for sampling):
        "low":    ±5% rel growth, ±25bps WACC, ±25bps terminal_g
        "medium": ±15% rel growth, ±50bps WACC, ±50bps terminal_g (default)
        "high":   ±25% rel growth, ±100bps WACC, ±100bps terminal_g

    Args:
        base_inputs: dict matching dcf_two_stage or dcf_three_stage signature
        num_simulations: number of MC draws (default 10000)
        uncertainty: "low" / "medium" / "high"
        seed: random seed for reproducibility
        method: "two_stage" or "three_stage"
    """
    presets = {
        "low":    {"growth_rel_std": 0.05, "wacc_abs_std": 0.0025, "term_abs_std": 0.0025},
        "medium": {"growth_rel_std": 0.15, "wacc_abs_std": 0.0050, "term_abs_std": 0.0050},
        "high":   {"growth_rel_std": 0.25, "wacc_abs_std": 0.0100, "term_abs_std": 0.0100},
    }
    if uncertainty not in presets:
        raise ValueError(f"uncertainty must be one of {list(presets)}, got {uncertainty!r}")

    if method == "two_stage":
        dcf_fn = dcf_two_stage
    elif method == "three_stage":
        dcf_fn = dcf_three_stage
    else:
        raise ValueError(f"method must be 'two_stage' or 'three_stage', got {method!r}")

    spec = presets[uncertainty]
    rng = random.Random(seed)

    base_growth_high = base_inputs["growth_high"]
    base_wacc = base_inputs["wacc"]
    base_term = base_inputs["growth_terminal"]
    growth_high_std = max(abs(base_growth_high) * spec["growth_rel_std"], 0.005)

    base_growth_mid = base_inputs.get("growth_mid")
    growth_mid_std = (
        max(abs(base_growth_mid) * spec["growth_rel_std"], 0.005)
        if base_growth_mid is not None else None
    )

    iv_samples = []
    error_count = 0

    for _ in range(num_simulations):
        sample = dict(base_inputs)
        sample["growth_high"] = rng.gauss(base_growth_high, growth_high_std)
        sample["wacc"] = max(0.03, rng.gauss(base_wacc, spec["wacc_abs_std"]))
        sample["growth_terminal"] = max(0.0, rng.gauss(base_term, spec["term_abs_std"]))

        if method == "three_stage" and base_growth_mid is not None:
            sample["growth_mid"] = rng.gauss(base_growth_mid, growth_mid_std)

        try:
            result = dcf_fn(**sample)
            iv = result["iv_per_share"]
            if iv > 0 and not (math.isnan(iv) or math.isinf(iv)):
                iv_samples.append(iv)
            else:
                error_count += 1
        except (ValueError, ZeroDivisionError):
            error_count += 1

    if len(iv_samples) < 100:
        raise ValueError(
            f"Only {len(iv_samples)}/{num_simulations} simulations valid. "
            "Inputs likely too unstable — review base assumptions or lower uncertainty."
        )

    iv_samples.sort()

    def _pctl(samples_sorted: list, p: float) -> float:
        k = (len(samples_sorted) - 1) * p
        floor_k = math.floor(k)
        ceil_k = math.ceil(k)
        if floor_k == ceil_k:
            return samples_sorted[int(k)]
        return samples_sorted[floor_k] * (ceil_k - k) + samples_sorted[ceil_k] * (k - floor_k)

    p5 = _pctl(iv_samples, 0.05)
    p25 = _pctl(iv_samples, 0.25)
    p50 = _pctl(iv_samples, 0.50)
    p75 = _pctl(iv_samples, 0.75)
    p95 = _pctl(iv_samples, 0.95)

    mean_iv = statistics.mean(iv_samples)
    stdev_iv = statistics.stdev(iv_samples) if len(iv_samples) > 1 else 0.0

    return {
        "method": f"Monte Carlo DCF ({method})",
        "uncertainty_preset": uncertainty,
        "num_simulations": num_simulations,
        "num_valid": len(iv_samples),
        "num_errors": error_count,
        "mean": mean_iv,
        "median_p50": p50,
        "stdev": stdev_iv,
        "p5": p5,
        "p25": p25,
        "p75": p75,
        "p95": p95,
        "ci_90_lower": p5,
        "ci_90_upper": p95,
        "ci_50_lower": p25,
        "ci_50_upper": p75,
        "formatted": (
            f"IV median ${p50:.2f} "
            f"(90% CI: ${p5:.2f}-${p95:.2f}, 50% CI: ${p25:.2f}-${p75:.2f})"
        ),
        "input_distributions": {
            "growth_high": {"mean": base_growth_high, "std": growth_high_std},
            "wacc": {"mean": base_wacc, "std": spec["wacc_abs_std"]},
            "growth_terminal": {"mean": base_term, "std": spec["term_abs_std"]},
            "growth_mid": (
                {"mean": base_growth_mid, "std": growth_mid_std}
                if base_growth_mid is not None else None
            ),
        },
    }


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
DISPATCH = {
    "dcf2": dcf_two_stage,
    "dcf3": dcf_three_stage,
    "dcf3_strict": dcf_three_stage_course_strict,  # COURSE-STRICT ACCT6111E
    "epv": epv,
    "wacc": wacc_calc,
    "sensitivity": lambda **kw: sensitivity_dcf(**kw),
    "sanity": lambda **kw: sanity_check(kw),
    "gaap_gap": lambda **kw: gaap_gap_check(**kw),
    "position_size": lambda **kw: position_size_check(**kw),
    "organic_check": lambda **kw: organic_revenue_check(**kw),
    "reverse_dcf": lambda **kw: reverse_dcf(**kw),
    "owner_earnings": lambda **kw: owner_earnings(**kw),
    "yield_velocity": lambda **kw: yield_velocity_check(**kw),
    "wilson_ci": lambda **kw: wilson_ci(**kw),
    "mc_dcf": lambda **kw: monte_carlo_dcf(**kw),
}


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nAvailable methods:", list(DISPATCH.keys()))
        sys.exit(1)

    method = sys.argv[1]
    payload = json.loads(sys.argv[2])

    if method not in DISPATCH:
        print(f"Unknown method: {method}")
        print("Available:", list(DISPATCH.keys()))
        sys.exit(1)

    fn = DISPATCH[method]
    if method == "sanity":
        result = sanity_check(payload)
    else:
        result = fn(**payload)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
