#!/usr/bin/env python3
"""
portfolio_sync.py — V4.8: one command to refresh portfolio state + breach check.

What it does:
    1. Reads positions.json (shares + avg_cost per holding)
    2. Fetches live prices via yfinance
    3. Recomputes value_usd per position, total, P/L
    4. Writes positions.json back (as_of = today)
    5. Prints holdings table + hard-limit breach check (A1 / A2 / B1 / A4)

Positions file: --positions PATH → BT_POSITIONS_PATH → <investment_dir>/positions.json →
                portfolio_structure/positions.example.json (bundled FAKE demo data — never written back)

Run cadence: weekly review (Monday), monthly review, or ad-hoc before any trade.

Usage:
    python3 portfolio_sync.py            # sync + report
    python3 portfolio_sync.py --dry-run  # report only, no write-back
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

from config import EXAMPLE_POSITIONS_PATH, resolve_positions_path

GREEN, YELLOW, RED, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"


def fetch_prices(symbols):
    import yfinance as yf  # optional heavy dep — imported lazily so --help works without it
    out = {}
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            px = t.fast_info.get("lastPrice") or t.fast_info.get("last_price")
            if not px:
                hist = t.history(period="2d")
                px = float(hist["Close"].iloc[-1])
            out[sym] = float(px)
        except Exception as e:
            print(f"  {YELLOW}WARN{RESET} {sym}: price fetch failed ({e}) — keeping stale value")
            out[sym] = None
    return out


def main():
    ap = argparse.ArgumentParser(description="V4.8 portfolio sync + hard-limit breach check")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--positions", default=None, help="positions.json path (default: config.resolve_positions_path())")
    args = ap.parse_args()

    positions_path = Path(args.positions).expanduser() if args.positions else resolve_positions_path()
    if positions_path.resolve() == EXAMPLE_POSITIONS_PATH.resolve() and not args.dry_run:
        print(f"  {YELLOW}NOTE{RESET} using bundled example positions — forcing --dry-run "
              f"(copy it to your investment dir or set BT_POSITIONS_PATH to sync real holdings)")
        args.dry_run = True

    st = json.loads(positions_path.read_text())
    lim = st["limits"]

    prices = fetch_prices([p["yf"] for p in st["positions"].values()])

    rows, total_pos = [], 0.0
    for tk, p in st["positions"].items():
        px = prices.get(p["yf"])
        if px:
            p["value_usd"] = round(p["shares"] * px, 0)
            p["last_price"] = round(px, 2)
        val = p["value_usd"]
        total_pos += val
        cost = p["shares"] * p["avg_cost"]
        pl_pct = (val - cost) / cost * 100
        rows.append((tk, p.get("last_price", "stale"), val, pl_pct, ",".join(p["tags"])))

    total = total_pos + st["cash_usd"]
    st["total_portfolio_usd"] = round(total, 0)
    st["as_of"] = date.today().isoformat()

    print(f"\n{'='*68}")
    print(f"  PORTFOLIO SYNC — {st['as_of']}   total ${total:,.0f} (cash ${st['cash_usd']:,.0f})")
    print(f"{'='*68}")
    print(f"  {'Ticker':<6} {'Price':>10} {'Value':>10} {'Weight':>7} {'P/L':>8}  Tags")
    for tk, px, val, pl, tags in sorted(rows, key=lambda r: -r[2]):
        w = val / total * 100
        color = GREEN if pl >= 0 else RED
        print(f"  {tk:<6} {px:>10} {val:>10,.0f} {w:>6.1f}% {color}{pl:>+7.1f}%{RESET}  {tags}")

    # ---- breach check ----
    print(f"\n  RULES check:")
    breaches = 0
    for tk, p in st["positions"].items():
        w = p["value_usd"] / total * 100
        if "crypto" not in p["tags"] and w > lim["single_stock_max_pct"]:
            print(f"  [{RED}BREACH{RESET}] A1 {tk} {w:.1f}% > {lim['single_stock_max_pct']}% single-stock cap")
            breaches += 1
    crypto = sum(p["value_usd"] for p in st["positions"].values() if "crypto" in p["tags"])
    if crypto / total * 100 > lim["crypto_total_max_pct"]:
        print(f"  [{YELLOW}EXCEPT{RESET}] A2 crypto {crypto/total*100:.1f}% > {lim['crypto_total_max_pct']}% "
              f"(no forced sell — record a formal exception in OVERRIDE_LOG.md)")
    ai = sum(p["value_usd"] for p in st["positions"].values() if "ai" in p["tags"])
    if ai / total * 100 > lim["ai_correlated_max_pct"]:
        print(f"  [{RED}BREACH{RESET}] B1 AI-correlated {ai/total*100:.1f}% > {lim['ai_correlated_max_pct']}% — new AI buys frozen")
        breaches += 1
    cash_pct = st["cash_usd"] / total * 100
    if cash_pct < lim["cash_reserve_min_pct"]:
        print(f"  [{RED}BREACH{RESET}] A4 cash {cash_pct:.1f}% < {lim['cash_reserve_min_pct']}% reserve — new capital refills cash first")
        breaches += 1
    if breaches == 0:
        print(f"  [{GREEN}OK{RESET}] all hard limits compliant")

    if not args.dry_run:
        positions_path.write_text(json.dumps(st, indent=2, ensure_ascii=False))
        print(f"\n  {positions_path.name} updated (as_of {st['as_of']})")
    print(f"{'='*68}\n")


if __name__ == "__main__":
    main()
