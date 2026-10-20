#!/usr/bin/env python3
"""
pre_trade_gate.py — V4.8: BUY gate (Rule C4) + SELL gate (Rule C10).

BUY: 每次買入前必須 run，唔過唔准落單。
SELL: 每次賣出前必須 run — 防 panic-sell / 短炒（典型失敗模式：持有幾日 / 幾星期就沽，對住 5 年持有哲學）。

Portfolio state comes from positions.json, resolved by config.resolve_positions_path():
    --positions PATH  →  BT_POSITIONS_PATH env  →  <investment_dir>/positions.json  →
    portfolio_structure/positions.example.json (bundled FAKE demo data)

BUY usage:
    python3 pre_trade_gate.py --ticker AAPL --amount 2000 \
        --price 150 --intrinsic 220 --tags tech \
        [--smart-money-entry 140] [--is-add] [--override]

SELL usage:
    python3 pre_trade_gate.py --action sell --ticker AAPL \
        --thesis-status intact|weakening|broken \
        [--trigger-hit "Q2 organic <4%"] [--recent-drop-pct -12] [--override]

Exit codes: 0 = PASS, 1 = override-acknowledged, 2 = FAIL
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

from config import resolve_positions_path

GREEN, YELLOW, RED, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"


def load_state(path=None):
    p = Path(path).expanduser() if path else resolve_positions_path()
    return json.loads(p.read_text())


def report(title, checks, override):
    print(f"\n{'='*64}")
    print(f"  {title}")
    print(f"{'='*64}")
    worst = 0
    for rule, lvl, msg in checks:
        icon = [f"{GREEN}PASS{RESET}", f"{YELLOW}WARN{RESET}", f"{RED}FAIL{RESET}"][lvl]
        print(f"  [{icon}] {rule}: {msg}")
        worst = max(worst, lvl)
    print(f"{'='*64}")
    hard_fails = [c for c in checks if c[1] == 2]
    if not hard_fails:
        print(f"  VERDICT: {GREEN}GATE PASS{RESET} — 可以執行（記得 log decision_log.py）")
        return 0
    if override:
        print(f"  VERDICT: {YELLOW}OVERRIDE ACKNOWLEDGED{RESET}")
        print("  ⚠️  必須先加 entry 去 journal/OVERRIDE_LOG.md 先准執行:")
        for c in hard_fails:
            print(f"      - {c[0]}: {c[2]}")
        return 1
    print(f"  VERDICT: {RED}GATE FAIL{RESET} — 唔准執行")
    print("  堅持要做: 重 run 加 --override 並記 OVERRIDE_LOG.md (Rule C5)")
    return 2


def buy_gate(a, st):
    lim = st["limits"]
    tags = [t.strip().lower() for t in a.tags.split(",") if t.strip()]
    ticker = a.ticker.upper()
    total = st["total_portfolio_usd"]
    cash = st["cash_usd"]
    checks = []

    mos = (a.intrinsic - a.price) / a.intrinsic * 100
    if mos >= lim["mos_hard_gate_pct"]:
        checks.append(("C1 MoS gate", 0, f"MoS {mos:.1f}% >= {lim['mos_hard_gate_pct']}% PASS"))
    elif mos >= lim["mos_watch_floor_pct"]:
        checks.append(("C2 MoS watch band", 1,
                       f"MoS {mos:.1f}% in {lim['mos_watch_floor_pct']}-{lim['mos_hard_gate_pct']}% band -> WATCH/GTC only"))
    else:
        checks.append(("C1 MoS gate", 2, f"MoS {mos:.1f}% < {lim['mos_watch_floor_pct']}% -> AUTO-REJECT (V4.6 Rule 1)"))

    if a.smart_money_entry:
        prem = (a.price - a.smart_money_entry) / a.smart_money_entry * 100
        lvl = 2 if prem >= lim["smart_money_premium_max_pct"] else (1 if prem >= 10 else 0)
        checks.append(("C3 Smart-money premium", lvl, f"+{prem:.0f}% vs entry ${a.smart_money_entry}"))

    existing = st["positions"].get(ticker, {}).get("value_usd", 0)
    post_pct = (existing + a.amount) / total * 100
    lvl = 2 if post_pct > lim["single_stock_max_pct"] else 0
    checks.append(("A1 Single-stock cap", lvl, f"post-trade {post_pct:.1f}% (cap {lim['single_stock_max_pct']}%)"))

    post_cash = cash - a.amount
    if post_cash < 0:
        checks.append(("A4 Cash reserve", 2, f"insufficient cash (${cash:,.0f} < ${a.amount:,.0f})"))
    elif post_cash / total * 100 < lim["cash_reserve_min_pct"]:
        checks.append(("A4 Cash reserve", 1, f"post-trade cash {post_cash/total*100:.1f}% < {lim['cash_reserve_min_pct']}% target"))
    else:
        checks.append(("A4 Cash reserve", 0, f"post-trade cash {post_cash/total*100:.1f}% OK"))

    ai_now = sum(v["value_usd"] for v in st["positions"].values() if "ai" in v.get("tags", []))
    ai_post = ai_now + (a.amount if "ai" in tags else 0)
    ai_pct = ai_post / total * 100
    if "ai" in tags and ai_pct > lim["ai_correlated_max_pct"]:
        checks.append(("B1 AI-correlated cap", 2, f"post-trade AI {ai_pct:.1f}% > {lim['ai_correlated_max_pct']}% — frozen"))
    else:
        checks.append(("B1 AI-correlated cap", 1 if ai_pct > lim["ai_correlated_max_pct"] else 0, f"AI exposure {ai_pct:.1f}%"))

    this_month = date.today().strftime("%Y-%m")
    buys = st["new_buys_this_month"] if st.get("new_buys_month") == this_month else 0
    if not a.is_add:
        lvl = 2 if buys >= lim["monthly_new_buys_max"] else 0
        checks.append(("C6 Patience quota", lvl, f"{buys}/{lim['monthly_new_buys_max']} new BUYs this month"))

    # C7: dividend-yield theses must use NET yield. Withholding depends on your tax residency —
    # set limits.dividend_withholding_pct in positions.json (default 30% = US non-treaty rate).
    wh = lim.get("dividend_withholding_pct", 30)
    checks.append(("C7 Dividend tax", 1, f"yield thesis 用 NET yield = gross x {1 - wh / 100:.2f} ({wh}% withholding)"))
    return report(f"BUY GATE — {ticker} ${a.amount:,.0f} @ ${a.price} | MoS {mos:.1f}%", checks, a.override)


def sell_gate(a, st):
    lim = st["limits"]
    ticker = a.ticker.upper()
    checks = []
    pos = st["positions"].get(ticker)
    if not pos:
        print(f"  {RED}ERROR{RESET}: {ticker} not in positions.json")
        return 2

    entry = st.get("entry_dates", {}).get(ticker)
    held_days = (date.today() - datetime.strptime(entry, "%Y-%m-%d").date()).days if entry else None

    # S1: thesis status is the master switch
    if a.thesis_status == "broken":
        checks.append(("S1 Thesis status", 0, "BROKEN — discipline exit, sell justified (NVO/BMY rule #6)"))
    elif a.thesis_status == "weakening":
        checks.append(("S1 Thesis status", 1, "WEAKENING — partial trim acceptable, full exit needs more evidence"))
    else:
        checks.append(("S1 Thesis status", 1, "INTACT — selling an intact thesis needs a pre-committed trigger"))

    # S2: pre-committed trigger
    if a.trigger_hit:
        checks.append(("S2 Pre-committed trigger", 0, f"trigger hit: '{a.trigger_hit}' — emotion-free execution"))
    elif a.thesis_status == "intact":
        checks.append(("S2 Pre-committed trigger", 2, "NO trigger hit + thesis intact = 呢個唔係計劃，係情緒"))

    # S3: panic-sell pattern
    if a.recent_drop_pct is not None and a.recent_drop_pct <= -8 and a.thesis_status == "intact":
        checks.append(("S3 Panic-sell check", 2,
                       f"5-day {a.recent_drop_pct:.0f}% drop + thesis intact = classic panic pattern。跌價本身唔係 sell signal"))
    elif a.recent_drop_pct is not None:
        checks.append(("S3 Panic-sell check", 0, f"5-day move {a.recent_drop_pct:.0f}% — not panic-driven"))

    # S4: holding period vs philosophy
    if held_days is not None:
        soft = lim.get("min_hold_days_soft", 180)
        if held_days < soft and a.thesis_status != "broken":
            checks.append(("S4 Holding period", 1,
                           f"held {held_days} days < {soft} soft floor（短炒警號 — 5 年持有哲學 reminder）"))
        else:
            checks.append(("S4 Holding period", 0, f"held {held_days} days"))

    # S5: post-sell reminders
    checks.append(("S5 After-sell protocol", 1,
                   "24hr cool-down before redeploying proceeds (C8) + decision_log.py mark-exit + post-mortem if loss"))
    return report(f"SELL GATE — {ticker} ({a.portion:.0%} of position) | thesis: {a.thesis_status}", checks, a.override)


def main():
    p = argparse.ArgumentParser(description="V4.8 pre-trade gate (buy + sell)")
    p.add_argument("--action", choices=["buy", "sell"], default="buy")
    p.add_argument("--ticker", required=True)
    p.add_argument("--override", action="store_true")
    p.add_argument("--positions", default=None, help="positions.json path (default: config.resolve_positions_path())")
    # buy args
    p.add_argument("--amount", type=float)
    p.add_argument("--price", type=float)
    p.add_argument("--intrinsic", type=float)
    p.add_argument("--tags", default="")
    p.add_argument("--smart-money-entry", type=float, default=None)
    p.add_argument("--is-add", action="store_true")
    # sell args
    p.add_argument("--thesis-status", choices=["intact", "weakening", "broken"], default="intact")
    p.add_argument("--trigger-hit", default=None, help="which pre-committed exit trigger fired")
    p.add_argument("--recent-drop-pct", type=float, default=None, help="5-day price move in percent")
    p.add_argument("--portion", type=float, default=1.0, help="fraction of position to sell")
    a = p.parse_args()

    st = load_state(a.positions)
    if a.action == "buy":
        if a.amount is None or a.price is None or a.intrinsic is None:
            p.error("buy requires --amount --price --intrinsic")
        sys.exit(buy_gate(a, st))
    else:
        sys.exit(sell_gate(a, st))


if __name__ == "__main__":
    main()
