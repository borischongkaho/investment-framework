# Version History

> Semantic versioning: MAJOR.MINOR.PATCH where MAJOR = breaking framework changes, MINOR = additive features, PATCH = bug fixes / case studies.

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
