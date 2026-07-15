import yfinance as yf
symbol = "DFALX"  # Example stock symbol
ticker = yf.Ticker(symbol)
print (ticker.fast_info)  # Print the stock information
print (ticker.info)  # Print the stock information
