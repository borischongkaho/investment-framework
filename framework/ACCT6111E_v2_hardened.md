# ACCT6111E Framework v2.0 — Hardened

> **Version**: v2.0 hardened
> **Released**: 2026-05-03
> **Based on**: CUHK MBA ACCT6111E (Dr. Bhaskaran Swaminathan)
> **Status**: Production framework after v1 → v2 hardening based on real failures

---

## 🚨 Why Hardening Was Necessary

Two real failures revealed v1 framework gaps:

### Failure 1: ABBV (May 2026)
- v1 produced $295 intrinsic, +31% MoS, STRONG BUY
- Truth: $185-210 intrinsic, ~0% MoS, HOLD
- **Root cause**: Wrong terminal value formula (plain Gordon Growth)

### Failure 2: FISV (April 2026)
- v1 produced HOLD「thesis intact」recommendation
- Truth: Active securities fraud lawsuit (Cypanga Sicav, Nov 2025) → AVOID
- **Root cause**: No mandatory forensic screening

---

## 🛡️ v2.0 Hardening Components

### 1. Phase 0.5 — Mandatory Forensic Screening

**Before ANY valuation work, run these searches in sequence**:

#### Litigation & Regulatory
1. "[Ticker] securities class action lawsuit"
2. "[Ticker] SEC investigation OR enforcement"
3. "[Ticker] DOJ investigation"
4. "[Ticker] accounting restatement OR material weakness"
5. "[Ticker] going concern auditor"

#### Management Integrity
6. "[Ticker] CEO change OR CFO change last 12 months"
7. "[Ticker] guidance cut OR guidance miss"
8. "[Ticker] earnings restatement"

#### Recent Earnings Verification
9. "[Ticker] latest quarterly earnings results"
10. Compare to last 4 quarters trend

#### Mandatory Escalation Rules

**🔴 IMMEDIATE AVOID Triggers**:
- Active securities fraud lawsuit (filed, not dismissed)
- Active SEC enforcement
- Financial restatement < 24 months
- Going concern auditor opinion
- CEO + CFO both changed < 12 months
- Revenue manipulation alleged
- D/E > 5x with declining revenue
- Interest coverage < 1.5x

**🟠 REQUIRES JUSTIFICATION (cap at HOLD)**:
- D/E 3.0-5.0x
- Recent guidance miss > 15%
- CEO change + missed guidance
- Goodwill > 50% of assets
- Negative book equity
- Pending major litigation > 5% mcap
- Recent serial acquisitions

**🟡 MONITOR (disclose but don't block BUY)**:
- D/E 2.0-3.0x
- Single missed quarter
- Industry disruption emerging
- Revenue growth decelerating
- Margin compression

#### Important Calibration: Distinguish Fraud vs Operational Lawsuits

- **Securities fraud lawsuit (alleging financial misrep)** → AVOID
- **Antitrust lawsuit** → MONITOR
- **Patent litigation** → MONITOR (unless material to revenue)
- **Labor/employment** → MONITOR
- **Old certified lawsuits (>5 years old conduct, current management not implicated)** → MONITOR + disclose

---

### 2. Default Assumptions Lock (D1-D7)

#### D1: Terminal Value Formula (CRITICAL FIX)

```
ALWAYS USE: TV = NOPAT(T+1) × (1 − g/ROI) / (WACC − g)
NEVER USE:  TV = FCFF(T+1) / (WACC − g)   [plain Gordon Growth]

Default ROI at terminal:
- Most conservative: ROI = WACC (growth doesn't add value)
- Base case: ROI = MIN(current ROIC, 2× WACC)
- Bull case: ROI = current ROIC, capped at 25%
```

**Why critical**: Plain Gordon implicitly assumes ROI = ∞ (zero reinvestment for growth) → mathematically impossible → produces inflated valuations 30-50%.

#### D2: Terminal Growth Rate
- Default: 2.5%
- Hard cap: 3.0%
- Never exceed: nominal GDP (~5%)

#### D3: WACC Floors
- US large-cap (>$10B): MINIMUM 7.0%
- US mid-cap ($2-10B): MINIMUM 8.0%
- US small-cap (<$2B): MINIMUM 9.5%
- International: +1% to floor

#### D4: Beta Treatment
- Always apply Blume adjustment: β_adj = 1/3 + 2/3 × β_raw
- Display BOTH raw and adjusted
- Use 5-year monthly regression

#### D5: Tax Rate
- Default: 21% (US federal statutory)
- Use effective only if 5-year average between 15-30%

#### D6: NWC Projection
- If historical NWC < 0 → project NWC = 0 (conservative)
- Never project negative NWC into perpetuity

#### D7: Discount Period Length
- Stage 1 (high growth): 2-3 years
- Stage 2 (transition): 5-7 years
- Total explicit forecast: 5-10 years
- Never use 3-year forecast

---

### 3. Validation Gates (7 Mandatory)

After valuation but BEFORE final output:

#### Gate 1: Method Convergence
```
ratio = max_value / min_value across methods
> 1.50 → WARN
> 2.00 → STOP, methods inconsistent
```

#### Gate 2: TV Concentration
```
TV / Total EV
> 60% → WARN, extend forecast
> 75% → STOP, perpetuity bet
```

#### Gate 3: EPV Sanity
```
IF EPV > Base DCF → STOP, growth value-destructive
Investigate ROI < WACC scenario
```

#### Gate 4: Reverse DCF Plausibility
```
g* = WACC - FCFF₁ / Current EV
g* > 4% → WARN, market overvaluing growth
g* > 6% → STOP, AVOID
g* < 0% → WARN, market pricing decline
```

#### Gate 5: FCFF Reconciliation
```
|TopDown - BottomUp| / TopDown > 10% → INVESTIGATE
```

#### Gate 6: Multiples Cross-Check
```
|DCF - Multiples| / DCF
> 30% → FLAG
> 50% → STOP
```

#### Gate 7: Margin of Safety Verification
```
For BUY: MoS ≥ 25%
For STRONG BUY: MoS ≥ 35% AND all gates pass AND no flags AND ROIC-WACC > 3%
MoS < 25% → max recommendation: HOLD or WATCH
MoS < 0% → AVOID or TRIM
```

---

### 4. Recommendation Cap Table (Binding)

The maximum recommendation Claude can output is constrained by the table below. Apply the MOST RESTRICTIVE applicable cap.

| Condition | Max Recommendation |
|---|---|
| Any 🔴 red flag triggered | AVOID |
| Forensic screening flagged 2+ 🟠 items | HOLD |
| Forensic screening flagged 1 🟠 item | BUY (with disclosed risk) |
| Validation gate FAILED (any) | HOLD |
| Method convergence ratio > 2.0 | "Cannot value" |
| MoS < 0% (overvalued) | TRIM/SELL |
| MoS 0-15% | HOLD |
| MoS 15-25% | WATCH (consider BUY if quality high) |
| MoS 25-35% | BUY |
| MoS 35%+ AND all gates pass AND no flags | STRONG BUY |
| Active fraud lawsuit | AVOID |
| CEO admitted prior guidance unrealistic | HOLD minimum 2 quarters |

#### Override Protocol
User can override caps ONLY by explicitly stating:
> "I understand the [specific risk] and accept the cap override for this analysis."

Override requires:
1. Explicit risk acknowledgment with specifics
2. User-provided counter-thesis
3. Position size CAP for overridden cases (max 2% portfolio)
4. Mandatory 3-month re-review trigger

---

### 5. Mandatory Workflow Execution Order

When user requests valuation, execute IN THIS EXACT ORDER:

1. **Acknowledge & Confirm** — ticker, date, purpose
2. **Phase 0.5 Forensic Screening** — all 10 searches mandatory
3. **Phase 0 Data Gathering** — 5+ years actuals
4. **Phase 1 Historical Analysis** — top-down AND bottom-up FCFF (run Gate 5)
5. **Phase 2 Competitive Position** — Lynch + Porter + Moat
6. **Phase 3 WACC** — apply D1-D7 + add credibility premium if 🟠 flags
7. **Phase 4 Multi-Method Valuation**
   - EPV
   - DCF (using locked terminal formula)
   - Multiples (minimum 4 peers)
   - Reverse DCF (Gate 4)
   - IF EPV > DCF → Gate 3 STOP
8. **Validation Gates** — run all 7, output status table
9. **Phase 5-7** — sensitivity, decision, bias check
10. **Phase 8 Final Report** — mandatory format with all required sections

---

### 6. Mandatory Output Elements

Every valuation report must include:

#### Section A: Forensic Screening Status
```
🔍 FORENSIC SCREENING (run on [date]):
- Litigation: [status with citations]
- SEC/DOJ: [status]
- Auditor: [status]
- Management: [status with dates]
- Guidance Track Record: [status]
Risk Premium Applied: +X.X% to WACC
```

#### Section B: Validation Gates
```
✓ VALIDATION GATES (7 gates):
Gate 1 (Methods):    [PASS/WARN/FAIL] — ratio: X.XX
Gate 2 (TV%):        [PASS/WARN/FAIL] — TV/EV: XX%
Gate 3 (EPV):        [PASS/WARN/FAIL]
Gate 4 (Reverse):    [PASS/WARN/FAIL] — implied g: X.X%
Gate 5 (FCFF):       [PASS/WARN/FAIL] — variance: X%
Gate 6 (Multiples):  [PASS/WARN/FAIL] — variance: X%
Gate 7 (MoS):        [PASS/WARN/FAIL] — actual: XX%
Overall Status: [GREEN/YELLOW/RED]
```

#### Section C: Recommendation Justification
```
📋 RECOMMENDATION CAP COMPLIANCE:
Applied Cap: [from Cap Table]
Triggers: [list any caps triggered]
Final Recommendation: [recommendation]
```

#### Section D: Assumptions Audit
```
🔧 KEY ASSUMPTIONS USED:
Terminal Value Formula: [exact formula]
Terminal Growth Rate: X.X%
Terminal ROI: X.X%
WACC: X.X% (floor: X.X%, +credibility: X.X%)
Beta: Raw X.XX → Blume-adjusted X.XX
Tax Rate: XX% (effective: XX%, used: XX%)
Forecast Period: X years
Peer Group Size: X companies
```

#### Section E: Business Overview (for end-user understanding)
```
🏢 BUSINESS OVERVIEW
- 30-second business description (no jargon)
- Segments breakdown
- How the company makes money
- Moat with rating (🟢 Wide / 🟢 Narrow / 🟡 Limited)
- Investment thesis (3 sentences)
- 4 specific risks with counter-arguments
- Reference analogy (similar company case)
```

---

### 7. Discrepancy Resolution Protocol

When user references prior valuation showing different result:

1. **Acknowledge difference** — don't split, don't defer, don't abandon
2. **Identify root cause** via checklist (formula? growth? WACC? peers?)
3. **Apply tie-breaker hierarchy**:
   - Most recent data wins
   - Most conservative wins (when equally defensible)
   - Framework default wins (when methodology disagrees)
   - Validation gates outcome wins
4. **Document resolution** with comparison table
5. **Update recommendation** with re-review trigger

---

## 📋 Cross-Validation Test Suite

Use these cases to validate any framework implementation:

### Test 1: ABBV @ $203
Expected v2.0 output:
- Forensic: GREEN
- Terminal formula: NOPAT × (1-g/ROI)/(WACC-g)
- Intrinsic: $185-210 range
- MoS: 0-5%
- Recommendation: HOLD
- Variance vs Claude.ai: ±5%

### Test 2: FISV @ $62
Expected v2.0 output:
- Forensic: 🔴 ACTIVE LAWSUIT detected
- Cap triggered: AVOID
- Cannot output BUY/HOLD with conviction
- Report cites lawsuit + CEO admission

### Test 3: GIS (clean defensive)
Expected: No false AVOID, BORDERLINE BUY at appropriate MoS

---

## Migration Notes

- Existing analyses NOT auto-rerun
- New rules apply to new analyses going forward
- User can request "v2.0 re-run" for any holding
- All v2.0 output should include version tag: `ACCT6111E v2.0 hardened`

---

## Continuous Improvement

Framework hardening is iterative. Track:
- False positives (legitimate buys wrongly capped)
- False negatives (dangerous stocks getting through)
- Edge cases (large-cap routine litigation, international stocks)
- Cross-Claude variance over time

Document in `framework/change_log.md`.

---

**Last updated**: 2026-05-03
**Version**: v2.0 hardened
