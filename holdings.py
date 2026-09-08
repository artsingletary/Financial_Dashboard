from config import HOLDINGS_COL
from markets import get_yahoo_price
from decimal import Decimal, ROUND_DOWN


def yahoo_display_price(price):
    return float(
        Decimal(str(price)).quantize(
            Decimal("0.01"),
            rounding = ROUND_DOWN
        )
    )

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

def calculate_portfolio_total(account_totals):
    return sum(account_totals.values())

def get_account_names(account_totals):
    return list(account_totals.keys())

def update_holdings(ws_holdings):
    for row in range(2, ws_holdings.max_row + 1):
        symbol = ws_holdings[
            f"{HOLDINGS_COL['symbol']}{row}"
        ].value

        if not symbol:
            continue

        shares = ws_holdings[
            f"{HOLDINGS_COL['shares']}{row}"
        ].value or 0

        shares = float(
            str(shares)
            .replace(",", "")
            .replace("$", "")
        )

        source = str(
            ws_holdings[
                f"{HOLDINGS_COL['source']}{row}"
            ].value
        ).strip().lower()

        if source == "yahoo":
            price = get_yahoo_price(symbol)

        elif source in ("manual", "tsp"):
            raw_price_value = ws_holdings[
                f"{HOLDINGS_COL['raw_price']}{row}"
            ].value

            if raw_price_value in (None, ""):
                raw_price_value = ws_holdings[
                    f"{HOLDINGS_COL['price']}{row}"
                ].value

            try:
                price = float(
                    str(raw_price_value)
                    .replace("$", "")
                    .replace(",", "")
                    .strip()
                )
            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid price on holdings row {row} "
                    f"for symbol {symbol}: {raw_price_value!r}"
                )

        else:
            print(f"Unknown source '{source}' on row {row}")
            continue

        if price is not None:
            raw_price = float(price)

            ws_holdings[
                f"{HOLDINGS_COL['raw_price']}{row}"
            ] = raw_price

            ws_holdings[
                f"{HOLDINGS_COL['price']}{row}"
            ] = yahoo_display_price(raw_price)

            ws_holdings[
                f"{HOLDINGS_COL['market_value']}{row}"
            ] = round(raw_price * shares, 2)
