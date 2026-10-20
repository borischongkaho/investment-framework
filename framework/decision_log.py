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

Storage: <investment_dir>/decision_log/decisions.json (single source of truth)
         resolved via BT_DECISIONS_PATH env var, else config.py (default ./data/decision_log/decisions.json)

Usage:
    python3 decision_log.py list
    python3 decision_log.py add < decision.json
    python3 decision_log.py mark-exit TICKER YYYY-MM-DD PRICE
    python3 decision_log.py enrich          # re-fetch realized returns
    python3 decision_log.py seed            # write the EXAMPLE decisions (edit seed_from_portfolio() first)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def _resolve_decisions_path() -> Path:
    override = os.environ.get("BT_DECISIONS_PATH")
    if override:
        return Path(override).expanduser()
    try:
        from config import load as load_config
        return load_config().decisions_path
    except Exception:
        return Path(__file__).resolve().parent.parent / "data" / "decision_log" / "decisions.json"


DECISIONS_PATH = _resolve_decisions_path()


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
    Bootstrap the ledger with EXAMPLE decisions (fake data — edit before use).
    Entry dates marked 'estimated' need user confirmation before backtest is reliable.
    """
    # EXAMPLE seed — FAKE, round-number positions for demonstration only.
    # Replace with your own history, or skip `seed` entirely and use `add` with your real decisions.
    seed_data = [
        {
            "ticker": "AAPL", "action": "BUY",
            "entry_date": "2025-01-15",
            "entry_price": 180.00, "shares": 48,
            "intrinsic_value": 230, "expected_return": 0.28,
            "sector": "tech", "asset_class": "equity",
            "thesis_tag": "Example — ecosystem moat, services mix shift",
            "thesis_summary": "Illustrative entry; replace with your own thesis",
            "horizon_years": 5,
            "data_quality": "confirmed",
        },
        {
            "ticker": "MSFT", "action": "BUY",
            "entry_date": "2025-06-01",  # ESTIMATED — user to confirm
            "entry_price": 400.00, "shares": 20,
            "intrinsic_value": 520, "expected_return": 0.30,
            "sector": "tech", "asset_class": "equity",
            "thesis_tag": "Example — cloud + AI platform",
            "horizon_years": 5,
            "data_quality": "entry_date_estimated",
        },
        # Closed position (exercises the post-mortem / realized_return path)
        {
            "ticker": "XOM", "action": "BUY",
            "entry_date": "2024-03-01",
            "entry_price": 100.00, "shares": 50,
            "exit_date": "2025-03-01", "exit_price": 110.00, "status": "CLOSED",
            "realized_return": (110.00 - 100.00) / 100.00,
            "sector": "energy", "asset_class": "equity",
            "thesis_tag": "Example — closed at pre-committed trigger",
            "horizon_years": 5,
            "data_quality": "confirmed",
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
