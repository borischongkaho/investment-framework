# boris-trade Valuation Framework — Canonical SPEC

> **Version**: v5.0.0-alpha (2026-05-09)
> **Status**: Draft for partner review. Locks the backbone before any further code changes.
> **Lineage**: CUHK MBA ACCT6111E (Dr. Bhaskaran Swaminathan, 2024R3) — 8-phase workflow, augmented by 5 V4.x deterministic gates derived from real-trade post-mortems (FISV, GIS, NVO/BMY).

---

## 0. Why this document exists

Without a single source of truth, framework scope drifts every session. New gates get added, old criteria mutate, and there is no reproducible spec to test against. Partner correctly flagged this on 2026-05-09: *"先定義整個 backbone framework，spec-driven 去做 development，eval 容易 match 到，唔會 drift scope"*.

**This document is the lockdown.** It defines, for every phase and gate of a V4.3+ valuation:

- Source authority (which course material / post-mortem motivates it)
- Input contract (what the phase requires before it can run)
- Output deliverables (what the phase must produce)
- Pass criteria, **deterministic where possible** (numerical thresholds, binary checks)
- Subjective elements that legitimately resist determinism (with rationale)
- Automation boundary (which work is Python / deterministic vs which requires LLM judgment)

Anything not in this document is **out of scope** for the current framework version. Adding a new phase or gate requires:
1. A documented post-mortem or course reference,
2. A version bump (5.0.0 → 5.1.0),
3. An updated section in this SPEC + matching test in `tests/test_smoke.py`.

---

## 1. Source Authority

**Canonical**: `Lectures on Valuation Swaminathan.pdf` + 10 weeks of ACCT6111E course material at `~/MBA/2024R3 Business Valuation and Analysis (ACCT6111E)/`.

**Derived working docs** (already track the canonical):
- `Claude_Business_Valuation_Tool.md` — the 8-phase Claude project prompt (39 KB, comprehensive)
- `Valuation_Operating_Model_SOP.md` — team SOP (sourcing → recommendation funnel)
- `企業估值策略與SOP報告.docx` — Chinese version

**Real-case validation**: `FISV_Full_Analysis_2026-04-23.md`, plus 16 backtest cases (8 Round 1 hindsight + 8 Round 2 including SJM 2024 + Apple 2013 course-canonical).

**Course-strict terminal value formula** (locked in v4.2.4):
```
TV = NOPAT × (1 − g/ROI) / (WACC − g)     [course canonical]
```
Plain Gordon Growth (`TV = FCFF × (1+g)/(WACC−g)`) is **deprecated** for primary valuations because it assumes ROI → ∞ and inflates intrinsics 30–50%. It remains in `valuation_calc.py` only for backward compatibility on legacy reports.

---

## 2. Architecture: 8 phases + 5 mandatory gates

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 0: Scope & Data Gathering                                │
├─────────────────────────────────────────────────────────────────┤
│  ✋ Gate 0.5: Forensic Screening    (V4.x — fail-stop)          │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: Historical Financial Analysis                         │
├─────────────────────────────────────────────────────────────────┤
│  ✋ Gate 0.7: Data Quality Gate     (V4.x — score x/9)          │
├─────────────────────────────────────────────────────────────────┤
│  Phase 2: Competitive Position                                  │
│  Phase 3: Cost of Capital (WACC)                                │
│  Phase 4: Multi-Method Valuation (EPV / DCF / Multiples / EVA)  │
├─────────────────────────────────────────────────────────────────┤
│  ✋ Gate 4.5: Sanity Bounds         (V4.x — auto-flag)          │
├─────────────────────────────────────────────────────────────────┤
│  Phase 5: Sensitivity Analysis                                  │
│  Phase 6: Investment Decision                                   │
├─────────────────────────────────────────────────────────────────┤
│  ✋ Gate 6.5: Bull/Bear Debate      (V4.x — Auto-VETO triggers) │
├─────────────────────────────────────────────────────────────────┤
│  Phase 7: Behavioral Bias Check                                 │
│  Phase 8: Output Report                                         │
├─────────────────────────────────────────────────────────────────┤
│  ✋ Gate 9: Final Action Gate       (V4.x — multi-judge audit)  │
└─────────────────────────────────────────────────────────────────┘
```

**Reading the symbols**:
- `Phase` = methodology block, 80% Swaminathan canonical
- `Gate` = deterministic enforcement layer, 100% Boris V4.x extension, born from a specific trade post-mortem
- `✋` = blocking — pipeline stops if the gate fails its criteria

---

## 3. Per-phase contracts

### Phase 0: Scope & Data Gathering
- **Source authority**: Course Week 1 (Admin + Overview); Claude_Business_Valuation_Tool.md Phase 0.
- **Input contract**: ticker, valuation_date, optional purpose tag (investment / academic / M&A).
- **Output deliverables**:
  - 5+ years Income Statement, Balance Sheet, Cash Flow Statement
  - Current price, shares outstanding (diluted), beta source
  - Risk-free rate (10Y or 30Y Treasury), ERP source (Damodaran preferred)
  - Analyst consensus (1-2 yr forward) if available
  - Source ledger: every data point linked to primary source URL
- **Deterministic pass criteria**:
  - [ ] All 5 financial-statement years present (else ⚠️ degraded mode)
  - [ ] Current price ≤ 7 days stale
  - [ ] Risk-free rate from FRED (DGS10 or TB4WK) cited with date
- **Subjective**: none — this phase is data plumbing.
- **Automation boundary**: 100% mechanical — should be done by data layer (FMP / yfinance / SEC EDGAR) with no LLM in the loop.

### ✋ Gate 0.5: Forensic Screening (V4.x)
- **Source authority**: NVO/BMY 6-discipline post-mortem 2026-04 + FISV save 2026-05-04.
- **Why it exists**: Pre-2026, framework valued FISV at attractive intrinsic without checking active securities-fraud lawsuit. V4.x added this gate after the save.
- **Input contract**: ticker, decision_date.
- **Output deliverables**: 10 web search queries × structured answers.
- **Deterministic pass criteria** (all binary, all must pass to advance):
  - [ ] **0** active securities-fraud lawsuits as of decision_date (operational lawsuits OK, distinguish per V2.0 calibration)
  - [ ] **0** going-concern audit qualifiers in last 4 fiscal quarters
  - [ ] **0** SEC restatements in last 8 fiscal quarters
  - [ ] **0** active CEO/CFO admission of accounting issues in last 12 months
  - [ ] Yield velocity over last 18 months ≤ +50% (else flag yield-trap, GIS pattern)
  - [ ] Organic revenue YoY ≥ 0 in at least 1 of last 2 quarters (or specific catalyst documented)
- **Auto-FAIL action**: pipeline halts, decision = `VETO`, reason logged. No further phases run.
- **Subjective**: the *specific* search query phrasing — boilerplate provided in `skills/mba-valuation/sop.md`.
- **Automation boundary**: search execution + result parsing automatable; final yes/no judgment can be deterministic if search results are structured (date + verdict columns).

### Phase 1: Historical Financial Analysis
- **Source authority**: Course Week 1-2 (Historical Analysis + Computing FCF); Claude tool Phase 1.
- **Input contract**: 5+ years statements from Phase 0.
- **Output deliverables**:
  - Simplified IS (Sales → EBIT → Net Income), with permanent vs transitory items separated
  - Operating vs financing balance sheet split
  - Historical FCFF (top-down + bottom-up, must reconcile within 5%)
  - 5-year ratios: ROIC, ROE, EBIT margin, FCFF margin, Sales/IC, D/E, interest coverage
  - Du Pont decomposition of ROIC (margin × turnover)
- **Deterministic pass criteria**:
  - [ ] FCFF top-down vs bottom-up reconcile within ±5%
  - [ ] ROIC computed using **average IC** (beginning + ending) / 2, not just ending IC
  - [ ] Tax rate normalized — exclude years with effective rate > 50% or < 0% (one-time effects)
  - [ ] All ratios shown for at least 5 fiscal years (else ⚠️ shorter history flag)
- **Subjective**: judgment on which items are "permanent" vs "one-time" (e.g. is a recurring restructuring "one-time"?). Document each call.
- **Automation boundary**: arithmetic 100% Python (`valuation_calc.py` helpers). One-time vs permanent classification requires LLM read of 10-K MD&A.

### ✋ Gate 0.7: Data Quality Gate (V4.x)
- **Source authority**: V4.2 release 2026-05-06; codified in `data_quality_gate.py`.
- **Why it exists**: V4.1 had no enforcement that data was current/sourced. Multiple early-2026 valuations used 18-month-stale figures.
- **Input contract**: completed Phase 1 output + source ledger.
- **9 deterministic checks** (each binary, each cited):
  1. [ ] 10-Q age ≤ 90 days from decision_date
  2. [ ] Latest annual guidance figure cited with source URL
  3. [ ] Most recent earnings call transcript referenced (link)
  4. [ ] Organic revenue YoY for last 8 quarters available
  5. [ ] EBIT margin trend (5Y) computed
  6. [ ] Capital structure (D/E + interest coverage) current
  7. [ ] GAAP vs Non-GAAP EPS reconciliation present (FISV lesson — gap > 30% triggers Auto-VETO downstream)
  8. [ ] Owner earnings calculation present (NI + D&A − maintenance CapEx ± ΔNWC)
  9. [ ] Peer cross-check — at least 3 peers with same metrics
- **Score**: integer 0–9.
- **Pass criteria for advancing**:
  - **≥ 8/9** → uncertainty preset = `low` for downstream Monte Carlo
  - **6–7/9** → uncertainty preset = `medium`, ⚠️ flag missing items in report
  - **< 6/9** → halt, decision = `INSUFFICIENT_DATA`, no valuation issued
- **Subjective**: none — every check has a numerical or boolean criterion.
- **Automation boundary**: 100% deterministic; `data_quality_gate.run_gate()` already implements this in Python.

### Phase 2: Competitive Position
- **Source authority**: Course Week 9 (Competitive Advantage); Claude tool Phase 2.
- **Input contract**: completed Phase 1.
- **Output deliverables**:
  - Peter Lynch life-cycle classification (Fast / Medium / Slow / Turnaround / Cyclical / Asset Play)
  - Porter's 5 Forces (Low / Medium / High per force)
  - Moat classification: Wide / Narrow / Limited / None
  - Capitalized intangible / valuation residual estimate (from book vs market value)
- **Deterministic pass criteria**:
  - [ ] Life-cycle classification picked from the 6 pre-defined categories (else fail)
  - [ ] All 5 Porter forces scored
- **Subjective**: moat width — explicitly subjective; document specific moat sources (switching cost / network / brand / scale / IP / regulatory).
- **Automation boundary**: structure deterministic, content requires LLM read of 10-K + industry analysis.

### Phase 3: Cost of Capital (WACC)
- **Source authority**: Course Week 2-3 (Cost of Capital).
- **Input contract**: market cap, debt details, beta source.
- **Output deliverables**:
  - re via CAPM with Blume-adjusted beta
  - Unlevered β if peer-group method used
  - rd from YTM of debt instruments OR rd ≈ Interest Expense / Avg Debt
  - WACC bridge showing each component's contribution
- **Deterministic pass criteria**:
  - [ ] Blume adjustment applied: `β_adj = 1/3 + 2/3 × β_raw`
  - [ ] Weights use **market values**, not book values
  - [ ] Small-cap premium (+3–4.7%) added if market cap < $2B
  - [ ] WACC ∈ [6%, 15%] (Gate 4.5 verifies)
- **Subjective**: ERP choice (5–6% range from Damodaran, historical, or implied) — document method.
- **Automation boundary**: 100% Python via `wacc_calc()`.

### Phase 4: Multi-Method Valuation
- **Source authority**: Course Week 4-6 (FCF Model, EVA, EPV, Multiples).
- **Input contract**: WACC, FCFF projections, peer multiples.
- **Output deliverables** (≥ 3 methods required):
  - **EPV** — zero-growth floor (mandatory for all cases)
  - **DCF** — Simplified Proforma (5y explicit + course-strict terminal) OR 3-Stage FCFF for younger companies
  - **Multiples** — at least 3 of {P/E, P/B, EV/EBITDA, EV/Sales, EV/IC} with peer median + 25th–75th percentile range
  - **EVA** (supplementary, equivalent to DCF mathematically)
  - **Residual Income (EBO)** for financials specifically
  - **V5.0-alpha NEW**: every IV produced as Monte Carlo distribution (p5/p25/p50/p75/p95) via `monte_carlo_dcf()`
- **Deterministic pass criteria**:
  - [ ] At least 3 methods used (else fail)
  - [ ] Terminal value uses course-strict formula `NOPAT × (1−g/ROI) / (WACC−g)` for DCF (not plain Gordon)
  - [ ] At terminal stage, `ROI = WACC` unless explicit moat justification documented (Apple 2013 / Tesla types)
  - [ ] Terminal Value share of EV ∈ [40%, 60%] (else explicit forecast period too short or terminal too aggressive)
  - [ ] DCF + Multiples reconcile within 30% (else investigate)
  - [ ] Monte Carlo `num_valid ≥ 95%` of `num_simulations` (else inputs unstable, lower uncertainty)
- **Subjective**: peer selection (4-8 names matching industry, growth, margin, leverage, size).
- **Automation boundary**: arithmetic 100% Python; method selection + assumption justification require LLM judgment.

### ✋ Gate 4.5: Sanity Bounds (V4.x)
- **Source authority**: V4.0 release 2026-05-06; codified in `valuation_calc.sanity_check()`.
- **Why it exists**: V3 had cases where IV came out 10× current price. Most were assumption errors, not real mispricings.
- **Input contract**: WACC, terminal_g, beta, IV per share, current price, growth rates.
- **Deterministic bounds** (each violation → flag):
  - WACC ∈ [6%, 15%]
  - growth_high ∈ [-20%, 50%]
  - growth_terminal ∈ [1%, 4%] (cap at GDP+ rate)
  - growth_terminal ≤ growth_high (terminal can't exceed near-term)
  - tax_rate ∈ [15%, 30%]
  - IV / Price ∈ [0.3, 3.0] (anything outside is "extreme — assumptions or market is broken")
  - beta ∈ [0.3, 2.5]
  - IV per share > 0
- **Pass criteria**: 0 HIGH-severity flags. MEDIUM flags issue ⚠️ but allow continuation.
- **Subjective**: none.
- **Automation boundary**: 100% Python.

### Phase 5: Sensitivity Analysis
- **Source authority**: Course Week 4 (sensitivity tables); Claude tool Phase 5.
- **Input contract**: Phase 4 base-case IV.
- **Output deliverables**:
  - WACC × terminal_g 2-variable grid
  - Bull / Base / Bear scenarios with explicit deltas (revenue ±2%, margin ±1-2pp, terminal_g ±0.5%, WACC ±0.5%)
  - **Reverse DCF** — implied growth that explains current market cap
  - Mauboussin S&P 1500 base-rate label for implied growth
- **Deterministic pass criteria**:
  - [ ] Reverse DCF implied growth labelled (Pessimistic / Conservative / Realistic / Optimistic / Aggressive / Top-decile / Heroic)
  - [ ] Implied growth ≤ 25% × 5y for non-Auto-VETO (else triggers V4.1 heroic-growth VETO)
- **Subjective**: scenario delta sizing.
- **Automation boundary**: arithmetic 100% Python via `sensitivity_dcf()` + `reverse_dcf()`.

### Phase 6: Investment Decision
- **Source authority**: Claude tool Phase 6 (Quality Checklist + Exit Strategy).
- **Input contract**: completed Phase 1-5.
- **Output deliverables**:
  - P/V ratio + label per Claude tool table
  - Investment Quality Checklist — 6 yes/no questions (must all be YES to advance to BUY)
  - Pre-committed exit triggers (3 hard, 3 soft)
  - Position size proposal
- **Deterministic pass criteria**:
  - [ ] Margin of Safety ≥ 25% for `BUY` recommendation (else downgrade to `WATCH`)
  - [ ] All 6 quality-checklist questions answered "YES"
  - [ ] Position size ≤ Tier cap from `position_size_check()` (Tier 1: 12%, Tier 2: 8%, Tier 3: 5%, Tier 4: 3%)
  - [ ] At least 3 hard exit triggers documented (price-based AND fundamentals-based)
- **Subjective**: 6-question checklist requires LLM read of business + history.
- **Automation boundary**: position-size enforcement + MoS threshold 100% deterministic; quality checklist requires LLM.

### ✋ Gate 6.5: Bull/Bear Debate (V4.x)
- **Source authority**: V4.0 release 2026-05-06 (replaces single pre-mortem from NVO/BMY post-mortem). Codified in `skills/mba-valuation/sop.md` Phase 6.5.
- **Why it exists**: pre-V4.0 framework had Boris write Bear case after Bull case → bias. V4.0 forces 2 independent sub-agent passes with adversarial framing.
- **Input contract**: completed Phase 1-6 base recommendation.
- **Output deliverables**:
  - **Bull Researcher Argument** — 600-1200 words, ≥ 5 cited specific numerical evidence
  - **Bear Researcher Argument** — 600-1200 words, ≥ 3 cited risks + Mauboussin base-rate counter
  - **Reconciliation Matrix** — 5 pillars (Moat / Valuation / Growth / Quality / Catalyst), Bull score vs Bear score per pillar (1-10)
  - **Pre-mortem** — 3 specific scenarios stock loses 30%
  - **Auto-VETO check** — 5 V4.1 hard rules
- **Deterministic pass criteria** (Auto-VETO triggers, ANY one halts):
  1. Position size > Tier cap
  2. Organic revenue declined 2+ consecutive quarters with no specific catalyst
  3. GAAP vs Non-GAAP gap > 30% sustained 4+ quarters
  4. Active securities-fraud lawsuit (also caught by Gate 0.5; double-check)
  5. Reverse DCF implied growth in `Heroic` band (>25% × 5y)
- **Soft criteria**: Bull cited evidence ≥ 5 specific numbers; Bear cited risks ≥ 3 + Mauboussin base-rate.
- **Subjective**: the actual Bull/Bear arguments — LLM-driven, cannot be deterministic.
- **Automation boundary**: 5 Auto-VETO checks 100% Python; Bull/Bear narrative requires LLM.

### Phase 7: Behavioral Bias Check
- **Source authority**: Course Week 10 (Investor Behavior).
- **Input contract**: completed Phase 1-6 + Gate 6.5 result.
- **Output deliverables**: written audit against 6 biases (Anchoring / Confirmation / Overconfidence / Loss Aversion / Recency / Herd) with specific evidence the analyst is or isn't suffering from each.
- **Deterministic pass criteria**:
  - [ ] All 6 biases explicitly addressed (skip = fail)
- **Subjective**: 100% — this phase is meta-cognitive review.
- **Automation boundary**: prompt template can require all 6 sections; content is LLM judgment.

### Phase 8: Output Report
- **Source authority**: `v42_advanced_report_template.md` (already locked) + Claude tool Phase 8 output format.
- **Input contract**: completed Phase 1-7 + all gate results.
- **Output deliverables** — 17-section advanced report (~9,700 words, ~25-35 min reading):
  - Section 1: Decision Card with **Monte Carlo IV distribution** (V5.0-alpha — single-point IV banned)
  - Section 9: Three-Method Valuation with full Monte Carlo p5/p25/p50/p75/p95
  - Section 17: Final Decision Card with **bear-case (p5) MoS** + **conviction tag** TIGHT/MODERATE/WIDE
  - Backtest hit rate citations: must include Wilson 95% CI + n
- **Deterministic pass criteria**:
  - [ ] Section 1 has MC distribution (not single-point)
  - [ ] Section 9 has 10K-simulation MC for DCF
  - [ ] Section 17 has bear-case MoS + conviction tag
  - [ ] Any hit rate cite includes Wilson CI
- **Subjective**: prose quality.
- **Automation boundary**: structure 100% template-enforceable; prose requires LLM.

### ✋ Gate 9: Final Action Gate (V4.x)
- **Source authority**: V4.0 release 2026-05-06 (3-judge audit) + 24-hour cool-down.
- **Why it exists**: pre-V4.0 had no final sanity check before execution. Boris's "I'm sure" judgement bypassed 2 critical risks in 2026-Q1.
- **Input contract**: completed Phase 8 report + all gate results.
- **Output deliverables**: 3 judge audits (Fundamentals / Risk / Discipline & Catalyst) — currently 3 Claude sub-agents.
- **Deterministic pass criteria**:
  - [ ] Judge 1 (Fundamentals) verdict: PASS / FAIL / VETO
  - [ ] Judge 2 (Risk) verdict: PASS / FAIL / VETO
  - [ ] Judge 3 (Discipline & Catalyst) verdict: PASS / FAIL / VETO
- **Aggregate rule**:
  - 3/3 PASS → execute at proposed size
  - 2/3 PASS → execute at Tier-2 cap (no Tier-1 sizing without unanimous)
  - 1/3 PASS → 24-hour mandatory cool-down + re-evaluation
  - 0/3 PASS or any VETO → 24-hour cool-down + decision = VETO
- **Subjective**: judge content is LLM judgment.
- **Automation boundary**: aggregation rule 100% Python; judge opinions LLM.
- **V5.1 future**: replace 3 Claude sub-agents with cross-family (Claude + GPT-4o + Gemini). **Parked 2026-05-09** — no extra API budget; revisit when commercial direction decided + budget available. Current Phase 9 stays single-family (Claude only) until then.

---

## 4. Deterministic vs subjective markers

| Element | Deterministic share | Subjective share |
|---|---|---|
| Phase 0 — data gathering | 100% | 0% |
| Gate 0.5 — forensic | 95% (search + numerical) | 5% (query phrasing) |
| Phase 1 — historical | 80% (arithmetic) | 20% (one-time classification) |
| Gate 0.7 — data quality | 100% | 0% |
| Phase 2 — competitive | 30% (life-cycle classification) | 70% (moat reasoning) |
| Phase 3 — WACC | 95% | 5% (ERP choice) |
| Phase 4 — valuation | 70% (formulas + course rules) | 30% (peer selection, growth assumptions) |
| Gate 4.5 — sanity | 100% | 0% |
| Phase 5 — sensitivity | 90% | 10% (scenario delta sizing) |
| Phase 6 — decision | 50% (MoS + position size) | 50% (6-question checklist) |
| Gate 6.5 — Bull/Bear | 100% on Auto-VETO; 0% on narrative | full |
| Phase 7 — bias check | 0% | 100% |
| Phase 8 — report | 80% (template) | 20% (prose) |
| Gate 9 — final action | 100% on aggregation; 0% on judge content | full |

**Implication**: ~75% of the framework is deterministic and Python-testable. The other 25% is irreducibly LLM-driven (narrative arguments, qualitative classification, behavioral self-audit). Spec-driven development should focus testing budget on the 75%.

---

## 5. Test harness expectation

For partner (Josep) review and future engineers, the framework should support:

1. **Unit tests** (already 24 passing in `tests/test_smoke.py` as of v5.0.0-alpha):
   - Each helper in `valuation_calc.py` has at least 1 unit test (Wilson CI edge cases, MC reproducibility, etc.)
   - Each gate has at least 1 happy-path + 1 fail-path test
2. **Integration tests** (TODO V5.0 GA):
   - Each gate runs against fixture financial data, output verified against expected pass/fail
   - Round-trip: lock prediction → resolve checkpoint → calibration report
3. **Backtest reproducibility** (TODO V5.0 GA):
   - `random_sample_backtest.py` runs with fixed seed → identical case list across runs
   - Forward returns from yfinance verified against snapshotted prices for known dates

---

## 6. Drift control rules (mandatory for any future change)

To prevent the drift Partner flagged, every framework change must:

1. **Cite a source** — either course material section, a specific post-mortem, or a passing backtest case.
2. **Bump version** in `VERSION.md` + `change_log.md`.
3. **Update this SPEC** with the new phase / gate / criterion.
4. **Add a passing test** (unit + integration where applicable).
5. **Re-run full test suite** before tagging.

Adding a new gate without all 5 of the above is **rejected by review**, regardless of how good the idea sounds in conversation.

---

## 7. What's locked in v5.0-alpha vs deferred

### Locked (this version)
- 8 phases + 5 gates structure
- Course-strict DCF terminal formula
- Monte Carlo IV distribution + Wilson CI for hit rates
- Forward prediction tracker scaffold (`forward_tracker.py`)
- Random sampling backtest scaffold (`random_sample_backtest.py`)
- 24 passing unit tests
- ADBE retrofit demo

### Deferred to v5.0 GA
- Random sample backtest **execution** (n=50+, awaits sampling-pool decision + FMP data layer)
- Forward predictions populated for all open V4.3 verdicts (NVDA, ADBE, BAM, etc.)
- Cross-LLM Phase 9 (Item #3) — **parked**, no extra API budget; revisit post-commercial decision
- Skills directory (`mba-valuation`, `invest-screen`, etc.) updated to reference SPEC sections by anchor
- Spec-anchored prompt templates in skills (e.g. Phase 4 prompt cites SPEC §4 for its pass criteria)

### Out of scope until v5.1
- Cross-LLM verification (Phase 9.2 and 9.3)
- Portfolio-level factor exposure analysis
- Monte Carlo reverse DCF (currently single-point)
- Sector rotation timing
- Tail risk / stress testing

---

## 8. How to use this SPEC

For Boris:
- Treat this as the contract. Any new feature request is screened against §3 first ("does this fit an existing phase or gate, or is it a new one needing v5.x bump?").
- When discussing valuation with anyone (partner, customer, future investor), point at the gate, not the model.

For partner (Josep):
- §3 is the place to review for completeness. Each gate has explicit deterministic criteria; tell us where they're wrong, missing, or non-deterministic.
- §4 splits work that's testable from work that's irreducibly LLM. Validation effort should concentrate on §3 deterministic criteria.

For future engineers (or LLM agents):
- Build against §3 input/output contracts.
- Add tests in `tests/test_smoke.py` matching the deterministic criteria.
- Cite SPEC section in any PR description.
