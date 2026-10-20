"""v5.2.0 sync tests — V4.9 operations scripts + 2026-10 accounting fixes.

All tests are offline: network-backed fetchers are stubbed or monkeypatched.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FRAMEWORK = ROOT / "framework"
EXAMPLE_POSITIONS = ROOT / "portfolio_structure" / "positions.example.json"


# --- 2026-10-07 lease double-count fix ---------------------------------------
def _bs_only(bs_record):
    def fetch(endpoint, ticker, **params):
        return [bs_record] if endpoint == "balance-sheet-statement" else None
    return fetch


def test_leases_not_double_counted_when_total_debt_already_includes_them():
    """FMP totalDebt = short + long debt + capitalLeaseObligations → leases must NOT be added again."""
    import valuation_inputs as vi
    bs = {"cashAndCashEquivalents": 100, "shortTermInvestments": 50, "totalDebt": 1200,
          "longTermDebt": 900, "shortTermDebt": 100, "capitalLeaseObligations": 200, "totalStockholdersEquity": 5000}
    out = vi.collect_inputs("TEST", _bs_only(bs))
    assert out["leases_in_total_debt"] is True
    assert out["net_debt_adjusted_v44"] == 1200 - 150           # not 1200 + 200 - 150


def test_leases_added_when_clearly_excluded_from_total_debt():
    """When totalDebt == funded debt only, ASC 842 leases are still added (V4.4 behaviour preserved)."""
    import valuation_inputs as vi
    bs = {"cashAndCashEquivalents": 100, "shortTermInvestments": 50, "totalDebt": 1000,
          "longTermDebt": 900, "shortTermDebt": 100, "capitalLeaseObligations": 200, "totalStockholdersEquity": 5000}
    out = vi.collect_inputs("TEST", _bs_only(bs))
    assert out["leases_in_total_debt"] is False
    assert out["net_debt_adjusted_v44"] == 1000 + 200 - 150


def test_valuation_inputs_reports_error_when_no_source_has_data(monkeypatch, capsys):
    import valuation_inputs as vi
    monkeypatch.setattr(vi, "get_fmp_raw", lambda endpoint, ticker, **p: None)
    monkeypatch.setattr(vi, "get_yf_raw", lambda endpoint, ticker, **p: None)
    out = vi.mandatory_inputs_v44("NOPE", "auto")
    assert "error" in out and "yfinance" in out["data_source"]


def test_wacc_calc_applies_same_lease_rule(monkeypatch):
    import wacc_calc as wc
    canned = {
        "profile": [{"beta": 1.1, "marketCap": 10_000}],
        "key-metrics-ttm": [{"taxBurdenTTM": 0.79}],
        "balance-sheet-statement": [{"totalDebt": 1200, "longTermDebt": 900, "shortTermDebt": 100,
                                     "capitalLeaseObligations": 200, "cashAndCashEquivalents": 100,
                                     "shortTermInvestments": 50}],
        "income-statement": [{"incomeBeforeTax": 1000, "incomeTaxExpense": 210}],
    }
    monkeypatch.setattr(wc, "get_fmp_raw", lambda endpoint, ticker, **p: canned.get(endpoint))
    out = wc.calc_wacc("TEST")
    assert out["inputs"]["leases_in_total_debt"] is True
    assert out["inputs"]["adjusted_net_debt"] == 1200 - 150
    assert 0.05 < out["wacc"] < 0.15


def test_pool_screen_value_uses_lease_rule_and_no_network():
    import pool_screen_capm as ps
    ps.POOL.clear(); ps.POOL["TEST"] = 5.0
    d = {"price": 100.0, "mcap": 1e10, "beta": 1.0, "quote_cur": "USD", "rep_cur": "USD",
         "ocf": 1.5e9, "capex": 3e8, "sbc": 1e8, "src": "TTM",
         "debt": 1.2e9, "lease": 2e8, "funded": 1e9, "cash": 5e8,
         "pretax": 1e9, "tax_exp": 2e8, "roic": 0.20, "provider": "FMP"}
    r = ps.value("TEST", d, rf=0.045, erp=0.055)
    assert r["net_debt"] == 1.2e9 - 5e8          # lease inside totalDebt → counted once
    assert r["iv"] > 0 and r["wacc"] > 0.045 and r["group"] == "WL"


def test_pool_example_loads():
    import pool_screen_capm as ps
    ps.load_pool(FRAMEWORK / "pool_example.json")
    assert len(ps.POOL) >= 10 and all(v > 0 for v in ps.POOL.values())
    assert ps.GROUP["AAPL"] == "mega_cap" and ps.DREAM == []


# --- V4.9 operations layer ---------------------------------------------------
def test_example_positions_schema_is_consistent():
    d = json.loads(EXAMPLE_POSITIONS.read_text())
    assert set(d) >= {"as_of", "total_portfolio_usd", "cash_usd", "positions", "entry_dates", "limits"}
    assert sum(p["value_usd"] for p in d["positions"].values()) + d["cash_usd"] == d["total_portfolio_usd"]
    for tk, p in d["positions"].items():
        assert {"shares", "avg_cost", "yf", "value_usd", "tags"} <= set(p) and tk in d["entry_dates"]


def test_resolve_positions_path_order(monkeypatch, tmp_path):
    import config
    monkeypatch.delenv("BT_POSITIONS_PATH", raising=False)
    monkeypatch.setenv("BT_INVESTMENT_DIR", str(tmp_path))     # empty dir → fall back to example
    assert config.resolve_positions_path() == config.EXAMPLE_POSITIONS_PATH
    real = tmp_path / "positions.json"; real.write_text("{}")
    assert config.resolve_positions_path() == real               # <investment_dir>/positions.json wins once it exists
    monkeypatch.setenv("BT_POSITIONS_PATH", str(tmp_path / "elsewhere.json"))
    assert config.resolve_positions_path() == tmp_path / "elsewhere.json"


def test_pre_trade_gate_buy_pass_fail_override():
    import pre_trade_gate as ptg
    st = ptg.load_state(EXAMPLE_POSITIONS)
    ns = argparse.Namespace(ticker="JNJ", amount=5000, price=100, intrinsic=150, tags="healthcare",
                            smart_money_entry=None, is_add=False, override=False)
    assert ptg.buy_gate(ns, st) == 0          # MoS 33%, 5% position, cash fine
    ns.intrinsic = 105                        # MoS 4.8% < watch floor → auto-reject
    assert ptg.buy_gate(ns, st) == 2
    ns.override = True
    assert ptg.buy_gate(ns, st) == 1          # override acknowledged, must be logged


def test_pre_trade_gate_sell_requires_trigger_when_thesis_intact():
    import pre_trade_gate as ptg
    st = ptg.load_state(EXAMPLE_POSITIONS)
    ns = argparse.Namespace(ticker="AAPL", thesis_status="intact", trigger_hit=None,
                            recent_drop_pct=None, portion=1.0, override=False)
    assert ptg.sell_gate(ns, st) == 2
    ns.thesis_status = "broken"
    assert ptg.sell_gate(ns, st) == 0
    ns.ticker = "ZZZZ"
    assert ptg.sell_gate(ns, st) == 2         # unknown ticker


def test_kelly_lite_quarter_kelly_cap_and_negative_edge():
    import kelly_lite as kl
    r = kl.kelly_size(mos_pct=33, win_prob=0.70, bear_downside_pct=25)
    assert r["odds_b"] == pytest.approx(1.32)
    assert r["f_star"] == pytest.approx((0.7 * 1.32 - 0.3) / 1.32)
    assert r["suggested"] == pytest.approx(r["f_star"] * kl.KELLY_FRACTION) and not r["capped"]
    big = kl.kelly_size(mos_pct=80, win_prob=0.9, bear_downside_pct=10)
    assert big["capped"] and big["suggested"] == kl.SINGLE_STOCK_CAP
    neg = kl.kelly_size(mos_pct=10, win_prob=0.3, bear_downside_pct=30)
    assert neg["f_star"] < 0 and neg["suggested"] == 0.0


def test_stress_test_scenarios_on_example():
    import stress_test as stt
    st = json.loads(EXAMPLE_POSITIONS.read_text())
    res = stt.run_scenarios(st)
    assert set(res) == set(stt.SCENARIOS)
    for r in res.values():
        assert -1 < r["drawdown"] <= 0 and len(r["lines"]) == len(st["positions"])
    assert stt.shock_for(["ai", "consumer"], stt.SCENARIOS[stt.WORST_CASE]) == -0.25   # most negative applicable
    assert stt.shock_for(["unknown_tag"], stt.SCENARIOS[stt.WORST_CASE]) == -0.15      # default broad-market shock


def test_decision_log_seed_writes_only_example_data(tmp_path):
    ledger = tmp_path / "decisions.json"
    env = {"BT_DECISIONS_PATH": str(ledger), "PATH": "/usr/bin:/bin"}
    r = subprocess.run([sys.executable, str(FRAMEWORK / "decision_log.py"), "seed"], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rows = json.loads(ledger.read_text())
    assert {d["ticker"] for d in rows} == {"AAPL", "MSFT", "XOM"}


def test_fmp_client_key_resolution(monkeypatch, tmp_path):
    import fmp_client as fc
    monkeypatch.setenv("FMP_API_KEY", "env-key-123")
    assert fc.load_api_key() == "env-key-123"
    monkeypatch.delenv("FMP_API_KEY")
    monkeypatch.setattr(fc, "CONFIG_PATH", tmp_path / "fmp.env")
    assert fc.load_api_key(required=False) is None
    (tmp_path / "fmp.env").write_text("FMP_API_KEY=file-key-456\n")
    assert fc.load_api_key() == "file-key-456"


# --- every script answers --help from the repo root --------------------------
SCRIPTS = sorted(p.name for p in FRAMEWORK.glob("*.py"))


@pytest.mark.parametrize("script", SCRIPTS)
def test_every_framework_script_prints_help(script):
    r = subprocess.run([sys.executable, str(FRAMEWORK / script), "--help"], cwd=ROOT,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"{script} --help failed:\n{r.stderr[-800:]}"


# --- privacy guard: no personal paths / identities in the public layer --------
# Patterns are written with a bracketed character so this file itself never contains the literal
# tokens (keeps `git diff | grep` privacy scans clean while still matching them in scanned files).
PERSONAL = re.compile(r"/U[s]ers/|boris[c]hong|@gma[i]l\.com|tele[g]ram", re.IGNORECASE)


@pytest.mark.parametrize("path", sorted(list(FRAMEWORK.glob("*.py")) + list(FRAMEWORK.glob("*.json"))
                                        + list((ROOT / "portfolio_structure").glob("*.json"))),
                         ids=lambda p: p.name)
def test_no_personal_data_in_framework_files(path):
    hits = [ln for ln in path.read_text(encoding="utf-8").splitlines() if PERSONAL.search(ln)]
    assert not hits, f"{path.name} contains personal references: {hits[:3]}"
