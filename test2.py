import yfinance as yf

ticker = yf.Ticker("DFIGX")

print("fast_info:")
print(ticker.fast_info)

print()

print("info prices:")
info = ticker.info

for key in [
    "regularMarketPrice",
    "previousClose",
    "navPrice",
    "currentPrice",
]:
    print(key, "=", info.get(key))