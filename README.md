# Investment Framework

> **Version**: ACCT6111E v2.0 hardened (2026-05-03)
> **Methodology**: CUHK MBA ACCT6111E (Dr. Bhaskaran Swaminathan)

Personal investment analysis framework built on Claude Code skills. Implements systematic value investing with **forensic screening, validation gates, and binding recommendation caps**.

---

## ⚠️ v2.0 Hardening Notice

**v2.0 fixes 7 critical bugs identified through real-world failures (ABBV over-bullish + FISV missed lawsuit)**.

If you're upgrading from v1, see [`framework/change_log.md`](framework/change_log.md) for breaking changes.

**Cross-validation testing**: Use the v2.0 test suite in `framework/ACCT6111E_v2_hardened.md` to verify any Claude instance produces consistent v2.0 output.

---

## Philosophy

- **20-30% margin of safety minimum** before deploying capital
- **Forensic screening mandatory** — no valuation without litigation/governance check
- **Strict terminal formula** — `NOPAT × (1-g/ROI) / (WACC-g)`, no plain Gordon Growth
- **Validation gates binding** — 7 mandatory checks before final output
- **Recommendation caps non-negotiable** — red flags trigger automatic AVOID

---

## Architecture

```
[/invest-source]     → Systematic idea generation (9 channels)
      ↓
[10-15 candidates]
      ↓
[/invest-screen]     → 10-min quick filter (6 filters + Phase 0.5 forensic)
      ↓
    GO / WATCHLIST / PASS
      ↓
[/mba-valuation]     → Full v2.0 8-phase valuation (45 min)
      ↓ Pass 7 validation gates → recommendation cap
[portfolio.md]       → Source of truth
      ↓
[/invest-portfolio]  → Weekly/monthly monitoring
      ↓
[journal/]           → Continuous learning system
```

---

## v2.0 Critical Components

### 1. Phase 0.5 — Forensic Screening (NEW)
10 mandatory web searches before any valuation:
- Securities class action / SEC / DOJ investigations
- Accounting restatement / Going concern auditor
- CEO/CFO change last 12 months
- Guidance miss/cut / Earnings restatement
- Latest quarterly results verification

### 2. Default Assumptions Lock (NEW)
- **D1: Terminal formula** — `NOPAT × (1-g/ROI)/(WACC-g)` ALWAYS
- **D2: Terminal growth** — 2.5% default, 3.0% hard cap
- **D3: WACC floors** — 7% large-cap / 8% mid / 9.5% small
- **D4-D7**: Beta Blume adjustment, tax, NWC, forecast period

### 3. 7 Validation Gates (NEW)
1. Method convergence (max/min ratio)
2. TV concentration (TV/EV)
3. EPV sanity (EPV ≤ DCF)
4. Reverse DCF plausibility (implied g)
5. FCFF reconciliation (top-down vs bottom-up)
6. Multiples cross-check
7. MoS verification

### 4. Recommendation Cap Table (NEW)
Binding caps:
- 🔴 Active fraud lawsuit → AVOID
- 🟠 Multiple flags → HOLD max
- MoS < 25% → cannot output BUY
- MoS < 0% → AVOID/TRIM

---

## Skills

| Skill | Purpose | v2.0 Hardened? |
|---|---|---|
| [invest-source](skills/invest-source/) | 9-channel systematic sourcing | ✅ |
| [invest-screen](skills/invest-screen/) | 6-filter + forensic screen | ✅ |
| [mba-valuation](skills/mba-valuation/) | Full 8-phase + 7 validation gates | ✅ |
| [invest-portfolio](skills/invest-portfolio/) | Weekly/monthly monitoring with v2.0 cap | ✅ |

---

## Setup

1. Clone this repo
2. Copy skill folders to your `~/.claude/skills/`
3. Create your personal portfolio dir (e.g., `~/Developer/investment/`)
4. Copy `portfolio_structure/portfolio.md` as starting template
5. (Optional) Setup Gmail API for report email delivery — see `skills/mba-valuation/scripts/`

---

## Cross-Validation Protocol

To verify your Claude instance correctly applies v2.0:

1. Run `/mba-valuation FISV current_price 62` → should detect Cypanga Sicav lawsuit and trigger AVOID
2. Run `/mba-valuation ABBV current_price 203` → should produce $185-210 intrinsic, HOLD
3. Run `/mba-valuation GIS current_price 35` → should produce reasonable BORDERLINE BUY (no false AVOID)

If any test fails, framework v2.0 is not properly implemented.

---

## Folder Structure

```
investment-framework/
├── README.md                        # This file
├── framework/
│   ├── ACCT6111E_v2_hardened.md     # Main framework v2.0
│   └── change_log.md                # v1 → v2 evolution
├── journal/
│   └── templates/                   # Decision log, post-mortem, thesis journal
│       ├── decision_log_template.md
│       ├── post_mortem_template.md
│       └── thesis_journal_template.md
├── skills/
│   ├── invest-source/               # 9-channel sourcing
│   ├── invest-screen/               # 6-filter screening
│   ├── mba-valuation/               # Full 8-phase + email integration
│   └── invest-portfolio/            # Monitoring
└── portfolio_structure/
    └── portfolio.md                 # Empty template
```

---

## What's NOT Included

- ❌ Personal portfolio data (use `portfolio.md` template)
- ❌ Specific stock valuation reports (build your own)
- ❌ Personal credentials (Gmail OAuth setup required separately)
- ❌ Trading P/L records

---

## Continuous Improvement

The framework is designed to evolve. Key principles:
- Document every decision (use journal templates)
- Post-mortem after every exit
- Update framework when patterns emerge
- Cross-validate between Claude instances regularly

---

## Credits

- **Methodology**: CUHK MBA ACCT6111E, Dr. Bhaskaran Swaminathan
- **Implementation**: Built with [Claude Code](https://claude.com/claude-code) skills
- **v2.0 Hardening**: Based on cross-validation between Claude instances

---

## License

MIT — adapt freely for your own investing workflow.

---

**Last updated**: 2026-05-03
**Framework version**: ACCT6111E v2.0 hardened
