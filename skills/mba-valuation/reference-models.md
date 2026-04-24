# Reference Models — 教授 6 個案例

每次做新 valuation 之前，揀 1-2 個最相似嘅 reference case 做類比。教授嘅 Excel 模型放喺 `/Users/borischong/MBA/2024R3 Business Valuation and Analysis (ACCT6111E)/` 入面。

---

## 1. SJM (J.M. Smucker) — 成熟穩定嘅 Gold Standard

**檔案**：`week1/SJM_Valuation_2024_1 (1).xlsx`（35 個 tabs）
**類型**：Medium Grower，零售食品（咖啡、寵物食品、consumer foods）
**教授用嘅方法**：Simplified Proforma DCF（主方法）+ EPV（floor）+ Multiples

### Key 數字
- WACC = 7.2%（re 9.74%、rd 2.84%、E/V 68%、D/V 32%）
- 內在價值 ≈ $118/股
- P/V ≈ 1.02（fairly valued）
- Terminal Value 佔 EV 50.1%（✅ 健康）

### 幾時 reference SJM
✅ 成熟、穩定、可預測嘅 cash flow business
✅ 想示範 Simplified Proforma 完整流程
✅ 可比對象：Wazup 長期穩定之後嘅狀態、The Station cafe business、任何 F&B

### Excel tab 結構（範本）
`1. Hist FCF` → `2. CAPM Regression` → `3. Peers Group` → `4. Cost of Debt` → `5. WACC` → `6. Earnings Forecasts` → `7. Equity Val` → `8. Firm Val` → `9. EPV` → `Simplified Proforma` → `Summary Valuation`

**呢個 tab 順序係教授嘅 canonical 流程**，任何新 case 都跟呢個結構。

---

## 2. Apple (2013) — 被忽略嘅價值機會

**檔案**：`week5/Apple_Valuation_2013.xlsx`、`week6/Apple_Valuation_2013(1).xlsx`
**類型**：Fast Grower 但市場當佢係 Slow Grower
**教授教咩**：即使係 Apple 都有被錯價嘅時候

### Key insight
2016 年 Apple P/E 只有 12（S&P 500 = 23），巴菲特首次買 Apple。到 2024：
- 股價 × 6.5
- EPS × 2.8
- P/E 由 12 → 28

### 教訓
**「Growth is embedded as an option」** —— 市場 2016 時無 price in Apple 嘅生態系統 lock-in 同 services 增長。呢啲 growth option 當市場未 recognize 嘅時候，就係最好嘅 entry point。

### 幾時 reference Apple 2013
✅ 分析被市場低估嘅大型成熟公司
✅ 睇市場係咪 underprice growth option
✅ 科技公司嘅 moat + services transition

### 關鍵方法
Simplified Proforma + EPV with R&D adjustment（Apple 嘅 R&D 75% 算 growth R&D，要加返 EBIT）

---

## 3. Tesla (2023) — 高增長估值嘅挑戰

**檔案**：`week8/TSLA_Valuation_2023.xls`、`week8/TSLA_Valuation_2023 pacc mba.pdf`
**類型**：Fast Grower，EV industry
**教授教咩**：點處理高增長 + margin 收斂 + 競爭加劇

### Key 數字
- Revenue $27B → $61B
- R&D/Sales 由 27.2% 降到 14.2%（規模經濟）
- EBIT margin 顯著改善

### 估值挑戰
1. 增長率可持續幾耐？
2. Margin 會點 converge？
3. BYD、legacy OEM 競爭加劇點影響？

### 方法
**3-Stage DCF（長 forecast period 10-15 年）**，EPV 唔適用，要用 EV/Sales 而唔係 P/E。

### 幾時 reference Tesla
✅ 高增長、margin 仲喺改善中
✅ 有顛覆性技術但競爭快速進入
✅ 科技 / EV / 新能源 / biotech growth names

---

## 4. ITW — Capital Efficiency 範例

**檔案**：`week2/ITW_Valuation_2024_Inputs (2).xls`
**類型**：多元化工業（Illinois Tool Works）
**教授教咩**：WACC 計算 + 多 segment 嘅 valuation

### 幾時 reference ITW
✅ 多 business segment 公司（要用 Segment Proforma）
✅ 資本密集但 high ROIC 嘅工業公司
✅ 示範 Cost of Capital 細節計算

---

## 5. MEMC — 週期性行業陷阱

**檔案**：`week7/MEMC/MEMC_EPV_DCF (1).xlsx`（28 個 tabs，極詳細）
**類型**：Cyclical（多晶矽晶圓）
**教授教咩**：週期性行業嘅高利潤係暫時嘅

### 核心 insight
2005-2008：太陽能補貼令需求激增、價格飆升、MEMC 利潤暴漲 → 估值表面好高
**但**：高回報吸引 new entrants → 新產能進入 → 價格回歸 cost → 經濟利潤消失

### 教授嘅關鍵問題
1. 短缺持續幾耐？
2. 高價維持幾耐？
3. 邊間公司有可持續 cost advantage？

### 方法
- **Normalized EPV**：用 mid-cycle margins，唔好用 peak
- **15-yr WACC DCF** with explicit cycle assumptions
- **唔好**用 trailing P/E（會被 peak earnings 誤導）

### 幾時 reference MEMC
✅ 商品型行業（steel、chemicals、shipping、semiconductor wafer、solar、oil & gas）
✅ 目前處於 peak 嘅公司
✅ 需要問「supernormal return 可維持幾耐」嘅情況

---

## 6. Trump Entertainment Resorts (TER) — 困境企業

**檔案**：`week5/TRE Case/HW 4 TER_EPV_DCF_LS_BSens (1).xlsx`
**類型**：Distressed / Turnaround
**教授教咩**：破產邊緣嘅公司點估值

### 方法組合
1. **Liquidation value**（asset-based）做絕對 floor
2. **EPV with normalized earnings** 做 base case
3. **DCF** 只有喺有明確 turnaround plan 先用
4. **Long-Short Strategy** tab：示範點 pair trade

### Sensitivity 特別重要
TER 範本有 **Balance Sheet Sensitivity** tab，因為 distressed case 嘅 asset value 可能大幅 writedown。

### 幾時 reference TER
✅ 高債務、negative cash flow 公司
✅ 有 turnaround 可能性但極高風險
✅ Deep value / special situation investing

---

## 揀 Reference Case Decision Tree

```
公司類型？
├── 成熟穩定 cash cow → SJM
├── 大型成熟但被低估 → Apple 2013
├── 高增長未成熟 → Tesla 2023
├── 多 segment 工業 → ITW
├── 週期性 / commodity → MEMC
└── 困境 / turnaround → TER
```

**永遠喺答案入面標明**：「呢個 case 我 reference 咗教授嘅 [case name]，因為 [相似原因]」

---

## 新 case 點攞教授嘅 Excel 結構

當需要為新公司（e.g. NVIDIA、Wazup）建立 valuation model：

1. **copy SJM 嘅 tab 結構**（最 canonical）
2. **適當時 borrow 特殊 tab**：
   - 高增長 → 加 Apple 嘅 `15-yr Firm DCF Expo`
   - 週期性 → 加 MEMC 嘅 `table14`（normalized EPV）
   - 困境 → 加 TER 嘅 `Balance Sheet Sensitivity`

3. **用 Python (openpyxl) 讀現有 Excel** 做 reference：
```python
import openpyxl
wb = openpyxl.load_workbook('week1/SJM_Valuation_2024_1 (1).xlsx', data_only=False)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    # inspect cells, formulas
```
