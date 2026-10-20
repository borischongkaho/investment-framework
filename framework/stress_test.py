#!/usr/bin/env python3
"""
stress_test.py — V4.9: portfolio scenario stress test（monthly review 用）。

Why: drawdown protocol 寫咗但從未演習。業界機構每月 run scenario。
     呢個讀 positions.json，套 3 個 shock scenario，印 worst-case 數字 +
     對 drawdown protocol 嘅 trigger levels。

純風險可視化 — 唔郁估值、唔郁原則。心理預演用。

Positions file: --positions PATH → BT_POSITIONS_PATH → <investment_dir>/positions.json →
                portfolio_structure/positions.example.json (bundled FAKE demo data)

Usage:
    python3 stress_test.py
    python3 stress_test.py --positions ~/my/positions.json
"""
import argparse
import json
from pathlib import Path

from config import resolve_positions_path

GREEN, YELLOW, RED, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"

# Scenario shocks by tag (sourced from historical analogs — 2022 AI correction / 2008 recession / 2022 stagflation)
SCENARIOS = {
    "A. AI 修正 (2022-style)": {"ai": -0.30, "tech": -0.30, "utilities": -0.25, "crypto": -0.35,
                                 "financials": -0.10, "consumer": -0.08, "_desc": "AI / 半導體 / AI 電力 領跌，crypto 跟"},
    "B. 全面衰退 (2008-style)": {"ai": -0.25, "tech": -0.25, "utilities": -0.15, "crypto": -0.45,
                                 "financials": -0.30, "consumer": -0.20, "payments": -0.25, "adservices": -0.30,
                                 "_desc": "risk-off，crypto + 廣告 + 金融最傷"},
    "C. 滯脹 (rates up)": {"ai": -0.15, "tech": -0.15, "utilities": -0.15, "crypto": -0.20,
                            "financials": 0.05, "consumer": -0.10, "payments": -0.05, "adservices": -0.12,
                            "_desc": "高息壓 utilities/長存續，金融受惠"},
}
WORST_CASE = "B. 全面衰退 (2008-style)"


def shock_for(tags, scen):
    # most negative applicable shock (conservative)
    vals = [scen[t] for t in tags if t in scen]
    return min(vals) if vals else -0.15  # default broad-market shock


def run_scenarios(st):
    """Return {scenario_name: {"post_total", "drawdown", "lines": [(ticker, old, shock, new)]}} — pure, no printing."""
    total, cash = st["total_portfolio_usd"], st["cash_usd"]
    out = {}
    for name, scen in SCENARIOS.items():
        lines, post_positions = [], 0.0
        for tk, p in st["positions"].items():
            sh = shock_for(p["tags"], scen)
            new_val = p["value_usd"] * (1 + sh)
            post_positions += new_val
            lines.append((tk, p["value_usd"], sh, new_val))
        post_total = post_positions + cash  # cash unshocked
        out[name] = {"post_total": post_total, "drawdown": (post_total - total) / total, "lines": lines}
    return out


def main():
    ap = argparse.ArgumentParser(description="V4.9 portfolio scenario stress test")
    ap.add_argument("--positions", default=None, help="positions.json path (default: config.resolve_positions_path())")
    a = ap.parse_args()
    path = Path(a.positions).expanduser() if a.positions else resolve_positions_path()
    st = json.loads(path.read_text())
    total = st["total_portfolio_usd"]
    cash = st["cash_usd"]

    print(f"\n{'='*64}")
    print(f"  PORTFOLIO STRESS TEST — base ${total:,.0f} (as_of {st['as_of']})")
    print(f"{'='*64}")

    results = run_scenarios(st)
    for name, scen in SCENARIOS.items():
        r = results[name]
        dd = r["drawdown"]
        color = GREEN if dd > -0.15 else (YELLOW if dd > -0.25 else RED)
        print(f"\n  {name}")
        print(f"  {scen['_desc']}")
        for tk, old, sh, new in sorted(r["lines"], key=lambda x: x[2]):
            print(f"    {tk:<5} {old:>9,.0f} → {new:>9,.0f}  ({sh:+.0%})")
        print(f"    cash  {cash:>9,.0f} → {cash:>9,.0f}  (  0%)")
        print(f"  {color}  → Portfolio ${r['post_total']:,.0f}  ({dd:+.1%})  drawdown ${total-r['post_total']:,.0f}{RESET}")

    print(f"\n  {'─'*60}")
    print(f"  drawdown protocol triggers（對照 worst case = Scenario B）:")
    worst_dd = results[WORST_CASE]["drawdown"]
    print(f"    Worst-case drawdown: {worst_dd:+.1%}")
    if worst_dd <= -0.20:
        print(f"    {YELLOW}→ -20% portfolio drawdown 會觸發 drawdown protocol review{RESET}")
        print(f"    → 預演：嗰陣唔好 panic sell，逐隻問 thesis intact?（過 SELL gate）")
        print(f"    → 有 cash buffer 嘅話係 add 機會（但 cash 而家得 {cash/total:.0%}）")
    print(f"{'='*64}\n")


if __name__ == "__main__":
    main()
