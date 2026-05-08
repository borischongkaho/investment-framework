# Investment Framework

> **Current Version**: V4.2 hardened (2026-05-08)
> **Methodology**: CUHK MBA ACCT6111E (Dr. Bhaskaran Swaminathan)
> **Status**: Production-ready, backtest-validated

Systematic value investing framework with **forensic screening, data quality gates, Bull/Bear debate, and 3-judge final action audit**. Built on Claude Code skills + Python framework code.

---

## 🏗️ 3-Layer Architecture

```
┌──────────────────────────────────────────────────────┐
│  Layer 1 (PUBLIC, this repo)                          │
│  - Framework methodology + Python lib                 │
│  - Skills (Claude Code)                               │
│  - Tests + anonymized case studies                    │
│  - FORK-FRIENDLY for personal use                     │
└─────────────┬────────────────────────────────────────┘
              │
              │ pip install / git clone
              ↓
┌──────────────────────────────────────────────────────┐
│  Layer 2 (PRIVATE, your fork)                         │
│  - Your portfolio.md                                  │
│  - Your decision_log/                                 │
│  - Your research reports/                             │
│  - Your journal/ (lessons learned)                    │
└─────────────┬────────────────────────────────────────┘
              │
              │ Reads framework + your data
              ↓
┌──────────────────────────────────────────────────────┐
│  Layer 3 (PRIVATE, optional)                          │
│  - Telegram bot                                       │
│  - Hermes scheduled agent                             │
│  - VPS deployment                                     │
└──────────────────────────────────────────────────────┘
```

See [`VERSION.md`](VERSION.md) for full version history.

---

## 📐 Framework Highlights (V4.2)

### Phase 0.5 — Forensic Screening
10 mandatory web searches before any valuation:
- Securities class action / SEC / DOJ investigations
- Accounting restatement / Going concern auditor
- CEO/CFO change last 12 months
- Guidance miss/cut / Earnings restatement

### Phase 0.7 — Data Quality Gate (V4.2 NEW)
9 mandatory checks via `framework/data_quality_gate.py`:
1. Data Currency (10-Q < 90 days)
2. Guidance Currency (no post-10Q changes)
3. Earnings Call Transcript reviewed
4. Organic Revenue 8Q (V4.1 auto-AVOID if 2+ negative)
5. Operating Margin 5Y trend
6. Capital Structure components
7. GAAP/Non-GAAP gap (V4.1 flag if > 30%)
8. Owner Earnings reconciliation (Buffett lens)
9. Sector Peer Cross-Check (V4.2 NEW)

### V4.1 Auto-VETO Triggers
5 hard rules (codified in `framework/valuation_calc.py`):
1. Position size > Tier cap (8% Tier 2, 12% Tier 1)
2. Organic revenue YoY < 0 for 2+ consecutive quarters
3. GAAP/Non-GAAP gap > 30% sustained
4. Active securities fraud lawsuit (Phase 0.5 detected)
5. Reverse DCF implied growth > sector top decile

### V4.0 Bull/Bear Debate (Phase 6.5)
2 sub-agents debate independently:
- **Bull**: 600-1200 word long-form bull case
- **Bear**: NVO/BMY 6 disciplines applied (moat expiry, price≠quality, numbers>narrative, yield trap, ROIC-WACC, kill sunk cost)
- Reconciliation matrix (5 pillars)

### V4.0 Phase 9 — Final Action Gate
3-judge fresh-context audit before real-money commit:
- Judge 1: Fundamentals
- Judge 2: Risk
- Judge 3: Discipline & Catalyst

Decision rule:
- 3 PASS → Execute
- 2 PASS + 1 FLAG → Execute with note
- 1 PASS + 2 FLAG → 24-hour cool-down
- Any VETO → Mandatory cool-down + skip

### Default Assumptions Lock (D1-D7)
- **D1**: Terminal formula `NOPAT × (1-g/ROI)/(WACC-g)` ALWAYS
- **D2**: Terminal growth 2.5% default, 3.0% hard cap
- **D3**: WACC floors — 7% large-cap / 8% mid / 9.5% small
- **D4-D7**: Beta Blume adjustment, tax, NWC, forecast period

### 7 Validation Gates
1. Method convergence (max/min ratio)
2. TV concentration (TV/EV < 65%)
3. EPV sanity (EPV ≤ DCF)
4. Reverse DCF plausibility (implied g vs base rate)
5. FCFF reconciliation
6. Multiples cross-check
7. MoS verification (≥ 25% for BUY)

### Recommendation Cap Table
- 🔴 Active fraud lawsuit → AVOID
- 🟠 Multiple flags → HOLD max
- MoS < 25% → cannot output BUY
- MoS < 0% → AVOID/TRIM

---

## 📊 Workflow

```
[/invest-source]     → Systematic idea generation (9 channels)
      ↓
[10-15 candidates]
      ↓
[/invest-screen]     → 10-min quick filter (6 filters + Phase 0.5 forensic)
      ↓
    GO / WATCHLIST / PASS
      ↓
[/mba-valuation]     → Full V4.2 8-phase valuation (60 min)
      ↓ Phase 0.5 forensic + 0.7 DQG + 4.5 sanity + 6.5 Bull/Bear + 9 audit
[V4.2 17-section Advanced Report]
      ↓
[portfolio.md]       → Source of truth
      ↓
[/invest-portfolio]  → Weekly/monthly monitoring
      ↓
[journal/]           → Continuous learning system
```

---

## 🛠️ Skills

| Skill | Purpose | Status |
|---|---|---|
| [invest-source](skills/invest-source/) | 9-channel systematic sourcing | ✅ V4.2 |
| [invest-screen](skills/invest-screen/) | 6-filter + forensic screen | ✅ V4.2 |
| [mba-valuation](skills/mba-valuation/) | Full 8-phase + 7 validation gates | ✅ V4.2 |
| [invest-portfolio](skills/invest-portfolio/) | Weekly/monthly monitoring | ✅ V4.2 |

---

## 🐍 Python Framework Code

| File | Purpose |
|---|---|
| `framework/valuation_calc.py` | DCF / EPV / WACC / 5 V4.1 auto-VETO functions / yield velocity / owner earnings |
| `framework/data_quality_gate.py` | 9 mandatory pre-calculation checks |
| `framework/decision_log.py` | Append-only decision ledger |
| `framework/backtest_runner.py` | Multi-benchmark performance scorecard |
| `framework/futu_costs.py` | Broker cost calculator (Futu HK rates) |
| `framework/excel_input_template.json` | 13 ACCT6111E cells mapped to verifiable sources |

### Quick Test
```bash
cd framework
python3 -c "from valuation_calc import dcf_two_stage, gaap_gap_check, reverse_dcf; print('OK')"
python3 valuation_calc.py dcf2 '{"fcf_year1": 100, "growth_high": 0.10, "years_high": 5, "growth_terminal": 0.025, "wacc": 0.09, "shares_outstanding": 50, "net_debt": 0}'
```

---

## 🚀 Setup (Personal Fork)

### Step 1: Fork this repo (or clone if read-only)

### Step 2: Copy skills to Claude Code
```bash
cp -r skills/* ~/.claude/skills/
```

### Step 3: Setup Python environment
```bash
cd framework
pip install pydantic anthropic python-telegram-bot google-api-python-client yfinance
```

### Step 4: Create your personal data layer
```bash
mkdir -p ~/your-personal-investment/{data,reports,journal}
cp portfolio_structure/portfolio.md ~/your-personal-investment/data/portfolio.md
# Edit with your real holdings (NEVER push to public repo)
```

### Step 5: (Optional) Setup Gmail API for email reports
See `skills/mba-valuation/scripts/`

### Step 6: (Optional) Setup Telegram bot for mobile checks
See your private layer's bot setup guide.

---

## ✅ Cross-Validation Protocol

Verify your Claude instance correctly applies V4.2:

1. **FISV test**: `/mba-valuation FISV` → should detect Cypanga Sicav class action lawsuit and trigger Phase 0.5 AVOID
2. **TJX test**: `/mba-valuation TJX current_price 157` → should produce -24% MoS = AUTO-VETO
3. **NVDA reverse DCF**: At $216 with $5T market cap → should detect HEROIC implied growth (35%+)
4. **WBA-pattern test**: Yield velocity > 50% in 18mo → should trigger yield trap warning

If any test fails, framework V4.2 is not properly implemented.

---

## 📊 Backtest Validation (V4.2)

Tested on 8 historical case studies (4 winners + 4 losers):

| Stock | Year | Outcome | V4.2 Verdict | Result |
|---|---|---|---|---|
| MSFT | 2022 | +118% | BUY | ✅ HIT |
| META | 2022 | +679% | BUY | ✅ HIT |
| NFLX | 2022 | +311% | BUY | ✅ HIT |
| NVDA | 2023 | +367% | BUY | ✅ HIT |
| PTON | 2021 | -96% | VETO | ✅ HIT |
| PYPL | 2021 | -80% | VETO | ✅ HIT |
| WBA | 2019 | -85% | VETO | ✅ HIT |
| GE | 2017 | -75% | VETO | ✅ HIT |

**8/8 retrospective hit rate**. Realistic deployment estimate ~70-80% (hindsight bias adjusted).

See [`journal/case_studies/V42_backtest_validation_summary.md`](journal/case_studies/V42_backtest_validation_summary.md).

---

## 📁 Folder Structure

```
investment-framework/
├── README.md                            # This file
├── VERSION.md                           # Full version history
├── framework/
│   ├── ACCT6111E_v2_hardened.md         # Methodology spec V2.0
│   ├── change_log.md                    # Version evolution log
│   ├── data_quality_gate.py             # 9-check Phase 0.7
│   ├── valuation_calc.py                # DCF/EPV/auto-VETO functions
│   ├── decision_log.py                  # Append-only ledger
│   ├── backtest_runner.py               # Multi-benchmark scorecard
│   ├── futu_costs.py                    # Broker cost calculator
│   ├── excel_input_template.json        # ACCT6111E input mapping
│   └── v42_advanced_report_template.md  # 17-section report format
├── skills/
│   ├── invest-source/SKILL.md
│   ├── invest-screen/SKILL.md
│   ├── invest-portfolio/SKILL.md
│   └── mba-valuation/SKILL.md
├── journal/
│   ├── case_studies/                    # Anonymized lessons (FISV, paper drills, backtest)
│   └── templates/                       # Decision log, post-mortem, thesis journal
└── portfolio_structure/
    └── portfolio.md                     # Empty template
```

---

## 🚫 What's NOT Included (Privacy by Design)

- ❌ Personal portfolio data
- ❌ Specific stock valuation reports
- ❌ Personal credentials / API keys
- ❌ Trading P/L records
- ❌ Real ticker counts / dollar amounts

These belong in your **personal layer** (Layer 2), never committed to public framework.

---

## 🎯 Continuous Improvement

Framework evolves through:
- Real-world failure → identify framework gap → add hard rule (e.g., FISV missed lawsuit → V2.0 Phase 0.5)
- Backtest validation → calibrate confidence
- Case studies (anonymized) → public knowledge accumulation
- Cross-validation between LLM instances → bias correction

See `journal/case_studies/` for live examples.

---

## 📚 References

- **CUHK MBA ACCT6111E**: Dr. Bhaskaran Swaminathan (course foundation)
- **Mauboussin S&P 1500**: Base rate paper (1950-2015)
- **NVO/BMY Disciplines**: 6 anti-patterns (moat expiry, price≠quality, numbers>narrative, yield trap, ROIC-WACC, kill sunk cost)
- **Howard Marks**: "You can't predict, but you can prepare"
- **William Thorndike**: *The Outsiders* (capital allocation)

---

## 📜 License

MIT — adapt freely for your own investing workflow.

---

## 🙏 Credits

- **Methodology**: CUHK MBA ACCT6111E, Dr. Bhaskaran Swaminathan
- **Implementation**: Built with [Claude Code](https://claude.com/claude-code) skills
- **Hardening**: Cross-validation between LLM instances + real-world failures (FISV, NVO/BMY post-mortems)

---

**Last updated**: 2026-05-08
**Framework version**: V4.2 hardened (production stable)
**Pending**: V5 release (PR-1 review in progress on private collab repo)
