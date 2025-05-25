import streamlit as st
import altair as alt
import pandas as pd
from datetime import timedelta

from utils.portfolio_metrics import (
    prepare_portfolio_df_from_transactions,
    load_transactions,
    get_unique_symbols,
    get_price_history,
    build_portfolio_value,
    get_benchmark_history
)

from utils.style_helpers import color_returns

st.title("📊 Portfolio Overview")

# Table: Portfolio Snapshot
st.subheader("Current Portfolio Snapshot")
portfolio_df = prepare_portfolio_df_from_transactions()
# Apply color mapping to return columns
return_cols = ["1D", "1M", "YTD", "1Y"]
styled_df = portfolio_df.style.map(color_returns, subset=return_cols)
styled_df = styled_df.format(na_rep="--", decimal=".", thousands=",", precision=2)

st.dataframe(styled_df, use_container_width=True)

# Chart: Performance vs Benchmark
st.subheader("Portfolio vs Benchmark Performance")
transactions = load_transactions()
symbols = get_unique_symbols(transactions)
start_date = transactions["date"].min()

price_df = get_price_history(symbols, start_date)
portfolio_value = build_portfolio_value(transactions, price_df)
benchmark = get_benchmark_history(start_date=start_date)

benchmark.index = benchmark.index.tz_localize(None)

performance_df = pd.DataFrame({
    "Portfolio": portfolio_value.squeeze(),
    "Benchmark (TSX60)": benchmark.squeeze()
}).dropna()
performance_df = performance_df / performance_df.iloc[0] * 100
performance_df = performance_df.reset_index().rename(columns={"index": "Date"})

chart = alt.Chart(performance_df).mark_line().encode(
    x="Date:T",
    y=alt.Y("value:Q", title="Performance (%)", scale=alt.Scale(zero=False)),
    color="variable:N"
).transform_fold(
    ["Portfolio", "Benchmark (TSX60)"],
    as_=["variable", "value"]
).properties(
    width=800,
    height=400
)

st.altair_chart(chart, use_container_width=True)
