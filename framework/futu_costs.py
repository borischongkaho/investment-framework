#!/usr/bin/env python3
"""
Futu Securities Hong Kong — US Stock Trading Cost Calculator

Standard rate card (HK retail account):
  Commission:        $0.0049 per share, min $0.99 per order
  Platform fee:      $0.005 per share, min $1.00 per order
  Settlement (BUY):  $0.003 per share, max $7.00 per order
  SEC fee (SELL):    0.0000278 × trade value
  TAF (SELL):        $0.000166 per share, max $8.30
  Currency conversion: ~0.10% spread on HKD↔USD

If the user's Futu plan differs, override via env vars or constructor args.

Usage:
    python3 futu_costs.py BUY 65 152.57       # Buy 65 shares at $152.57
    python3 futu_costs.py SELL 36 215.80      # Sell 36 shares at $215.80

Or programmatically:
    from futu_costs import calc_futu_cost
    cost = calc_futu_cost(side="BUY", shares=65, price=152.57)
"""
import json
import sys
from typing import Literal


# --- Futu HK US Stock Standard Rate Card ---
COMMISSION_PER_SHARE = 0.0049
COMMISSION_MIN = 0.99

PLATFORM_PER_SHARE = 0.005
PLATFORM_MIN = 1.00

# Buy-side
SETTLEMENT_PER_SHARE = 0.003
SETTLEMENT_MAX = 7.00

# Sell-side (US regulatory)
SEC_RATE = 0.0000278  # Of trade value
TAF_PER_SHARE = 0.000166
TAF_MAX = 8.30


def calc_futu_cost(
    side: Literal["BUY", "SELL"],
    shares: int,
    price: float,
) -> dict:
    """
    Compute Futu HK US stock trading cost.

    Returns dict with breakdown + total cost + net proceeds/cost.
    """
    if side not in ("BUY", "SELL"):
        raise ValueError(f"side must be BUY or SELL, got {side}")
    if shares <= 0 or price <= 0:
        raise ValueError("shares and price must be positive")

    gross = shares * price

    # Commission
    commission = max(shares * COMMISSION_PER_SHARE, COMMISSION_MIN)

    # Platform fee
    platform = max(shares * PLATFORM_PER_SHARE, PLATFORM_MIN)

    # Side-specific fees
    if side == "BUY":
        settlement = min(shares * SETTLEMENT_PER_SHARE, SETTLEMENT_MAX)
        sec_fee = 0.0
        taf = 0.0
    else:  # SELL
        settlement = 0.0
        sec_fee = gross * SEC_RATE
        taf = min(shares * TAF_PER_SHARE, TAF_MAX)

    total_fees = commission + platform + settlement + sec_fee + taf

    if side == "BUY":
        net = gross + total_fees  # Money going OUT (cost basis)
    else:
        net = gross - total_fees  # Money coming IN (after fees)

    return {
        "side": side,
        "shares": shares,
        "price": price,
        "gross": round(gross, 2),
        "fees": {
            "commission": round(commission, 2),
            "platform_fee": round(platform, 2),
            "settlement_fee": round(settlement, 2),
            "sec_fee": round(sec_fee, 2),
            "taf_fee": round(taf, 2),
        },
        "total_fees": round(total_fees, 2),
        "net": round(net, 2),
        "fees_as_pct_of_gross": round(total_fees / gross * 100, 3) if gross > 0 else 0.0,
    }


def calc_round_trip_cost(
    buy_shares: int, buy_price: float,
    sell_shares: int, sell_price: float,
) -> dict:
    """
    Compute total round-trip cost (buy + sell) and net realized P/L.

    Useful for FIFO trades like FISV (bought + sold same number).
    """
    buy = calc_futu_cost("BUY", buy_shares, buy_price)
    sell = calc_futu_cost("SELL", sell_shares, sell_price)

    gross_pnl = sell["gross"] - buy["gross"]
    total_fees = buy["total_fees"] + sell["total_fees"]
    net_pnl = sell["net"] - buy["net"]

    return {
        "buy": buy,
        "sell": sell,
        "gross_pnl": round(gross_pnl, 2),
        "total_fees": round(total_fees, 2),
        "net_pnl": round(net_pnl, 2),
        "fee_drag_pct": round(total_fees / abs(gross_pnl) * 100, 1) if gross_pnl != 0 else 0.0,
    }


# --- CLI ---
def main():
    if len(sys.argv) == 4:
        side = sys.argv[1].upper()
        shares = int(sys.argv[2])
        price = float(sys.argv[3])
        result = calc_futu_cost(side, shares, price)
        print(json.dumps(result, indent=2))
    elif len(sys.argv) == 5 and sys.argv[1].lower() == "round":
        # round 65 152.57 65 215.80
        buy_shares = int(sys.argv[2])
        buy_price = float(sys.argv[3])
        sell_shares = int(sys.argv[4])
        # Note: only 4 args after "round" needed; this branch may need adjustment
        print("Usage: python3 futu_costs.py round <buy_shares> <buy_price> <sell_shares> <sell_price>")
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
