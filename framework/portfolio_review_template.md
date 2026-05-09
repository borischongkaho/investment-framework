# Portfolio Review — boris v4.2 Advanced Template

> **Purpose**: Canonical layout spec for portfolio-level reviews (the orchestration deliverable that synthesizes per-stock v5 reports).
>
> **Companion to**: `framework/v42_advanced_report_template.md` (per-stock 17-section template).
>
> **Used by**: `/invest-portfolio` skill (Monthly Deep Review section). Per-stock reports stay in v4.2 17-section format; the portfolio-level synthesis follows THIS template.
>
> **Invariants**: Three-layer explanation pattern (係咩 / 影響 / 類比) for every major decision · Status emojis (🔴🟠🟡🟢) for thesis flags · Concrete trade actions with limit prices · Calendar catalysts table · Multi-option action plan (選項 A / B / C) · Explicit follow-up questions

---

## Output Language

繁體中文廣東話口語 throughout. English ticker / financial-term inserts (e.g. P/V, MoS, GAAP gap, reverse DCF heroic) are OK because they are framework-specific terms.

NEVER write in Mandarin or formal Chinese — boris-style is conversational Cantonese.

## Structural Skeleton (mandatory sections)

```
═══════════════════════════════════════════════════════════════════════
📋 FULL PORTFOLIO REVIEW — YYYY-MM-DD
   Framework: ACCT6111E v5 hardened (subsumes v2.0 + v3.0 + v4.0/4.1/4.2)
   Scope: N 個股 full v5 pipeline + N ETFs thematic
═══════════════════════════════════════════════════════════════════════

## 🚨 決策卡 (Executive Summary)

[組合總值 / 成本 / P/L 三行]

**但結構性問題嚴重：**

| 指標 | 你而家 | Framework Limit | 狀態 |
| ... 至少 5-7 行：position count, sector concentration, tier cap, fragmentation, Phase 9 PASS rate ... |

### 🔴 Forensic + Phase 9 出 N 個 IMMEDIATE-SELL trigger 表
[ticker / trigger / weight / P/L / 行動]

### 🟠 N 個大贏家 lock-in 鎖盈 trim
[bullet list of winners with P/L%]

### 🟢 最高 conviction HOLD
[bullet list]

---

## PART A — 結構性診斷 (Structural Diagnostic)

### A.1 持倉太多 — Fragmentation
- 三層解釋（係咩 / 影響 / 類比）
- 細倉表（< USD $3K min size）

### A.2 行業集中度
- Sector exposure table
- Sub-cluster 拆解（特別 Tech sub-clusters）
- 三層解釋 if any cluster > limit

### A.3 集中度沒有問題嘅地方
- Quick reaffirmation

### A.4 v5 Position Sizing + Validation 健康度評分
- Pass/fail table for 6-7 hard checks
- Final score line

---

## PART B — 🔴 法證篩查緊急發現

每個 IMMEDIATE-SELL 名 (FIG / GME / 8448 / TER / ARM / etc.) 寫一個 sub-section:

### B.N {TICKER} ({Name}) 🔴 {SHORT-REASON}
**v5 Phase 9: {VETO/BORDERLINE/CONDITIONAL}** • V4.1 #N triggers fired • Forensic 🔴/🟠/🟡

[項目表 / 詳情]

**Thesis Status**: 🔴 BROKEN / WEAKENING / etc.

**第一層（係咩）**：[what is happening — framework-level finding]
**第二層（影響）**：[impact on user's portfolio specifically — HKD amount, weight, P&L]
**第三層（類比）**：[reference case from lecture / historical analog — Lecture 6B, 7, 9a, 9b, Outsiders, Mauboussin, NVO/BMY]

**🎯 Action**: SELL N sh / TRIM N sh / etc.
- 限價 USD ≥ X / HKD ≥ Y
- 釋放 HKD Z
- [other execution detail]

---

## PART C — 各 Cluster 持倉檢視 (Per-Cluster Detail)

組織 by cluster:
- C.1 Tech / AI Cluster — sub-clusters: AI Software, AI Hardware, Mature Semi, SaaS/Internet, HK AI
- C.2 Precious Metals + Mining
- C.3 Energy Cluster
- C.4 Auto / EV
- C.5 Index ETFs
- C.6 Special Situations / Cleanup

For each stock:
```
#### {flag emoji} {TICKER} — {wt}% — {THESIS STATUS}

**v5 Phase 9: {verdict}** • V4.1 #N fired • Forensic {color}

- N 股, entry HKD X → HKD Y, +/-Z%, +/-HKD W
- Current USD A / HKD B
- Intrinsic USD C / HKD D
- **MoS X%**

[For BIG decisions only — TRIM ≥30%, SELL, or HOLD-with-major-trigger:]
**第一層（係咩）**：framework finding
**第二層（影響）**：portfolio impact in HKD
**第三層（類比）**：lecture analog

**🎯 Action**: {recommendation}
- 限價, 釋放 HKD, etc.

**Triggers to monitor:**
- 🔴 hard sell trigger 1
- 🔴 hard sell trigger 2
- 🟠 watch trigger
- 🟢 add zone trigger
```

---

## PART D — 5-Pillar Reconciliation (Bull vs Bear)

| Pillar | Bull Strength | Bear Strength | Net Winner |
|---|---|---|---|
| AI Hardware/Software | ... | ... | ... |
| Precious Metals | ... | ... | ... |
| Energy/Power | ... | ... | ... |
| Mature/Underperformers | ... | ... | ... |
| Fragmentation Risk | ... | ... | ... |

**Aggregate Verdict**: [synthesis paragraph]

---

## PART E — 行動計劃 (Action Plan)

> **執行時機 handoff**: 行動計劃出 limit price 係 thesis 嘅答案（呢個價值得 trim/sell 嗎），唔係 timing 嘅答案（而家市價落 vs 等 technical pullback）。對於每個 SELL/TRIM 行（特別係 winner lock-in），用 `/trade-timing TICKER` 攞 live TA + R:R + reclaim/support level，再決定執行嗰刻嘅 timing。本 template 唔出 entry/stop/target with R:R math — 嗰個係 `/trade-timing` skill 範圍。

### E.1 即時 SELL（呢一兩個禮拜內，Tier 1 priority）
| # | Ticker | Qty | 限價 | 預期收回 HKD | 理由 |
| every row has limit price + HKD released + reason |
| **小計** total |

### E.2 戰術 TRIM（鎖盈 + sector rebalance）
[same row format]

### E.3 戰術 CONSOLIDATE（簡化）
[ETF swaps, holding count reductions]

### E.4 結果預期
| 指標 | Before | After | 改善 |
| effect of E.1+E.2+E.3 |

### E.5 Cash Deployment Options
- 選項 A: cash reserve
- 選項 B: top-conviction add
- 選項 C: T-bills/screen

---

## PART F — 監察觸發點

### F.1 Hard Sell Triggers (per ticker)
| Ticker | Hard Trigger |

### F.2 Sector Concentration Triggers

### F.3 Macro Triggers
- Fed pivot, USD, VIX, real yields, China PMI

### F.4 Calendar Catalysts (next 90 days)
| Date | Event | Tickers Affected |

---

## PART G — Framework Compliance Check

### v5 Hardened Validation Gates
| Gate | Status |
| Phase 0.5, 0.7, 4.5, 7, 9, V4.1 etc. — pass/fail per gate |

### ACCT6111E 課程 Reference
| 框架 / Lecture | 應用 |
| Lecture 6B EPV / 7 cyclicals / 9a competitive advantage / 9b investor behavior / Outsiders / Mauboussin / NVO/BMY 6 |

---

## PART H — Critical Caveats & 假設聲明

Numbered list (10 items typical):
1. 價格時效
2. FX rate 假設
3. Cash position unknown
4. Entry thesis baseline
5. Per-stock v5 reports location
6. Missing data flags
7. Broker data inconsistencies
8. Country-specific accounting differences
9. Tax considerations
10. Trim execution timing risk

---

## 🎯 最終建議 (Final Recommendation)

### 選項 A：完整執行 (推薦)
[bullet list of effects + time frame + suitability]

### 選項 B：Phase Approach (保守)
[same]

### 選項 C：Forensic-Only (Minimum)
[same — note this option's gap]

### ✅ 我建議：[A / B / C]
[Reasoning paragraph with 4-5 numbered points]

---

## 📋 Next Steps (建議)

1. Set up portfolio.md baseline (if first review)
2. 建立 reviews/ folder
3. Confirm action items — execution scripts vs manual?
4. 後續跟進 (date-stamped events)
5. Deep DCF 候選

### 要唔要我：
- **(A)** 執行 checklist (Tier 1 / 2 / 3 ordered, with limit prices + dates)?
- **(B)** Specific ticker sensitivity (e.g. PLTR DCF stress test)?
- **(C)** Capital deployment search via /invest-source?
- **(D)** Set up quarterly v5 light auto-review?
- **(E)** 跑 `/trade-timing` 對 top 3 trim names 攞 execution timing (entry/exit + R:R)?

---

**Sources** (real-time web data {DATE}):

- N 個個別 v5 reports 寫入 `data/research/full_reports/{DATE}_portfolio/{TICKER}.md`
- Per-stock 17-section format per `framework/v42_advanced_report_template.md`
- Forensic primary sources for IMMEDIATE-SELL names (lawsuit dockets, SEC filings, earnings PRs)
- Macro: Damodaran ERP, FRED H.15 RF, Mauboussin S&P 1500 base rate, USD/HKD FX

---

**下次 review**: {DATE + 90 days} (quarterly v5 light) 或更早 if any V4.1 hard trigger fires
```

---

## Three-Layer Explanation Pattern (CRITICAL)

For every major decision (IMMEDIATE-SELL, TRIM ≥30%, structural breach, big winner lock-in), use this exact 3-paragraph pattern:

**第一層（係咩）**: What the framework flagged. Quote the v5 trigger / gate / threshold. Cite specific finding (GAAP gap %, reverse DCF implied g%, MoS%, Phase 9 verdict).

**第二層（影響）**: What this means for THIS specific portfolio. HKD position, weight, P/L. The "your money" angle.

**第三層（類比）**: A reference analog from the curriculum or market history. Specific lecture (e.g. "Lecture 6B EPV"), specific historical case (e.g. "Valeant 2015", "Apple 2013", "Sears post-turnaround"), or framework rule (e.g. "Outsiders capital allocation principle", "NVO/BMY discipline #5 numbers vs narrative", "Mauboussin S&P 1500 base rate top 8% heroic").

If a decision is BIG enough to be in the report, it deserves the 3-layer treatment. Don't skimp.

## Status Flags Convention

- 🟢 INTACT: thesis fully valid, framework gates pass, MoS positive
- 🟡 INTACT-CAUTIOUS: thesis valid but no MoS / borderline / monitor
- 🟠 WEAKENING: thesis showing cracks, V4.1 triggers fired, requires action
- 🔴 BROKEN: thesis broken, IMMEDIATE-SELL or hard TRIM required

## V5 Integration Requirements

Every per-stock entry must include:
- **Phase 9 verdict**: PASS / CONDITIONAL / BORDERLINE / VETO
- **V4.1 triggers fired**: list which of #1 (position size) / #2 (organic decline) / #3 (GAAP gap) / #4 (lawsuit RED) / #5 (reverse DCF heroic)
- **MoS%**: computed vs intrinsic per Phase 7 Gate 7
- **Forensic color**: 🔴 RED IMMEDIATE / 🟠 ORANGE cap-at-HOLD / 🟡 MONITOR / 🟢 clean

These are MORE rigorous than v2.0/v4.2 portfolio review (which only used 6-question gate). Always integrate the v5 deeper findings into the boris-style layout.

## Forbidden Layouts

Do NOT produce:
- Clinical bullet-list dashboard with verdicts only (the user explicitly preferred boris layout)
- English-only or Mandarin output
- Recommendations without limit prices
- Action plan without phase-level prioritization (E.1 / E.2 / E.3)
- Final recommendation without 3-option trade-off (A / B / C)
- Closing without explicit (A)/(B)/(C)/(D) follow-up question menu

## Tooling

- Per-stock v5 reports: spawn parallel agents per ticker, each writes to `data/research/full_reports/{DATE}_portfolio/{TICKER}.md` using v4.2 17-section template
- Aggregate dashboard: synthesize using THIS template into `99_portfolio_dashboard.md` in same dir
- Top-of-project copy: `cp 99_portfolio_dashboard.md ./` for easy access
- Portfolio source of truth: `data/portfolio.md` (gitignored)

## Companion Skill — /trade-timing (absorbed, in-repo)

This template is the **thesis authority** (months/years horizon — "should this position exist at this size?"). For **execution timing** (hours/days horizon — "is THIS MOMENT a good entry/exit?"), hand off to the in-repo `/trade-timing` skill.

**When to invoke handoff**:
- After v5 produces a TRIM/SELL with limit price → user wants to know "now or wait for technical pullback?"
- For winner lock-in trims (e.g. +200%+ gainers) where R:R math + reclaim/support levels matter for execution
- Before executing big-size trims to verify TA isn't screaming "wait one day"

**How to invoke**:
- `/trade-timing TICKER` or "睇下 TICKER" / "can buy TICKER?" / "setup TICKER?" / "scan TICKER"
- Returns: live OHLC, MA/ATR context, exact R:R math, reclaim/support/avoid levels

**Authority boundary** (per "break down by function; unify authority at the gate"):
- This template = **thesis 權威**
- `/trade-timing` skill = **timing 權威**
- 兩個 gates 答唔同問題 — 唔好 conflate。 This template 從來唔會出 entry/stop/target with R:R math; `/trade-timing` 從來唔會出 5-year DCF / Phase 9 verdict.

**Cross-reference path**: `skills/trade-timing/SKILL.md`

**What NOT to do**: do NOT have this template (or `/invest-portfolio` / `/mba-valuation`) emit entry/stop/target with R:R. Do NOT create a unified gate that supersedes thesis + timing into one verdict — that re-introduces multi-engine conflict. Each skill keeps its own authority.

## Reference Implementation

The 2026-05-08 portfolio review is the canonical reference implementation. See:
- Aggregate: `data/research/full_reports/2026-05-08_portfolio/99_portfolio_dashboard.md`
- Sample per-stock: `GOOG.md`, `NVDA.md`, `PLTR.md` (full v5 17-section)
- Pre-analysis: `00_portfolio_overview.md`
- ETF combined: `98_etf_macro_view.md`

These are gitignored personal data; structure is reproducible from this template.
