#!/usr/bin/env python3
"""
Backtest Runner — Multi-Benchmark Alpha Scorecard
investment framework.

For each historical decision (BUY / SELL / HOLD), compute:
- Absolute return from entry to today (or to sell date)
- Alpha vs SPY (market)
- Alpha vs sector ETF (XLV / XLK / XLF / etc.)
- For crypto: alpha vs BTC HODL

Output: ~/Developer/investment/backtest/scorecard.md

Decisions are read from a JSON manifest at:
~/Developer/investment/decision_log/decisions.json

Usage:
    python3 backtest_runner.py
    python3 backtest_runner.py --ticker NVDA       # single ticker
    python3 backtest_runner.py --as-of 2026-05-06  # backtest as if today is X
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# yfinance has noisy warnings, suppress them
import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd


HOME = Path.home()
INVEST_DIR = HOME / "Developer" / "investment"
DECISIONS_PATH = INVEST_DIR / "decision_log" / "decisions.json"
SCORECARD_PATH = INVEST_DIR / "backtest" / "scorecard.md"

# Sector ETF mapping (US stocks)
SECTOR_ETFS = {
    "tech": "XLK",
    "healthcare": "XLV",
    "financials": "XLF",
    "consumer_disc": "XLY",
    "consumer_staples": "XLP",
    "energy": "XLE",
    "industrials": "XLI",
    "materials": "XLB",
    "utilities": "XLU",
    "real_estate": "XLRE",
    "communications": "XLC",
}


def fetch_total_return(ticker: str, start_date: str, end_date: str) -> Optional[float]:
    """
    Total return (price + dividends, dividend reinvested) from start to end.
    Uses adjusted close which already reflects splits + dividends.
    Returns: pct return as float (e.g. 0.49 = +49%), or None if data missing.
    """
    try:
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True,
            threads=False,
        )
        if data.empty or len(data) < 2:
            return None
        first = float(data["Close"].iloc[0].iloc[0] if hasattr(data["Close"].iloc[0], 'iloc') else data["Close"].iloc[0])
        last = float(data["Close"].iloc[-1].iloc[0] if hasattr(data["Close"].iloc[-1], 'iloc') else data["Close"].iloc[-1])
        return (last - first) / first
    except Exception as e:
        print(f"  ⚠️  yfinance error for {ticker}: {e}", file=sys.stderr)
        return None


def fetch_close(ticker: str, on_date: str) -> Optional[float]:
    """Fetch the closest available close price on or after a date."""
    try:
        target = datetime.strptime(on_date, "%Y-%m-%d")
        end = (target + timedelta(days=10)).strftime("%Y-%m-%d")
        data = yf.download(ticker, start=on_date, end=end, progress=False, auto_adjust=True, threads=False)
        if data.empty:
            return None
        v = data["Close"].iloc[0]
        return float(v.iloc[0] if hasattr(v, "iloc") else v)
    except Exception:
        return None


def compute_alpha_row(decision: dict, as_of: str) -> dict:
    """
    For one decision, compute USER actual return + alpha vs benchmarks.

    Asset return = (current_or_exit_price - user_entry_price) / user_entry_price
    Benchmark return = market total return from entry_date to as_of (or exit_date)
    Alpha = asset_return - benchmark_return
    """
    ticker = decision["ticker"]
    entry_date = decision["entry_date"]
    entry_price = float(decision["entry_price"])
    exit_date = decision.get("exit_date") or as_of
    asset_class = decision.get("asset_class", "equity")
    sector = decision.get("sector", "tech")

    entry_dt = datetime.strptime(entry_date, "%Y-%m-%d")
    exit_dt = datetime.strptime(exit_date, "%Y-%m-%d")
    days = (exit_dt - entry_dt).days
    is_closed = decision.get("status") == "CLOSED"

    # CLOSED positions always show realized return regardless of days held.
    # Only HOLDING positions get TOO_RECENT (need ≥30d to be meaningful).
    if days < 30 and not is_closed:
        return {
            "ticker": ticker,
            "entry_date": entry_date,
            "days_held": days,
            "status": "TOO_RECENT",
            "absolute_return": None,
            "alpha_spy": None,
            "alpha_sector": None,
            "alpha_btc": None,
        }

    # Determine the asset's exit price for return calc
    if decision.get("exit_price"):
        exit_price = float(decision["exit_price"])
    else:
        exit_price = fetch_close(ticker, exit_date)

    asset_return = (exit_price - entry_price) / entry_price if exit_price else None

    # Benchmarks: use market total return over the same period
    spy_return = fetch_total_return("SPY", entry_date, exit_date)
    sector_etf = SECTOR_ETFS.get(sector, "SPY")
    sector_return = (
        fetch_total_return(sector_etf, entry_date, exit_date)
        if sector_etf != "SPY"
        else spy_return
    )
    btc_return = (
        fetch_total_return("BTC-USD", entry_date, exit_date)
        if asset_class == "crypto"
        else None
    )

    return {
        "ticker": ticker,
        "entry_date": entry_date,
        "exit_date": exit_date,
        "days_held": days,
        "years_held": round(days / 365.25, 2),
        "asset_class": asset_class,
        "sector": sector,
        "sector_etf": sector_etf,
        "absolute_return": asset_return,
        "spy_return": spy_return,
        "sector_return": sector_return,
        "btc_return": btc_return,
        "alpha_spy": (asset_return - spy_return) if (asset_return is not None and spy_return is not None) else None,
        "alpha_sector": (asset_return - sector_return) if (asset_return is not None and sector_return is not None) else None,
        "alpha_btc": (asset_return - btc_return) if (asset_return is not None and btc_return is not None) else None,
        "status": decision.get("status", "HOLDING"),
        "thesis_tag": decision.get("thesis_tag", "—"),
    }


def fmt_pct(v):
    if v is None:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v*100:.1f}%"


def render_scorecard(rows: list, as_of: str) -> str:
    md = []
    md.append(f"# 📊 Backtest Scorecard\n")
    md.append(f"**As of**: {as_of}  ")
    md.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    md.append(f"**Decisions tracked**: {len(rows)}\n")
    md.append("---\n")

    md.append("## 📋 Per-Decision Detail\n")
    md.append(
        "| Ticker | Entry | Exit | Years | Return | vs SPY | vs Sector | vs BTC | Status |"
    )
    md.append(
        "|---|---|---|---|---|---|---|---|---|"
    )
    for r in rows:
        if r["status"] == "TOO_RECENT":
            md.append(
                f"| {r['ticker']} | {r['entry_date']} | — | <30d | TOO RECENT | — | — | — | {r['status']} |"
            )
            continue
        md.append(
            f"| {r['ticker']} | {r['entry_date']} | {r['exit_date']} | {r['years_held']} | "
            f"{fmt_pct(r['absolute_return'])} | {fmt_pct(r['alpha_spy'])} | "
            f"{fmt_pct(r['alpha_sector'])} ({r['sector_etf']}) | {fmt_pct(r['alpha_btc'])} | {r['status']} |"
        )

    # Aggregate stats
    valid = [r for r in rows if r.get("alpha_spy") is not None]
    if valid:
        md.append("\n---\n")
        md.append("## 📈 Aggregate Performance\n")

        avg_alpha_spy = sum(r["alpha_spy"] for r in valid) / len(valid)
        win_count = sum(1 for r in valid if r["alpha_spy"] > 0)
        win_rate = win_count / len(valid)

        md.append(f"- **Sample size**: {len(valid)} decisions (≥30 days hold)")
        md.append(f"- **Avg alpha vs SPY**: {fmt_pct(avg_alpha_spy)}")
        md.append(f"- **Win rate (positive alpha vs SPY)**: {win_rate*100:.0f}% ({win_count}/{len(valid)})")

        # Per-sector breakdown
        sectors = {}
        for r in valid:
            s = r["sector"]
            sectors.setdefault(s, []).append(r)
        md.append("\n### By Sector\n")
        md.append("| Sector | N | Avg Return | Avg Alpha vs SPY | Avg Alpha vs Sector ETF |")
        md.append("|---|---|---|---|---|")
        for sector, items in sorted(sectors.items()):
            n = len(items)
            avg_ret = sum(r["absolute_return"] for r in items) / n
            avg_a_spy = sum(r["alpha_spy"] for r in items) / n
            sector_alphas = [r["alpha_sector"] for r in items if r["alpha_sector"] is not None]
            avg_a_sec = (sum(sector_alphas) / len(sector_alphas)) if sector_alphas else None
            md.append(
                f"| {sector} | {n} | {fmt_pct(avg_ret)} | {fmt_pct(avg_a_spy)} | {fmt_pct(avg_a_sec)} |"
            )

        # Caveats
        md.append("\n---\n")
        md.append("## ⚠️ Caveats\n")
        md.append("- Sample size <10 → 任何 alpha 數字都係 noise，唔可以單靠 scorecard 落 decision")
        md.append("- 5+ 年 hold horizon 嘅 thesis，1Y/2Y alpha 唔代表 thesis 錯")
        md.append("- SPY 對 healthcare / crypto 唔公平 — 多睇 sector ETF column")
        md.append("- 已 sell 嘅 decision 已包含實際結果；HOLDING 嘅係 mark-to-market")

    md.append("\n---\n")
    md.append("*Generated by `backtest_runner.py`*")
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="Multi-benchmark backtest scorecard")
    parser.add_argument("--ticker", help="Filter to single ticker (writes to a separate file to avoid clobbering full scorecard)")
    parser.add_argument("--as-of", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Backtest as-of date (YYYY-MM-DD)")
    parser.add_argument("--output", default=None,
                        help="Output markdown path (default: scorecard.md, or TICKER_scorecard.md when --ticker is set)")
    args = parser.parse_args()

    if args.output is None:
        if args.ticker:
            args.output = str(SCORECARD_PATH.parent / f"{args.ticker.upper()}_scorecard.md")
        else:
            args.output = str(SCORECARD_PATH)

    if not DECISIONS_PATH.exists():
        print(f"❌ Decision log not found: {DECISIONS_PATH}")
        print("   Run decision_log.py first to bootstrap from portfolio.md")
        sys.exit(1)

    with open(DECISIONS_PATH) as f:
        decisions = json.load(f)

    if args.ticker:
        decisions = [d for d in decisions if d["ticker"] == args.ticker.upper()]

    print(f"📊 Backtesting {len(decisions)} decisions as of {args.as_of}...")
    rows = []
    for d in decisions:
        print(f"  • {d['ticker']} ({d['entry_date']})...", end=" ", flush=True)
        row = compute_alpha_row(d, args.as_of)
        rows.append(row)
        if row["status"] == "TOO_RECENT":
            print("skipped (too recent)")
        elif row.get("alpha_spy") is not None:
            print(f"alpha vs SPY: {fmt_pct(row['alpha_spy'])}")
        else:
            print("data missing")

    md = render_scorecard(rows, args.as_of)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md)
    print(f"\n✅ Scorecard written to: {output_path}")


if __name__ == "__main__":
    main()
