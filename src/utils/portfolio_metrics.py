from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

# Core Portfolio Logic

def load_transactions(path="src/data/transactions.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df.sort_values("date", inplace=True)
    return df

def get_unique_symbols(transactions) -> list[str]:
    return transactions["symbol"].unique().tolist()

def get_price_history(symbols, start_date) -> pd.DataFrame:
    price_data = {}
    for symbol in symbols:
        hist = yf.Ticker(symbol).history(start=start_date)
        price_data[symbol] = hist["Close"]
    
    price_df = pd.DataFrame(price_data)
    price_df = price_df.tz_localize(None)
    price_df.index = price_df.index.normalize()
    price_df = price_df.dropna(how='any')

    return price_df

def build_portfolio_value(transactions, price_df):
    dates = price_df.index
    portfolio_qty = pd.DataFrame(0, index=dates, columns=price_df.columns)

    print(dates)
    print(transactions["date"])

    for _, row in transactions.iterrows():
        if row["date"] not in portfolio_qty.index:
            continue
        if row["action"] == "BUY":
            portfolio_qty.loc[row["date"]:, row["symbol"]] += row["quantity"]
        elif row["action"] == "SELL":
            portfolio_qty.loc[row["date"]:, row["symbol"]] -= row["quantity"]

    return (portfolio_qty * price_df).sum(axis=1)

def get_benchmark_history(symbol="XIU.TO", start_date=None):
    try:
        data = yf.download(symbol, start=start_date)
        return data["Close"]
    except Exception as e:
        print(f"Error fetching benchmark history: {e}")
        return pd.Series(dtype=float)


# Snapshot Reporting

def fetch_ticker_info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "Company Name": info.get("longName", ""),
        }
    except Exception as e:
        print(f"Warning: Could not fetch info for {symbol}: {e}")
        return {
            "Company Name": "",
        }

def fetch_price_history(symbol, period="1y"):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        return hist["Close"]
    except Exception as e:
        print(f"Warning: Could not fetch price history for {symbol}: {e}")
        return pd.Series(dtype=float)

def calculate_returns(close_series, periods):
    returns = {}
    latest_date = close_series.index.max()
    latest_price = close_series.loc[latest_date]

    for label, days in periods.items():
        past_date = latest_date - timedelta(days=days)

        eligible_dates = close_series.index[close_series.index <= past_date]
        if len(eligible_dates) == 0:
            returns[label] = np.nan
            continue
        closest_date = eligible_dates.max()
        past_price = close_series.loc[closest_date]

        ret = (latest_price - past_price) / past_price * 100
        returns[label] = ret

    return returns

def prepare_portfolio_df_from_transactions(transactions_path="src/data/transactions.csv"):
    tx = load_transactions(transactions_path)
    latest_positions = tx.groupby("symbol")["quantity"].sum()
    symbols = latest_positions[latest_positions > 0].index.tolist()

    all_data = []
    for sym in symbols:
        qty = latest_positions[sym]
        info = fetch_ticker_info(sym)
        prices = fetch_price_history(sym)

        if prices.empty:
            print(f"Skipping {sym} due to missing price data.")
            continue

        latest_price = prices.iloc[-1]
        market_value = latest_price * qty

        periods = {
            "1D": 1,
            "1M": 30,
            "YTD": (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
            "1Y": 365,
        }
        returns = calculate_returns(prices, periods)

        row = {
            "Ticker": sym,
            "Company Name": info["Company Name"],
            "Current Price": latest_price,
            **returns
        }
        all_data.append((row, market_value))

    # Build DataFrame from rows
    portfolio_df = pd.DataFrame([r for r, _ in all_data])

    # Calculate weights based on market values
    total_value = sum(mv for _, mv in all_data)
    weights = [(mv / total_value * 100) if total_value > 0 else 0 for _, mv in all_data]

    # Insert weight column
    portfolio_df.insert(2, "Weight (%)", weights)

    # Rounding
    portfolio_df["Current Price"] = portfolio_df["Current Price"].round(2)
    for col in ["1D", "1M", "YTD", "1Y"]:
        portfolio_df[col] = portfolio_df[col].round(2)
    portfolio_df["Weight (%)"] = portfolio_df["Weight (%)"].round(2)

    return portfolio_df