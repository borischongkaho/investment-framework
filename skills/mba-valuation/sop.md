# Valuation SOP — Phase 1-7 執行步驟

跟教授嘅 Excel 模型結構（SJM 範本 tab 1-9）做。每個 phase 完成之後 summarize 先 move on。

---

## Phase 1：Historical Financial Analysis

### 1.1 簡化 Income Statement
```
Sales
− COGS (含 D&A)
= Gross Profit
− SG&A
− Other Operating Exp
= EBIT
− Interest Expense (net)
= EBT
− Income Taxes
= Net Income
− Preferred Dividends
= Net Income to Common
```
**拆開 recurring vs one-time**，tech 公司 R&D 拆 25% maintenance / 75% growth。

### 1.2 簡化 Balance Sheet
```
OPERATING ASSETS:
  Operating Cash = min(Total Cash, 2% × Revenue)
  A/R, Inventory, Other Current, Net PP&E
  Goodwill & Intangibles, Other LT Operating

OPERATING LIABILITIES:
  A/P, Accrued, Other Current, Deferred Revenue

NON-OPERATING:
  Excess Cash, Marketable Securities, Investments

FINANCING:
  ST Debt, Current LT Debt, LT Debt, Preferred, Common Equity
```

Derived：
- **NWC** = Op Current Assets − Op Current Liab
- **IC** = NWC + Net FA + Goodwill + Other LT Op
- **Net Debt** = Total Debt − Excess Cash

### 1.3 Historical FCFF

**Top-Down：**
```
EBIT × (1−Tax) = NOPAT
+ D&A − CapEx − ΔNWC = FCFF
```

**Bottom-Up（cross-check）：**
```
Net Income + Interest×(1−Tax) = NOPAT
+ D&A − CapEx − ΔNWC = FCFF
```

兩方法要 reconcile（差異 < 5%）

### 1.4 5 年歷史 ratios
- **ROIC = NOPAT / IC(期初)** ← 最重要
- Du Pont：ROIC = (NOPAT/Sales) × (Sales/IC)
- Revenue CAGR、NOPAT CAGR
- Sustainable g = b × ROI
- FCFF Margin、CapEx/Sales、CapEx/D&A
- D/E、Interest Coverage

**輸出做 table**，每年一 column，每個 metric 一 row。

---

## Phase 2：Competitive Position

### 2.1 Peter Lynch Lifecycle
| Category | Valuation Approach |
|---|---|
| Fast Grower | Multi-stage DCF |
| Medium Grower | Simplified Proforma |
| Slow Grower | EPV, DDM |
| Turnaround | EPV + liquidation |
| Cyclical | Normalize over cycle |
| Asset Play | Asset-based, SOTP |

### 2.2 Porter 5 Forces
Rivalry / New Entrants / Supplier Power / Buyer Power / Substitutes —— 每個 rate Low/Med/High。越多 Low → 越寬 moat。

### 2.3 Moat Analysis
**Cost advantages**：scale、patents、government resources、organizational know-how
**Demand-side**：brand loyalty、switching cost、network effects、distribution dominance

**動態分析**（cyclical）：幾耐先會有新 entrant 進入，令 price 回歸 cost level？

---

## Phase 3：Cost of Capital (WACC)

### 3.1 Cost of Equity (CAPM)
```
re = rf + βe × ERP
rf = 10-yr US Treasury (FRED DGS10)
ERP = 5-6% (large cap) or Damodaran 最新
```

### 3.2 Beta
**Method A（主）**：60 個月 regression vs S&P 500
- R² < 0.15 → 用 Method B
**Method B（備）**：Peer group
1. 5-10 peers 嘅 βL、D/E、Tax
2. Unlever：βU = βL / [1 + (1−Tc)(D/E)]
3. Weighted average by market cap
4. Re-lever：βL = βU × [1 + (1−Tc)(D/E)_target]

**永遠 Blume adjust**：β_adj = 1/3 + 2/3 × β_raw
**Small-cap premium**：market cap < $2B → +3-4.7%

### 3.3 Cost of Debt
Weighted YTM by market value of each instrument。無細節就用 credit rating + rf + default spread。

### 3.4 WACC
```
WACC = (E/V)×re + (D/V)×rd×(1−Tc) + (P/V)×rp
```
**用市值做權重**，唔用 book value。

---

## Phase 4：Multi-Method Valuation

至少做 3 個方法，詳見 `methodology.md`：
- **EPV**（floor）
- **Simplified Proforma DCF**（主方法）
- **Multiples**（市場驗證）
- **EVA** 或 **3-Stage**（補充）

---

## Phase 5：Sensitivity + Scenarios

### 5.1 Two-variable table
Value/share across：
- WACC (±1%, ±2% in 0.5% increments)
- Terminal growth (0% to 4% in 0.5% increments)

### 5.2 Scenarios
| Scenario | Rev Growth | EBIT Margin | TG | WACC |
|---|---|---|---|---|
| Bull | +2% | +1-2% | +0.5% | −0.5% |
| Base | Consensus | Historical avg | 2-3% | Calculated |
| Bear | −2% | −1-2% | −0.5% | +0.5% |

### 5.3 Reverse DCF
```
g* = WACC − FCFF₁/EV₀
```
如果 g* > 名義 GDP → 市場 overvalue growth。

### 5.4 壓力測試問題
1. 競爭優勢 erode 快過預期？
2. 行業 cyclical downturn？
3. Management 策略改變？
4. Regulatory / tax 變化？

---

## Phase 6：Investment Decision

### 6.1 P/V Ratio
| P/V | Action |
|---|---|
| < 0.70 | Strong Buy |
| 0.70 - 0.85 | Buy |
| 0.85 - 1.15 | Hold |
| 1.15 - 1.30 | Trim |
| > 1.30 | Sell |

Minimum **20-30% margin of safety** 先 initiate position。

### 6.2 Catalyst
識別咩事件會 close price-value gap：earnings beat、new product、margin improvement、M&A、activist、sector rotation。

### 6.3 6-Question Quality Check
全部答 YES 先建議 BUY：
1. Investment thesis 清晰？
2. 2 句話講到 business model？
3. 明白 moat 點樣防止競爭 erode profitability？
4. 對 valuation model + inputs 有信心？margin of safety >20-30%？
5. 願意 hold 5+ 年？
6. Exit plan 有冇？

---

## Phase 7：Behavioral Bias Audit

| Bias | Countermeasure |
|---|---|
| Anchoring | 多方法 cross-validate |
| Confirmation | 主動搵 disconfirming evidence |
| Overconfidence | 闊 sensitivity range |
| Loss Aversion | Pre-defined exit rules |
| Recency | 5-10 年歷史平均 |
| Herd | Trust analysis，敢 contrarian |
