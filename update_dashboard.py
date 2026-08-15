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
    get_account_names
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

# Markets 
MARKETS = {
   "Dow": {
      "ticker": "^DJI",
      "row": 2
   },
   "S&P 500": {
     "ticker": "^GSPC",
       "row": 3
   },
   "Nasdaq": { 
   "ticker": "^IXIC",
   "row": 4
   }
}



def log_activity(ws_log, action, status = "Success"):
   ws_log.append([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        action,
        status
    ])

def update_market_sheet(ws_market):
   values = {}

   for name, info in MARKETS.items():
      symbol = info["ticker"]
      row = info["row"]
      
      #data = yf.Ticker(symbol).history(period="max")

      ticker = yf.Ticker(symbol)

      data = ticker.history(period="1d")

      if not data.empty:
          price = round(data['Close'].iloc[-1], 2)
      else:
          info = ticker.fast_info

          if info and info.get('last_price') is not None:
              price = round(info['last_price'], 2)
          else:
              print(f"No price available for {symbol}. Skipping.")
              continue

      close = data['Close']
      high = data['High']

      current = round(close.iloc[-1], 2)
      record_close = round(close.max(), 2)
      record_close_date = close.idxmax().date()
      record_high = high.max()
      pct_from_high = (current / record_high) - 1


      # Prices
      ws_market[f"B{row}"] = current
      ws_market[f"C{row}"] = record_close

      # Date 
      ws_market[f"D{row}"] = record_close_date
      ws_market[f"D{row}"].number_format = "mmm d, yyyy"

      # Percent from high (formatted properly)
      ws_market[f"E{row}"] = pct_from_high
      ws_market[f"E{row}"].number_format = "0.00%"

      # Save for history log
      values[name] = {
          "price": current,
          "pct_from_high": pct_from_high
       }
   return values

# --------------------------
# Append to History Sheet
#--------------------------

def update_history(ws_history, values):

    row = [
        date.today(),
        values["Dow"]["price"],
        values["S&P 500"]["price"],
        values["Nasdaq"]["price"]
    ]

    ws_history.append(row)

def get_yahoo_price(symbol):
    ticker = yf.Ticker(symbol.upper())

    # Try fast_info first
    try:
        price = ticker.fast_info.get("lastPrice")
        if price is not None:
            return round(price, 2)
    except Exception:
        pass

    # Try info (works for many mutual funds)
    try:
        info = ticker.info

        for field in (
            "regularMarketPrice",
            "previousClose",
            "navPrice",
        ):
            price = info.get(field)
            if price is not None:
                return round(price, 2)
    except Exception:
        pass

    # Finally try history
    try:
        data = ticker.history(period="1d")
        if not data.empty:
            return round(data["Close"].iloc[-1], 2)
    except Exception:
        pass

    return None

def update_holdings (ws_holdings):
   for row in range(2, ws_holdings.max_row + 1):

       symbol = ws_holdings[f"{HOLDINGS_COL['symbol']}{row}"].value
       if not symbol:
              continue

       shares = ws_holdings[f"{HOLDINGS_COL['shares']}{row}"].value or 0
       shares = float(str(shares).replace(",", "").replace("$", ""))

       source = str(ws_holdings[f"{HOLDINGS_COL['source']}{row}"].value).strip().lower()

       if source == "yahoo":
          price = get_yahoo_price(symbol)

          if price is not None:
            ws_holdings[f"{HOLDINGS_COL['price']}{row}"] = price

       elif source in ("manual", "tsp"):
          raw_price = ws_holdings[f"{HOLDINGS_COL['price']}{row}"].value

          try:
            price = float(
               str(raw_price)
               .replace("$", "")
               .replace(",", "")
              .strip()
            )   
          except (TypeError, ValueError):
            raise ValueError(
                f"Invalid price on holdings row {row}"
                f"for symbol {symbol}: {raw_price!r}")
       else: 
            print(f"Unknown source '{source}' on row {row}")
            continue

       # Calculate Market Value for EVERY holding
       if price is not None:
            ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"] = round(price * shares, 2)

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
