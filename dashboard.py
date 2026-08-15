from datetime import datetime
from config import (
    DASHBOARD_CELLS,
    GREEN_THRESHOLD,
    YELLOW_THRESHOLD,
    GREEN,
    YELLOW,
    RED,
)

def update_dashboard_data(
                        ws_dashboard_data, 
                        account_totals, 
                        taxable_total, 
                        tax_deferred_total,
                        roth_total,
                        cash_total,
                        us_stock_total,
                        international_stock_total,
                        bond_total,
                        alternative_total,
                        balanced_total,
                        cash_allocation,
                        largest_account,
                        largest_value,
                        largest_symbol,
                        largest_description,
                        largest_holding_value
                        ):

    portfolio_total = sum(account_totals.values())

    ws_dashboard_data[f"B2"] = round(portfolio_total, 2)
    ws_dashboard_data[f"B3"] = taxable_total
    ws_dashboard_data[f"B4"] = tax_deferred_total
    ws_dashboard_data[f"B5"] = roth_total
    ws_dashboard_data[f"B6"] = cash_total
    ws_dashboard_data[f"B7"] = us_stock_total
    ws_dashboard_data[f"B8"] = international_stock_total
    ws_dashboard_data[f"B9"] = bond_total
    ws_dashboard_data[f"B10"] = alternative_total
    ws_dashboard_data[f"B11"] = balanced_total
    ws_dashboard_data[f"B12"] = cash_allocation
    ws_dashboard_data[f"B12"].number_format = "0.00%"
    ws_dashboard_data[f"B13"] = f"{largest_account}: ${largest_value:,.2f}"
    ws_dashboard_data[f"B14"] = f"{largest_symbol} ({largest_description}): ${largest_holding_value:,.2f}"
    ws_dashboard_data[f"B15"] = datetime.now().date()
    ws_dashboard_data[f"B15"].number_format = "mmm d, yyyy"

    # Chart Data - Asset Allocation
    ws_dashboard_data[f"D1"] = "Asset Class"
    ws_dashboard_data[f"E1"] = "Value"

    ws_dashboard_data[f"D2"] = "US Stock"
    ws_dashboard_data[f"E2"] = us_stock_total

    ws_dashboard_data[f"D3"] = "International Stock"
    ws_dashboard_data[f"E3"] = international_stock_total

    ws_dashboard_data[f"D4"] = "Bonds"
    ws_dashboard_data[f"E4"] = bond_total

    ws_dashboard_data[f"D5"] = "Alternative"
    ws_dashboard_data[f"E5"] = alternative_total

    ws_dashboard_data[f"D6"] = "Balanced"
    ws_dashboard_data[f"E6"] = balanced_total

    ws_dashboard_data[f"D7"] = "Cash"
    ws_dashboard_data[f"E7"] = cash_total


def update_dashboard(ws_dashboard, ws_dashboard_data, values):
    # Last Updated
    ws_dashboard["D2"] = "Last Updated:"
    ws_dashboard["E2"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Portfolio Summary
    ws_dashboard["B5"] = ws_dashboard_data["B2"].value
    ws_dashboard["B6"] = ws_dashboard_data["B3"].value
    ws_dashboard["B7"] = ws_dashboard_data["B4"].value
    ws_dashboard["B8"] = ws_dashboard_data["B5"].value
    ws_dashboard["B9"] = ws_dashboard_data["B6"].value
    ws_dashboard["B10"] = ws_dashboard_data["B12"].value
    ws_dashboard["B10"].number_format = "0.00%"

    # Asset Allocation
    ws_dashboard["B13"] = ws_dashboard_data["B7"].value
    ws_dashboard["B14"] = ws_dashboard_data["B8"].value
    ws_dashboard["B15"] = ws_dashboard_data["B9"].value
    ws_dashboard["B16"] = ws_dashboard_data["B10"].value
    ws_dashboard["B17"] = ws_dashboard_data["B11"].value
    ws_dashboard["B18"] = ws_dashboard_data["B6"].value

    # Largest Positions
    ws_dashboard["B21"] = ws_dashboard_data["B13"].value
    ws_dashboard["B22"] = ws_dashboard_data["B14"].value

    # Markets
    for market, cells in DASHBOARD_CELLS.items():
        ws_dashboard[cells["price"]] = values[market]["price"]
        ws_dashboard[cells["status"]] = values[market]["pct_from_high"]
        ws_dashboard[cells["status"]].number_format = "0.00%"

def apply_color(ws, cell, pct):
    if pct >= GREEN_THRESHOLD:
        ws[cell].fill = GREEN
    elif pct >= YELLOW_THRESHOLD:
        ws[cell].fill = YELLOW
    else:
        ws[cell].fill = RED
