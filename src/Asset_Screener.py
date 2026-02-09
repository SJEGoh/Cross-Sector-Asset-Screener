import streamlit as st
from helper import get_dataframe, get_filtered_universe, get_tickers, get_range, rich, poor, get_scatter
from main import get_fig



def main():
    st.set_page_config(page_title="Cross Sector Asset Screener", layout="wide")
    st.title("Cross Sector Asset Screener")
    
    t1, t2 = st.tabs(["Screener", "Visualizer"])
    with t1:
        df = get_dataframe()
        with st.expander("Filter settings", expanded = True):
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
                x_period = st.number_input(
                    "Second Order Kalman Time Period",
                    min_value = 1,
                    max_value = 252,
                    step = 1,
                    value = 5
                )

                x_axis = "Second Order Kalman"
            indics.append(x_axis)
            periods.append(x_period)
            with c3:
                y_period = st.number_input(
                    "Distance from DMA Period",
                    min_value = 1,
                    max_value = 252,
                    step = 1,
                    value = 20
                )

                y_axis = "Distance from DMA"
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
            fig, scanner_df = get_fig(tickers, day_delay, indics, periods, [3, 3], bench_x, bench_y)
            scanner_df["Volume (Z)"] = scanner_df["Volume (Z)"].map(lambda x: f"{x:.1f}")
        except:
            st.write("Ticker has no data. Choose another.")
            st.stop()


        st.plotly_chart(fig)

        if not scanner_df.empty:
            st.divider()  # Adds a visual line separator
            st.subheader("Top Signals")

            top_x = scanner_df.sort_values(by = "Signal_x", ascending = False).head(10)
            low_x = scanner_df.sort_values(by = "Signal_x", ascending = True).head(10)
            top_y = scanner_df.sort_values(by = "Signal_y", ascending = False).head(10)
            low_y = scanner_df.sort_values(by = "Signal_y", ascending = True).head(10)


            col1, col2 = st.columns(2)

            with col1:
                st.success("Most Expensive")
                top_x = top_x[["Ticker", "Signal_x", "Volume (Z)"]]
                top_x.columns = ["Ticker", "Z-score", "Volume (Z)"]
                st.dataframe(
                    top_x.head(10)[["Ticker", "Z-score", "Volume (Z)"]]
                    .style.background_gradient(subset=["Z-score"], cmap="Greens").format({"Z-score": "{:.1f}"}),
                    hide_index=True,
                    width="stretch"
                )

            with col2:
                st.error("Least Expensive")
                low_x = low_x[["Ticker", "Signal_x", "Volume (Z)"]]
                low_x.columns = ["Ticker", "Z-score", "Volume (Z)"]
                st.dataframe(
                    low_x.head(10)[["Ticker", "Z-score", "Volume (Z)"]]
                    .style.background_gradient(subset=["Z-score"], cmap="Reds_r").format({"Z-score": "{:.1f}"}),
                    hide_index=True,
                    width="stretch"
                )

            # 3. (Optional) Show the Turning Points (Buy/Sell signals) below
            with st.expander("Show Turning Points (Improving vs Weakening)"):
                c3, c4 = st.columns(2)
                with c3:
                    st.info("✨ Improving (Need to customize heuristic for signal strength)")
                    top_y = top_y[["Ticker", "Signal_x", "Volume (Z)"]]
                    top_y.columns = ["Ticker", "Z-score", "Volume (Z)"]
                    st.dataframe(top_y.head(10)[["Ticker", "Z-score", "Volume (Z)"]].style.format({"Z-score": "{:.1f}"}), hide_index=True, width = "stretch")
                with c4:
                    st.warning("⚠️ Weakening")
                    low_y = low_y[["Ticker", "Signal_x", "Volume (Z)"]]
                    low_y.columns = ["Ticker", "Z-score", "Volume (Z)"]
                    st.dataframe(low_y.head(10)[["Ticker", "Z-score", "Volume (Z)"]].style.format({"Z-score": "{:.1f}"}), hide_index=True, width = "stretch")
    with t2:
        curr_ticker = st.selectbox("Select Ticker", options = df["ticker"].unique().tolist(), index = 0)

        feature = st.selectbox(
            "Select Feature",
            options = ["Distance from DMA", "Second Order Kalman"]
        )
        period = st.number_input(
            "Select Period",
            min_value = 1,
            max_value = 252,
            step = 1,
            value = 5
        )
        visual_period = st.number_input(
            "Select Period to visualise",
            min_value = 1,
            max_value = 252,
            step = 1,
            value = 5
        )
        st.plotly_chart(get_scatter(curr_ticker, feature, period, visual_period))

        

if __name__ == "__main__":
    main()
