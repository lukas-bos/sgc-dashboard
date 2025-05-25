import streamlit as st
from utils.data_loader import load_portfolio
from utils.market_data import enrich_portfolio_with_prices

st.title("Portfolio Overview")

portfolio_df = load_portfolio()
portfolio_df = enrich_portfolio_with_prices(portfolio_df)

st.dataframe(portfolio_df)

total_value = portfolio_df["value"].sum()
st.metric("Total Portfolio Value", f"${total_value:,.2f}")
