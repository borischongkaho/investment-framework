#!/usr/bin/env python3
"""
Forward Prediction Tracker — V5 Foundation Item #4.

Why this exists:
    Backtest hit rates are hindsight. The only honest evidence that a
    valuation framework adds alpha is *forward* — locking in predictions
    today and verifying them at fixed checkpoints (3 / 6 / 9 / 12 months).
    Everything else is post-hoc rationalisation.

What this module does:
    1. lock_prediction(...)  — at each V4.3 verdict, persist the prediction
       (verdict + IV distribution + price + horizon) to an append-only JSON file.
    2. auto_update_checkpoints(...) — for each prediction whose 3 / 6 / 9 / 12
       month checkpoint is past due, fetch the actual price via yfinance and
       record it. Idempotent.
    3. calibration_report(...) — aggregate predicted return vs actual return
       per verdict type, per checkpoint horizon. Outputs Wilson CI on hit rate
       plus a calibration table (predicted decile → mean actual return).

Storage:
    A single JSON array at config.forward_predictions_path. Append-only —
    never delete a prediction; only update its `checkpoints` sub-object as
    time passes.

CLI:
    python3 forward_tracker.py lock --ticker NVDA --verdict TRIM \
        --price 215.80 --iv-p50 200 --iv-p5 165 --iv-p95 240 \
        --mos -7.3 --predicted-12m -7.0
    python3 forward_tracker.py checkpoints              # auto-update all due
    python3 forward_tracker.py report                   # print calibration
    python3 forward_tracker.py list --status active     # what's still tracking
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


# ---- Path resolution ---------------------------------------------------------
def _resolve_path(override: Optional[str]) -> Path:
    if override:
        return Path(override).expanduser()
    try:
        from config import load as load_config
        return load_config().forward_predictions_path
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from config import load as load_config
        return load_config().forward_predictions_path


# ---- Storage primitives ------------------------------------------------------
def _load(path: Path) -> list:
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _save(path: Path, predictions: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(predictions, f, indent=2, default=str)


def _next_id(existing: list, ticker: str) -> str:
    today = date.today().isoformat()
    same_day_same_ticker = sum(
        1 for p in existing
        if p["ticker"] == ticker and p["locked_at"].startswith(today)
    )
    suffix = f"-{same_day_same_ticker + 1:02d}" if same_day_same_ticker else ""
    return f"PRED-{today}-{ticker}{suffix}"


# ---- Prediction lifecycle ----------------------------------------------------
def lock_prediction(
    *,
    ticker: str,
    verdict: str,
    entry_price: float,
    iv_p50: float,
    iv_p5: Optional[float] = None,
    iv_p95: Optional[float] = None,
    mos_pct: Optional[float] = None,
    predicted_12m_return_pct: Optional[float] = None,
    data_quality_score: Optional[int] = None,
    auto_veto_triggered: bool = False,
    phase9_pass: bool = True,
    framework_version: str = "v5.0.0-alpha",
    rationale_link: Optional[str] = None,
    storage_path: Optional[str] = None,
) -> dict:
    """Append a new prediction. Returns the stored payload."""
    valid_verdicts = {"BUY", "HOLD", "SELL", "TRIM", "ADD", "VETO", "PAPER_ONLY"}
    if verdict not in valid_verdicts:
        raise ValueError(f"verdict must be one of {sorted(valid_verdicts)}, got {verdict!r}")
    if entry_price <= 0:
        raise ValueError(f"entry_price must be positive, got {entry_price}")
    if iv_p50 <= 0:
        raise ValueError(f"iv_p50 must be positive, got {iv_p50}")

    # Default MoS to (p50 - price) / price if not given
    if mos_pct is None:
        mos_pct = (iv_p50 - entry_price) / entry_price * 100

    locked_at = datetime.now().isoformat(timespec="seconds")
    locked_date = date.fromisoformat(locked_at[:10])

    prediction = {
        "ticker": ticker.upper(),
        "verdict": verdict,
        "locked_at": locked_at,
        "entry_price": entry_price,
        "iv_p50": iv_p50,
        "iv_p5": iv_p5,
        "iv_p95": iv_p95,
        "mos_pct": mos_pct,
        "predicted_12m_return_pct": predicted_12m_return_pct,
        "data_quality_score": data_quality_score,
        "auto_veto_triggered": auto_veto_triggered,
        "phase9_pass": phase9_pass,
        "framework_version": framework_version,
        "rationale_link": rationale_link,
        "checkpoints": {
            label: {
                "due_date": (locked_date + timedelta(days=int(months * 30.5))).isoformat(),
                "actual_price": None,
                "actual_return_pct": None,
                "status": "pending",
                "recorded_at": None,
            }
            for label, months in [("3m", 3), ("6m", 6), ("9m", 9), ("12m", 12)]
        },
    }

    path = _resolve_path(storage_path)
    existing = _load(path)
    prediction["id"] = _next_id(existing, ticker.upper())
    existing.append(prediction)
    _save(path, existing)
    return prediction


def _fetch_close(ticker: str, target_date: date) -> Optional[float]:
    """Closing price on or near target_date. Returns None on data gap."""
    try:
        import warnings
        warnings.filterwarnings("ignore")
        import yfinance as yf
    except ImportError:
        return None

    start = target_date - timedelta(days=7)
    end = target_date + timedelta(days=7)
    try:
        data = yf.download(
            ticker, start=start.isoformat(), end=end.isoformat(),
            progress=False, auto_adjust=True, threads=False,
        )
        if data is None or data.empty:
            return None
        # Use the closest trading day on or after target
        data = data.sort_index()
        for ts, row in data.iterrows():
            if ts.date() >= target_date:
                close = row["Close"]
                return float(close.iloc[0] if hasattr(close, "iloc") else close)
        # Fallback: last available
        last = data["Close"].iloc[-1]
        return float(last.iloc[0] if hasattr(last, "iloc") else last)
    except Exception:
        return None


def auto_update_checkpoints(
    as_of: Optional[date] = None,
    storage_path: Optional[str] = None,
) -> dict:
    """For each prediction whose checkpoint is past due, fetch the actual
    price and record actual_return_pct. Idempotent — already-recorded
    checkpoints are skipped."""
    today = as_of or date.today()
    path = _resolve_path(storage_path)
    predictions = _load(path)

    updated = 0
    failed = 0
    skipped = 0

    for pred in predictions:
        for label, ckpt in pred["checkpoints"].items():
            if ckpt["status"] != "pending":
                continue
            due = date.fromisoformat(ckpt["due_date"])
            if due > today:
                continue

            close = _fetch_close(pred["ticker"], due)
            if close is None:
                ckpt["status"] = "data_unavailable"
                ckpt["recorded_at"] = today.isoformat()
                failed += 1
                continue

            ckpt["actual_price"] = close
            ckpt["actual_return_pct"] = (close - pred["entry_price"]) / pred["entry_price"] * 100
            ckpt["status"] = "recorded"
            ckpt["recorded_at"] = today.isoformat()
            updated += 1

    _save(path, predictions)
    return {"updated": updated, "failed": failed, "skipped": skipped, "total_predictions": len(predictions)}


# ---- Calibration analysis ----------------------------------------------------
def _verdict_hit(verdict: str, actual_return_pct: float) -> Optional[str]:
    """Return HIT / MISS / PARTIAL for a verdict given an actual outcome.
    None if verdict isn't actionable (PAPER_ONLY)."""
    if verdict in ("BUY", "ADD"):
        if actual_return_pct > 5:
            return "HIT"
        if actual_return_pct > -5:
            return "PARTIAL"
        return "MISS"
    if verdict in ("SELL", "VETO", "TRIM"):
        if actual_return_pct < -5:
            return "HIT"
        if actual_return_pct < 5:
            return "PARTIAL"
        return "MISS"
    if verdict == "HOLD":
        if -10 < actual_return_pct < 30:
            return "HIT"
        return "PARTIAL"
    return None


def calibration_report(storage_path: Optional[str] = None) -> dict:
    """Aggregate predicted vs actual across all locked predictions with at
    least one recorded checkpoint."""
    try:
        from valuation_calc import wilson_ci
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        from valuation_calc import wilson_ci

    path = _resolve_path(storage_path)
    predictions = _load(path)

    by_verdict_horizon = {}  # (verdict, horizon) -> list of (predicted_return, actual_return, hit_label)
    for pred in predictions:
        for label, ckpt in pred["checkpoints"].items():
            if ckpt["status"] != "recorded":
                continue
            actual = ckpt["actual_return_pct"]
            predicted = pred.get("predicted_12m_return_pct")
            hit = _verdict_hit(pred["verdict"], actual)
            if hit is None:
                continue
            key = (pred["verdict"], label)
            by_verdict_horizon.setdefault(key, []).append({
                "predicted": predicted, "actual": actual, "hit": hit,
                "ticker": pred["ticker"], "id": pred["id"],
            })

    summary = []
    for (verdict, horizon), records in sorted(by_verdict_horizon.items()):
        n = len(records)
        hits = sum(1 for r in records if r["hit"] == "HIT")
        partials = sum(1 for r in records if r["hit"] == "PARTIAL")
        score = hits + 0.5 * partials
        ci = wilson_ci(round(score), n, 0.95) if n > 0 else None
        actuals = [r["actual"] for r in records]
        summary.append({
            "verdict": verdict, "horizon": horizon, "n": n,
            "hits": hits, "partials": partials,
            "misses": n - hits - partials,
            "hit_rate": (score / n) if n > 0 else None,
            "wilson_lower": ci["lower"] if ci else None,
            "wilson_upper": ci["upper"] if ci else None,
            "mean_actual_return": (sum(actuals) / n) if n > 0 else None,
        })

    return {
        "total_predictions": len(predictions),
        "active": sum(1 for p in predictions if any(c["status"] == "pending" for c in p["checkpoints"].values())),
        "fully_resolved": sum(1 for p in predictions if all(c["status"] != "pending" for c in p["checkpoints"].values())),
        "by_verdict_horizon": summary,
    }


def list_predictions(status: str = "all", storage_path: Optional[str] = None) -> list:
    path = _resolve_path(storage_path)
    predictions = _load(path)
    if status == "all":
        return predictions
    if status == "active":
        return [p for p in predictions if any(c["status"] == "pending" for c in p["checkpoints"].values())]
    if status == "resolved":
        return [p for p in predictions if all(c["status"] != "pending" for c in p["checkpoints"].values())]
    raise ValueError(f"status must be all/active/resolved, got {status!r}")


# ---- CLI ---------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--storage", help="Override storage JSON path (default: config.forward_predictions_path)")
    sub = p.add_subparsers(dest="cmd", required=True)

    lock_p = sub.add_parser("lock", help="Lock a new V4.3+ prediction")
    lock_p.add_argument("--ticker", required=True)
    lock_p.add_argument("--verdict", required=True, choices=["BUY", "HOLD", "SELL", "TRIM", "ADD", "VETO", "PAPER_ONLY"])
    lock_p.add_argument("--price", type=float, required=True, help="Entry price")
    lock_p.add_argument("--iv-p50", type=float, required=True, help="Median intrinsic value (Monte Carlo p50)")
    lock_p.add_argument("--iv-p5", type=float, help="Bear case p5")
    lock_p.add_argument("--iv-p95", type=float, help="Bull case p95")
    lock_p.add_argument("--mos", type=float, dest="mos_pct", help="Margin of safety pct")
    lock_p.add_argument("--predicted-12m", type=float, dest="predicted_12m_return_pct")
    lock_p.add_argument("--dq-score", type=int, dest="data_quality_score")
    lock_p.add_argument("--veto", action="store_true", dest="auto_veto_triggered")
    lock_p.add_argument("--phase9-fail", action="store_true", help="Set if Phase 9 audit failed")
    lock_p.add_argument("--rationale", dest="rationale_link", help="Path or URL to full report")

    sub.add_parser("checkpoints", help="Auto-update due checkpoints from yfinance")
    sub.add_parser("report", help="Print calibration report")

    list_p = sub.add_parser("list", help="List predictions")
    list_p.add_argument("--status", choices=["all", "active", "resolved"], default="all")

    args = p.parse_args()

    if args.cmd == "lock":
        kwargs = {k: v for k, v in vars(args).items() if k not in ("cmd", "storage", "phase9_fail", "price")}
        kwargs["entry_price"] = args.price
        kwargs["phase9_pass"] = not args.phase9_fail
        kwargs["storage_path"] = args.storage
        result = lock_prediction(**kwargs)
        print(f"Locked prediction {result['id']}")
        print(json.dumps(result, indent=2, default=str))

    elif args.cmd == "checkpoints":
        out = auto_update_checkpoints(storage_path=args.storage)
        print(json.dumps(out, indent=2))

    elif args.cmd == "report":
        rpt = calibration_report(storage_path=args.storage)
        print(f"Total predictions: {rpt['total_predictions']}  "
              f"(active: {rpt['active']}, resolved: {rpt['fully_resolved']})\n")
        if not rpt["by_verdict_horizon"]:
            print("No resolved checkpoints yet — predictions still tracking.")
            return
        print(f"{'Verdict':10s} {'Horizon':8s} {'n':>4s} {'Hit Rate (95% CI)':25s} {'Mean Actual':>14s}")
        print("-" * 70)
        for row in rpt["by_verdict_horizon"]:
            ci_str = (f"{row['hit_rate']*100:.0f}% [{row['wilson_lower']*100:.0f}, {row['wilson_upper']*100:.0f}]"
                      if row["hit_rate"] is not None else "—")
            mean_str = f"{row['mean_actual_return']:+.1f}%" if row["mean_actual_return"] is not None else "—"
            print(f"{row['verdict']:10s} {row['horizon']:8s} {row['n']:>4d} {ci_str:25s} {mean_str:>14s}")

    elif args.cmd == "list":
        items = list_predictions(args.status, storage_path=args.storage)
        print(f"{len(items)} predictions ({args.status})\n")
        for p in items:
            statuses = {label: c["status"] for label, c in p["checkpoints"].items()}
            print(f"  {p['id']:35s} {p['verdict']:8s} entry ${p['entry_price']:>8.2f} → IV p50 ${p['iv_p50']:.2f}  {statuses}")


if __name__ == "__main__":
    main()
