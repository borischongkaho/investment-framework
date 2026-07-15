#!/usr/bin/env python3
"""
Random Sample Backtest — V5 Foundation Item #2.

Pulls a random sample of tickers from a pool, asks the user (or future LLM
integration) to provide a V4.3 verdict for each at a historical entry date,
measures the 5-year forward return via yfinance, and aggregates a hit rate
with Wilson 95% CI.

Status: scaffolding. Verdict generation is currently manual / stubbed. Once
FMP API + point-in-time fundamentals are wired in, the loop becomes fully
automated.

Usage:
    # Dry run — print sampled tickers without calling APIs
    python3 random_sample_backtest.py --pool sp500 --n 50 --seed 20260509 --dry-run

    # With saved verdict file (manually authored or LLM-generated):
    python3 random_sample_backtest.py --pool sp500 --n 50 --seed 20260509 \
        --verdicts cases/v5_round1_verdicts.json \
        --out V5_random_sample_50_2026-05-XX.md

Verdict file schema (per case):
    {
      "ticker": "AAPL",
      "entry_date": "2014-06-15",
      "verdict": "BUY" | "HOLD" | "SELL" | "VETO" | "PAPER_ONLY",
      "intrinsic_value": 95.50,
      "current_price_at_entry": 88.30,
      "data_quality_score": 8,        # Phase 0.7 score, x/9
      "auto_veto_triggered": false,
      "rationale_short": "..."
    }
"""

import argparse
import json
import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    from valuation_calc import wilson_ci
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from valuation_calc import wilson_ci


# ---- Sample pool loaders -----------------------------------------------------
# Curated minimal pool for scaffolding. Replace with FMP point-in-time
# constituents once API is wired.
POOL_SP500_2014 = [
    # 50-name representative slice of S&P 500 as of 2014; expand to full list
    # via FMP /v3/historical-sp500-constituents endpoint when API is configured.
    "AAPL", "MSFT", "JNJ", "WMT", "PG", "JPM", "XOM", "CVX", "PFE", "KO",
    "PEP", "MRK", "DIS", "V", "MA", "HD", "MCD", "BA", "CAT", "MMM",
    "GE", "T", "VZ", "CSCO", "INTC", "IBM", "ORCL", "QCOM", "TXN", "AMGN",
    "BMY", "ABT", "MDT", "GILD", "BIIB", "CMCSA", "NKE", "UNH", "WFC", "BAC",
    "C", "GS", "MS", "AXP", "USB", "COST", "TGT", "F", "GM", "DE",
]
POOL_NASDAQ100_2014 = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "FB", "INTC", "CSCO", "CMCSA", "NVDA",
    "QCOM", "AMGN", "GILD", "BIIB", "REGN", "ALXN", "ADBE", "PYPL", "NFLX",
    "ADP", "INTU", "ORLY", "ROST", "EA", "ATVI", "TXN", "AVGO", "MU", "AMAT",
    "KLAC", "MCHP", "FISV", "PAYX", "MAR", "SBUX", "MDLZ", "PEP", "WBA",
    "BMRN", "VRTX", "MNST",
]
POOL_HSI_2014 = [
    "0700.HK", "0939.HK", "1299.HK", "0941.HK", "0005.HK", "1398.HK",
    "0016.HK", "0883.HK", "0386.HK", "0857.HK", "0688.HK", "0001.HK",
    "0388.HK", "0011.HK", "0002.HK", "0017.HK", "1928.HK", "1109.HK",
    "0762.HK", "1113.HK", "0823.HK", "0066.HK", "0388.HK",
]

POOLS = {
    "sp500": POOL_SP500_2014,
    "nasdaq100": POOL_NASDAQ100_2014,
    "hsi": POOL_HSI_2014,
    "combined": list(set(POOL_SP500_2014 + POOL_NASDAQ100_2014 + POOL_HSI_2014)),
}


# ---- Sampling ----------------------------------------------------------------
def sample_tickers(pool: str, n: int, seed: int) -> list:
    """Reproducible random sample from a named pool."""
    if pool not in POOLS:
        raise ValueError(f"Unknown pool {pool!r}. Choose from {list(POOLS)}.")
    universe = POOLS[pool]
    if n > len(universe):
        raise ValueError(
            f"Sample size {n} exceeds pool size {len(universe)} for {pool!r}. "
            "Either reduce n or load a wider pool (FMP integration pending)."
        )
    rng = random.Random(seed)
    return sorted(rng.sample(universe, n))


def sample_entry_dates(tickers: list, year_min: int, year_max: int, seed: int) -> dict:
    """Each ticker gets a uniformly-random entry date inside [year_min, year_max]."""
    rng = random.Random(seed + 1)  # offset so dates aren't correlated with ticker draw
    out = {}
    for t in tickers:
        y = rng.randint(year_min, year_max)
        m = rng.randint(1, 12)
        d = rng.randint(1, 28)
        out[t] = date(y, m, d).isoformat()
    return out


# ---- Forward return ----------------------------------------------------------
def fetch_forward_return(ticker: str, entry_date: str, years: int = 5) -> dict:
    """
    Total return (entry_date → entry_date + years) via yfinance.
    Returns dict; pct return None if data missing or company delisted.
    """
    try:
        import yfinance as yf
    except ImportError:
        return {"error": "yfinance not installed; pip install yfinance"}

    start = datetime.fromisoformat(entry_date)
    end = start + timedelta(days=int(years * 365.25))

    try:
        data = yf.download(
            ticker, start=start.date().isoformat(), end=end.date().isoformat(),
            progress=False, auto_adjust=True, threads=False,
        )
        if data is None or data.empty or len(data) < 2:
            return {"error": "no_data", "ticker": ticker, "entry_date": entry_date}
        first = float(data["Close"].iloc[0].iloc[0] if hasattr(data["Close"].iloc[0], "iloc") else data["Close"].iloc[0])
        last = float(data["Close"].iloc[-1].iloc[0] if hasattr(data["Close"].iloc[-1], "iloc") else data["Close"].iloc[-1])
        return {
            "ticker": ticker, "entry_date": entry_date, "years": years,
            "entry_price": first, "exit_price": last,
            "total_return_pct": (last - first) / first * 100,
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker, "entry_date": entry_date}


# ---- Scoring -----------------------------------------------------------------
def score_case(verdict: dict, forward: dict, hit_threshold_pct: float = 0.0) -> str:
    """
    Map verdict + forward return to one of:
        HIT, PARTIAL, MISS, VETO_HIT, VETO_MISS, SKIP

    hit_threshold_pct: minimum forward return for BUY to count as HIT (default 0%).
    """
    if forward.get("error"):
        return "SKIP"

    fwd = forward["total_return_pct"]
    v = verdict["verdict"]

    if v == "BUY":
        if fwd > hit_threshold_pct:
            return "HIT"
        if -10 < fwd <= hit_threshold_pct:
            return "PARTIAL"
        return "MISS"
    if v in ("SELL", "VETO"):
        if fwd < -10:
            return "VETO_HIT"
        if fwd < hit_threshold_pct:
            return "PARTIAL"
        return "VETO_MISS"
    if v == "HOLD":
        if -10 <= fwd <= 30:
            return "HIT"
        return "PARTIAL"
    if v == "PAPER_ONLY":
        return "SKIP"
    return "SKIP"


def aggregate(scores: list) -> dict:
    """Hit rate + Wilson CI. PARTIAL counts as 0.5."""
    n = sum(1 for s in scores if s != "SKIP")
    hits = sum(1 for s in scores if s in ("HIT", "VETO_HIT"))
    partials = sum(1 for s in scores if s == "PARTIAL")

    if n == 0:
        return {"error": "no scoreable cases"}

    hit_score = hits + 0.5 * partials
    point_estimate = hit_score / n
    # Wilson CI uses integer count; fold partials into hits at 0.5 weight via rounding
    wilson_input = round(hit_score)
    ci = wilson_ci(wilson_input, n, 0.95)

    return {
        "n_total": len(scores),
        "n_scored": n,
        "n_skipped": len(scores) - n,
        "hits": hits,
        "partials": partials,
        "misses": sum(1 for s in scores if s in ("MISS", "VETO_MISS")),
        "hit_rate": point_estimate,
        "wilson_lower": ci["lower"],
        "wilson_upper": ci["upper"],
        "ci_width": ci["ci_width"],
        "ci_interpretation": ci["interpretation"],
        "formatted": (
            f"{point_estimate*100:.1f}% [{ci['lower']*100:.1f}%, {ci['upper']*100:.1f}%] "
            f"(n={n}, 95% CI; PARTIAL=0.5)"
        ),
    }


# ---- CLI ---------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pool", default="sp500", choices=list(POOLS), help="Sampling pool (default: sp500)")
    p.add_argument("--n", type=int, default=50, help="Sample size (default: 50)")
    p.add_argument("--seed", type=int, default=20260509, help="RNG seed for reproducibility")
    p.add_argument("--year-min", type=int, default=2014, help="Earliest entry year (default: 2014)")
    p.add_argument("--year-max", type=int, default=2018, help="Latest entry year (default: 2018)")
    p.add_argument("--years-forward", type=int, default=5, help="Forward return window (default: 5)")
    p.add_argument("--dry-run", action="store_true", help="Print sample only, don't fetch returns")
    p.add_argument("--verdicts", help="Path to verdicts JSON file (one entry per ticker)")
    p.add_argument("--out", help="Output markdown path for the scorecard")
    args = p.parse_args()

    tickers = sample_tickers(args.pool, args.n, args.seed)
    entries = sample_entry_dates(tickers, args.year_min, args.year_max, args.seed)

    print(f"Sampled {len(tickers)} from pool={args.pool!r} seed={args.seed}")
    for t in tickers[:10]:
        print(f"  {t} → entry {entries[t]}")
    if len(tickers) > 10:
        print(f"  … and {len(tickers) - 10} more")

    if args.dry_run:
        print("\n[dry-run] No verdicts loaded, no returns fetched. Exiting.")
        sys.exit(0)

    # Load verdicts
    verdicts = {}
    if args.verdicts:
        with open(args.verdicts) as f:
            data = json.load(f)
        for entry in data:
            verdicts[entry["ticker"]] = entry
    else:
        print(
            "\n⚠️  No --verdicts file passed. Cannot score without verdicts.\n"
            "    Generate verdicts via V4.3 pipeline (manual or future LLM integration),\n"
            "    save as JSON list, and re-run with --verdicts cases/<file>.json"
        )
        sys.exit(1)

    # Score each case
    print("\nFetching forward returns + scoring …")
    rows = []
    for t in tickers:
        if t not in verdicts:
            print(f"  {t}: no verdict, skipping")
            rows.append({"ticker": t, "entry": entries[t], "score": "SKIP", "reason": "no_verdict"})
            continue
        fwd = fetch_forward_return(t, entries[t], args.years_forward)
        s = score_case(verdicts[t], fwd)
        rows.append({"ticker": t, "entry": entries[t], "verdict": verdicts[t]["verdict"],
                     "forward": fwd, "score": s})
        marker = {"HIT": "✅", "VETO_HIT": "✅", "PARTIAL": "🟡",
                  "MISS": "❌", "VETO_MISS": "❌", "SKIP": "⏭️"}.get(s, "?")
        print(f"  {marker} {t} ({verdicts[t]['verdict']:8s}) → {s}")

    summary = aggregate([r["score"] for r in rows])
    print(f"\n=== AGGREGATE ===\n{summary['formatted']}")
    print(f"Interpretation: {summary['ci_interpretation']}")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            f.write(f"# V5 Random Sample Backtest — {date.today().isoformat()}\n\n")
            f.write(f"- Pool: `{args.pool}`  Seed: `{args.seed}`  N: {args.n}\n")
            f.write(f"- Entry window: {args.year_min}–{args.year_max}  Forward: {args.years_forward}y\n\n")
            f.write(f"## Aggregate\n\n**{summary['formatted']}**\n\n")
            f.write(f"- {summary['ci_interpretation']}\n")
            f.write(f"- Hits: {summary['hits']} / Partials: {summary['partials']} / Misses: {summary['misses']} / Skipped: {summary['n_skipped']}\n\n")
            f.write("## Per-Case\n\n| Ticker | Entry | Verdict | Score |\n|---|---|---|---|\n")
            for r in rows:
                f.write(f"| {r['ticker']} | {r['entry']} | {r.get('verdict', '—')} | {r['score']} |\n")
        print(f"\n📝 Scorecard written: {out_path}")


if __name__ == "__main__":
    main()
