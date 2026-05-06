# 🧪 Paper Trades — Training Pool

> **Purpose**: V4.0 framework training + stress-test，唔涉真錢。
> **Separation**: 完全獨立於 real portfolio (`~/Developer/investment/decision_log/decisions.json`)。
> **Data isolation**: 呢度 `paper_decisions.json` 唔混入 backtest scorecard。

---

## 🎯 Why Paper Trades?

1. **Framework polish**：每次 paper drill 跑齊 Phase 0.5 → 9，validate prompt design + decision tree
2. **Bias detection**：低 stake → emotion-free → 觀察 framework output
3. **Sample size acceleration**：Real trade limited by capital；paper unlimited iteration
4. **Education**：Mistakes 喺 paper 學，唔好喺 real money 學

---

## 🛡️ Hard Separation Rules

| Rule | Rationale |
|---|---|
| **Paper trades 永遠唔可以 input real `decisions.json`** | 防止 backtest scorecard 污染 |
| **Paper trades 唔影響 portfolio sizing / cash management** | 真實 capital 規劃唔受影響 |
| **Paper trade outcomes 用 `paper_decisions.json`** | 獨立 ledger |
| **Paper trade lessons 寫入 `training_log.md`** | Knowledge compounding |
| **Real trade 同 paper trade 唔可以同一日做（避免 confusion）** | Mental separation |

---

## 📂 Folder Structure

```
paper_trades/
├── README.md                          # 呢個 file
├── paper_decisions.json               # Separate ledger (PAPER mode only)
├── training_log.md                    # Lessons learned from each drill
├── YYYY-MM-DD_TICKER_OUTCOME_drill.md # Individual drill records
└── stress_test_index.md               # Cross-drill pattern tracking
```

---

## 📋 Drill Outcome Categories

| Outcome | Threshold | Action |
|---|---|---|
| **PASS** | Phase 9: 3/3 PASS | If real money: Execute |
| **CONDITIONAL** | Phase 9: 2 PASS + 1 FLAG | If real money: Execute + log disagreement |
| **BORDERLINE** | Phase 9: 1 PASS + 2 FLAG | If real money: 24hr cool-down + re-debate |
| **VETO** | Phase 9: any VETO | If real money: 24hr cool-down + skip |

---

## 🎓 V4.0 Training Drill Format

每個 drill markdown 包：

```
## 1. Setup (ticker, date, hypothesis)
## 2. Phase 0.5 Forensic
## 3. Phase 1-4 Valuation (Python calc references)
## 4. Phase 4.5 Sanity Bounds
## 5. Phase 6.5 Bull/Bear Debate (full transcripts)
## 6. Phase 9 Final Action Gate (3-judge audit)
## 7. Outcome + Confidence
## 8. Lesson Learned
## 9. Update training_log.md
```

---

## 📊 Drill Stress-Test Goals

每隻 paper trade 應該 stress-test 唔同 framework gate。我哋而家做 3 隻：

| Drill | Ticker | Expected Outcome | Stress-Tests |
|---|---|---|---|
| 1 | ADBE | PASS | Standard happy-path（3/3 PASS）|
| 2 | TJX | VETO | Overvalued auto-VETO logic |
| 3 | HSY | BORDERLINE | Bull/Bear edge case，24hr cool-down trigger |

---

## 🚀 Workflow Per Drill

```
1. Open drill template → fill setup
2. Phase 0.5: 10 forensic searches
3. Phase 1-4: input → valuation_calc.py → record output
4. Phase 4.5: auto-flag check
5. Phase 6.5: spawn 2 sub-agents (Bull / Bear) for debate
6. Phase 9: spawn 3 judges fresh-context audit
7. Compile drill markdown
8. Append paper_decisions.json
9. Update training_log.md with 1-2 sentence lesson
10. Cross-link in stress_test_index.md
```

---

## 📅 Cadence

- **Initial batch**：3 drills (ADBE / TJX / HSY) — done 2026-05-06
- **Ongoing**：每週 1-2 drill on watchlist names
- **Quarterly review**：累積 12+ drills 後做 framework audit
- **Real-trade prep**：真 buy 之前 24hr 必先做 paper drill（dress rehearsal）

---

## ⚙️ Last Updated

2026-05-06 — Initial pool setup + 3 stress-test drills (ADBE PASS / TJX VETO / HSY BORDERLINE)
