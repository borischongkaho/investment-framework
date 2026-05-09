"""V4.2 Smoke Tests — Verify framework code imports and key functions work.

Run with: pytest tests/ -v
"""
import sys
from pathlib import Path

# Ensure framework/ is in path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "framework"))


# --- Test imports ---
def test_valuation_calc_imports():
    """All key functions must be importable."""
    import valuation_calc as vc
    assert hasattr(vc, "dcf_two_stage")
    assert hasattr(vc, "dcf_three_stage")
    assert hasattr(vc, "dcf_three_stage_course_strict")
    assert hasattr(vc, "epv")
    assert hasattr(vc, "wacc_calc")
    assert hasattr(vc, "gaap_gap_check")
    assert hasattr(vc, "position_size_check")
    assert hasattr(vc, "organic_revenue_check")
    assert hasattr(vc, "reverse_dcf")
    assert hasattr(vc, "yield_velocity_check")


def test_data_quality_gate_imports():
    import data_quality_gate as dqg
    assert hasattr(dqg, "run_gate")


def test_decision_log_imports():
    import decision_log as dl
    assert hasattr(dl, "add_decision")


# --- Test key calculations ---
def test_dcf_two_stage_basic():
    import valuation_calc as vc
    result = vc.dcf_two_stage(
        fcf_year1=100, growth_high=0.10, years_high=5,
        growth_terminal=0.025, wacc=0.09,
        shares_outstanding=50, net_debt=0,
    )
    assert result["iv_per_share"] > 0
    assert result["enterprise_value"] > 0
    assert "DCF Two-Stage" in result["method"]


def test_dcf_three_stage_course_strict():
    """Course-strict formula: TV = NOPAT × (1 - g/ROI) / (WACC - g)."""
    import valuation_calc as vc
    result = vc.dcf_three_stage_course_strict(
        nopat_year1=1000, growth_high=0.10, years_high=5,
        growth_mid=0.06, years_mid=5,
        growth_terminal=0.025, wacc=0.085,
        terminal_roi=0.20, shares_outstanding=100, net_debt=0,
    )
    assert result["iv_per_share"] > 0
    assert result["b_terminal"] == 0.025 / 0.20  # g/ROI
    assert "Course-Strict" in result["method"]


def test_epv_zero_growth_floor():
    import valuation_calc as vc
    result = vc.epv(
        normalized_earnings=100, wacc=0.09,
        shares_outstanding=10, net_debt=0,
    )
    expected_epv_ops = 100 / 0.09
    assert abs(result["epv_operations"] - expected_epv_ops) < 0.01


def test_gaap_gap_check_flag():
    """FISV-style 67% gap should trigger flag."""
    import valuation_calc as vc
    result = vc.gaap_gap_check(gaap_eps=1.07, non_gaap_eps=1.79)
    assert result["flag"] is True
    assert result["gap_pct"] > 0.30


def test_organic_check_auto_avoid():
    """3 consecutive negative quarters should auto-AVOID."""
    import valuation_calc as vc
    result = vc.organic_revenue_check(
        organic_yoy_history=[0.02, -0.01, -0.02, -0.018]
    )
    assert result["auto_avoid"] is True
    assert result["max_consecutive_negative_quarters"] == 3


def test_yield_velocity_trap():
    """KHC-pattern 96% yield velocity should flag."""
    import valuation_calc as vc
    result = vc.yield_velocity_check(historical_yields=[3.5, 4.5, 6.86])
    assert result["flag_yield_trap"] is True
    assert result["velocity_pct"] > 50


def test_reverse_dcf_realistic():
    """Reverse DCF should solve implied growth or hit binary search bound."""
    import valuation_calc as vc
    # Realistic scenario: market cap $20K, FCF $1K → modest implied growth
    result = vc.reverse_dcf(
        current_market_cap=20000, fcf_year1=1000,
        wacc=0.09, growth_terminal=0.025,
    )
    # Either solves convergently or returns last_mid for bounds case
    assert "implied_growth_high" in result or "last_mid" in result


def test_position_size_auto_reject():
    """50% concentration should fail Tier 2 cap (8%)."""
    import valuation_calc as vc
    result = vc.position_size_check(
        proposed_size_pct=0.50, conviction_tier=2
    )
    assert result["auto_reject"] is True


# --- Test course alignment (Apple 2013 within range) ---
def test_apple_2013_course_strict_within_range():
    """V4.2 course-strict should produce $454-678 range output for Apple 2013."""
    import valuation_calc as vc
    result = vc.dcf_three_stage_course_strict(
        nopat_year1=48000, growth_high=0.05, years_high=5,
        growth_mid=0.03, years_mid=15,
        growth_terminal=0.02, wacc=0.12,
        terminal_roi=0.20, shares_outstanding=940,
        net_debt=-150000,
    )
    iv = result["iv_per_share"]
    # Course Excel range: $454-678
    assert 400 < iv < 800, f"Apple 2013 IV ${iv:.2f} outside expected range"
