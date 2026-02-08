import streamlit as st
# Must be the very first Streamlit command
st.set_page_config(page_title="Backtester", layout="wide")

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from helper import get_polygon_data, get_tickers, get_dataframe, UNIVERSE
from features import get_indic
from portfolio import SignalPortfolio

INDICATOR_OPTIONS = [
    "DMA", "Kalman Innovation", "First Order Kalman", "Second Order Kalman", 
    "Percentage Retracement", "Second Order Percentage Retracement", "Second Order DMA", 
    "Lag/Lead Days", "Rolling Alpha", "Lag/Lead Corr"
]

REQUIRES_BENCHMARK = ["Lag/Lead Days", "Rolling Alpha", "Lag/Lead Corr"]

def main():
    st.title("Backtester")
    df = get_dataframe()
    
    # --- MOVED TICKER SELECTION HERE (OUTSIDE COLUMNS) ---
    # This ensures it spans the top and doesn't push one side down
    c1, c2 = st.columns(2)
    with c1:
        ticker = st.selectbox("Select Asset to Backtest", options=df["ticker"].unique().tolist(), key="Important")
    with c2:
        length = st.number_input("Length (days)", min_value = 5, max_value = 365)
    st.divider() # Optional: Adds a nice line to separate settings from logic
    
    # Define the main columns 
    c1, c2 = st.columns(2)

    # --- BUY SIDE (Left Column) ---
    with c1:
        st.subheader("🟢 Buy Side")
        
        # Buy Entry
        st.caption("Entry Logic")
        cc1, cc2 = st.columns(2)
        with cc1:
            buy_indic = st.selectbox("Select Indicator", options=INDICATOR_OPTIONS, key="b_ind")
            if buy_indic in REQUIRES_BENCHMARK:
                buy_bench = st.selectbox("Select Benchmark", options=df["ticker"].unique().tolist(), key="b_bench")
        with cc2:
            buy_op = st.selectbox("Operator", [">", "<"], key="b_op")
            buy_threshold = st.number_input("Threshold", value=0.0, key="b_val")

        # Buy Exit
        st.write("") # Spacer
        st.caption("Exit Logic (Close Long)")
        cc1, cc2 = st.columns(2)
        with cc1:
            close_buy_indic = st.selectbox("Select Indicator", options=INDICATOR_OPTIONS, key="cb_ind")
            if close_buy_indic in REQUIRES_BENCHMARK:
                close_buy_bench = st.selectbox("Select Benchmark", options=df["ticker"].unique().tolist(), key="cb_bench")
        with cc2:
            close_buy_op = st.selectbox("Operator", [">", "<"], key="cb_op")
            close_buy_threshold = st.number_input("Threshold", value=0.0, key="cb_val")

    # --- SHORT SIDE (Right Column) ---
    with c2:
        st.subheader("🔴 Short Side")
        
        # Short Entry
        st.caption("Entry Logic")
        cc1, cc2 = st.columns(2)
        with cc1:
            sell_indic = st.selectbox("Select Indicator", options=INDICATOR_OPTIONS, key="s_ind")
            if sell_indic in REQUIRES_BENCHMARK:
                sell_bench = st.selectbox("Select Benchmark", options=df["ticker"].unique().tolist(), key="s_bench")
        with cc2:
            sell_op = st.selectbox("Operator", [">", "<"], key="s_op")
            sell_threshold = st.number_input("Threshold", value=0.0, key="s_val")

        # Short Exit
        st.write("") # Spacer
        st.caption("Exit Logic (Close Short)")
        cc1, cc2 = st.columns(2)
        with cc1:
            close_sell_indic = st.selectbox("Select Indicator", options=INDICATOR_OPTIONS, key="cs_ind")
            if close_sell_indic in REQUIRES_BENCHMARK:
                close_sell_bench = st.selectbox("Select Benchmark", options=df["ticker"].unique().tolist(), key="cs_bench")
        with cc2:
            close_sell_op = st.selectbox("Operator", [">", "<"], key="cs_op")
            close_sell_threshold = st.number_input("Threshold", value=0.0, key="cs_val")
        
# --- EXECUTION LOGIC ---
    st.divider()
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        
        # 1. FETCH DATA
        with st.status("Fetching Data...", expanded=True) as status:
            df = get_polygon_data(ticker, days_back=730)
            if df.empty:
                status.error("No data found.")
                st.stop()
            
            # 2. CALCULATE INDICATORS
            status.write("Calculating indicators...")
            
            # Helper to safely get indicator data
            def get_signal_data(indic, bench):
                if indic in REQUIRES_BENCHMARK:
                    if not bench: return None
                    bench_df = get_polygon_data(bench, days_back=1000)
                    # Align dates
                    aligned_bench = bench_df.reindex(df.index).ffill()
                    return get_indic(indic)(df[["Close"]], aligned_bench[["Close"]], 20)
                return get_indic(indic)(df[["Close"]], 20)

        # Calculate the 4 columns needed

            # Handle Series vs DataFrame return types
            def extract_series(res):
                if isinstance(res, pd.DataFrame): return res.iloc[:, -1]
                return res

            df['Buy_Ind'] = extract_series(get_signal_data(buy_indic, buy_bench if 'buy_bench' in locals() else None))
            df['Exit_Buy_Ind'] = extract_series(get_signal_data(close_buy_indic, close_buy_bench if 'close_buy_bench' in locals() else None))
            
            df['Sell_Ind'] = extract_series(get_signal_data(sell_indic, sell_bench if 'sell_bench' in locals() else None))
            df['Exit_Sell_Ind'] = extract_series(get_signal_data(close_sell_indic, close_sell_bench if 'close_sell_bench' in locals() else None))
            df = df.iloc[-length:]
            print(df)
            status.write(f"Simulation running on {length} days.")
            status.update(label="Complete", state="complete", expanded=False)


        # 3. RUN SIMULATION LOOP
        port = SignalPortfolio(initial_cash=10000)
        equity = []
        
        # Helper: Logic Check
        check = lambda val, op, thresh: (val > thresh) if op == ">" else (val < thresh)

        for i in range(len(df)):
            row = df.iloc[i]
            price = row['Close']
            sig = None # Default to Hold
            date = df.index[i]
            # CURRENT STATE
            pos = port.position
            
            # LOGIC TREE
            if pos > 0: # Long
                if check(row['Exit_Buy_Ind'], close_buy_op, close_buy_threshold):
                    sig = 0 # Close
            
            elif pos < 0: # Short
                if check(row['Exit_Sell_Ind'], close_sell_op, close_sell_threshold):
                    sig = 0 # Close
                    
            else: # Flat
                if check(row['Buy_Ind'], buy_op, buy_threshold):
                    sig = 1 # Long
                elif check(row['Sell_Ind'], sell_op, sell_threshold):
                    sig = -1 # Short
            
            equity.append(port.equity)
            port.update(sig, price, date)
        # 4. RESULTS PROCESSING
        # Extract history from the class
        res_df = pd.DataFrame(port.history)
        
        if res_df.empty:
            st.error("No trades or history generated.")
            st.stop()
            
        res_df.set_index("Date", inplace=True)
        
        # Calculate Metrics
        final_equity = res_df['Equity'].iloc[-1]
        total_ret = (final_equity / 10000) - 1
        
        # Max Drawdown
        roll_max = res_df['Equity'].cummax()
        dd = (res_df['Equity'] / roll_max) - 1
        max_dd = dd.min()
        
        # Hit Rate (Reconstruct trades)
        trades = []
        entry_eq = 0
        pos_arr = res_df['Position'].values
        eq_arr = res_df['Equity'].values
        
        for i in range(1, len(pos_arr)):
            prev = pos_arr[i-1]
            curr = pos_arr[i]
            
            if prev == 0 and curr != 0: # Entry
                entry_eq = eq_arr[i-1]
            elif prev != 0 and curr == 0: # Exit
                trades.append(eq_arr[i] - entry_eq)
            elif prev != 0 and curr != 0 and np.sign(prev) != np.sign(curr): # Flip
                trades.append(eq_arr[i] - entry_eq)
                entry_eq = eq_arr[i]

        win_rate = len([t for t in trades if t > 0]) / len(trades) if trades else 0.0

        # --- DISPLAY ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Return", f"{total_ret:.2%}")
        m2.metric("Final Equity", f"${final_equity:,.2f}")
        m3.metric("Max Drawdown", f"{max_dd:.2%}")
        m4.metric("Win Rate", f"{win_rate:.0%} ({len(trades)} trades)")
        
        # Plot
        st.subheader("Equity Curve")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=res_df.index, y=res_df['Equity'], name="Strategy", line=dict(color="#00ff00")))
        fig.add_trace(go.Scatter(x=res_df.index, y=res_df['Price'], name="Asset Price", line=dict(color="gray", dash="dot"), yaxis="y2"))
        
        fig.update_layout(
            template="plotly_dark",
            yaxis2=dict(overlaying="y", side="right", showgrid=False),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
if __name__ == "__main__":
    main()
