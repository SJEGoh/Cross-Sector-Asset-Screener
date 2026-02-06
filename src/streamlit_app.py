import streamlit as st
from helper import get_dataframe, get_filtered_universe, get_tickers
from main import get_fig



def main():
    st.set_page_config(page_title="Cross Sector Asset Screener", layout="wide")
    st.title("Cross Sector Asset Screener")
    

    df = get_dataframe()
    with st.expander("Filter settings", expanded = False):
        filtered_df = get_filtered_universe(df)
        tickers = get_tickers(filtered_df)
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
    fig, scanner_df = get_fig(tickers, day_delay)
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()
