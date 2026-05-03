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
