# Valuation Methodology — 5 個方法 + 點揀

教授 (Dr. Swaminathan) 嘅核心信念：**任何方法都有局限，所以要用至少 3 個方法 cross-validate**。

---

## 方法 1：Earnings Power Value (EPV) — 估值地板

### 公式
```
EPV (firm)  = Adjusted NOPAT / WACC
EPV (equity) = Adjusted EBIT × (1 − Tax) / Cost of Equity
```

### 核心假設
**零增長**。假設公司永遠停喺今日嘅盈利水平 → EPV 係保守地板。

### 調整 NOPAT
- **正常化** EBIT（用 cycle 平均，唔用 peak / trough）
- **R&D 拆分**：tech/pharma 公司 R&D 入面 25-30% 係維護性、70-75% 係增長性。EPV 要將增長性 R&D 加返落 EBIT
- **剔除 one-time items**
- **CapEx 只計 maintenance**

### 點解讀
| 條件 | 意義 |
|---|---|
| Market Price < EPV | 深度低估 —— 連零增長都唔肯畀 |
| Market Price ≈ EPV | Fair pricing，無 growth premium |
| Market Price > EPV | Market pricing in growth，要驗證 ROI > WACC |

### 幾時用
✅ 成熟穩定（SJM、PG、KO）
❌ 高增長（會嚴重低估）
❌ 負盈利（無得計）

### 經典案例
**NVIDIA**：EPV 零增長 = $112/股；10.4% growth = $899（接近市價）。教授用呢個示範 growth premium。

---

## 方法 2：Simplified Proforma DCF — 主力方法

教授 default。EPV 假設零增長嘅 limitation → Simplified Proforma 畀幾年快速增長後 fade 落 GDP 以下。

### 6 個 Sub-step

#### 2A：Revenue 預測
| 期 | 方法 | Source |
|---|---|---|
| Year 1-3 | 分析師 consensus | IBES / Yahoo |
| Year 4-5 | Fade toward industry / GDP | Industry analysis |
| Terminal | ≤ 名義 GDP (2-3%) | Max 5.3% |

**Critical rule**：Terminal 時 ROI = WACC（增長唔再創造價值）

#### 2B：Expense Ratios
5 年歷史平均做 baseline，調整規模經濟、M&A synergies、競爭壓力

#### 2C：Reinvestment
```
ΔNWC(t) = Sales(t+1) × [NWC/Sales 歷史] − NWC(t)
CapEx(t) = Sales(t+1) × [(Net FA+Intangibles)/Sales 歷史] − Net FA(t) + D&A(t)
```

#### 2D：D&A
```
D&A(t) = IC(t) × [D&A/IC 歷史]
```

#### 2E：Projected FCFF
```
NOPAT = (Sales − COGS − SG&A − D&A) × (1 − Tax)
FCFF = NOPAT + D&A − CapEx − ΔNWC
```

#### 2F：內在價值
```
EV = Σ FCFF(t)/(1+WACC)^t + TV/(1+WACC)^T
TV = NOPAT(T+1)/WACC                         (當 ROI = WACC)
OR = NOPAT(T+1)(1−g/ROI)/(WACC−g)           (當 ROI > WACC)

Equity = EV + Excess Cash − Debt − Preferred
Per share = Equity / Diluted Shares
```

### Sanity checks
- TV 應佔 EV **40-60%**，>70% 即 forecast period 太短
- Top-down FCFF ≈ Bottom-up FCFF（<5% 差異）
- 終期 ROI 收斂到 WACC

---

## 方法 3：Valuation by Multiples

```
Target Value = Median(Comparable Multiples) × Target Metric
```

### Peers 揀選（4-8 間）
同行業、相似增長、相似 margin/ROIC、相似 beta/leverage、相似 size (0.5x-2x)

### 主要 multiples
| Multiple | 主要 driver | 相關性 |
|---|---|---|
| P/E | Earnings growth | ~30% |
| P/B | ROE | ~69%（最高） |
| P/S | Profit Margin | ~60% |
| EV/EBITDA | EBIT growth | 行業標準 |
| EV/Sales | Operating margin | 適合無盈利 |
| EV/IC | ROIC | 適合資本密集 |

### 注意
- 用 **median** 唔用 mean
- 範圍用 25th-75th percentile
- M&A transaction multiples 含 control premium 20-40% + synergy，要 adjust

---

## 方法 4：3-Stage FCFF Model — 詳細 DCF

當 5 年 explicit forecast 唔夠（e.g. Tesla）：

```
Stage 1 (Year 1-2)：高增長
  g₁ = 分析師預測, b₁ = 歷史 reinvestment

Stage 2 (Year 3-16)：Exponential transition
  g(t) = g(t-1) × EXP[1/(T-2) × LN(g_T/g₁)]
  b(t) = b(t-1) − (b₁−b_T)/(T-2)
  ROI fades linearly → WACC

Stage 3 (Year 16+)：Steady state
  g = 2-3%, ROI = WACC
  TV = NOPAT(T+1)(1−g/ROI)/(WACC−g)
```

幾時用：✅ Tesla / Amazon 早年；❌ 成熟公司（過度設計）

---

## 方法 5：EVA / Discounted EVA — 補充視角

```
Firm Value = IC₀ + Σ EVA(t)/(1+WACC)^t + Terminal EVA/(1+WACC)^T
EVA(t) = (ROIC(t) − WACC) × IC(t-1)
```

數學上同 DCF 等價，但拆解做：已投入資本 + 未來超額回報。可即時睇到公司有冇 destroy value（EVA < 0 即係跑輸 cost of capital）。

### EVA 改善 3 個途徑
1. 提高 ROIC
2. 投更多 capital 落 ROIC > WACC 項目
3. 清算 ROIC < WACC 資本

---

## 方法揀選矩陣

| 公司類型 | 主方法 | 副方法 | 唔用 |
|---|---|---|---|
| **成熟穩定** (SJM, PG) | Simplified Proforma | EPV + Multiples | 3-Stage |
| **高增長有盈利** (Apple 2013, NVIDIA) | Simplified Proforma + 3-Stage | EPV (floor) + Multiples | — |
| **高增長無盈利** (Tesla 2020) | 3-Stage DCF (long forecast) | EV/Sales multiples | EPV, P/E |
| **週期性** (MEMC) | Normalized EPV (mid-cycle) | DCF with cycle | Trailing P/E |
| **困境** (TER) | EPV + Liquidation | DCF if turnaround plan | Multiples |
| **資產密集** (REIT) | Asset-based + EV/IC | DCF | P/E |
| **金融機構** | Residual Income + P/B | DDM | FCFF |
| **私營小企業** (Wazup) | EPV + Multiples (peer-derived) | 簡化 DCF | 3-Stage |

---

## 教授金句

1. **「Valuation is mechanical, value investing is a complete process」**
2. **「Not all growth creates value」** — 只有 ROI > WACC 先有意義
3. **「Terminal value should be 40-60% of EV」** — >70% forecast period 唔夠長
4. **「Margin of safety 20-30% minimum」**
5. **「The investor's chief problem is likely to be himself」** — Graham
