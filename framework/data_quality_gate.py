#!/usr/bin/env python3
"""
V4.2 Data Quality Gate — Mandatory pre-calculation verification.

Runs 9 checks before allowing any ACCT6111E Excel calculation to proceed.
Output: PASS / FAIL with specific missing items.

Source of failure modes: GIS post-mortem 2026-05-06
- 5/4 entry used stale FY26 EPS estimate ($4.50 vs reality $3.70-3.78)
- 5/4 entry missed 3/18 FY26 guide cut (7 weeks public)
- 5/4 entry missed organic decline pattern (3 consecutive Q)
- 5/4 entry used stale yield (4.7% level, missed 6.86% TTM velocity)

Usage:
    python3 data_quality_gate.py <ticker> [--data data.json]

    OR programmatically:
    from data_quality_gate import run_gate
    result = run_gate(ticker_data_dict)
"""
import json
import sys
from datetime import datetime, date
from pathlib import Path


# -----------------------------------------------------------------------------
# Check Functions
# -----------------------------------------------------------------------------

def check_data_currency(data: dict) -> dict:
    """Check 1: Latest 10-Q release < 90 days."""
    latest_10q_date = data.get("latest_10q_date")
    if not latest_10q_date:
        return {"pass": False, "reason": "Missing latest_10q_date"}

    try:
        d = datetime.strptime(latest_10q_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return {"pass": False, "reason": f"Invalid date format: {latest_10q_date}"}

    days_old = (date.today() - d).days
    return {
        "pass": days_old <= 90,
        "days_old": days_old,
        "threshold": 90,
        "reason": f"10-Q {days_old} days old (threshold 90)" if days_old > 90 else "OK",
    }


def check_guidance_currency(data: dict) -> dict:
    """Check 2: Latest management guidance same quarter as 10-Q."""
    has_post_10q_guide = data.get("post_10q_guidance_change", None)
    if has_post_10q_guide is None:
        return {"pass": False, "reason": "Must explicitly set post_10q_guidance_change (true/false)"}

    if has_post_10q_guide is True:
        return {
            "pass": False,
            "reason": "⚠️ Post-10Q guidance change exists. Re-verify all data with latest guide.",
            "action": "Search news for ticker + 'guidance' + last 90 days",
        }

    return {"pass": True, "reason": "Guidance current with 10-Q"}


def check_call_transcript_review(data: dict) -> dict:
    """Check 3: Latest earnings call transcript reviewed."""
    transcript_date = data.get("latest_call_transcript_date")
    if not transcript_date:
        return {"pass": False, "reason": "No earnings call transcript reviewed"}

    try:
        d = datetime.strptime(transcript_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return {"pass": False, "reason": f"Invalid transcript date: {transcript_date}"}

    days_old = (date.today() - d).days
    return {
        "pass": days_old <= 120,
        "days_old": days_old,
        "reason": f"Transcript {days_old} days old" if days_old > 120 else "OK",
    }


def check_organic_revenue_history(data: dict) -> dict:
    """Check 4: 8 quarters organic revenue YoY reviewed + acquisition disaggregated."""
    organic_history = data.get("organic_revenue_yoy_8q", [])
    if len(organic_history) < 4:
        return {
            "pass": False,
            "reason": f"Need ≥4Q organic history (got {len(organic_history)})",
        }

    # Detect declining streak
    consecutive_negative = 0
    for q in reversed(organic_history):
        if q < 0:
            consecutive_negative += 1
        else:
            break

    flag = consecutive_negative >= 2
    return {
        "pass": True,  # Pass means data present; flag separately
        "data_present": True,
        "consecutive_negative_streak": consecutive_negative,
        "flag_auto_avoid": flag,
        "history": organic_history,
        "reason": (
            f"⚠️ {consecutive_negative} consecutive Q negative organic — V4.1 auto-AVOID"
            if flag else "OK"
        ),
    }


def check_margin_trend(data: dict) -> dict:
    """Check 5: 5 years operating margin trend."""
    margin_5y = data.get("operating_margin_5y", [])
    if len(margin_5y) < 3:
        return {"pass": False, "reason": f"Need ≥3Y margin history (got {len(margin_5y)})"}

    direction = "expanding" if margin_5y[-1] > margin_5y[0] else "compressing"
    delta_bps = (margin_5y[-1] - margin_5y[0]) * 100

    return {
        "pass": True,
        "history": margin_5y,
        "direction": direction,
        "delta_bps": round(delta_bps, 1),
        "flag_compressing": margin_5y[-1] < margin_5y[-2],
        "reason": f"Margin {direction} {delta_bps:.0f}bps over period",
    }


def check_capital_structure(data: dict) -> dict:
    """Check 6: Capital structure components from latest 10-Q."""
    required = ["total_debt", "cash_and_investments", "shares_outstanding_diluted"]
    missing = [k for k in required if k not in data]

    if missing:
        return {"pass": False, "reason": f"Missing: {missing}"}

    net_debt = data["total_debt"] - data["cash_and_investments"]
    return {
        "pass": True,
        "total_debt": data["total_debt"],
        "cash": data["cash_and_investments"],
        "net_debt": net_debt,
        "shares_diluted": data["shares_outstanding_diluted"],
        "reason": "All capital structure data present",
    }


def check_gaap_nongaap_reconciliation(data: dict) -> dict:
    """Check 7: GAAP vs Non-GAAP reconciliation."""
    gaap_eps = data.get("gaap_eps_ttm")
    nongaap_eps = data.get("nongaap_eps_ttm")

    if gaap_eps is None or nongaap_eps is None:
        return {"pass": False, "reason": "Missing gaap_eps_ttm or nongaap_eps_ttm"}

    if gaap_eps == 0:
        return {"pass": True, "flag": True, "reason": "GAAP EPS = 0 (extreme quality concern)"}

    gap_pct = (nongaap_eps - gaap_eps) / abs(gaap_eps)
    flag = abs(gap_pct) > 0.30
    return {
        "pass": True,
        "gap_pct": round(gap_pct * 100, 1),
        "flag_quality": flag,
        "haircut_recommendation": 0.15 if flag else 0,
        "reason": (
            f"⚠️ GAAP/Non-GAAP gap {gap_pct*100:.1f}% > 30% — apply 15% intrinsic haircut"
            if flag else "Gap acceptable"
        ),
    }


def check_owner_earnings_reconciliation(data: dict) -> dict:
    """Check 8: Owner Earnings vs Reported FCF."""
    net_income = data.get("net_income_ttm")
    da = data.get("depreciation_amortization_ttm")
    maint_capex = data.get("maintenance_capex_estimate")
    reported_fcf = data.get("reported_fcf_ttm")

    if any(v is None for v in [net_income, da, maint_capex, reported_fcf]):
        return {"pass": False, "reason": "Missing one of: NI, D&A, maint_capex, reported_FCF"}

    owner_earnings = net_income + da - maint_capex
    fcf_oe_gap = (reported_fcf - owner_earnings) / abs(owner_earnings) if owner_earnings else 0
    flag = abs(fcf_oe_gap) > 0.20

    return {
        "pass": True,
        "owner_earnings": owner_earnings,
        "reported_fcf": reported_fcf,
        "gap_pct": round(fcf_oe_gap * 100, 1),
        "flag": flag,
        "reason": (
            f"⚠️ FCF/OE gap {fcf_oe_gap*100:.1f}% — investigate growth vs maintenance capex split"
            if flag else "OK"
        ),
    }


def check_sector_peer_cross_check(data: dict) -> dict:
    """Check 9: Sector peer 3+ comparison done."""
    peers = data.get("sector_peers_organic_growth", {})
    if len(peers) < 3:
        return {
            "pass": False,
            "reason": f"Need ≥3 sector peers organic growth (got {len(peers)})",
        }

    # Compare ticker organic to peer organic
    ticker_organic = data.get("organic_revenue_yoy_8q", [None])[-1]
    peer_avg = sum(peers.values()) / len(peers) if peers else 0
    diff = ticker_organic - peer_avg if ticker_organic else None

    return {
        "pass": True,
        "peer_average_organic": round(peer_avg * 100, 1),
        "ticker_organic": round(ticker_organic * 100, 1) if ticker_organic else None,
        "diff_vs_peer": round(diff * 100, 1) if diff else None,
        "interpretation": (
            "Idiosyncratic underperformance" if diff and diff < -0.02
            else "Sector-wide pattern" if diff and abs(diff) < 0.01
            else "Idiosyncratic outperformance" if diff and diff > 0.02
            else "Aligned with peers"
        ),
        "peers": peers,
    }


# -----------------------------------------------------------------------------
# Master Gate Runner
# -----------------------------------------------------------------------------

CHECKS = [
    ("Check 1: Data Currency (10-Q < 90d)", check_data_currency),
    ("Check 2: Guidance Currency", check_guidance_currency),
    ("Check 3: Earnings Call Transcript", check_call_transcript_review),
    ("Check 4: Organic Revenue 8Q history", check_organic_revenue_history),
    ("Check 5: Operating Margin 5Y trend", check_margin_trend),
    ("Check 6: Capital Structure components", check_capital_structure),
    ("Check 7: GAAP/Non-GAAP reconciliation", check_gaap_nongaap_reconciliation),
    ("Check 8: Owner Earnings reconciliation", check_owner_earnings_reconciliation),
    ("Check 9: Sector Peer Cross-Check", check_sector_peer_cross_check),
]


def run_gate(data: dict) -> dict:
    """Run all 9 checks. Returns aggregated PASS/FAIL + flags."""
    results = []
    pass_count = 0
    fail_count = 0
    flags = []

    for name, fn in CHECKS:
        try:
            result = fn(data)
        except Exception as e:
            result = {"pass": False, "reason": f"Exception: {e}"}

        result["check_name"] = name
        results.append(result)

        if result.get("pass"):
            pass_count += 1
        else:
            fail_count += 1

        # Collect any flags
        for k, v in result.items():
            if k.startswith("flag_") and v is True:
                flags.append(f"{name} → {k}")

    overall_pass = fail_count == 0
    return {
        "ticker": data.get("ticker", "UNKNOWN"),
        "timestamp": datetime.now().isoformat(),
        "overall_gate_pass": overall_pass,
        "passed_checks": pass_count,
        "failed_checks": fail_count,
        "total_checks": len(CHECKS),
        "flags": flags,
        "details": results,
        "verdict": (
            "✅ GATE PASS — proceed to ACCT6111E Excel calculation"
            if overall_pass else
            "❌ GATE FAIL — fix missing data before calculation"
        ),
    }


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--example":
        # Example usage
        example_data = {
            "ticker": "ADBE",
            "latest_10q_date": "2026-04-15",
            "post_10q_guidance_change": False,
            "latest_call_transcript_date": "2026-04-15",
            "organic_revenue_yoy_8q": [0.11, 0.115, 0.112, 0.11, 0.105, 0.11, 0.11, 0.11],
            "operating_margin_5y": [0.32, 0.34, 0.35, 0.36, 0.37],
            "total_debt": 5000,
            "cash_and_investments": 7000,
            "shares_outstanding_diluted": 440,
            "gaap_eps_ttm": 10.50,
            "nongaap_eps_ttm": 13.00,
            "net_income_ttm": 5600,
            "depreciation_amortization_ttm": 1200,
            "maintenance_capex_estimate": 600,
            "reported_fcf_ttm": 8000,
            "sector_peers_organic_growth": {"MSFT": 0.13, "CRM": 0.09, "INTU": 0.12},
        }
        result = run_gate(example_data)
        print(json.dumps(result, indent=2, default=str))
        return

    # Read data from JSON arg or file
    if sys.argv[1].startswith("{"):
        data = json.loads(sys.argv[1])
    elif Path(sys.argv[1]).exists():
        data = json.loads(Path(sys.argv[1]).read_text())
    else:
        print(f"❌ Could not parse: {sys.argv[1]}")
        sys.exit(1)

    result = run_gate(data)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
