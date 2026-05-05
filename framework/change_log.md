# Framework Change Log

## v2.0 Hardened — 2026-05-03

### Critical Bug Fixes

1. **Terminal Value Formula** — Locked to `NOPAT × (1-g/ROI)/(WACC-g)`, banned plain Gordon Growth which inflated valuations 30-50%
2. **Forensic Screening** — Added mandatory Phase 0.5 with 10 search queries before any valuation
3. **Validation Gates** — Added 7 binding gates (method convergence, TV concentration, EPV sanity, reverse DCF, FCFF reconciliation, multiples cross-check, MoS verification)
4. **Recommendation Cap Table** — Binding caps based on red flags + MoS thresholds
5. **WACC Risk Premiums** — Added credibility/litigation premiums automatic
6. **Default Assumptions Lock** — D1-D7 default parameters non-negotiable without justification

### Real-World Failures That Triggered v2.0

#### Failure 1: ABBV @ $203 (May 2026)
- v1: STRONG BUY ($295 intrinsic, +31% MoS)
- v2.0: HOLD ($200 intrinsic, ~0% MoS)
- Root cause: Plain Gordon Growth + asserted multiples premium

#### Failure 2: FISV @ $62 (April 2026)
- v1: HOLD「thesis intact」
- v2.0: 🔴 AVOID (active securities fraud lawsuit + CEO admission)
- Root cause: No mandatory forensic screening

### Calibration Adjustments

- **Securities fraud vs operational lawsuits** — Distinguished (MSFT antitrust ≠ FISV fraud)
- **Lawsuit time horizon** — 12-month review minimum, plus dismiss/settle conditions
- **Override protocol strengthened** — Counter-thesis + position cap + re-review trigger

---

## v1.0 — Original Framework

Based on CUHK MBA ACCT6111E (Dr. Bhaskaran Swaminathan) original methodology.

8 Phases:
0. Scope & data gathering
1. Historical financial analysis
2. Competitive position
3. Cost of capital
4. Multi-method valuation (EPV / DCF / Multiples / EVA / 3-Stage)
5. Sensitivity analysis
6. Investment decision
7. Behavioral bias check
8. Output report

**Issues identified**: Descriptive (describes how) but not prescriptive (doesn't enforce). Soft warnings instead of binding rules.

---

## Future Roadmap

- **v2.1** — Address remaining edge cases (international stocks data limitation, cyclical company normalization)
- **v2.2** — Add automated cross-Claude validation harness
- **v3.0** — Possible AI agent integration with auto-update on new SEC filings

---

## 2026-05-03 — Course Alignment Verification

### Regression Test Results

Tested v2.0 framework against original CUHK MBA ACCT6111E course Excel models:

#### Apple 2013 Test
- Course Excel: 3-stage DCF $454/share, Full DCF $678/share
- v2.0 Expected: $440-470 (3-stage), $660-695 (full)
- **Result: ✅ PASS** — formula identical, methodology aligned

#### SJM 2024 Test
- Course Excel range: $113-$144/share across methods
- Course EPV (3% growth): $124.88
- v2.0 Expected: same range
- **Result: ✅ PASS** — formula identical

### Key Validation

The course Excel uses:
- Terminal Formula: `NOPAT × (1 − g/ROI) / (WACC − g)` ✓ matches v2.0 D1
- Default Terminal ROI = WACC ✓ matches v2.0 D1 conservative case
- Reinvestment b = g/ROI ✓ matches v2.0
- 3-stage DCF (High + 15yr Transition + Steady) ✓ matches v2.0 D7

### Conclusion

**v2.0 hardened framework is 100% course-faithful in valuation methodology**. The hardening adds:
- Phase 0.5 Forensic Screening (NEW)
- 7 Validation Gates (NEW)
- Recommendation Cap Table (NEW)
- Discrepancy Resolution Protocol (NEW)

These are **enhancements on top of course-faithful base**, not deviations from course methodology.


---

## 2026-05-05 — v3.0 Rules Trigger（FISV Post-Mortem）

### Real-World Validation of v2.0

FISV trade（2026-04-14 buy → 2026-05-04 trim → 2026-05-05 Q1 confirm）provided **first real-world validation of v2.0 framework hardening**:

- V1 framework missed Cypanga Sicav v. Fiserv lawsuit (resulting in over-bullish BUY thesis at $58.86)
- V2.0 Phase 0.5 forensic screening caught it on re-run (5/4)
- Trim executed 5/4 @ $63 → realized +$972.90 (+7.03%)
- 5/5 Q1 announce: -7.4% drop to $58.16 → avoided -$1,137.40 vs hold-through
- **Total framework value-add: $2,110.30 on single trade**

### v3.0 Framework Updates Triggered

Based on FISV post-mortem (see investor's private journal/post_mortems/FISV_2026-05-05.md):

| # | Rule Add | Phase |
|---|---|---|
| 1 | GAAP vs Non-GAAP gap > 30% sustained = quality flag, haircut intrinsic 15% | Phase 1 |
| 2 | Organic revenue YoY < 0 for 2+ consecutive quarters = auto-AVOID | Phase 1 |
| 3 | Superinvestor signal weighting cap 20% | Phase 7 |
| 4 | Pre-mortem mandatory @ entry day (3 reasons + monitoring triggers) | Phase 6.5 |
| 5 | Position size cap 8-12% per single stock regardless of conviction | Phase 7 |
| 6 | Mauboussin S&P 1500 base rate cross-check on Stage 1 growth | Phase 4 |
| 7 | Forensic re-screen trigger → action within 72 hours | Phase 0.5 ext |

### Status: Pending v3.0 Documentation

These 7 rules will be merged into ACCT6111E_v3_hardened.md upon next major framework revision. Currently logged in investor's lessons_learned.md.

