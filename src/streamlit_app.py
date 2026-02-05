import streamlit as st
from helper import get_dataframe, get_filtered_universe, get_tickers, get_all_data
from main import get_fig



def main():
    st.title("Cross Sector Asset Screener")
    st.set_page_config(page_title="Cross Sector Asset Screener", layout="wide")

    df = get_dataframe()

    filtered_df = get_filtered_universe(df)
    tickers = get_tickers(filtered_df)
    bulk_data = get_all_data(tickers)
    c1, c2, c3 =  st.columns(3)
    with c1:
        day_delay = st.number_input(
            "Days ago",
            min_value = 0,
            max_value = 5,
            step = 1,
            value = "min"
        )
    with c2:
        x_axis = st.selectbox(
            "Select x axis",
            options = ["Coming soon", "Coming soon"]
        )
    with c3:
        y_axis = st.selectbox(
            "Select y axis",
            options = ["Coming soon", "Coming soon"]
        )
    st.plotly_chart(get_fig(tickers, day_delay))


if __name__ == "__main__":
    main()
