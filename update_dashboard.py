# config.py - settings, sheet_names, mappings, colors
# workbook.py - opening, sheets, saving
# markets.py - Yahoo market prices
# holdings.py - holdings updates and portfolio calculations
# dashboard.py - Dashboard Data and Dashboard updates
# activity.py History and activity log updates
# update_dashboard.py = main workflow only

import os
import yfinance as yf
import traceback
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from datetime import datetime, date
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil   
from config import HOLDINGS_COL
from holdings import (
    calculate_account_totals,
    calculate_taxable_totals,
    calculate_tax_deferred_totals,
    calculate_roth_totals,
    calculate_cash_totals,
    calculate_us_stock_totals,
    calculate_international_stock_totals,
    calculate_bond_totals,
    calculate_alternative_totals,
    calculate_balanced_totals,
    calculate_cash_allocation,
    calculate_largest_account,
    calculate_largest_holding,
    calculate_portfolio_total,
    get_account_names,
    update_holdings
)

from workbook import (
    open_workbook,
    get_market_sheet,
    get_dashboard_sheet,
    get_history_sheet,
    get_activity_sheet,
    get_holdings_sheet,
    save_workbook
)

from dashboard import (update_dashboard, 
                       update_dashboard_data, 
                       apply_color
)

from markets import update_market_sheet
from activity import log_activity, update_history

def main():
    try:
         wb, file = open_workbook()

         ws_market = get_market_sheet(wb)
         ws_dashboard = get_dashboard_sheet(wb)
         ws_dashboard_data = wb["Dashboard Data"]
         ws_history = get_history_sheet(wb)
         ws_log = get_activity_sheet(wb)
         ws_holdings = get_holdings_sheet(wb)

         log_activity(ws_log, "Starting update")

         values = update_market_sheet(ws_market)
         log_activity(ws_log, "Market data updated")

         update_holdings(ws_holdings)
         log_activity(ws_log, "Holdings updated")

         account_totals = calculate_account_totals(ws_holdings)
         print(account_totals)

         taxable_total = calculate_taxable_totals(ws_holdings)
         print(f"Total Taxable: {taxable_total}")

         tax_deferred_total = calculate_tax_deferred_totals(ws_holdings)
         print(f"Total Tax Defferred: {tax_deferred_total}")
            
         roth_total = calculate_roth_totals(ws_holdings)
         print(f"Total Roth: {roth_total}")

         cash_total = calculate_cash_totals(ws_holdings)
         print(f"Total Cash: {cash_total}")

         us_stock_total = calculate_us_stock_totals(ws_holdings)
         print(f"Total US Stock: {us_stock_total}")

         international_stock_total = calculate_international_stock_totals(ws_holdings)
         print(f"Total International Stock: {international_stock_total}")

         bond_total = calculate_bond_totals(ws_holdings)
         print(f"Total Bond: {bond_total}")

         alternative_total = calculate_alternative_totals(ws_holdings)
         print(f"Total Alternative: {alternative_total}")

         balanced_total = calculate_balanced_totals(ws_holdings)
         print(f"Total Balanced: {balanced_total}")

         portfolio_total = calculate_portfolio_total(account_totals)
         print(f"Portfolio Total: {portfolio_total}")

         cash_allocation = calculate_cash_allocation(
                                cash_total,
                                portfolio_total)

         largest_account, largest_value = calculate_largest_account(account_totals)
         print(f"Largest Account: {largest_account} with value {largest_value}")

         largest_symbol, largest_description, largest_holding_value = calculate_largest_holding(ws_holdings)
         print(f"Largest Holding: {largest_symbol} ({largest_description}) with value {largest_holding_value:,.2f}")

         update_dashboard_data(
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
                               )


         update_history(ws_history, values)
         log_activity(ws_log, "History updated")

         update_dashboard(ws_dashboard, ws_dashboard_data, values)
         log_activity(ws_log, "Dashboard updated")

         log_activity(ws_log, "Workbook saved")
         save_workbook(wb, file)

         print("Dashboard updated successfully.")
    except Exception:
         print("Error occurred while updating dashboard.")
         traceback.print_exc()

if __name__ == "__main__":
    main()
