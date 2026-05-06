# V4.2 Advanced Investment Report Template

> **Purpose**：Boris-readable，self-contained decision document。讀完一次就 enough info to decide。
> **Reading time target**：25-35 分鐘（trade off depth vs digestibility）
> **Language**：繁體中文 / 廣東話口語為主，technical terms 加英文 in parens
> **Audience assumption**：Boris 由零知識開始 → ending 有 conviction-grade decision

---

## 📐 Report Structure（17 Sections）

```
┌─ Section 1: Decision Card（1 page Executive Summary）
│
├─ PART A: UNDERSTANDING THE BUSINESS（讀完真係識間公司）
│  ├─ Section 2: Business Deep-Dive（5-min explanation + 30-sec recap）
│  ├─ Section 3: Industry & Moat Layers
│  └─ Section 4: Capital Allocation Track Record
│
├─ PART B: VERIFYING THE DATA（V4.2 NEW — show your work）
│  ├─ Section 5: Phase 0.7 Data Quality Gate Results（9 checks）
│  ├─ Section 6: Excel Input Mapping（13 ACCT6111E cells with sources）
│  └─ Section 7: Sentiment + Macro Read（5 indicators + Marks 7Q）
│
├─ PART C: THE NUMBERS（Excel-Faithful Transparent）
│  ├─ Section 8: Quality Profile（ROIC-WACC, σ persistence, reinvestment math）
│  ├─ Section 9: Three-Method Valuation（EPV / DCF / Multiples — full Excel cells）
│  ├─ Section 10: Sanity Bounds Check（Phase 4.5）
│  ├─ Section 11: Reverse DCF + Base Rate（Mauboussin lens）
│  └─ Section 12: Validation Gates（7 gates, hard rules）
│
├─ PART D: THE DEBATE（full transcripts）
│  ├─ Section 13: Bull Researcher Argument（long-form, evidence-cited）
│  ├─ Section 14: Bear Researcher Argument（NVO/BMY 6 discipline applied）
│  ├─ Section 15: Reconciliation Matrix
│  └─ Section 16: 3-Judge Audit（full opinions）
│
└─ Section 17: Final Decision Card + Action Triggers + Sources
```

---

## ✍️ Writing Guidelines Per Section

### Section 1 — Decision Card
- 1 table with: Current price, Intrinsic, MoS, Phase 9 verdict, Action, Size, Limit price
- 1-paragraph "thesis in plain language"
- Top 3 reasons + Top 3 risks (bullet points)
- Pre-committed exit triggers

### Section 2 — Business Deep-Dive
- **30-second recap**：你聽到呢個 ticker 第一個反應應該係咩
- **5-minute explanation**：點賺錢、business model 邊度 unique、收入點樣 flow
- **Customer journey example**：用 1 個 concrete user/customer 例子
- **Numbers that matter**：3-5 key metrics 用嘅 framework

### Section 3 — Industry & Moat Layers
- Industry structure (Porter 5 Forces 簡化版)
- Moat 分 4-5 layers，逐層拆：
  1. 最深嘅 moat（unbreakable）
  2. 第二層
  3. 第三層
  4. Erosion risks
- Moat rating: 🟢🟢 Wide / 🟢 Narrow / 🟡 Limited / 🔴 None

### Section 4 — Capital Allocation Track Record
- Outsiders framework apply：
  - Buyback timing（counter-cyclical?）
  - Dividend payout ratio
  - M&A track record (last 3 deals incremental ROIC)
  - Net debt trajectory
- Letter grade: A+ / A / B+ / B / C / D

### Section 5 — Phase 0.7 Data Quality Gate
- Show all 9 checks with raw data + PASS/FAIL
- Source citation for each

### Section 6 — Excel Input Mapping
- Table: Excel cell name → data value → source → verify date
- 13 cells minimum
- Highlight any cells with stale or estimated data

### Section 7 — Sentiment + Macro
- 5 sentiment indicators with current readings
- Marks 7Q macro lean (current period)
- Cycle position implication for this trade

### Section 8 — Quality Profile
- 10Y ROIC mean + σ
- Spread vs WACC
- Incremental ROIC (last 3-5 years)
- Reinvestment rate × Incremental ROIC = Organic growth math
- Persistence rating

### Section 9 — Three-Method Valuation
- **EPV calculation**: every input + Excel formula equivalent
- **Strict DCF**: Stage 1, Stage 2, Terminal (NOPAT × (1-g/ROI)/(WACC-g))
- **Multiples**: Peer comparables table, EPS forecasts, multiples range
- Reconciliation: weighted intrinsic + scenario sensitivities

### Section 10 — Sanity Bounds (Phase 4.5)
- WACC reasonable?
- Terminal growth ≤ GDP+?
- Margin assumptions vs sector peer?
- Stage 1 growth vs Mauboussin base rate?

### Section 11 — Reverse DCF
- Solve implied growth from current market cap
- Compare to: sector base rate, company history, peer assumption
- Asymmetric setup quantification

### Section 12 — Validation Gates
- 7 gates (V2.0 + V4.1) with PASS/FAIL each
- Auto-VETO triggers (V4.1 + V4.2) checked

### Section 13 — Bull Researcher Argument
- 600-1200 words 嘅 long-form bull case
- 3-5 cited evidence points
- Quantitative grounding (specific numbers, not vague)
- "If I had to bet on this stock for 5 years..." narrative

### Section 14 — Bear Researcher Argument
- 600-1200 words 嘅 long-form bear case
- NVO/BMY 6 discipline systematically applied
- Mauboussin base rate counter-argument
- Pre-mortem: 3 specific scenarios stock loses 30%
- Quantitative grounding

### Section 15 — Reconciliation Matrix
- 5-pillar matrix: Moat / Valuation / Growth / Quality / Catalyst
- Bull strength vs Bear strength per pillar (1-10)
- Net winner per pillar
- Aggregate verdict + uncertainty quantification

### Section 16 — 3-Judge Audit
- Judge 1 (Fundamentals): 200-word opinion + verdict
- Judge 2 (Risk): 200-word opinion + verdict
- Judge 3 (Discipline & Catalyst): 200-word opinion + verdict
- Numerical sanity check by each judge (separately)

### Section 17 — Final Decision Card
- Action: BUY / HOLD / TRIM / SELL / PAPER ONLY
- Size: $X (Y% of portfolio)
- Limit price + alternatives
- Time horizon
- Exit triggers (3 hard, 3 soft)
- Add zones (price + condition)
- Trim zones (price + condition)
- Catalyst calendar entries
- Sources cited

---

## 🎯 Format Rules

- **Tables over paragraphs** for data
- **Concrete numbers** > vague qualifiers
- **Hyperlinks to sources** in every section that uses external data
- **Cantonese narrative + English technical terms** (mixed naturally)
- **Three-layer explanation** for any complex concept
- **Visual hierarchy**: H2 for major sections, H3 for sub-sections, **bold** for key terms
- **No marketing tone** — Boris wants institutional-grade analysis
- **Self-contained** — reader 唔需要 follow-up questions

---

## 📊 Length Calibration

| Section | Target Words |
|---|---|
| 1. Decision Card | 200 |
| 2. Business Deep-Dive | 800 |
| 3. Industry & Moat | 600 |
| 4. Capital Allocation | 400 |
| 5. Data Quality Gate | 500 (mostly tables) |
| 6. Excel Input Mapping | 400 (table) |
| 7. Sentiment + Macro | 500 |
| 8. Quality Profile | 500 |
| 9. Three-Method Valuation | 1,200 (calc-heavy) |
| 10. Sanity Bounds | 200 |
| 11. Reverse DCF | 400 |
| 12. Validation Gates | 200 |
| 13. Bull Argument | 1,000 |
| 14. Bear Argument | 1,000 |
| 15. Reconciliation | 400 |
| 16. 3-Judge Audit | 800 |
| 17. Decision Card | 600 |

**Total target**: ~9,700 words ≈ 30-40 minutes Boris reading time

---

## 🎓 Versioning

- V4.0：Bull/Bear + Phase 9 introduced
- V4.1：Auto-VETO triggers + 5 new calc functions
- V4.2：Data Quality Gate + Excel-faithful mapping + this advanced report format
