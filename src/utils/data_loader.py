import pandas as pd

def load_portfolio(path="src/data/portfolio.csv"):
    df = pd.read_csv(path)
    return df