#!/usr/bin/env python3
"""
DCF Model Builder — V4.4 + Anthropic FSI Standard
Boris's investment system.

Generates institutional-quality live Excel DCF models with:
- Case selector (1=Bear, 2=Base, 3=Bull)
- Scenario assumption blocks (horizontal across years)
- Consolidation column with INDEX formulas
- Mid-year convention discounting (0.5/1.5/2.5...)
- WACC sheet (CAPM standardized V4.4)
- Sensitivity tables (WACC × Terminal Growth) — live formulas
- Blue=input / black=formula / green=sheet-link colour coding
- Cell comments on every hardcoded input

Usage:
    python3 dcf_model_builder.py            # builds all configs in CONFIGS
    python3 dcf_model_builder.py EXMPL      # single ticker

Then recalc:
    soffice --headless --convert-to xlsx --outdir /tmp <file>  (or recalc.py)
"""

import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.comments import Comment

OUT_DIR = Path("./models")
OUT_DIR.mkdir(exist_ok=True)

# ---- Style constants (Anthropic FSI standard) ----
BLUE = Font(color="0000FF")           # hardcoded inputs
BLACK = Font(color="000000")          # formulas
GREEN = Font(color="008000")          # sheet links
WHITE_BOLD = Font(color="FFFFFF", bold=True)
BLACK_BOLD = Font(color="000000", bold=True)
HDR_FILL = PatternFill("solid", fgColor="1F4E79")     # dark blue section header
SUB_FILL = PatternFill("solid", fgColor="D9E1F2")     # light blue sub-header
OUT_FILL = PatternFill("solid", fgColor="BDD7EE")     # medium blue output
CENTER_FILL = PatternFill("solid", fgColor="BDD7EE")  # sensitivity center
INPUT_FILL = PatternFill("solid", fgColor="F2F2F2")   # light grey input
thin = Side(style="thin", color="BBBBBB")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def hdr(ws, cell, text, span):
    """Dark-blue merged section header."""
    ws[cell] = text
    col = cell[0]
    row = int(cell[1:])
    end_col = chr(ord(col) + span - 1)
    ws.merge_cells(f"{cell}:{end_col}{row}")
    c = ws[cell]
    c.fill = HDR_FILL
    c.font = WHITE_BOLD
    c.alignment = Alignment(horizontal="left", vertical="center")


def inp(ws, cell, value, comment=None, fmt=None):
    """Blue hardcoded input with grey fill + source comment."""
    ws[cell] = value
    c = ws[cell]
    c.font = BLUE
    c.fill = INPUT_FILL
    c.border = BORDER
    if fmt:
        c.number_format = fmt
    if comment:
        c.comment = Comment(f"Source: {comment}", "DCF Builder")


def fml(ws, cell, formula, fmt=None, link=False, bold=False, out=False):
    """Black formula (or green if sheet-link)."""
    ws[cell] = formula
    c = ws[cell]
    c.font = GREEN if link else (BLACK_BOLD if bold else BLACK)
    c.border = BORDER
    if fmt:
        c.number_format = fmt
    if out:
        c.fill = OUT_FILL
        c.font = BLACK_BOLD


def lbl(ws, cell, text, bold=False):
    ws[cell] = text
    ws[cell].font = BLACK_BOLD if bold else BLACK


PCT = "0.0%"
USD = "$#,##0"
USD2 = "$#,##0.00"
NUM = "#,##0"
FAC = "0.000"


def build_model(cfg):
    """Build a full DCF .xlsx for one company config."""
    wb = Workbook()

    # ============ WACC SHEET ============
    wq = wb.active
    wq.title = "WACC"
    hdr(wq, "A1", f"{cfg['ticker']} — WACC (CAPM V4.4)", 3)
    lbl(wq, "A3", "COST OF EQUITY", bold=True)
    lbl(wq, "A4", "Risk-Free Rate (10Y UST)")
    inp(wq, "B4", cfg["rf"], "Fed H.15 2026-05-21", PCT)
    lbl(wq, "A5", "Beta (5-yr)")
    inp(wq, "B5", cfg["beta"], "FMP 5-yr monthly beta", FAC)
    lbl(wq, "A6", "Equity Risk Premium")
    inp(wq, "B6", cfg["erp"], "Damodaran 2026", PCT)
    lbl(wq, "A7", "Country Premium")
    inp(wq, "B7", cfg.get("country", 0.0), "Damodaran country risk", PCT)
    lbl(wq, "A8", "Cost of Equity", bold=True)
    fml(wq, "B8", "=B4+B5*B6+B7", PCT, bold=True)

    lbl(wq, "A10", "COST OF DEBT", bold=True)
    lbl(wq, "A11", "Pre-Tax Cost of Debt")
    inp(wq, "B11", cfg["cost_debt"], "Credit rating / bond yield", PCT)
    lbl(wq, "A12", "Tax Rate")
    inp(wq, "B12", cfg["tax"], "FY income statement", PCT)
    lbl(wq, "A13", "After-Tax Cost of Debt", bold=True)
    fml(wq, "B13", "=B11*(1-B12)", PCT, bold=True)

    lbl(wq, "A15", "CAPITAL STRUCTURE", bold=True)
    lbl(wq, "A16", "Share Price")
    inp(wq, "B16", cfg["price"], "Longbridge live quote", USD2)
    lbl(wq, "A17", "Shares Outstanding (M)")
    inp(wq, "B17", cfg["shares"], "Mcap / price", NUM)
    lbl(wq, "A18", "Market Cap ($M)")
    fml(wq, "B18", "=B16*B17", USD)
    lbl(wq, "A19", "Total Debt ($M)")
    inp(wq, "B19", cfg["debt"], "Balance sheet + ASC 842 leases", USD)
    lbl(wq, "A20", "Cash ($M)")
    inp(wq, "B20", cfg["cash"], "Balance sheet", USD)
    lbl(wq, "A21", "Net Debt ($M)")
    fml(wq, "B21", "=B19-B20", USD)
    lbl(wq, "A22", "Enterprise Value ($M)")
    fml(wq, "B22", "=B18+B21", USD)

    lbl(wq, "A24", "WACC", bold=True)
    lbl(wq, "A25", "Equity Weight")
    fml(wq, "B25", "=B18/B22", PCT)
    lbl(wq, "A26", "Debt Weight")
    fml(wq, "B26", "=B21/B22", PCT)
    lbl(wq, "A27", "WACC", bold=True)
    fml(wq, "B27", "=B25*B8+B26*B13", PCT, bold=True, out=True)
    for col, w in {"A": 30, "B": 16, "C": 16}.items():
        wq.column_dimensions[col].width = w

    # ============ DCF SHEET ============
    ws = wb.create_sheet("DCF")
    hdr(ws, "A1", f"{cfg['name']} ({cfg['ticker']}) — DCF Model V4.4", 8)
    ws["A2"] = f"Ticker: {cfg['ticker']} | Date: {date.today()} | Mid-Year Convention"
    ws["A2"].font = BLACK

    lbl(ws, "A4", "CASE SELECTOR (1=Bear 2=Base 3=Bull)", bold=True)
    inp(ws, "B4", 2, "Boris selects scenario", "0")
    fml(ws, "C4", '=IF(B4=1,"BEAR",IF(B4=2,"BASE","BULL"))', bold=True)

    # Market data
    hdr(ws, "A6", "MARKET DATA", 8)
    lbl(ws, "A7", "Share Price")
    fml(ws, "B7", "=WACC!B16", USD2, link=True)
    lbl(ws, "A8", "Shares Outstanding (M)")
    fml(ws, "B8", "=WACC!B17", NUM, link=True)
    lbl(ws, "A9", "Net Debt ($M)")
    fml(ws, "B9", "=WACC!B21", USD, link=True)
    lbl(ws, "A10", "WACC")
    fml(ws, "B10", "=WACC!B27", PCT, link=True)
    lbl(ws, "A11", "Base FCF ($M, V4.4 SBC-adj)")
    inp(ws, "B11", cfg["base_fcf"], "OCF - CapEx - SBC (V4.4)", USD)

    # Scenario blocks: Bear(15), Base(19), Bull(23) — rows for g1,g2,g3,g4,g5, termg, wacc_adj
    yrs = ["FY1", "FY2", "FY3", "FY4", "FY5"]
    blocks = [("BEAR CASE ASSUMPTIONS", 14, cfg["bear"]),
              ("BASE CASE ASSUMPTIONS", 20, cfg["base"]),
              ("BULL CASE ASSUMPTIONS", 26, cfg["bull"])]
    for title, r, sc in blocks:
        hdr(ws, f"A{r}", title, 8)
        ws[f"A{r+1}"] = "Assumption"
        ws[f"A{r+1}"].font = BLACK_BOLD
        ws[f"A{r+1}"].fill = SUB_FILL
        for i, y in enumerate(yrs):
            cc = ws.cell(row=r+1, column=2+i, value=y)
            cc.font = BLACK_BOLD
            cc.fill = SUB_FILL
        # Growth row
        ws[f"A{r+2}"] = "Revenue/FCF Growth (%)"
        ws[f"A{r+2}"].font = BLACK
        for i, g in enumerate(sc["growth"]):
            inp(ws, f"{chr(66+i)}{r+2}", g, f"{title} growth yr{i+1}", PCT)
        # Terminal growth
        ws[f"A{r+3}"] = "Terminal Growth (%)"
        ws[f"A{r+3}"].font = BLACK
        inp(ws, f"B{r+3}", sc["term_g"], f"{title} terminal g", PCT)
        # WACC override
        ws[f"A{r+4}"] = "WACC (scenario)"
        ws[f"A{r+4}"].font = BLACK
        inp(ws, f"B{r+4}", sc["wacc"], f"{title} WACC", PCT)

    # Consolidation column (selected case) — INDEX across Bear/Base/Bull
    hdr(ws, "A32", "SELECTED CASE (INDEX consolidation)", 8)
    ws["A33"] = "Driver"
    ws["A33"].font = BLACK_BOLD
    ws["A33"].fill = SUB_FILL
    for i, y in enumerate(yrs):
        cc = ws.cell(row=33, column=2+i, value=y)
        cc.font = BLACK_BOLD; cc.fill = SUB_FILL
    # growth consolidation: INDEX(bear_g, base_g, bull_g)
    ws["A34"] = "Growth (%)"
    ws["A34"].font = BLACK
    for i in range(5):
        col = chr(66+i)
        # bear row16, base row22, bull row28 — CHOOSE robust vs INDEX multi-area
        fml(ws, f"{col}34", f"=CHOOSE($B$4,{col}16,{col}22,{col}28)", PCT)
    ws["A35"] = "Terminal Growth"
    ws["A35"].font = BLACK
    fml(ws, "B35", "=CHOOSE($B$4,B17,B23,B29)", PCT)
    ws["A36"] = "Scenario WACC"
    ws["A36"].font = BLACK
    fml(ws, "B36", "=CHOOSE($B$4,B18,B24,B30)", PCT)

    # FCF projection (mid-year convention)
    hdr(ws, "A38", "FCF PROJECTION + DISCOUNTING (Mid-Year Convention)", 8)
    ws["A39"] = "Year"
    ws["A39"].font = BLACK_BOLD; ws["A39"].fill = SUB_FILL
    for i, y in enumerate(yrs):
        cc = ws.cell(row=39, column=2+i, value=y); cc.font = BLACK_BOLD; cc.fill = SUB_FILL
    # FCF row 40: FCF(n) = FCF(n-1) * (1+growth)
    ws["A40"] = "Unlevered FCF ($M)"; ws["A40"].font = BLACK
    fml(ws, "B40", "=$B$11*(1+B34)", USD)
    for i in range(1, 5):
        col = chr(66+i); prev = chr(65+i)
        fml(ws, f"{col}40", f"={prev}40*(1+{col}34)", USD)
    # Period (mid-year): 0.5, 1.5, ...
    ws["A41"] = "Discount Period"; ws["A41"].font = BLACK
    for i in range(5):
        inp(ws, f"{chr(66+i)}41", 0.5+i, "Mid-year convention", FAC)
    # Discount factor
    ws["A42"] = "Discount Factor"; ws["A42"].font = BLACK
    for i in range(5):
        col = chr(66+i)
        fml(ws, f"{col}42", f"=1/(1+$B$36)^{col}41", FAC)
    # PV of FCF
    ws["A43"] = "PV of FCF ($M)"; ws["A43"].font = BLACK
    for i in range(5):
        col = chr(66+i)
        fml(ws, f"{col}43", f"={col}40*{col}42", USD)

    # Terminal value
    hdr(ws, "A45", "TERMINAL VALUE", 8)
    ws["A46"] = "Terminal FCF ($M)"; ws["A46"].font = BLACK
    fml(ws, "B46", "=F40*(1+B35)", USD)
    ws["A47"] = "Terminal Value ($M)"; ws["A47"].font = BLACK
    fml(ws, "B47", "=B46/(B36-B35)", USD)
    ws["A48"] = "PV of Terminal Value ($M)"; ws["A48"].font = BLACK
    fml(ws, "B48", "=B47/(1+B36)^F41", USD)

    # Valuation bridge
    hdr(ws, "A50", "VALUATION SUMMARY", 8)
    ws["A51"] = "Sum PV of FCFs ($M)"; ws["A51"].font = BLACK
    fml(ws, "B51", "=SUM(B43:F43)", USD)
    ws["A52"] = "PV of Terminal Value ($M)"; ws["A52"].font = BLACK
    fml(ws, "B52", "=B48", USD)
    ws["A53"] = "Enterprise Value ($M)"; ws["A53"].font = BLACK
    fml(ws, "B53", "=B51+B52", USD)
    ws["A54"] = "(-) Net Debt ($M)"; ws["A54"].font = BLACK
    fml(ws, "B54", "=B9", USD)
    ws["A55"] = "Equity Value ($M)"; ws["A55"].font = BLACK
    fml(ws, "B55", "=B53-B54", USD)
    ws["A56"] = "Shares Outstanding (M)"; ws["A56"].font = BLACK
    fml(ws, "B56", "=B8", NUM)
    ws["A57"] = "IMPLIED PRICE / SHARE"; ws["A57"].font = BLACK_BOLD
    fml(ws, "B57", "=B55/B56", USD2, bold=True, out=True)
    ws["A58"] = "Current Share Price"; ws["A58"].font = BLACK
    fml(ws, "B58", "=B7", USD2)
    ws["A59"] = "Implied Upside / (Downside)"; ws["A59"].font = BLACK_BOLD
    fml(ws, "B59", "=B57/B58-1", PCT, bold=True, out=True)
    ws["A60"] = "Margin of Safety (MoS)"; ws["A60"].font = BLACK_BOLD
    fml(ws, "B60", "=(B57-B58)/B57", PCT, bold=True, out=True)

    # Sensitivity table: WACC (rows) × Terminal Growth (cols), 5x5
    hdr(ws, "A63", "SENSITIVITY: WACC (rows) × TERMINAL GROWTH (cols)", 8)
    ws["A64"] = "Implied $/share"; ws["A64"].font = BLACK_BOLD
    # axis values around base
    base_wacc_cell = "B36"
    # build axis as base WACC -2step..+2step (step 0.5pp), term g -1pp..+1pp (step 0.5pp)
    wacc_steps = [-0.01, -0.005, 0, 0.005, 0.01]
    tg_steps = [-0.01, -0.005, 0, 0.005, 0.01]
    # column headers (terminal growth)
    for j, ts in enumerate(tg_steps):
        cc = ws.cell(row=64, column=2+j)
        cc.value = f"=$B$35+{ts}"
        cc.number_format = PCT; cc.font = BLACK_BOLD; cc.fill = SUB_FILL
    # rows
    for i, wsd in enumerate(wacc_steps):
        rr = 65+i
        rc = ws.cell(row=rr, column=1)
        rc.value = f"=$B$36+{wsd}"
        rc.number_format = PCT; rc.font = BLACK_BOLD; rc.fill = SUB_FILL
        for j, ts in enumerate(tg_steps):
            col = chr(66+j)
            w = f"($B$36+{wsd})"
            g = f"($B$35+{ts})"
            # full DCF recalc: sum PV FCF (with scenario WACC w) + PV TV - net debt, /shares
            pv_fcf = "+".join([f"{chr(66+k)}40/(1+{w})^{chr(66+k)}41" for k in range(5)])
            tv = f"(F40*(1+{g})/({w}-{g}))/(1+{w})^F41"
            formula = f"=(({pv_fcf})+({tv})-$B$9)/$B$8"
            cell = ws.cell(row=rr, column=2+j)
            cell.value = formula
            cell.number_format = USD2
            cell.font = BLACK
            cell.border = BORDER
            if i == 2 and j == 2:  # center = base case
                cell.fill = CENTER_FILL
                cell.font = BLACK_BOLD

    for col, w in {"A": 32, "B": 13, "C": 13, "D": 13, "E": 13, "F": 13, "G": 13, "H": 13}.items():
        ws.column_dimensions[col].width = w

    fn = OUT_DIR / f"{cfg['ticker']}_DCF_Model_{date.today()}.xlsx"
    wb.save(fn)
    return fn


# ---- Example config (replace with your own tickers / inputs) ----
# NOTE: This is an illustrative example only. Populate with your own
# research-derived inputs. All values below are placeholders for demonstration.
CONFIGS = {
    "EXMPL": dict(ticker="EXMPL", name="Example Corp", price=100.00, shares=1000, debt=2000, cash=500,
                beta=1.00, rf=0.0457, erp=0.055, country=0.0, cost_debt=0.05, tax=0.25, base_fcf=800,
                bear=dict(growth=[0.03,0.03,0.03,0.03,0.03], term_g=0.02, wacc=0.10),
                base=dict(growth=[0.08,0.07,0.06,0.05,0.04], term_g=0.03, wacc=0.09),
                bull=dict(growth=[0.12,0.11,0.10,0.08,0.06], term_g=0.035, wacc=0.085)),
}


def main():
    targets = [sys.argv[1].upper()] if len(sys.argv) > 1 else list(CONFIGS.keys())
    for t in targets:
        fn = build_model(CONFIGS[t])
        print(f"✅ {fn.name}")


if __name__ == "__main__":
    main()
