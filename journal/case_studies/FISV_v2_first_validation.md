# Case Study: FISV — V2.0 Hardening 嘅 First Real-World Validation

**Date**: 2026-05-05
**Trade**: Fiserv, Inc. (FISV)
**Result**: V2.0 framework saved $2,110 on a single trade
**Lessons → v3.0 rule additions**: 7

---

## Background

呢個 case study 記錄 v2.0 hardened framework 嘅 first real-world validation。
Investor 用 v1 framework 4/14 入場 FISV @ $58.86，後再 v2.0 framework 5/4 re-run forensic 發現問題，trim 嗰日，第二日 Q1 結果 confirm thesis 已 broken。

**Public lessons** for the open-source framework community.

---

## Timeline

| Date | Action | Framework Used | Result |
|---|---|---|---|
| 2026-04-10 | Initial screen → BUY thesis | V1 | MoS 32% @ $58.86; missed lawsuit |
| 2026-04-14 | Executed buy 235 shares @ $58.86 | V1 | $13,832 deployed (~50% of portfolio) |
| 2026-04-27 | Routine review → HOLD | V1 | Intrinsic updated $87 → $90 |
| 2026-05-04 | V2.0 hardened re-run with Phase 0.5 forensic | **V2.0** | **Detected Cypanga Sicav v. Fiserv lawsuit** |
| 2026-05-04 | Decision reverse: BUY → AVOID → TRIM ALL | V2.0 | Sold 235 @ $63.00 = $14,805 |
| 2026-05-05 | FISV Q1 2026 results announced pre-market | — | -7.4% drop confirms thesis broken |

---

## V1 vs V2.0 Framework Difference

### What V1 Missed

1. **No mandatory forensic search**
   - Cypanga Sicav class action lawsuit publicly filed Nov 2025
   - V1 thesis didn't surface this in any search
   - Result: 32% MoS BUY recommendation that should have been AVOID

2. **No GAAP vs Non-GAAP gap analysis**
   - FISV gap: GAAP EPS $1.07 vs Non-GAAP $1.79 = **67% gap**
   - V1 used Non-GAAP for valuation → over-stated earnings power
   - Real GAAP earnings supported lower intrinsic

3. **No organic revenue trend analysis**
   - Q1 2026 revealed Organic revenue **-4% YoY**
   - V1 thesis assumed organic stabilization post-Argentina noise
   - Reality: ex-Argentina also mature/declining

4. **Superinvestor signal over-weighted**
   - Klarman (Baupost) +145% increase Q4 2025
   - V1 weighted as strong confirmatory signal
   - Reality: superinvestor signals are confirmatory, not unconditional

### What V2.0 Caught

V2.0 Phase 0.5 mandatory forensic screening (10 searches) directly surfaced:
- Active securities fraud lawsuit
- Quality concerns (GAAP-Non-GAAP gap)
- Capital allocation questions ($30B net debt)
- Combined → AVOID recommendation

Trim executed before Q1 catalyst → captured profit AND avoided loss.

---

## Q1 2026 Results (5/5 announcement) — Thesis Broken Confirmed

| Metric | Q1 2026 | YoY |
|---|---|---|
| Revenue | $5.03B | **-2%** |
| Organic revenue | — | **-4%** |
| GAAP EPS | $1.07 | **-29%** |
| Non-GAAP EPS | $1.79 | beat consensus |
| Free Cash Flow | $259M | **-30%** ($371M prior) |
| Stock reaction | -7.4% to $58.16 | — |

All 4 forensic concerns materialized in single quarter.

---

## Financial Outcome

```
V1 path (counterfactual hold-through):
  235 × ($58.16 - $58.86) = -$164.50 loss

V2.0 actual path:
  Realized: 235 × ($63.00 - $58.86) = +$972.90 (+7.03%)
  Avoided loss: 235 × ($63.00 - $58.16) = +$1,137.40
  Total: +$2,110.30

V2.0 framework alpha on single trade: $2,110 / $13,832 = 15.3%
```

---

## V3.0 Rules Triggered

7 new rules added to framework backlog:

| # | Rule | Category |
|---|---|---|
| 1 | GAAP vs Non-GAAP gap > 30% sustained = quality flag, haircut intrinsic 15% | Phase 1 |
| 2 | Organic revenue YoY < 0 for 2+ consecutive quarters = auto-AVOID | Phase 1 |
| 3 | Superinvestor signal weighting cap 20% | Phase 7 |
| 4 | Pre-mortem mandatory @ entry day (3 reasons + monitoring triggers) | Phase 6.5 |
| 5 | Position size cap 8-12% per single stock regardless of conviction | Phase 7 |
| 6 | Mauboussin S&P 1500 base rate cross-check on Stage 1 growth | Phase 4 |
| 7 | Forensic re-screen trigger → action within 72 hours | Phase 0.5 ext |

---

## Behavioral Lessons

### What Worked
1. ✅ Acknowledging v1 thesis was wrong (no ego defense)
2. ✅ Pre-committed trim trigger executed without emotion
3. ✅ Capital efficiently redeployed to higher-conviction trades

### What Didn't
1. ❌ Initial entry over-confidence on Klarman signal alone
2. ❌ Position size 50% concentration on lawsuit-uncleared trade
3. ❌ Trim could have been 4 days earlier (Cypanga lawsuit was public news)

---

## Key Takeaway

> **"It's not what you don't know that gets you into trouble. It's what you know for sure that just ain't so."** — Mark Twain

V1 framework gave certainty (32% MoS = BUY). V2.0 forensic gate added humility (lawsuit detected → AVOID).

**Framework hardening's value isn't prediction; it's systematic process that doesn't let red flags slip through.**

---

## Reproducibility

This case study uses the v2.0 hardened framework documented in:
- `framework/ACCT6111E_v2_hardened.md`
- `framework/change_log.md`

The 7 new rules are pending in v3.0 (see change_log.md 2026-05-05 entry).

Anyone can re-run the analysis with public 10-K, 10-Q, and SEC filings + the v2.0 framework.

---

**Author note**: This case is shared as an open lesson. Investor identity / portfolio specifics are anonymized; framework methodology + outcome are public.
