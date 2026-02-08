import streamlit as st
from helper import get_dataframe, get_filtered_universe, get_tickers, get_range, rich, poor
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
        periods = []
        bench_x = None
        bench_y = None
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
                    options = ["DMA", "Kalman Innovation", "First Order Kalman", "Second Order Kalman", "Percentage Retracement", "Second Order Percentage Retracement",
                    "Second Order DMA", "Lag/Lead Days", "Rolling Alpha", "Lag/Lead Corr"]
                )
                if x_axis == "Lag/Lead Days" or x_axis == "Rolling Alpha" or x_axis == "Lag/Lead Corr":
                    bench_x = st.multiselect("Select x Benchmark", df["ticker"].unique().tolist())
                    st.write("Note: Using this may take a while")
        indics.append(x_axis)
        periods.append(x_period)
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
                    options = ["DMA", "Kalman Innovation","First Order Kalman", "Second Order Kalman", "Percentage Retracement", "Second Order Percentage Retracement",
                    "Second Order DMA", "Lag/Lead Days", "Rolling Alpha", "Lag/Lead Corr"]
                )
                if y_axis == "Lag/Lead Days" or y_axis == "Rolling Alpha" or y_axis == "Lag/Lead Corr":
                    bench_y = st.multiselect("Select y Benchmark", df["ticker"].unique().tolist())
                    st.write("Note: Using this may take a while")
        indics.append(y_axis)
        periods.append(y_period)
    _, b1, _, b3 = st.columns([0.2, 0.2, 0.2, 0.4])
    with b1:
        if st.button(":red[Cheap Assets]"):
            poor()
    with b3:
        if st.button(":green[Expensive Assets]"):
            rich()

    try:
        fig, scanner_df = get_fig(tickers, day_delay, indics, periods, [get_range(x_axis) if not (bench_x == "Lag/Lead Days") else periods[0], get_range(y_axis) if not (bench_y == "Lag/Lead Days") else periods[1]], bench_x, bench_y)
        scanner_df["Signal Strength"] = scanner_df["Signal Strength"].map(lambda x: f"{x:.1f}")
        scanner_df["Volume (Z)"] = scanner_df["Volume (Z)"].map(lambda x: f"{x:.1f}")
    except:
        st.write("Please select a benchmark or change axes")
        return

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
