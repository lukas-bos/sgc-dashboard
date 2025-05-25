import streamlit as st

def main():
    st.set_page_config(
        page_title="SGC Portfolio Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.title("📊 SGC Portfolio Dashboard")
    st.markdown("""
    Welcome to your personal portfolio dashboard.  
    Use the sidebar to navigate through:
    - **Portfolio Overview**
    - **Performance Summary**
    - **Holdings Breakdown**

    This app pulls live market data using `yfinance` and calculates current portfolio stats.
    """)


if __name__ == "__main__":
    main()