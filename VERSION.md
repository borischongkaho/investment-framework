# Version History

> Semantic versioning: MAJOR.MINOR.PATCH where MAJOR = breaking framework changes, MINOR = additive features, PATCH = bug fixes / case studies.

---

## v5.2.0 — V4.9 operations layer + accounting fixes (2026-10-20)

> **Status**: Additive. Folds the private-layer V4.7 → V4.9 operations scripts (June–Oct 2026) into the
> public framework, plus the 2026-10-07 accounting corrections. All prior calls remain compatible.
> Every script in `framework/` now answers `--help` from a fresh clone without optional deps.

### New scripts (V4.7–V4.9 operations layer)
- ✅ `framework/pre_trade_gate.py` — **mandatory gate before any BUY (Rule C4) or SELL (Rule C10)**.
  BUY checks: MoS hard gate / watch band, smart-money premium, single-stock cap, cash reserve,
  AI-correlated cap, monthly patience quota, net-of-withholding dividend yield. SELL checks: thesis status,
  pre-committed trigger, panic-sell pattern, soft holding-period floor, post-sell protocol.
  Exit 0 = PASS, 1 = override acknowledged (must be logged), 2 = FAIL.
- ✅ `framework/kelly_lite.py` — quarter-Kelly position-sizing reference (`kelly_size()` pure function + CLI),
  always capped by the single-stock rule; sizing aid only, never overrides the cap rules.
- ✅ `framework/pool_screen_capm.py` — one-shot CAPM-WACC + Owner-FCF two-stage DCF screen over a watch pool.
  Pool comes from a JSON file (`--pool`, bundled generic example `framework/pool_example.json`);
  `--tickers DECK:6,LULU:5 [--g 6] [--with-pool]` for ad-hoc names; FMP with 12-hour on-disk cache
  (`$BT_CACHE_DIR`, default `~/.cache/boris-investment/fmp_cache`), auto-falls back to yfinance on 429.
- ✅ `framework/portfolio_sync.py` — refresh prices / values / P&L in `positions.json` via yfinance and run
  the hard-limit breach check (A1 / A2 / B1 / A4). Never writes back into the bundled example file.
- ✅ `framework/stress_test.py` — monthly three-scenario stress test (2022-style AI correction, 2008-style
  recession, stagflation) with drawdown-protocol trigger readout; `run_scenarios()` is pure for testing.
- ✅ `framework/fmp_client.py` — Financial Modeling Prep `/stable/` client + CLI (profile, statements,
  ratios, DCF, owner earnings, estimates, insider, filings, screener …). Single shared key loader:
  `FMP_API_KEY` env var first, then `$BT_CONFIG_DIR/fmp.env`.
- ✅ `portfolio_structure/positions.example.json` — machine-readable portfolio state schema with two FAKE
  positions; the operations scripts run against it out of the box. Resolution order for the real file:
  `BT_POSITIONS_PATH` → `<investment_dir>/positions.json` → bundled example (see `config.resolve_positions_path()`).

### Accounting fix — operating leases were double-counted (2026-10-07)
- 🐛 V4.4 computed `Adjusted Net Debt = totalDebt + capitalLeaseObligations − cash`. FMP's `totalDebt`
  (and yfinance's `Total Debt`) **already includes** lease liabilities (verified across AAPL / MSFT / NVDA /
  GOOGL / COST / AMZN), so lease-heavy names carried inflated net debt and depressed IV.
- ✅ `valuation_inputs.py`, `wacc_calc.py` and `pool_screen_capm.py` now add leases **only when they are
  evidently not inside totalDebt** (`|totalDebt − (funded + leases)| < |totalDebt − funded|` ⇒ included).
  New output field `leases_in_total_debt` makes the decision auditable. Covered by tests for both branches.

### Data source — FMP free tier → yfinance fallback
- ✅ `valuation_inputs.py --source auto|fmp|yf`: when FMP has no financials for a ticker (premium /
  restricted / unknown), falls back to yfinance mapped onto FMP field names so every V4.4 derivation runs
  unchanged. Output carries `data_source`, `source_notes` (what yfinance cannot supply: ROIC, FMP owner
  earnings, FMP DCF …) and `fmp_unavailable` (per-endpoint reason). Exit code 2 + `"error"` when no source
  has data. `pool_screen_capm.py --source` has the same switch.

### Python 3.14 compatibility
- ✅ `wacc_calc.py` argparse help strings escape `%` as `%%` (3.14 raises on bare `%` in help text).
- ✅ `valuation_inputs.py` f-strings no longer use the invalid `\$` escape (SyntaxWarning on 3.12+).
- ✅ `backtest_runner.py` / `dcf_model_builder.py` guard their heavy imports (yfinance, pandas, openpyxl) so
  `--help` works without them; `data_quality_gate.py`, `futu_costs.py`, `valuation_calc.py` gained `--help`.

### Path / config hygiene (public layer)
- ✅ `config.py` (public multi-user version kept) gains `decisions_path`, `scorecard_path`, `positions_path`,
  `models_dir` and `resolve_positions_path()`. `decision_log.py`, `backtest_runner.py` and
  `dcf_model_builder.py` resolve their storage through it (env overrides `BT_DECISIONS_PATH`, `BT_MODELS_DIR`)
  instead of a hard-coded home-relative directory.
- ✅ `decision_log.py seed` now writes three clearly-labelled EXAMPLE decisions instead of an author-specific
  ledger.
- ✅ `.gitignore` adds `positions.json`, `data/`, `models/`.

### Tests
- `tests/test_v52_sync.py` (NEW): lease rule both branches (inputs + WACC + pool screen), yfinance fallback
  error path, BUY / SELL gate exit codes, Kelly sizing (cap + negative edge), stress scenarios, decision-log
  seed isolation, FMP key resolution, `--help` on every `framework/*.py`, and a privacy guard that fails if
  any framework / example file mentions a home path or personal identity. Suite: 33 → 84 tests, all green.

### Skills
- ⚠️ `skills/` remain the **v4.3 anonymized versions**. The canonical latest skills (invest-source /
  invest-screen / mba-valuation / invest-portfolio V4.7+) live in the private layer and are not part of
  this sync.

---

## v5.1.0-alpha — V4.4 Accounting Hardening + V2.1 Reporting (2026-05-28)

> **Status**: Additive to v5.0.0-alpha. All prior calls remain compatible. Folds the V4.4
> accounting-hardening track and V2.1 reporting spec into the v5 line.

### What changed
- ✅ `framework/wacc_calc.py` (NEW): standardized CAPM WACC — `Re = Rf + β×ERP + Country Premium`.
  Removes ad-hoc per-memo discount rates (root cause of +15-40% intrinsic bias).
- ✅ `framework/valuation_inputs.py` (NEW): mandatory pre-flight inputs check — ASC 842 operating
  leases added to net debt, SBC deducted from FCF, sanity warnings on stale/estimated cells.
- ✅ `framework/dcf_model_builder.py` (NEW): generates institutional live .xlsx DCF — case selector
  (Bear/Base/Bull via CHOOSE), mid-year convention, WACC sheet, live sensitivity table, colour
  coding + cell comments. Ships with a single illustrative example config.
- ✅ `framework/V44_V21_methodology.md` (NEW): full methodology — V4.4 hardening (CAPM WACC,
  ASC 842 leases, SBC-adj FCF, mid-year convention, SOTP), multi-method reconciliation,
  V2.1 17-section reporting spec, Q6 HARD GATE, scenario ranges, risk-budget sizing,
  portfolio construction layer, 6-Q / Auto-VETO (8) / 3-Judge gates, thesis tracker.
- ✅ `portfolio_structure/thesis_tracker_template.md` (NEW): falsifiable thesis scorecard template
  (pillar trends over time, disconfirming-evidence watch, quarterly review).

### Why this matters
Three systematic biases (ad-hoc WACC 1-3pp too low, operating leases excluded, SBC not deducted)
compounded to +15-40% upward intrinsic bias. V4.4 corrects all three. V2.1 adds decision
compression (Decision Sheet, scenario ranges, risk-budget sizing) — the gap an independent review
flagged as more important than additional analytical depth.

### Validation
- 50-case historical backtest: 76% hit rate, Wilson 95% CI [56%, 89%].
- Q6 HARD GATE precision 91%; Auto-VETO precision 93% (backtest sample).

---

## v5.0.0-alpha — Statistical Confidence Layer (2026-05-09)

> **Status**: Pre-commercial foundation phase. Backwards-compatible — all V4.x calls still work. Single-point IV in Section 1 / 9 / 17 of any new report is **deprecated** in favour of distribution-based output.

### What changed
- ✅ `valuation_calc.py` adds two functions:
  - `wilson_ci(successes, n, confidence=0.95)` — binomial CI for backtest hit rates. Stable for small n and extreme p.
  - `monte_carlo_dcf(base_inputs, num_simulations=10000, uncertainty="medium")` — replaces single-point IV with sampled distribution (p5/p25/p50/p75/p95).
- ✅ `tests/test_smoke.py` extended from 12 → 19 tests. New coverage: Wilson backtest case (14/16), extreme proportions (0/n and n/n), CI tightening with sample size, MC distribution invariants, MC seed reproducibility, MC uncertainty preset response.
- ✅ `framework/v42_advanced_report_template.md` updated:
  - Section 1 Decision Card now requires Monte Carlo IV range (median + 90% CI), not single point.
  - Section 9 Three-Method Valuation now requires MC distribution for DCF (10K simulations).
  - Section 17 Final Decision Card now requires bear-case (p5) MoS and conviction tag (TIGHT/MODERATE/WIDE).
  - Format Rules add "statistical honesty" requirement: every quantitative claim has uncertainty.
- ✅ Demo retrofit: `ADBE_2026-05-06_v42_ADVANCED.md` annotated with V5 distribution block. Even in p5 bear case, IV $423 > price $385 → +10% MoS retained — strongest signal of conviction.

### Why this matters (critic 5/9 priority #1)
"87.5% backtest hit rate (n=16)" without CI was overstated. With Wilson CI: **87.5% [64.0%, 96.5%] (n=16)** — directionally positive but sample too small for any narrow claim. Same logic for IV: distribution > point.

### Pure stdlib, no new dependencies
Both functions use only `math`, `random`, `statistics` — no NumPy / SciPy required. Keeps `pyproject.toml` lean.

### Pending (V5.0 GA)
- Random sampling backtest n=50+ (Item #2 of foundation plan)
- Cross-LLM verification: GPT-4o + Gemini independent Phase 9 audit (Item #3)
- Live forward prediction tracking system (Item #4)
- README.md update once V5.0 GA ships

---

## v4.2.x — Current Stable (2026-05-08)

### v4.2.3 — 2026-05-08
- ✅ Backtest validation: 8 historical case studies (4 winners + 4 losers) — 8/8 hit rate
- ✅ Honest hindsight bias adjustment: realistic deployment ~70-80% accuracy
- ✅ Identified V4.3 improvement areas (compounder premium, exponential growth pricing)
- ✅ Added `framework/valuation_calc.py` (full V4.1+V4.2 functions including yield_velocity)
- ✅ Added `framework/decision_log.py` (append-only ledger)
- ✅ Added `framework/backtest_runner.py` (multi-benchmark scorecard)
- ✅ Added `framework/futu_costs.py` (broker cost calculator — Futu HK rate card)

### v4.2.2 — 2026-05-07
- ✅ Price Trigger Discipline case study: when concentrated position drops, framework correctly held without adding
- ✅ V4.1 position size auto-VETO override of MoS opportunity demonstrated

### v4.2.1 — 2026-05-06
- ✅ Data Quality Gate (Phase 0.7) — 9 mandatory checks
- ✅ Excel-Faithful Mapping (13 ACCT6111E cells)
- ✅ V4.2 Advanced Report Format — 17 sections

### v4.2.0 — 2026-05-06 (initial)
- ✅ Phase 0.7 Data Quality Gate
- ✅ Yield Velocity check (NEW from GIS post-mortem)
- ✅ Sector Cross-Check (NEW from GIS post-mortem)

---

## v4.1.x — Auto-VETO Triggers (2026-05-06)

### v4.1.0
- ✅ V4.1 Auto-VETO triggers codified in Python
- ✅ 5 hard rules: position size, organic decline, GAAP gap, securities lawsuit, reverse DCF heroic
- ✅ Paper trade pool (3 drills: ADBE PASS, TJX VETO, HSY BORDERLINE)
- ✅ Catalyst calendar, anti-portfolio, drawdown protocol

---

## v4.0.x — Calculation Safety + Action Gate (2026-05-06)

### v4.0.0
- ✅ Python mandatory for DCF/EPV/WACC (no LLM mental math)
- ✅ Phase 6.5 Bull/Bear debate (replaces single pre-mortem)
- ✅ Phase 9 Final Action Gate (3-judge audit)
- ✅ 24-hour cool-down rule
- ✅ TradingAgents second-opinion integration (separate, never overrides)

---

## v2.0 — Forensic Hardening (2026-04-XX)

### v2.0-hardened (tag exists)
- ✅ Phase 0.5 Forensic Screening (10 mandatory searches)
- ✅ 7 Validation Gates
- ✅ Recommendation Cap Table
- ✅ Strict Terminal Formula: NOPAT × (1 - g/ROI) / (WACC - g)
- ✅ Course alignment regression test (Apple 2013, SJM 2024)

---

## v3.0 — Pending Rules (Triggered, Not Released)

7 rules identified from FISV post-mortem 2026-05-05:
1. GAAP/Non-GAAP gap > 30% sustained = quality flag
2. Organic revenue YoY < 0 for 2+ quarters = auto-AVOID
3. Superinvestor signal weighting cap 20%
4. Pre-mortem mandatory @ entry day
5. Position size cap 8-12% per stock
6. Mauboussin S&P 1500 base rate cross-check
7. Forensic re-screen → 72h action window

These were absorbed directly into v4.0/v4.1/v4.2 rather than released as standalone v3.0.

---

## v5.0 — Pending PR-1 Review

Currently on `pr-1` branch in `investment-framework-collab` (PRIVATE). Will merge to public after Boris approval.

Key v5 changes:
- Stop-gate tokens (mandatory at every gate)
- Phase 0.5/0.7/4.5/6.5/9 gates blocking (not advisory)
- Recommendation cap tightened (MoS 25-35% capped at BUY)
- pyproject.toml + tests/ for productization
- Persona neutralization for public sharing
- New trade-timing skill
- Portfolio review template

---

## Next Branches

- `main` — v4.2 stable (production-ready)
- `v5-pending` — v5 changes from PR-1 (when merged)
- `v4.2.x` tags — patch versions

---

## Migration Path

Users on older versions:
- v2.0 → v4.2: Add Python framework code, adopt Phase 0.7 + 6.5 + 9
- v4.2 → v5: Update parsers for new JSON schema (data_quality_gate output changed)

See `framework/change_log.md` for detailed change history.
