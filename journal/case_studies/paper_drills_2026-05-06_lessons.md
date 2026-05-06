# 📒 Paper Trade Training Log

> Append-only log of lessons from each V4.0 paper drill.
> Cross-pollinate findings into `lessons_learned.md` (real portfolio) when patterns emerge.

---

## 2026-05-06 — Initial Pool Setup + 3-Drill Stress Test

**Setup**: Build separate paper_trades pool independent from real portfolio decision_log.

**Initial drills**:
1. ✅ ADBE — Expected PASS — Result: PASS (3/3 judges)
2. ✅ TJX — Expected VETO — Result: VETO (auto-VETO + 3/3 judges)
3. ✅ HSY — Expected BORDERLINE — Result: BORDERLINE (1 PASS / 2 FLAG)

**All 3 expected outcomes matched. Framework prediction accuracy: 100% on prescribed cases.**

---

## Drill Lessons (cumulative)

### From ADBE drill (PASS path)

1. **V4.1 Position Cap function 直接 catch sizing error** — 原計劃 $3K = 14% of $20K portfolio, Tier 2 max 8% → auto-flag (not VETO) requires resizing. Correct behavior — trade still executable at $1.6K.

2. **Reverse DCF reveals largest expectation gap** — ADBE market implies 2.6% growth; realistic 11% × 5 years. Gap = 8.4% per year underpriced. **Reverse DCF 係 alpha source detection 嘅最 powerful tool**.

3. **Bull/Bear Debate 直接帶出 NVO/BMY 6 條紀律** — Bear automatically cite Pillar 1 (moat expiry from AI) + Pillar 3 (numbers > narrative on growth fade). Discipline working.

4. **Wide moat + 26% borderline MoS = sizing 控制風險，唔係 reject trade** — Tier 2 cap 8% = 正確 risk management without rejecting positive-EV trade.

### From TJX drill (VETO path)

5. **VETO triggers 唔需要 debate** — Negative MoS + position size 違規 = auto-VETO 直接 reject。**呢個係 V4.1 design 嘅 win** — 防止 quality narrative 蒙蔽 valuation discipline.

6. **Wide moat + clean forensic ≠ BUY signal** — TJX 全部 quality check pass（ROIC-WACC 24.5% spread, σ stable, capital allocation A），但 -24% MoS 直接 disqualify. **Quality 同 valuation 係兩個 independent gate**.

7. **Sector-adjusted base rate matters** — Cross-market base rate 12% = top 25%; retail sector base rate 12% = top 5-10%. **Reverse DCF 必須對返 sector，唔係 cross-sector**.

8. **Mean reversion math 係 silent killer** — 即使 thesis growth 全對，valuation compression（31x → 22x）抵銷 growth → annualized return -5% to 0%. **Quality 喺貴價買 = expensive way to lose money**.

9. **Anti-portfolio integration** — TJX added to anti_portfolio.md → 6/12 個月後 audit framework call.

### From HSY drill (BORDERLINE path)

10. **BORDERLINE outcome 係 framework 最重要 design** — Phase 9 嘅 24-hour cool-down 防止 borderline 被 emotion 推 over edge. **HSY drill confirm mechanism work**.

11. **Specific catalyst override of V4.1 auto-flag = case-by-case judgment** — 唔係 "rebuttable presumption"，係 high bar to override. Judge 2/3 拒絕 override = 正確 conservatism.

12. **Sector-wide pattern matters more than stock narrative** — KO/PG/KHC 同樣 organic decline → 唔係 HSY-specific recovery story，係 sector reset. Useful lens.

13. **Asymmetric reward 唔等於 BUY signal** — -15% / +30% 數學 attractive，但 3-year horizon + uncertain timing = annualized 7-10% expected return. **Capital opportunity cost matters**.

14. **Cross-decision dependency awareness** — Judge 3 proposed wait until 5/8 BAM results before allocating to borderline trade. Real portfolio decisions 互相影響 cash position.

---

## 🎯 Aggregate Insights (3 drills)

### Framework Validation
- ✅ Phase 0.5 Forensic catches all 3 stocks（all clean — no false positives）
- ✅ Phase 4.5 Sanity Bounds catches TJX multiple FAIL
- ✅ Phase 6.5 Bull/Bear properly differentiated outcomes
- ✅ Phase 9 Final Action Gate + Auto-VETO triggers work as designed
- ✅ V4.1 new functions（GAAP gap, position cap, organic check, reverse DCF）all activated correctly

### Decision Quality Gates Order of Importance
1. **Auto-VETO triggers** (negative MoS, position cap, lawsuit) — fastest, highest signal
2. **Phase 4.5 Sanity Bounds** (multiples extreme, growth heroic) — catches outliers
3. **Phase 6.5 Bull/Bear** — primary discipline against narrative bias
4. **Phase 9 Judge Audit** — final independent check before execution

### Most Surprising Finding
**Reverse DCF reveals which stock has biggest mispricing, not which stock has biggest MoS**.

ADBE 26% MoS but 8.4% implied growth gap = highest conviction.
HSY 23% MoS but 1.5% implied growth (already pessimistic) = market already partially priced.
TJX -24% MoS + 12% implied growth (heroic for retail) = market priced for perfection.

**呢個 reframes "MoS" 為 "expectation gap"**.

### Pattern Watch
- [x] Bull/Bear debate over-weighting Bear bias? **NO** — ADBE Bull dominated, TJX Bear dominated, HSY genuinely tied
- [x] Phase 9 judges agreeing too often (groupthink)? **NO** — HSY had split decision (1 PASS / 2 FLAG)
- [x] Forensic Phase 0.5 missing real signals? **NA** — all 3 clean, no test of real signal
- [x] Sanity bounds catching real outliers? **YES** — TJX caught immediately

---

## ➡️ Next Drill Candidates

When ready for next batch of paper drills:

| Suggested | Rationale |
|---|---|
| **MA / V** | Wide moat at fair value — test "no MoS but quality" decision |
| **NSRGY** | International staples — test cross-currency / non-US logic |
| **CPRT** | High-quality at low MoS — test edge case |
| **GOOGL** | Active legal case — test forensic Phase 0.5 with real signal |
| **MSCI** | Premium-priced wide moat — test discipline against quality bias |

---

## 🔄 Last Updated

- 2026-05-06: Initial 3 drills completed, all expected outcomes matched
- Next drill: TBD（建議 weekly cadence on watchlist names）
