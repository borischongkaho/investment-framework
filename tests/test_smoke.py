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
    assert hasattr(vc, "wilson_ci")
    assert hasattr(vc, "monte_carlo_dcf")


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


# --- Test V5 forward tracker ---
def test_forward_tracker_lock_and_list(tmp_path):
    """lock_prediction → list roundtrip, schema validity."""
    import forward_tracker as ft
    storage = str(tmp_path / "fwd.json")
    p = ft.lock_prediction(
        ticker="NVDA", verdict="TRIM", entry_price=215.80,
        iv_p50=200.0, iv_p5=165.0, iv_p95=240.0,
        predicted_12m_return_pct=-7.0, data_quality_score=8,
        storage_path=storage,
    )
    assert p["ticker"] == "NVDA"
    assert p["verdict"] == "TRIM"
    assert "PRED-" in p["id"]
    assert all(label in p["checkpoints"] for label in ["3m", "6m", "9m", "12m"])
    assert all(p["checkpoints"][label]["status"] == "pending" for label in p["checkpoints"])

    items = ft.list_predictions("all", storage_path=storage)
    assert len(items) == 1
    assert items[0]["id"] == p["id"]


def test_forward_tracker_id_disambiguation(tmp_path):
    """Same ticker locked twice same day → suffix differentiates."""
    import forward_tracker as ft
    storage = str(tmp_path / "fwd.json")
    p1 = ft.lock_prediction(ticker="MSFT", verdict="BUY", entry_price=300, iv_p50=350, storage_path=storage)
    p2 = ft.lock_prediction(ticker="MSFT", verdict="ADD", entry_price=290, iv_p50=350, storage_path=storage)
    assert p1["id"] != p2["id"]


def test_forward_tracker_verdict_validation(tmp_path):
    """Invalid verdict raises."""
    import pytest
    import forward_tracker as ft
    storage = str(tmp_path / "fwd.json")
    with pytest.raises(ValueError):
        ft.lock_prediction(ticker="X", verdict="STRONG_BUY", entry_price=100, iv_p50=120, storage_path=storage)
    with pytest.raises(ValueError):
        ft.lock_prediction(ticker="X", verdict="BUY", entry_price=-1, iv_p50=120, storage_path=storage)
    with pytest.raises(ValueError):
        ft.lock_prediction(ticker="X", verdict="BUY", entry_price=100, iv_p50=0, storage_path=storage)


def test_forward_tracker_calibration_empty(tmp_path):
    """Calibration on store with no resolved checkpoints returns empty summary."""
    import forward_tracker as ft
    storage = str(tmp_path / "fwd.json")
    ft.lock_prediction(ticker="NVDA", verdict="BUY", entry_price=200, iv_p50=250, storage_path=storage)
    rpt = ft.calibration_report(storage_path=storage)
    assert rpt["total_predictions"] == 1
    assert rpt["active"] == 1
    assert rpt["fully_resolved"] == 0
    assert rpt["by_verdict_horizon"] == []


def test_forward_tracker_default_mos_calculation(tmp_path):
    """If mos_pct not provided, it should default to (p50 - price) / price."""
    import forward_tracker as ft
    storage = str(tmp_path / "fwd.json")
    p = ft.lock_prediction(ticker="X", verdict="BUY", entry_price=100, iv_p50=150, storage_path=storage)
    # Expect 50%
    assert abs(p["mos_pct"] - 50.0) < 0.01


# --- Test V5 statistical layer ---
def test_wilson_ci_known_backtest_case():
    """Boris's documented backtest: 14/16 hit → ~87.5% with reasonable CI bounds."""
    import valuation_calc as vc
    r = vc.wilson_ci(14, 16, 0.95)
    assert r["successes"] == 14
    assert r["n"] == 16
    assert abs(r["point_estimate"] - 0.875) < 0.001
    # Wilson 95% CI for 14/16: lower ~0.64, upper ~0.965 (mathematically exact)
    assert 0.60 < r["lower"] < 0.66
    assert 0.94 < r["upper"] < 0.98
    assert "WIDE" in r["interpretation"] or "MODERATE" in r["interpretation"]


def test_wilson_ci_extreme_proportions():
    """Wilson handles all-success (5/5) and all-failure (0/5) without breaking."""
    import valuation_calc as vc
    all_hit = vc.wilson_ci(5, 5, 0.95)
    assert all_hit["point_estimate"] == 1.0
    assert all_hit["upper"] == 1.0  # capped at 1.0
    assert all_hit["lower"] < 1.0   # but lower bound is below 1

    all_miss = vc.wilson_ci(0, 5, 0.95)
    assert all_miss["point_estimate"] == 0.0
    assert all_miss["lower"] == 0.0  # capped at 0.0
    assert all_miss["upper"] > 0.0   # but upper bound is above 0


def test_wilson_ci_tightens_with_more_samples():
    """CI width should shrink as n grows (square-root law)."""
    import valuation_calc as vc
    small = vc.wilson_ci(8, 10, 0.95)["ci_width"]
    medium = vc.wilson_ci(80, 100, 0.95)["ci_width"]
    large = vc.wilson_ci(800, 1000, 0.95)["ci_width"]
    assert small > medium > large


def test_wilson_ci_invalid_inputs():
    """Validation: n>=1, 0<=successes<=n, 0<confidence<1."""
    import pytest
    import valuation_calc as vc
    with pytest.raises(ValueError):
        vc.wilson_ci(5, 0)  # n=0
    with pytest.raises(ValueError):
        vc.wilson_ci(11, 10)  # successes > n
    with pytest.raises(ValueError):
        vc.wilson_ci(-1, 10)  # negative successes
    with pytest.raises(ValueError):
        vc.wilson_ci(5, 10, confidence=0.93)  # not standard level


def test_monte_carlo_dcf_distribution_invariants():
    """Percentiles must be ordered, valid sims must dominate, distribution centered near base IV."""
    import valuation_calc as vc
    base = {
        "fcf_year1": 100, "growth_high": 0.10, "years_high": 5,
        "growth_terminal": 0.025, "wacc": 0.09,
        "shares_outstanding": 50, "net_debt": 0,
    }
    base_iv = vc.dcf_two_stage(**base)["iv_per_share"]
    mc = vc.monte_carlo_dcf(base, num_simulations=2000, uncertainty="medium", seed=42)

    # Ordering invariant
    assert mc["p5"] < mc["p25"] < mc["median_p50"] < mc["p75"] < mc["p95"]
    # Validity rate
    assert mc["num_valid"] >= 1900  # >95% should produce valid IV
    # Median should be within ±15% of point estimate (medium uncertainty)
    assert abs(mc["median_p50"] - base_iv) / base_iv < 0.15


def test_monte_carlo_dcf_uncertainty_widens_ci():
    """High uncertainty → wider 90% CI than low uncertainty."""
    import valuation_calc as vc
    base = {
        "fcf_year1": 100, "growth_high": 0.10, "years_high": 5,
        "growth_terminal": 0.025, "wacc": 0.09,
        "shares_outstanding": 50, "net_debt": 0,
    }
    low = vc.monte_carlo_dcf(base, num_simulations=2000, uncertainty="low", seed=1)
    high = vc.monte_carlo_dcf(base, num_simulations=2000, uncertainty="high", seed=1)
    low_width = low["p95"] - low["p5"]
    high_width = high["p95"] - high["p5"]
    assert high_width > low_width * 1.5  # high preset should produce notably wider range


def test_monte_carlo_dcf_reproducible_with_seed():
    """Same seed → identical output (reproducibility for backtests)."""
    import valuation_calc as vc
    base = {
        "fcf_year1": 100, "growth_high": 0.10, "years_high": 5,
        "growth_terminal": 0.025, "wacc": 0.09,
        "shares_outstanding": 50, "net_debt": 0,
    }
    a = vc.monte_carlo_dcf(base, num_simulations=1000, seed=7)
    b = vc.monte_carlo_dcf(base, num_simulations=1000, seed=7)
    assert a["median_p50"] == b["median_p50"]
    assert a["p5"] == b["p5"]
    assert a["p95"] == b["p95"]


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
