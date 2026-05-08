#!/usr/bin/env python3
"""
Decision Log — Append-only record of every BUY/SELL/HOLD decision.

Each decision captures:
- ticker, action, entry_date, entry_price, shares
- thesis_summary (1-2 sentences)
- intrinsic_value at decision time
- expected_return + horizon
- sector, asset_class

Auto-enriched after 1Y / 2Y / 3Y with realized alpha + reflection prompt.

Storage: ~/Developer/investment/decision_log/decisions.json (single source of truth)

Usage:
    python3 decision_log.py list
    python3 decision_log.py add < decision.json
    python3 decision_log.py mark-exit TICKER YYYY-MM-DD PRICE
    python3 decision_log.py enrich          # re-fetch realized returns
    python3 decision_log.py seed            # bootstrap from portfolio.md known data
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HOME = Path.home()
DECISIONS_PATH = HOME / "Developer" / "investment" / "decision_log" / "decisions.json"


def load_decisions() -> list:
    if not DECISIONS_PATH.exists():
        return []
    return json.loads(DECISIONS_PATH.read_text())


def save_decisions(decisions: list):
    DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DECISIONS_PATH.write_text(json.dumps(decisions, indent=2, default=str))


def add_decision(payload: dict) -> dict:
    """
    Add a new decision. Required fields:
    ticker, action, entry_date, entry_price, shares, thesis_tag

    Optional: intrinsic_value, expected_return, horizon_years, sector, asset_class
    """
    required = {"ticker", "action", "entry_date", "entry_price", "shares", "thesis_tag"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    decisions = load_decisions()

    record = {
        "id": f"{payload['ticker']}-{payload['entry_date']}-{payload['action']}",
        "ticker": payload["ticker"].upper(),
        "action": payload["action"].upper(),
        "entry_date": payload["entry_date"],
        "entry_price": float(payload["entry_price"]),
        "shares": float(payload["shares"]),
        "intrinsic_value": payload.get("intrinsic_value"),
        "expected_return": payload.get("expected_return"),
        "horizon_years": payload.get("horizon_years", 5),
        "sector": payload.get("sector", "tech"),
        "asset_class": payload.get("asset_class", "equity"),
        "thesis_tag": payload.get("thesis_tag", ""),
        "thesis_summary": payload.get("thesis_summary", ""),
        "research_memo": payload.get("research_memo"),
        "exit_date": payload.get("exit_date"),
        "exit_price": payload.get("exit_price"),
        "status": payload.get("status", "HOLDING"),
        "data_quality": payload.get("data_quality", "confirmed"),
        # V4.0 Action Gate fields — track cool-down enforcement
        "gate_passed_at": payload.get("gate_passed_at"),  # ISO timestamp when 3-model audit passed
        "gate_audit_results": payload.get("gate_audit_results"),  # {"claude": "PASS", "gpt": "FLAG", "gemini": "PASS"}
        "gate_flag_rationale": payload.get("gate_flag_rationale"),  # the user's "why I disagreed" if any FLAG
        "cool_down_until": payload.get("cool_down_until"),  # ISO timestamp; if set, can't execute before this
        "created_at": datetime.now().isoformat(),
    }

    if any(d["id"] == record["id"] for d in decisions):
        raise ValueError(f"Decision already exists: {record['id']}")

    decisions.append(record)
    save_decisions(decisions)
    return record


def mark_exit(ticker: str, exit_date: str, exit_price: float):
    """Mark the latest open position for a ticker as exited."""
    decisions = load_decisions()
    for d in reversed(decisions):
        if d["ticker"] == ticker.upper() and d["status"] == "HOLDING":
            d["exit_date"] = exit_date
            d["exit_price"] = exit_price
            d["status"] = "CLOSED"
            d["realized_return"] = (exit_price - d["entry_price"]) / d["entry_price"]
            save_decisions(decisions)
            return d
    raise ValueError(f"No open position found for {ticker}")


def list_decisions():
    decisions = load_decisions()
    if not decisions:
        print("(no decisions logged)")
        return
    print(f"Total: {len(decisions)} decisions\n")
    for d in decisions:
        status_icon = {"HOLDING": "🟢", "CLOSED": "✅", "WATCHLIST": "👀"}.get(d["status"], "•")
        line = (
            f"{status_icon} {d['ticker']:6} {d['action']:4} "
            f"{d['entry_date']} @ ${d['entry_price']:>8.2f} "
            f"x {d['shares']:>6.2f}  [{d['sector']}]"
        )
        if d.get("data_quality") != "confirmed":
            line += f"  ⚠️ {d['data_quality']}"
        if d["status"] == "CLOSED":
            line += f"  → exit {d['exit_date']} @ ${d['exit_price']:.2f}"
        print(line)


def seed_from_portfolio():
    """
    Bootstrap from known portfolio.md data.
    Entry dates marked 'estimated' need user confirmation before backtest is reliable.
    """
    seed_data = [
        # Active US equity holdings
        {
            "ticker": "NVDA", "action": "BUY",
            "entry_date": "2024-11-01",  # ESTIMATED — user to confirm
            "entry_price": 118.44, "shares": 108,
            "intrinsic_value": 163, "expected_return": 0.40,
            "sector": "tech", "asset_class": "equity",
            "thesis_tag": "AI infrastructure leader, CUDA moat",
            "thesis_summary": "AI compute leader, CUDA ecosystem lock-in, fabless 100% ROIC",
            "horizon_years": 5,
            "data_quality": "entry_date_estimated",
        },
        {
            "ticker": "WEX", "action": "BUY",
            "entry_date": "2026-05-04",
            "entry_price": 152.57, "shares": 65,
            "intrinsic_value": 200, "expected_return": 0.30,
            "sector": "financials", "asset_class": "equity",
            "thesis_tag": "Mid-cap fleet card + EV transition",
            "thesis_summary": "EV transition fear mispriced; Q1 confirms thesis",
            "horizon_years": 5,
            "data_quality": "confirmed",
        },
        {
            "ticker": "GIS", "action": "BUY",
            "entry_date": "2026-05-04",
            "entry_price": 34.62, "shares": 100,
            "sector": "consumer_staples", "asset_class": "equity",
            "thesis_tag": "Consumer staples value",
            "horizon_years": 5,
            "data_quality": "confirmed",
        },
        # Crypto
        {
            "ticker": "BTC-USD", "action": "BUY",
            "entry_date": "2024-01-15",  # ESTIMATED
            "entry_price": 53382.32, "shares": 0.23649861,
            "sector": "crypto", "asset_class": "crypto",
            "thesis_tag": "Digital gold, macro hedge",
            "horizon_years": 7,
            "data_quality": "entry_date_estimated",
        },
        {
            "ticker": "ETH-USD", "action": "BUY",
            "entry_date": "2024-03-01",  # ESTIMATED — known underwater from prior cycle
            "entry_price": 3288.50, "shares": 5.5170138,
            "sector": "crypto", "asset_class": "crypto",
            "thesis_tag": "Programmable L1, DeFi infra",
            "horizon_years": 5,
            "data_quality": "entry_date_estimated",
        },
        {
            "ticker": "BNB-USD", "action": "BUY",
            "entry_date": "2024-06-01",  # ESTIMATED
            "entry_price": 342.91, "shares": 0.681,
            "sector": "crypto", "asset_class": "crypto",
            "thesis_tag": "Binance ecosystem token (small position)",
            "horizon_years": 3,
            "data_quality": "entry_date_estimated",
        },
        # Closed positions (post-mortem)
        {
            "ticker": "FISV", "action": "BUY",
            "entry_date": "2026-04-14",
            "entry_price": 58.86, "shares": 235,
            "exit_date": "2026-05-04", "exit_price": 63.00, "status": "CLOSED",
            "realized_return": (63.00 - 58.86) / 58.86,
            "sector": "financials", "asset_class": "equity",
            "thesis_tag": "Payments platform — V2.0 trim trigger validated",
            "horizon_years": 5,
            "data_quality": "confirmed",
        },
        {
            "ticker": "NVO", "action": "BUY",
            "entry_date": "2024-12-01",  # ESTIMATED
            "entry_price": 39.20, "shares": 229,
            "exit_date": "2026-04-10", "exit_price": 37.76, "status": "CLOSED",
            "realized_return": (37.76 - 39.20) / 39.20,
            "sector": "healthcare", "asset_class": "equity",
            "thesis_tag": "GLP-1 leader — thesis broken (CagriSema + Lilly)",
            "horizon_years": 5,
            "data_quality": "entry_date_estimated",
        },
        {
            "ticker": "BMY", "action": "BUY",
            "entry_date": "2024-12-01",  # ESTIMATED
            "entry_price": 58.90, "shares": 85,
            "exit_date": "2026-04-10", "exit_price": 58.62, "status": "CLOSED",
            "realized_return": (58.62 - 58.90) / 58.90,
            "sector": "healthcare", "asset_class": "equity",
            "thesis_tag": "Pharma value — patent cliff catch failed",
            "horizon_years": 5,
            "data_quality": "entry_date_estimated",
        },
    ]

    decisions = load_decisions()
    existing_ids = {d["id"] for d in decisions}

    added = 0
    skipped = 0
    for entry in seed_data:
        candidate_id = f"{entry['ticker']}-{entry['entry_date']}-{entry['action']}"
        if candidate_id in existing_ids:
            skipped += 1
            continue
        try:
            add_decision(entry)
            added += 1
        except ValueError as e:
            print(f"  ⚠️  {entry['ticker']}: {e}")

    print(f"✅ Seeded {added} decisions ({skipped} already existed)")
    print(f"\n⚠️  Decisions with estimated entry dates need user confirm:")
    for d in load_decisions():
        if d.get("data_quality") == "entry_date_estimated":
            print(f"   • {d['ticker']:8} entry: {d['entry_date']} ← please confirm")


def main():
    parser = argparse.ArgumentParser(description="Decision log management")
    parser.add_argument("cmd", choices=["list", "add", "mark-exit", "seed", "enrich"])
    parser.add_argument("args", nargs="*")
    args = parser.parse_args()

    try:
        if args.cmd == "list":
            list_decisions()
        elif args.cmd == "seed":
            seed_from_portfolio()
        elif args.cmd == "add":
            stdin_data = sys.stdin.read().strip()
            if not stdin_data:
                print("❌ Error: 'add' expects JSON on stdin. Pipe a JSON object in.", file=sys.stderr)
                sys.exit(1)
            try:
                payload = json.loads(stdin_data)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}", file=sys.stderr)
                sys.exit(1)
            rec = add_decision(payload)
            print(f"✅ Added: {rec['id']}")
        elif args.cmd == "mark-exit":
            if len(args.args) != 3:
                print("Usage: mark-exit TICKER YYYY-MM-DD PRICE", file=sys.stderr)
                sys.exit(1)
            rec = mark_exit(args.args[0], args.args[1], float(args.args[2]))
            print(f"✅ Closed: {rec['id']} → return {rec['realized_return']*100:.1f}%")
        elif args.cmd == "enrich":
            print("(enrich: re-fetches realized returns at 1Y/2Y/3Y marks — TBD)")
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
