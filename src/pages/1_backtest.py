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
        
    st.divider()
    
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True):
        
        # 1. DATA FETCHING
        with st.status("Running Simulation...", expanded=True) as status:
            status.write("Fetching market data...")
            df = get_polygon_data(ticker, days_back=730)
            
            if df.empty:
                status.error(f"No data found for {ticker}")
                st.stop()
            
            # 2. INDICATOR CALCULATION
            status.write("Calculating signals...")
            
            # Helper to calculate and extract series safely
            def get_series(ind_name, bench_ticker):
                try:
                    if ind_name in REQUIRES_BENCHMARK:
                        if not bench_ticker: return None
                        b_df = get_polygon_data(bench_ticker, days_back=1000)
                        b_data = b_df.reindex(df.index).ffill()
                        res = get_indic(ind_name)(df[["Close"]], b_data[["Close"]], 20)
                    else:
                        res = get_indic(ind_name)(df[["Close"]], 20)
                    
                    # Handle if it returns DataFrame or Series
                    if isinstance(res, pd.DataFrame): return res.iloc[:, -1]
                    return res
                except Exception as e:
                    return None

            # Calculate the 4 Control Signals
            df['B_Entry'] = get_series(buy_indic, buy_bench if 'buy_bench' in locals() else None)
            df['B_Exit'] = get_series(close_buy_indic, close_buy_bench if 'close_buy_bench' in locals() else None)
            df['S_Entry'] = get_series(sell_indic, sell_bench if 'sell_bench' in locals() else None)
            df['S_Exit'] = get_series(close_sell_indic, close_sell_bench if 'close_sell_bench' in locals() else None)

            # Drop NaNs to start simulation clean
            df = df.dropna()
            
            if df.empty:
                status.error("❌ Data Wipeout: Indicators generated NaNs (likely missing benchmark or short history).")
                st.stop()
                
            status.write(f"Simulating {len(df)} trading days...")

            # 3. SIMULATION LOOP
            port = SignalPortfolio(initial_cash=10000)
            
            # Logic Lambda: (Value > Threshold) or (Value < Threshold)
            check = lambda val, op, thresh: (val > thresh) if op == ">" else (val < thresh)
            
            for i in range(len(df)):
                row = df.iloc[i]
                price = row['Close']
                date = df.index[i]  # Capture Date
                
                # Signal Logic
                sig = None # Default: Hold/None
                
                # Current Position
                pos = port.position
                
                if pos > 0: # LONG
                    if check(row['B_Exit'], close_buy_op, close_buy_threshold): sig = 0
                
                elif pos < 0: # SHORT
                    if check(row['S_Exit'], close_sell_op, close_sell_threshold): sig = 0
                    
                else: # FLAT
                    if check(row['B_Entry'], buy_op, buy_threshold): sig = 1
                    elif check(row['S_Entry'], sell_op, sell_threshold): sig = -1
                
                # Update Portfolio (PASS THE DATE)
                port.update(sig, price, date)
                
            status.update(label="Backtest Complete", state="complete", expanded=False)

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
        
        # Sharpe Ratio (Annualized)
        daily_ret = res_df['Equity'].pct_change().dropna()
        if daily_ret.std() > 0:
            sharpe = (daily_ret.mean() / daily_ret.std()) * (252**0.5)
        else:
            sharpe = 0.0
        
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
        m2.metric("Sharpe Ratio", f"{sharpe:.2f}")
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
