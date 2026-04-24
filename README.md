# Investment Framework

Personal investment analysis framework built on Claude Code skills. Implements the CUHK MBA ACCT6111E (Dr. Swaminathan) value investing methodology with systematic idea sourcing, quick screening, 8-phase full valuation, and portfolio monitoring.

## Philosophy

- **20-30% margin of safety minimum** before deploying capital
- **5+ year horizon**, durable moat preferred
- **Numbers over narrative** — every thesis backed by DCF
- **Three independent valuation methods** (EPV + DCF + Multiples) for cross-validation
- **Systematic discipline** — 6-question gate before every buy decision

## Architecture

```
[/invest-source]     → Systematic idea generation (9 channels)
      ↓
[10-15 candidates]
      ↓
[/invest-screen]     → 10-minute quick filter (6 filters)
      ↓
    GO / WATCHLIST / PASS
      ↓
[/mba-valuation]     → Full 8-phase valuation (30-45 min)
      ↓
[portfolio.md]       → Source of truth for holdings, watchlist, exit triggers
      ↓
[/invest-portfolio]  → Weekly/monthly monitoring, thesis re-validation
```

## Skills

Four Claude Code skills work together:

| Skill | Purpose | Duration |
|---|---|---|
| **[invest-source](skills/invest-source/)** | Systematic idea sourcing across 9 channels (13F, insider buying, quality-at-lows, spin-offs, fallen angels, activist 13D, event calendar) | Monthly scan |
| **[invest-screen](skills/invest-screen/)** | 10-minute quick filter with 6-filter framework + NVO/BMY lesson gate (6 discipline rules) | 10 min per candidate |
| **[mba-valuation](skills/mba-valuation/)** | Full 8-phase valuation (EPV / DCF / Multiples / Proforma / 3-Stage) with sensitivity analysis | 30-45 min per stock |
| **[invest-portfolio](skills/invest-portfolio/)** | Portfolio monitoring, news checks, thesis re-validation, weekly/monthly reviews | Scheduled |

## 9 Sourcing Channels

**Tier 1 — High signal (monthly)**
1. Superinvestor 13F new positions (Berkshire, Pershing Square, Baupost, Appaloosa, etc.)
2. 13F conviction sizing (% increases)
3. 13F + insider buying overlap
4. Spin-off tracking (mechanical mispricing)

**Tier 2 — Medium signal (quarterly)**
5. Activist 13D filings (Elliott, Starboard, Third Point)
6. Fallen angel credit downgrades
7. Quality-at-52-week-lows

**Tier 3 — Forward-looking (ad-hoc)**
8. Event calendar anticipation

**Tier 4 — Reactive (event-driven)**
9. Post-earnings drops > 10% on quality names

## 6-Filter Screening Framework

Every candidate gets filtered through:
1. **Market Cap & Liquidity** — avoid micro-caps and illiquid names
2. **Business Understandability** — Warren Buffett "within circle of competence" test
3. **Financial Health** — Debt/Equity, Interest Coverage, Current Ratio, FCF, ROIC, Revenue trend
4. **Red Flags** — fads, serial acquirers, accounting shenanigans, excessive leverage, management red flags
5. **Valuation Quick Gauge** — P/E, EV/EBITDA, P/FCF vs history and peers
6. **Moat / Competitive Position** — network effects, switching costs, scale, brand

Plus **Filter 4B**: NVO/BMY Lesson Gate (6 hard rules learned from past mistakes).

## 8-Phase Full Valuation

Based on CUHK MBA ACCT6111E (Dr. Swaminathan). Each phase is documented in [skills/mba-valuation/](skills/mba-valuation/):

| Phase | Purpose |
|---|---|
| 0 | Scope + data gathering |
| 1 | Historical financial analysis (5yr FCFF, ROIC, Du Pont) |
| 2 | Competitive position (Lynch lifecycle, Porter 5 Forces, Moat) |
| 3 | Cost of capital (CAPM, Beta, WACC) |
| 4 | Multi-method valuation (EPV / DCF / Multiples / EVA / 3-Stage) |
| 5 | Sensitivity + scenarios (Bull / Base / Bear) |
| 6 | Investment decision (P/V ratio, margin of safety, 6-question gate) |
| 7 | Behavioral bias check |
| 8 | Output report (standardized format + PDF) |

## Portfolio Structure

See [portfolio_structure/](portfolio_structure/) for the folder layout:

```
portfolio_structure/
├── portfolio.md              # Source of truth: holdings, watchlist, exit triggers
├── research/
│   ├── full_reports/         # 8-phase valuation reports (markdown + PDF)
│   └── *.md                  # Quick memos, thesis notes
├── sourcing/                 # Idea sourcing reports (YYYY-MM-DD_sourcing.md)
└── reviews/                  # Weekly / monthly portfolio reviews
```

## 6-Question Discipline Gate

From painful past mistakes (NVO / BMY post-mortem), every candidate MUST pass:

1. **Moat has expiry date?** — Patent cliff, license expiry, contract expiry
2. **ROIC-WACC spread > 2%?** — Growth must create excess value
3. **Dividend yield > 4%?** — Yield trap red flag, check FCF payout ratio
4. **Net Debt > 50% of Market Cap?** — Debt-heavy compresses equity value
5. **Thesis has numbers support?** — Narrative-only thesis is red flag
6. **"Would I buy today?"** — If answer is No, don't hold

## Setup

1. Clone this repo
2. Copy the skill folders from `skills/` into your `~/.claude/skills/` directory
3. Create your personal portfolio directory (e.g., `~/Developer/investment/`)
4. Copy `portfolio_structure/portfolio.md` as your starting template — fill in your actual holdings
5. Invoke skills from Claude Code:
   - `/invest-source` — monthly idea scan
   - `/invest-screen TICKER` — quick filter
   - `/mba-valuation TICKER` — full 8-phase valuation
   - `/invest-portfolio` — portfolio review

## Output Format (every valuation)

All deliverables follow a standard decision format:

```
📊 估值結果 (table: EPV / DCF / Multiples / Weighted)
🎯 三層解釋 (1 sentence → business impact → daily analogy)
🧭 投資選項 A / B / C (with trade-offs)
✅ 建議 (with rationale)
⚠️ Red flags
🧠 Framework used (MBA lecture / reference case)
📋 Exit triggers (to monitor)
```

## Reference Cases

The framework references specific historical cases to calibrate judgments:
- **Apple 2013** — quality at temporary discount
- **SJM** — EPV zero-growth floor
- **MEMC** — capex cycle bust
- **TER** — distressed turnaround
- **Moody's** — duopoly network moat
- **ITW** — high-quality compounder temporarily depressed

## Credits

- Methodology: CUHK MBA ACCT6111E, Dr. Bhaskaran Swaminathan
- Implementation: Built with [Claude Code](https://claude.com/claude-code) skills
- Personal use — shared as reference for others building similar systematic frameworks

## License

MIT — feel free to adapt for your own investing workflow.

---

**This is a framework repository.** Actual portfolio data, research reports with specific stock analyses, and personal investment decisions are NOT included. Build your own portfolio.md based on the template, run the skills, and develop your own positions.
