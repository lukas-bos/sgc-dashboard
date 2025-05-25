import yfinance as yf

def fetch_latest_prices(symbols):
    tickers = yf.Tickers(" ".join(symbols))
    data = {sym: tickers.tickers[sym].info["regularMarketPrice"] for sym in symbols}
    return data

def enrich_portfolio_with_prices(df):
    prices = fetch_latest_prices(df["symbol"].tolist())
    df["price"] = df["symbol"].map(prices)
    df["value"] = df["price"] * df["quantity"]
    return df