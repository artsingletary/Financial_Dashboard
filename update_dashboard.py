import os
import yfinance as yf
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from datetime import datetime, date
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil   

#--------------------------
# Constants
#--------------------------

# File Settings
WORKBOOK_FOLDER = os.path.expanduser("~/OneDrive/Active")
WORKBOOK_NAME = "Financial Dashboard.xlsx"

# Worksheet Names
DASHBOARD_SHEET = "Dashboard"
MARKET_SHEET = "Market Data"
HISTORY_SHEET = "History"
ACTIVITY_SHEET = "Activity Log"
HOLDINGS_SHEET = "Holdings"
TSP_PRICE_SHEET = "TSP Prices"

HOLDINGS_COL = {
    "account_type": "A",
    "symbol": "B",
    "expense_ratio": "C",
    "description": "D",
    "shares": "E",
    "price": "F",
    "market_value": "G",
    "source": "H",
    "asset_class": "I",
    "allocation_category": "J",
    "account": "K",
    "owner": "L",
    "tax_status": "M",
    "target": "N",
    "notes": "O" 
    }
   


# Dashboard Colors
GREEN = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
YELLOW = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
RED = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

# Dashboard Thresholds
GREEN_THRESHOLD = -0.01  # Within 1% of record high
YELLOW_THRESHOLD = -0.03  # Within 3% of record high

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

# Dashboard Cells Mapping
DASHBOARD_CELLS = {
   "Dow": {
      "price": "B25",
      "status": "C25"
   },
   "S&P 500": {
      "price": "B26",
      "status": "C26"
   },
   "Nasdaq": {
      "price": "B27",
      "status": "C27"
   }
}

# Open the workbook and return the workbook object and file path
def open_workbook():
    file = os.path.join(WORKBOOK_FOLDER, WORKBOOK_NAME)
    if not os.path.exists(file):
        raise FileNotFoundError(f"Workbook not found at {file}. Please ensure the file exists.")
    wb = load_workbook(file)
    return wb, file

def get_market_sheet(wb):
    return wb[MARKET_SHEET]

def get_dashboard_sheet(wb):
    return wb[DASHBOARD_SHEET]

def get_history_sheet(wb):
    for name in wb.sheetnames:
        if name.strip().lower() == "history":
            return wb[name]
    return wb.create_sheet(HISTORY_SHEET)

def get_activity_sheet(wb):
    return wb[ACTIVITY_SHEET]

def get_holdings_sheet(wb):
    return wb[HOLDINGS_SHEET]

#--------------------------
# Update Market Data
#--------------------------

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

       source = str(ws_holdings[f"{HOLDINGS_COL['source']}{row}"].value).strip().lower()

       if source == "yahoo":
          price = get_yahoo_price(symbol)

          if price is not None:
            ws_holdings[f"{HOLDINGS_COL['price']}{row}"] = price

       elif source in ("manual", "tsp"):
            price = ws_holdings[f"{HOLDINGS_COL['price']}{row}"].value
       else: 
           print(f"Unknown source '{source}' on row {row}")
           continue

       # Calculate Market Value for EVERY holding
       if price is not None:
            ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"] = round(price * shares, 2)


def calculate_account_totals(ws_holdings):
    account_totals = {}

    for row in range(2, ws_holdings.max_row + 1):
        account = ws_holdings[f"{HOLDINGS_COL['account']}{row}"].value

        if account is not None:
            account = " ".join(str(account).split())

        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if not account:
            continue

        account_totals[account] = account_totals.get(account, 0) + value

    return account_totals

def calculate_taxable_totals(ws_holdings):
    total = 0

    for row in range(2, ws_holdings.max_row + 1):
        tax_status = ws_holdings[f"{HOLDINGS_COL['tax_status']}{row}"].value
        market_value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if str(tax_status).strip().lower() == "taxable":
            total += market_value

    return round(total, 2)


def calculate_tax_deferred_totals(ws_holdings):
    total = 0

    for row in range(2, ws_holdings.max_row + 1):
        tax_status = ws_holdings[f"{HOLDINGS_COL['tax_status']}{row}"].value
        market_value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if str(tax_status).strip().lower() == "tax deferred":
            total += market_value

    return round(total, 2)

def calculate_roth_totals(ws_holdings):
    roth_total = 0

    for row in range(2, ws_holdings.max_row + 1):
        tax_status = ws_holdings[f"{HOLDINGS_COL['tax_status']}{row}"].value
        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if tax_status == "Roth-Tax Free":
            roth_total += value

    return round(roth_total, 2)


def calculate_cash_totals(ws_holdings):
    cash_total = 0

    for row in range(2, ws_holdings.max_row + 1):
        allocation_category = ws_holdings[f"{HOLDINGS_COL['allocation_category']}{row}"].value
        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if allocation_category == "Cash":
            cash_total += value

    return round(cash_total, 2)

def calculate_us_stock_totals(ws_holdings):
    us_stock_total = 0

    for row in range(2, ws_holdings.max_row + 1):
        allocation_category = ws_holdings[f"{HOLDINGS_COL['allocation_category']}{row}"].value
        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if allocation_category == "US Stock":
            us_stock_total += value

    return round(us_stock_total, 2)


def calculate_international_stock_totals(ws_holdings):
    international_stock_total = 0

    for row in range(2, ws_holdings.max_row + 1):
        allocation_category = ws_holdings[f"{HOLDINGS_COL['allocation_category']}{row}"].value
        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if allocation_category == "International Stock":
            international_stock_total += value

    return round(international_stock_total, 2)


def calculate_bond_totals(ws_holdings):
    bond_total = 0

    for row in range(2, ws_holdings.max_row + 1):
        allocation_category = ws_holdings[f"{HOLDINGS_COL['allocation_category']}{row}"].value
        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if allocation_category == "Bond":
            bond_total += value

    return round(bond_total, 2)

def calculate_alternative_totals(ws_holdings):
    alternative_total = 0

    for row in range(2, ws_holdings.max_row + 1):
        allocation_category = ws_holdings[f"{HOLDINGS_COL['allocation_category']}{row}"].value
        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if allocation_category == "Alternative":
            alternative_total += value

    return round(alternative_total, 2)

def calculate_balanced_totals(ws_holdings):
    balanced_total = 0

    for row in range(2, ws_holdings.max_row + 1):
        allocation_category = ws_holdings[f"{HOLDINGS_COL['allocation_category']}{row}"].value
        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if allocation_category == "Balanced":
            balanced_total += value

    return round(balanced_total, 2)

def calculate_cash_allocation(cash_total, portfolio_total):
    if portfolio_total == 0:
        return 0
    return round(cash_total / portfolio_total, 4)

def calculate_largest_account(account_totals):
    largest_account = max(account_totals, key=account_totals.get)

    largest_value = account_totals[largest_account]
    return largest_account, round(largest_value, 2)

def calculate_largest_holding(ws_holdings):
    largest_symbol = None
    largest_description = None
    largest_value = 0

    for row in range(2, ws_holdings.max_row + 1):
        symbol = ws_holdings[f"{HOLDINGS_COL['symbol']}{row}"].value
        description = ws_holdings[f"{HOLDINGS_COL['description']}{row}"].value
        value = ws_holdings[f"{HOLDINGS_COL['market_value']}{row}"].value or 0

        if value > largest_value:
            largest_value = value
            largest_symbol = symbol
            largest_description = description

    return largest_symbol, largest_description, round(largest_value, 2)

def get_account_names(account_totals):
    return list(account_totals.keys())

def calculate_portfolio_total(account_totals):
    return sum(account_totals.values())

def save_workbook(wb, file):
    wb.save(file)

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
    except Exception as e:
         print(f"Error: {e}")

if __name__ == "__main__":
    main()
