# V4.4 Accounting Hardening + V2.1 Reporting Spec

> Additive to v5.0.0-alpha foundation. All V4.x / V5.0-alpha calls remain compatible.
> This document is **methodology only** — no portfolio holdings or personal data.

---

## Part 1 — V4.4 Accounting Hardening

V4.4 corrects three systematic biases discovered via framework audit. Cumulative effect of the
pre-V4.4 errors was an upward intrinsic-value bias of roughly +15-40%.

### 1.1 Standardized CAPM WACC (`wacc_calc.py`)

Replaces ad-hoc per-memo discount rates with a single CAPM formula:

```
Re  = Rf + β × ERP + Country Premium
WACC = (E/V) × Re + (D/V) × Rd × (1 − Tax)
```

Defaults (override per name):
- `Rf` = current 10Y Treasury (e.g. 4.57%)
- `ERP` = 5.5% (Damodaran; conservative vs implied ~4.5%)
- `Debt premium` = 1.5% over Rf unless rating-implied
- Beta = 5-yr monthly

Typical WACC ranges: large/stable 7-9%, growth 9-12%, high-vol 12-17%.

### 1.2 ASC 842 Operating Leases in Net Debt

Operating lease liabilities are capitalized and **added to net debt** in the equity bridge.
Excluding them understated net debt (and overstated equity value) for lease-heavy names.

```
Adj Net Debt = Total Debt + Operating Lease Liabilities − Cash & Equivalents
```

### 1.3 SBC-Adjusted Free Cash Flow

Stock-based compensation is a real economic cost (dilution). V4.4 deducts SBC from FCF:

```
Adj FCF (V4.4) = OCF − CapEx − SBC
```

Materiality check: SBC as % of FCF. >10% deserves explicit discussion (common for high-growth tech).

### 1.4 Mid-Year Convention (DCF)

Cash flows are assumed mid-year: discount periods 0.5, 1.5, 2.5 … rather than 1, 2, 3.
Year-end discounting understates intrinsic value by ~2-4%.

```
Discount Factor (year n) = 1 / (1 + WACC)^(n − 0.5)
```

### 1.5 SOTP for Mixed-Model Businesses

Companies with a financing arm (e.g. captive lender) must separate Industrial vs Financial Services
before computing leverage. A blended "Total Debt / Total EBITDA" mis-measures the operating business.

---

## Part 2 — Multi-Method Reconciliation (mandatory)

Single-method DCF = false precision. Every valuation reconciles 5-7 methods:

| # | Method | Notes |
|---|---|---|
| 1 | EPV (Earnings Power Value) | Zero-growth floor |
| 2 | FCF DCF (V4.4) | Primary, mid-year convention |
| 3 | Owner Earnings DCF | Cross-check vs FCF method |
| 4 | API DCF | If available from data provider |
| 5 | Multiples (peer-based) | EV/EBITDA, P/E, peer median |
| 6 | Analyst Consensus | Wall Street range |
| 7 | SOTP / Precedent Transactions | Where applicable |

Output: weighted intrinsic + median + mean + range spread + convergence confidence.
Pure DCF for high-WACC / wide-moat names systematically under-values optionality —
the weighted blend corrects this. EPV is typically down-weighted (5-10%) as a floor outlier.

---

## Part 3 — V2.1 Reporting Spec (17 sections)

Target ~12,000 words for a BUY memo. Front-loaded decision compression so a reader can decide
from the 1-page Decision Sheet alone, with full depth available for the deep read.

```
PART 0  Decision Compression
  0.1  Decision Sheet (1 page)
  0.2  Portfolio Construction Impact
  0.3  Scenario Ranges (bear/base/bull + probabilities)
PART A  Understanding the Business
  1    Decision Card (detailed)
  2    Business Introduction (5 sub-sections)
  3    Comparative Landscape (peer table)
  4    Capital Allocation Track Record (Outsiders grade)
PART B  Verifying the Data
  5    Data Quality Gate (9 checks)
  6    Excel Input Mapping (cells + sources)
  7    Sentiment + Macro
PART C  The Numbers
  8    Quality Profile (10-yr ROIC)
  9    Multi-Method Valuation (5-7 methods)
  10   Sanity Bounds
  11   Reverse DCF + Base Rate
  12   Quality Gates (6-Q + Auto-VETO + operational)
PART D  The Debate
  13   Bull Argument (long-form)
  14   Bear Argument (+ 6-discipline check)
  15   Reconciliation Matrix (5-pillar)
  16   3-Judge Audit (Fundamentals / Risk / Discipline)
PART E  Action
  17   Final Decision Card + Triggers + "what would prove me wrong"
```

### 3.1 Q6 HARD GATE Rule

Price (Q6) is an **independent hard gate**, not one equal-weighted question. If MoS < 20%:
verdict = WATCHLIST / PASS regardless of business quality (Q1-Q5). No amount of quality
justifies overpaying. A borderline MoS (14-20%) permits only a reduced "starter" size.

### 3.2 Scenario Ranges (replace point estimates)

Bear / Base / Bull each with probability weight + sensitivity table (WACC, terminal g, margin,
growth). Expected value = Σ(probability × intrinsic). For cyclicals, normalize to mid-cycle
earnings, never current trough.

### 3.3 Risk-Budget Position Sizing

```
Size = Base conviction (1-2% starter / 3-5% normal / 6-8% high)
       × Volatility adj (β-based)
       × Correlation adj (sector overlap penalty)
       × Downside adj (bear-case drawdown)
Hard caps: single position 8%, single sector 25%, top-3 combined 50%.
```

### 3.4 Portfolio Construction Layer

Every memo quantifies its impact on portfolio concentration, beta, sector exposure, and
drawdown — because at small portfolio sizes, construction risk often dominates single-name
selection skill.

---

## Part 4 — Quality Gates

### 6-Q Quality Gate (Swaminathan)
Q1 Business · Q2 Management · Q3 Financials · Q4 Growth · Q5 Returns · Q6 Price (HARD GATE).
Each Q: verdict + numeric evidence + insight. Threshold ≥ 5/6 to be a BUY candidate
(subject to Q6 hard gate).

### Auto-VETO (8 triggers)
1. Position size > tier cap
2. Organic revenue decline 2+ consecutive Q
3. GAAP/Non-GAAP gap > 30% (unexplained)
4. Material securities litigation
5. Reverse DCF heroic (implied growth > 15%)
6. Auditor change < 12 months
7. Late filings > 30 days
8. Senior exec (CEO/CFO/CAO) sudden departure

### 3-Judge Audit
Fundamentals / Risk / Discipline — each votes PASS / HOLD / FAIL with reasoning, concerns,
strengths. ≥ 2 PASS to proceed. Empirically (50-case backtest): 0-PASS verdicts ~100%
accurate at rejection; 3-PASS ~91% accurate.

---

## Part 5 — Thesis Tracker (time dimension)

A thesis must be **falsifiable**. Track each position's pillars over time:

| Pillar | Original Expectation | Current Status | Trend |
|--------|---------------------|----------------|-------|

Plus: catalyst calendar, disconfirming-evidence watch (tracked as rigorously as confirming
evidence), conviction level, update log. Review quarterly minimum + after each earnings.

A blank template lives in `portfolio_structure/thesis_tracker_template.md`.

---

## Part 6 — Live Excel DCF (`dcf_model_builder.py`)

Generates an institutional-standard live .xlsx (formulas, not hardcoded values):
- Case selector (1=Bear / 2=Base / 3=Bull) with CHOOSE consolidation
- Scenario assumption blocks horizontal across years
- Mid-year convention discounting
- WACC sheet (CAPM)
- Sensitivity table (WACC × Terminal Growth, live formulas)
- Colour coding: blue = input, black = formula, green = sheet-link; cell comments on inputs

Edit any blue input → implied price, MoS, and sensitivity table recalc automatically.
The shipped CONFIGS is a single illustrative example; populate with your own research.

---

## Validation Notes

- 50-case historical backtest: 76% hit rate, Wilson 95% CI [56%, 89%].
- Q6 HARD GATE precision 91%; Auto-VETO precision 93% (on the backtest sample).
- Independent third-party review graded the framework "above-average / B+"; the cited gap was
  decision compression + portfolio risk control (addressed in V2.1), not analytical rigor.
- Known biases still being calibrated: cyclical-trough MoS threshold (too strict by ~3-7pp),
  secular-growth optionality (under-valued by pure DCF).
