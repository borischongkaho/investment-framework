#!/usr/bin/env python3
"""
kelly_lite.py — V4.9: position sizing 參考（唔取代 cap rules）。

Why: V4.8 sizing 靠 cap (15%/30%) + conviction 直覺。業界（Thorp/Greenblatt 暗用）
     用 Kelly criterion — size 同「edge × 賠率」掛鈎。風險高嘅倉自動細啲。

呢個係 SIZING 工具，唔係估值工具 — MoS / intrinsic 照用 V4.6 計法。
輸出係建議 %，永遠受 RULES cap 上限約束（fractional Kelly 1/4 = 保守）。

公式（fractional Kelly, 1/4）:
    f* = (p·b - (1-p)) / b
    p  = win probability（由 3-Judge confidence 嚟）
    b  = win/loss odds = upside_to_intrinsic / downside_to_bear
    suggested % = max(0, f* · kelly_fraction)，再 cap 落 single-stock limit

Usage:
    python3 kelly_lite.py --mos 33 --win-prob 0.70 --bear-downside 25
    python3 kelly_lite.py --ticker AAPL --mos 33 --win-prob 0.70 --bear-downside 25 --portfolio 250000
"""
import argparse

GREEN, YELLOW, RED, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"
SINGLE_STOCK_CAP = 0.15   # Rule A1 (winner exception handled manually)
KELLY_FRACTION = 0.25     # quarter-Kelly = 保守，防 over-bet on estimate error


def kelly_size(mos_pct, win_prob, bear_downside_pct, kelly_fraction=KELLY_FRACTION, cap=SINGLE_STOCK_CAP):
    """Quarter-Kelly sizing. Returns odds, full Kelly, fractional Kelly and the capped suggestion."""
    upside = mos_pct / 100.0
    downside = bear_downside_pct / 100.0
    b = upside / downside if downside > 0 else 99
    f_star = (win_prob * b - (1 - win_prob)) / b
    f_frac = max(0.0, f_star * kelly_fraction)
    return {
        "odds_b": b,
        "f_star": f_star,
        "f_frac": f_frac,
        "suggested": min(f_frac, cap),
        "capped": f_frac > cap,
    }


def main():
    p = argparse.ArgumentParser(description="V4.9 Kelly-lite sizing")
    p.add_argument("--ticker", default="(candidate)")
    p.add_argument("--mos", type=float, required=True, help="margin of safety percent (upside to intrinsic)")
    p.add_argument("--win-prob", type=float, required=True, help="win probability 0-1 (from 3-Judge confidence)")
    p.add_argument("--bear-downside", type=float, required=True, help="downside percent in bear case (positive number)")
    p.add_argument("--portfolio", type=float, default=100_000, help="total portfolio USD (default 100,000 — illustrative)")
    a = p.parse_args()

    r = kelly_size(a.mos, a.win_prob, a.bear_downside)
    b, f_star, f_frac, suggested, capped = r["odds_b"], r["f_star"], r["f_frac"], r["suggested"], r["capped"]

    print(f"\n{'='*60}")
    print(f"  KELLY-LITE SIZING — {a.ticker}")
    print(f"{'='*60}")
    print(f"  Inputs:")
    print(f"    Upside (MoS):       {a.mos:.0f}%")
    print(f"    Bear downside:      {a.bear_downside:.0f}%")
    print(f"    Win odds (b):       {b:.2f} : 1")
    print(f"    Win probability:    {a.win_prob:.0%}")
    print(f"  ─────────────────────────────────")
    print(f"    Full Kelly f*:      {f_star:+.1%}")
    print(f"    Quarter-Kelly:      {f_frac:.1%}  (×{KELLY_FRACTION} safety)")

    if f_star <= 0:
        print(f"\n  {RED}NEGATIVE EDGE{RESET} — Kelly 話唔好買（odds × prob 唔抵）")
        print(f"  即使 MoS pass，呢個 risk/reward 唔值搏")
    else:
        cap_note = f"  {YELLOW}(capped from {f_frac:.1%} by {SINGLE_STOCK_CAP:.0%} single-stock rule){RESET}" if capped else ""
        print(f"\n  {GREEN}SUGGESTED SIZE: {suggested:.1%}{RESET} of portfolio{cap_note}")
        print(f"  = ${suggested * a.portfolio:,.0f} on ${a.portfolio:,.0f} base")
    print(f"\n  ⚠️  Sizing 參考 only。Cap rules (A1) + cash (A4) + ")
    print(f"      AI cap (B1) + quota (C6) 全部仍然 binding。過 pre_trade_gate 為準。")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
