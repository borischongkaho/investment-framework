# Case Study: Price Trigger Discipline — When Lower Price Is Not A Buy Signal

**Framework**: V4.2 hardened
**Date**: 2026-05-07
**Trigger Type**: Mid-cap quality stock dropped 3.5% in 2 days post-entry
**Lesson**: V4.1 position size auto-VETO overrides MoS-based add temptation

---

## Scenario (Anonymized)

A V4.2 framework user holds an existing position in a wide-moat quality stock. The stock dropped ~3-5% over a few days with **no fundamental change**:
- Recent earnings already confirmed thesis (revenue beat, EPS beat, guidance raised)
- Recent governance / catalyst positive
- Forensic clean
- Sector peers in line

User considers adding to the position because:
- Margin of Safety improved from 27% → 29%
- Reverse DCF now shows -15.8% implied perpetual decline (market priced for severe distress)
- "Average down" emotional pull strong

---

## Why "Price Drop" Looked Tempting

| Metric | At Entry | After Drop |
|---|---|---|
| Price | $P (cost basis) | $P × ~0.93 |
| MoS | ~26% | ~29% |
| Reverse DCF implied | ~-8% growth | ~-16% growth (more pessimistic) |
| Pre-committed add zone | <$P × 0.88 | unchanged (NOT yet hit) |

**Surface analysis**: Better MoS, larger expectation gap → "buy more" temptation.

**Framework discipline**: Pre-committed add trigger NOT yet met. Position already over Tier 2 cap.

---

## V4.2 Framework Application

### V4.1 Auto-VETO Triggers (5 checks)

```
1. Position size > Tier cap
   Current concentration: ~50% of portfolio
   Tier 2 cap: 8%
   → 🔴 AUTO-REJECT for new buy

2. Organic decline 連 2Q
   8Q history: all positive 4-6%
   → ✅ NOT triggered

3. GAAP/Non-GAAP gap > 30%
   ~12% gap
   → ✅ NOT triggered

4. Securities lawsuit
   Clean
   → ✅ NOT triggered

5. Reverse DCF heroic
   -15.8% implied (pessimistic, NOT heroic)
   → ✅ NOT triggered
```

**Result**: 1 of 5 triggers fired (position size). **Auto-VETO binding for new buy regardless of MoS**.

### Phase 0.7 Data Quality Gate Re-Run

All 9 checks PASS — no fundamental data change since entry. Drop is pure sentiment/technical.

### 3-Judge Audit

```
Judge 1 (Fundamentals): HOLD, 80% confidence
Judge 2 (Risk):        HOLD, 85% confidence
Judge 3 (Discipline):  HOLD, 88% confidence

Aggregate: 0 PASS / 3 HOLD / 0 VETO
Decision: HOLD existing, DO NOT ADD
```

---

## Key Lessons (Cross-Reference Lessons Learned)

### Lesson 1: Concentration Cap Binding Even On Quality

V4.1 position size auto-VETO must override MoS opportunity. Mathematical risk concentration is independent of stock quality. Even top-decile ROIC + clean forensic + improving MoS does not justify violating Tier 2 cap.

> **"Diversification is protection against ignorance. It makes little sense if you know what you're doing."** — Buffett
>
> But: **Buffett has 100x your due diligence depth + 60 years pattern recognition**. Retail concentration cap is risk-asymmetry insurance.

### Lesson 2: Average Down Temptation = Sunk Cost Fallacy

NVO/BMY discipline 6 says "Kill sunk cost." When a position is down, the emotional pull to "average down" feels like:
- Lower average cost
- Faster breakeven
- Confirm conviction

But these are sunk-cost rationalizations. Forward decision must be standalone:
- Ask: "Given current data, would I buy fresh today at this price with this concentration?"
- Answer: "AUTO-VETO triggered. No."
- Therefore: No add.

### Lesson 3: Symmetric Discipline

Don't chase up (paying above limit price). Don't chase down (averaging on price drop). Both are emotional reactions. Pre-committed triggers only.

### Lesson 4: Price Action ≠ Fundamental Change

A 3.5% drop in 2 days with zero data point change is noise, not signal. **Fundamentals drive buy decisions, not price action**. If reverse DCF gets more pessimistic but business unchanged, the framework already accounts for this through MoS calculation — no emotional override needed.

### Lesson 5: Capital Opportunity Cost

When deciding to add to a winner-but-concentrated position vs deploying to a different thesis:
- Add to position with diminishing diversification return
- Vs add to new high-conviction position with hard catalyst

Risk-adjusted analysis usually favors diversification. Single-stock idiosyncratic risk in concentrated position dominates marginal MoS expansion.

---

## V4.2 Framework Validation

This stress test demonstrates V4.2 framework working as designed:

✅ **Phase 0.7 Data Quality Gate**: Re-runs without false positive (no flag where no change)
✅ **V4.1 Auto-VETO**: Binding when triggered, regardless of other favorable factors
✅ **Pre-committed triggers**: Honored over emotional override
✅ **Bull/Bear debate**: Bear wins on concentration discipline pillar
✅ **3-Judge Audit**: Independent confirmation of HOLD verdict

---

## Generalized Rule

**Price Drop Reaction Decision Tree**:

```
Stock drops X% from entry without fundamental change:

1. Re-run Phase 0.7 Data Quality Gate
   If PASS (no fundamental change): proceed
   If FAIL: re-evaluate full thesis

2. Check V4.1 Auto-VETO triggers
   If position size flag: HOLD, no add (regardless of MoS)
   If no flags: proceed

3. Check pre-committed add zone
   If price < pre-committed zone: small DCA per pre-commit
   If price in HOLD zone: hold, no action

4. Capital opportunity check
   If alternatives offer better risk-adjusted return: redirect
   If position is highest-conviction option: proceed per pre-commit

5. Behavioral check
   Ask: "Would I buy fresh today at this price?"
   If no: don't add (sunk cost trap)
   If yes: re-verify all 4 above first
```

---

## Application Beyond Single Trade

This discipline framework applies to any portfolio facing concentration vs opportunity tradeoff:

- **Index funds**: re-balancing on weakness when single stock exceeds target weight
- **Pension funds**: liability-driven sizing limits override quality conviction
- **Hedge funds**: risk parity constraints binding even on highest conviction trades

The principle is universal: **risk-adjusted optimization > unconstrained alpha-chasing**.

---

## Reproducibility

```bash
# V4.1 auto-VETO check function
python3 valuation_calc.py position_size '{"proposed_size_pct": 0.50, "conviction_tier": 2}'
# Output: auto_reject: true (50% > 8% Tier 2 cap)

# V4.2 reverse DCF
python3 valuation_calc.py reverse_dcf '{"current_market_cap": X, "fcf_year1": Y, "wacc": Z, "growth_terminal": W}'
# Output: implied_growth + base_rate_assessment

# Phase 0.7 Data Quality Gate
python3 data_quality_gate.py /path/to/data.json
# Output: 9-check verdict + flags
```

---

## Anonymization Note

This case study is shared as a public lesson on framework discipline. Specific portfolio details (position size, dollar amounts, ticker identity) are anonymized. The principle is what matters, not the specific trade.

The investor in this scenario chose to honor the pre-committed framework discipline and did not add at the lower price. The decision reaffirmed:
- V4.2 framework working as designed
- Pre-committed triggers binding
- Capital opportunity cost analysis correctly weighted

This is documented as a successful framework validation, not a successful trade prediction.
