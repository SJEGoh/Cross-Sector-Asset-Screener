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
        
        indics = []
        with c2:
            sc1, sc2 = st.columns(2)
            with sc1:
                x_period = st.number_input(
                    "x Time Period",
                    min_value = 1,
                    max_value = 252,
                    step = 1,
                    value = 5
                )
            with sc2:
                x_axis = st.selectbox(
                    "Select x axis",
                    options = ["DMA", "Kalman Innovation"]
                )
        indics.append({x_axis: x_period})
        with c3:
            sc1, sc2 = st.columns(2)
            with sc1:
                y_period = st.number_input(
                    "y Time Period",
                    min_value = 1,
                    max_value = 252,
                    step = 1,
                    value = 20
                )
            with sc2:
                y_axis = st.selectbox(
                    "Select y axis",
                    options = ["DMA", "Kalman Innovation"]
                )
        indics.append({y_axis: y_period})
    fig, scanner_df = get_fig(tickers, day_delay, indics)
    st.plotly_chart(fig)

    if not scanner_df.empty:
        st.divider()  # Adds a visual line separator
        st.subheader("Top Signals")

        leading = scanner_df[scanner_df["Quadrant"].str.contains("LEADING")]
        lagging = scanner_df[scanner_df["Quadrant"].str.contains("LAGGING")]
        improving = scanner_df[scanner_df["Quadrant"].str.contains("IMPROVING")]
        weakening = scanner_df[scanner_df["Quadrant"].str.contains("WEAKENING")]

        col1, col2 = st.columns(2)

        with col1:
            st.success("🚀 Top Leading")
            st.dataframe(
                leading.head(10)[["Ticker", "Signal Strength", "Volume (Z)"]]
                .style.background_gradient(subset=["Signal Strength"], cmap="Greens"),
                hide_index=True,
                width="stretch"
            )

        with col2:
            st.error("🛑 Top Lagging")
            st.dataframe(
                lagging.head(10)[["Ticker", "Signal Strength", "Volume (Z)"]]
                .style.background_gradient(subset=["Signal Strength"], cmap="Reds"),
                hide_index=True,
                width="stretch"
            )

        # 3. (Optional) Show the Turning Points (Buy/Sell signals) below
        with st.expander("Show Turning Points (Improving vs Weakening)"):
            c3, c4 = st.columns(2)
            with c3:
                st.info("✨ Improving (Need to customize heuristic for signal strength)")
                st.dataframe(improving.head(10)[["Ticker", "Signal Strength", "Volume (Z)"]], hide_index=True, width = "stretch")
            with c4:
                st.warning("⚠️ Weakening")
                st.dataframe(weakening.head(10)[["Ticker", "Signal Strength", "Volume (Z)"]], hide_index=True, width = "stretch")

if __name__ == "__main__":
    main()
