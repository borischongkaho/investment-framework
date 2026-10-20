#!/usr/bin/env python3
"""
FMP (Financial Modeling Prep) API client - STABLE endpoint version.

Updated 2026-05-19: /api/v3/ legacy endpoints deprecated for new users.
Now uses /stable/ endpoint structure with ?symbol= query params.

Setup (either):
    export FMP_API_KEY=your_key_here            # env var always wins
    # or write it to $BT_CONFIG_DIR/fmp.env (default ~/.config/boris-investment/fmp.env):
        FMP_API_KEY=your_key_here

Usage examples:
    python fmp_client.py profile NVDA
    python fmp_client.py quote NVDA
    python fmp_client.py income NVDA --years 5
    python fmp_client.py ratios NVDA
    python fmp_client.py dcf NVDA
    python fmp_client.py transcript NVDA --year 2026 --quarter 1
    python fmp_client.py insider NVDA
    python fmp_client.py screener --market-cap-min 5000000000 --pe-max 15
"""

import os
import sys
import json
import argparse
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error


CONFIG_DIR = Path(os.environ.get("BT_CONFIG_DIR") or (Path.home() / ".config" / "boris-investment")).expanduser()
CONFIG_PATH = CONFIG_DIR / "fmp.env"
FMP_BASE = "https://financialmodelingprep.com/stable"


def load_api_key(required=True):
    """FMP API key: FMP_API_KEY env var first, then CONFIG_PATH (KEY=value lines).

    Shared by valuation_inputs.py / wacc_calc.py / pool_screen_capm.py.
    Missing key -> exit 1 (or return None when required=False).
    """
    key = (os.environ.get("FMP_API_KEY") or "").strip()
    if key and key != "YOUR_API_KEY_HERE":
        return key
    if CONFIG_PATH.exists():
        for line in CONFIG_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith("FMP_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key and key != "YOUR_API_KEY_HERE":
                    return key
    if not required:
        return None
    print(f"ERROR: FMP_API_KEY not set — export FMP_API_KEY=... or write it to {CONFIG_PATH}", file=sys.stderr)
    sys.exit(1)


def fmp_get(endpoint, params=None):
    """Make a GET request to FMP /stable/ API."""
    api_key = load_api_key()
    url = f"{FMP_BASE}/{endpoint}"

    if params is None:
        params = {}
    params["apikey"] = api_key

    qs = urllib.parse.urlencode(params)
    full_url = f"{url}?{qs}"

    try:
        with urllib.request.urlopen(full_url, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        if e.code == 401:
            print(f"401: API key invalid", file=sys.stderr)
        elif e.code == 402:
            print(f"402: Endpoint requires PAID tier - {body[:300]}", file=sys.stderr)
        elif e.code == 403:
            print(f"403: Forbidden - {body[:300]}", file=sys.stderr)
        elif e.code == 429:
            print(f"429: Rate limit (250 calls/day on free)", file=sys.stderr)
        else:
            print(f"HTTP {e.code}: {e.reason} - {body[:300]}", file=sys.stderr)
        return {"_error": f"HTTP {e.code}", "_body": body[:300]}
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return {"_error": str(e)}


# ─── Core ───────────────────────────────────────────────────────

def get_profile(ticker):
    return fmp_get("profile", {"symbol": ticker.upper()})


def get_quote(ticker):
    return fmp_get("quote", {"symbol": ticker.upper()})


def get_search_symbol(query):
    return fmp_get("search-symbol", {"query": query})


def get_search_name(query):
    return fmp_get("search-name", {"query": query})


# ─── Financial Statements ───────────────────────────────────────

def get_income_statement(ticker, limit=5, period="annual"):
    return fmp_get("income-statement", {"symbol": ticker.upper(), "limit": limit, "period": period})


def get_balance_sheet(ticker, limit=5, period="annual"):
    return fmp_get("balance-sheet-statement", {"symbol": ticker.upper(), "limit": limit, "period": period})


def get_cash_flow(ticker, limit=5, period="annual"):
    return fmp_get("cash-flow-statement", {"symbol": ticker.upper(), "limit": limit, "period": period})


# ─── Ratios & Metrics ───────────────────────────────────────────

def get_ratios(ticker, limit=5, period="annual"):
    return fmp_get("ratios", {"symbol": ticker.upper(), "limit": limit, "period": period})


def get_ratios_ttm(ticker):
    return fmp_get("ratios-ttm", {"symbol": ticker.upper()})


def get_key_metrics(ticker, limit=5, period="annual"):
    return fmp_get("key-metrics", {"symbol": ticker.upper(), "limit": limit, "period": period})


def get_key_metrics_ttm(ticker):
    return fmp_get("key-metrics-ttm", {"symbol": ticker.upper()})


def get_financial_growth(ticker, limit=5):
    return fmp_get("financial-growth", {"symbol": ticker.upper(), "limit": limit})


def get_financial_score(ticker):
    """Piotroski + Altman Z scores."""
    return fmp_get("financial-score", {"symbol": ticker.upper()})


# ─── Valuation ──────────────────────────────────────────────────

def get_dcf(ticker):
    return fmp_get("discounted-cash-flow", {"symbol": ticker.upper()})


def get_advanced_dcf(ticker):
    return fmp_get("advanced-discounted-cash-flow", {"symbol": ticker.upper()})


def get_owner_earnings(ticker):
    return fmp_get("owner-earnings", {"symbol": ticker.upper()})


# ─── Analyst & Estimates ────────────────────────────────────────

def get_analyst_estimates(ticker, period="annual"):
    return fmp_get("analyst-estimates", {"symbol": ticker.upper(), "period": period})


def get_price_target_consensus(ticker):
    return fmp_get("price-target-consensus", {"symbol": ticker.upper()})


def get_price_target_news(ticker, limit=20):
    return fmp_get("price-target-news", {"symbol": ticker.upper(), "limit": limit})


def get_upgrades_downgrades(ticker, limit=20):
    return fmp_get("grades-news", {"symbol": ticker.upper(), "limit": limit})


def get_ratings_snapshot(ticker):
    return fmp_get("ratings-snapshot", {"symbol": ticker.upper()})


# ─── Earnings ────────────────────────────────────────────────────

def get_earnings_calendar(ticker):
    return fmp_get("earnings", {"symbol": ticker.upper()})


def get_earnings_transcript(ticker, year, quarter):
    return fmp_get("earning-call-transcript", {"symbol": ticker.upper(), "year": year, "quarter": quarter})


def get_earnings_transcript_dates(ticker):
    return fmp_get("earning-call-transcript-dates", {"symbol": ticker.upper()})


# ─── Insider & Institutional ────────────────────────────────────

def get_insider_trading(ticker, limit=20):
    return fmp_get("insider-trading", {"symbol": ticker.upper(), "limit": limit})


def get_insider_trading_search(symbol=None, name=None, limit=20):
    params = {"limit": limit}
    if symbol: params["symbol"] = symbol.upper()
    if name: params["name"] = name
    return fmp_get("insider-trading", params)


def get_institutional_holders(ticker):
    return fmp_get("institutional-ownership/institutional-holders", {"symbol": ticker.upper()})


def get_etf_holders(ticker):
    return fmp_get("etf-holdings", {"symbol": ticker.upper()})


# ─── Senate / House Trading ─────────────────────────────────────

def get_senate_trading(symbol=None):
    params = {}
    if symbol: params["symbol"] = symbol.upper()
    return fmp_get("senate-trading-activity", params)


def get_house_trading(symbol=None):
    params = {}
    if symbol: params["symbol"] = symbol.upper()
    return fmp_get("house-disclosure", params)


# ─── SEC & News ──────────────────────────────────────────────────

def get_sec_filings(ticker, limit=20):
    return fmp_get("sec-filings-search/symbol", {"symbol": ticker.upper(), "limit": limit})


def get_sec_filings_by_type(ticker, filing_type, limit=20):
    """e.g. 8-K, 10-Q, 10-K, 4 (Form 4)"""
    return fmp_get("sec-filings-search/symbol", {"symbol": ticker.upper(), "type": filing_type, "limit": limit})


def get_stock_news(ticker, limit=20):
    return fmp_get("news/stock", {"symbols": ticker.upper(), "limit": limit})


def get_press_releases(ticker, limit=20):
    return fmp_get("news/press-releases", {"symbols": ticker.upper(), "limit": limit})


# ─── Peers & Screener ────────────────────────────────────────────

def get_peers(ticker):
    return fmp_get("stock-peers", {"symbol": ticker.upper()})


def stock_screener(**criteria):
    """Screener criteria keys:
        marketCapMoreThan, marketCapLowerThan
        priceMoreThan, priceLowerThan
        betaMoreThan, betaLowerThan
        volumeMoreThan
        dividendMoreThan
        sector, industry, exchange
        country, isEtf, isActivelyTrading
        limit
    """
    return fmp_get("company-screener", criteria)


# ─── Dividends ───────────────────────────────────────────────────

def get_dividend_history(ticker, limit=20):
    return fmp_get("dividends", {"symbol": ticker.upper(), "limit": limit})


# ─── Historical Price ───────────────────────────────────────────

def get_historical_eod(ticker, from_date=None, to_date=None):
    params = {"symbol": ticker.upper()}
    if from_date: params["from"] = from_date
    if to_date: params["to"] = to_date
    return fmp_get("historical-price-eod/full", params)


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FMP /stable/ API client v2")
    sub = parser.add_subparsers(dest="command")

    # Single-ticker commands
    for cmd in ["profile", "quote", "ratios", "ratios-ttm", "key-metrics", "key-metrics-ttm",
                "dcf", "advanced-dcf", "owner-earnings", "financial-growth", "financial-score",
                "analyst-estimates", "price-target", "ratings",
                "earnings-calendar", "earnings-dates",
                "insider", "institutional", "etf-holders", "peers",
                "sec-filings", "stock-news", "press-releases", "dividend-history",
                "upgrades-downgrades"]:
        s = sub.add_parser(cmd)
        s.add_argument("ticker")
        if cmd in ["sec-filings", "stock-news", "press-releases", "insider", "dividend-history",
                   "upgrades-downgrades"]:
            s.add_argument("--limit", type=int, default=20)

    # Statements (with years arg)
    for cmd in ["income", "balance", "cashflow"]:
        s = sub.add_parser(cmd)
        s.add_argument("ticker")
        s.add_argument("--years", type=int, default=5)
        s.add_argument("--period", default="annual", choices=["annual", "quarter"])

    # Transcript
    s = sub.add_parser("transcript")
    s.add_argument("ticker")
    s.add_argument("--year", type=int, required=True)
    s.add_argument("--quarter", type=int, required=True)

    # SEC filings by type
    s = sub.add_parser("sec-by-type")
    s.add_argument("ticker")
    s.add_argument("type", help="e.g. 8-K, 10-Q, 10-K, 4")
    s.add_argument("--limit", type=int, default=20)

    # Senate / House
    s = sub.add_parser("senate")
    s.add_argument("--symbol", default=None)
    s = sub.add_parser("house")
    s.add_argument("--symbol", default=None)

    # Search
    s = sub.add_parser("search-symbol")
    s.add_argument("query")
    s = sub.add_parser("search-name")
    s.add_argument("query")

    # Screener
    s = sub.add_parser("screener")
    s.add_argument("--market-cap-min", type=int)
    s.add_argument("--market-cap-max", type=int)
    s.add_argument("--price-min", type=float)
    s.add_argument("--price-max", type=float)
    s.add_argument("--beta-max", type=float)
    s.add_argument("--sector")
    s.add_argument("--industry")
    s.add_argument("--country", default="US")
    s.add_argument("--limit", type=int, default=50)

    # Historical EOD
    s = sub.add_parser("historical")
    s.add_argument("ticker")
    s.add_argument("--from", dest="from_date", default=None)
    s.add_argument("--to", dest="to_date", default=None)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Dispatch
    result = None
    if args.command == "profile": result = get_profile(args.ticker)
    elif args.command == "quote": result = get_quote(args.ticker)
    elif args.command == "ratios": result = get_ratios(args.ticker)
    elif args.command == "ratios-ttm": result = get_ratios_ttm(args.ticker)
    elif args.command == "key-metrics": result = get_key_metrics(args.ticker)
    elif args.command == "key-metrics-ttm": result = get_key_metrics_ttm(args.ticker)
    elif args.command == "dcf": result = get_dcf(args.ticker)
    elif args.command == "advanced-dcf": result = get_advanced_dcf(args.ticker)
    elif args.command == "owner-earnings": result = get_owner_earnings(args.ticker)
    elif args.command == "financial-growth": result = get_financial_growth(args.ticker)
    elif args.command == "financial-score": result = get_financial_score(args.ticker)
    elif args.command == "analyst-estimates": result = get_analyst_estimates(args.ticker)
    elif args.command == "price-target": result = get_price_target_consensus(args.ticker)
    elif args.command == "ratings": result = get_ratings_snapshot(args.ticker)
    elif args.command == "earnings-calendar": result = get_earnings_calendar(args.ticker)
    elif args.command == "earnings-dates": result = get_earnings_transcript_dates(args.ticker)
    elif args.command == "insider": result = get_insider_trading(args.ticker, args.limit)
    elif args.command == "institutional": result = get_institutional_holders(args.ticker)
    elif args.command == "etf-holders": result = get_etf_holders(args.ticker)
    elif args.command == "peers": result = get_peers(args.ticker)
    elif args.command == "sec-filings": result = get_sec_filings(args.ticker, args.limit)
    elif args.command == "sec-by-type": result = get_sec_filings_by_type(args.ticker, args.type, args.limit)
    elif args.command == "stock-news": result = get_stock_news(args.ticker, args.limit)
    elif args.command == "press-releases": result = get_press_releases(args.ticker, args.limit)
    elif args.command == "dividend-history": result = get_dividend_history(args.ticker, args.limit)
    elif args.command == "upgrades-downgrades": result = get_upgrades_downgrades(args.ticker, args.limit)
    elif args.command == "income": result = get_income_statement(args.ticker, args.years, args.period)
    elif args.command == "balance": result = get_balance_sheet(args.ticker, args.years, args.period)
    elif args.command == "cashflow": result = get_cash_flow(args.ticker, args.years, args.period)
    elif args.command == "transcript": result = get_earnings_transcript(args.ticker, args.year, args.quarter)
    elif args.command == "senate": result = get_senate_trading(args.symbol)
    elif args.command == "house": result = get_house_trading(args.symbol)
    elif args.command == "search-symbol": result = get_search_symbol(args.query)
    elif args.command == "search-name": result = get_search_name(args.query)
    elif args.command == "historical": result = get_historical_eod(args.ticker, args.from_date, args.to_date)
    elif args.command == "screener":
        criteria = {}
        if args.market_cap_min: criteria["marketCapMoreThan"] = args.market_cap_min
        if args.market_cap_max: criteria["marketCapLowerThan"] = args.market_cap_max
        if args.price_min: criteria["priceMoreThan"] = args.price_min
        if args.price_max: criteria["priceLowerThan"] = args.price_max
        if args.beta_max: criteria["betaLowerThan"] = args.beta_max
        if args.sector: criteria["sector"] = args.sector
        if args.industry: criteria["industry"] = args.industry
        if args.country: criteria["country"] = args.country
        criteria["limit"] = args.limit
        criteria["isActivelyTrading"] = "true"
        result = stock_screener(**criteria)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
