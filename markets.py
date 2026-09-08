import yfinance as yf
from config import MARKETS

def get_yahoo_price(symbol):
    ticker = yf.Ticker(symbol.upper())

    # Try info (works for many mutual funds)
    try:
        info = ticker.info

        quote_type = (info.get("quoteType") or "").upper()

        if quote_type == "MUTUALFUND":
           fields = (
               "navPrice",
               "regularMarketPrice",
               "previousClose",
           )
        else:
            fields = (
                "regularMarketPrice",
                "previousClose",
                "navPrice",
            )

        for field in fields:
            price = info.get(field)

            if price is not None:
                return float(price)

    except Exception:
        pass

    # Finally try history
    try:
        data = ticker.history(period="1d")

        if not data.empty:
            return float(data["Close"].iloc[-1])

    except Exception:
        pass

    return None


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