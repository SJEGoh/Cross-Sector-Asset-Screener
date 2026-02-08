from helper import get_volume, get_polygon_data
from features import get_indic
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np
# Ok just make this into a giant function. Inputs: (day, universe, )

@st.cache_data(ttl="1d")
def get_master_data(tickers):
    master_dict = {}

    
    for i, ticker in enumerate(tickers):
        try:
            df = get_polygon_data(ticker, days_back=730)
            
            if not df.empty and len(df) > 100:
                master_dict[ticker] = df
                
        except Exception as e:
            print(f"Skipping {ticker}: {e}")
            
    return master_dict

def get_fig(tickers, day_delay, indics, periods, chart_range, bench_x, bench_y):
    fig = go.Figure()
    all_x = []
    all_y = []
    all_volumes = []
    all_labels = []
    all_skews = []
    all_kurts = []
    scanner_data = []
    master_dict = get_master_data(tickers)
    for ticker in tickers:
        try:
            data = master_dict[ticker]
        except:
            print(f"Skipping {ticker}")
            continue
        if data.empty or data.shape[0] < 100:
            continue

        # Definitely a better way to do this but eh

        if bench_x:
            bx = get_polygon_data(bench_x[0], days_back = 730)
            try:
                indic_result = get_indic(indics[0])(data[["Close"]], bx, periods[0])

                # 2. Check if data exists
                if indic_result.empty:
                    print(f"Skipping {ticker}: Indicator returned no data (dates didn't align?).")
                    continue

                # 3. Handle DataFrame vs Series (Crucial for Lag/Lead)
                if isinstance(indic_result, pd.DataFrame):
                    # Default to the first column (Peak_Lag_Days) if it's the Lag indicator
                    # Or you can add logic: if 'Max_Correlation' in indic_result.columns ...
                    result_series = indic_result.iloc[:, 0] 
                else:
                    result_series = indic_result

                # 4. Check if we have enough history for the day_delay
                target_idx = -1 * (day_delay + 1)
                if len(result_series) < abs(target_idx):
                    print(f"Skipping {ticker}: Not enough history for delay {day_delay}.")
                    continue

                # 5. Get the value safely
                x_val = result_series.iloc[target_idx]
                all_x.append(x_val)

            except Exception as e:
                print(f"Error calculating X-axis for {ticker}: {e}")
                continue
        else:
            all_x.append(x_val := get_indic(indics[0])(data[["Close"]], periods[0]).iloc[-1 * (day_delay + 1)])
        if bench_y:
            by = get_polygon_data(bench_y[0], days_back = 730)
            try:
                indic_result = get_indic(indics[1])(data[["Close"]], by, periods[0])

                # 2. Check if data exists
                if indic_result.empty:
                    print(f"Skipping {ticker}: Indicator returned no data (dates didn't align?).")
                    continue

                # 3. Handle DataFrame vs Series (Crucial for Lag/Lead)
                if isinstance(indic_result, pd.DataFrame):
                    # Default to the first column (Peak_Lag_Days) if it's the Lag indicator
                    # Or you can add logic: if 'Max_Correlation' in indic_result.columns ...
                    result_series = indic_result.iloc[:, 0] 
                else:
                    result_series = indic_result

                # 4. Check if we have enough history for the day_delay
                target_idx = -1 * (day_delay + 1)
                if len(result_series) < abs(target_idx):
                    print(f"Skipping {ticker}: Not enough history for delay {day_delay}.")
                    continue

                # 5. Get the value safely
                y_val = result_series.iloc[target_idx]
                all_y.append(y_val)

            except Exception as e:
                print(f"Error calculating X-axis for {ticker}: {e}")
                continue
        else:
                    all_y.append(y_val := get_indic(indics[1])(data[["Close"]], periods[1]).iloc[-1 * (day_delay + 1)])


        all_volumes.append(vol_val := get_volume(data).iloc[-1 * (day_delay + 1)]) 
        all_labels.append(ticker)

        quadrant = "Neutral"
        if x_val < 0 and y_val > 0:
            quadrant = "IMPROVING (Buy Beta)"
        elif x_val > 0 and y_val > 0:
            quadrant = "LEADING (Hold)"
        elif x_val > 0 and y_val < 0:
            quadrant = "WEAKENING (Sell Vol)"
        elif x_val < 0 and y_val < 0:
            quadrant = "LAGGING (Avoid)"

        rets = data["Close"].pct_change()
        
        # Calculate Rolling Skew & Kurtosis
        # We access .iloc[idx] to ensure we respect the 'day_delay' (No lookahead)
        all_skews.append(skew_val := rets.rolling(periods[0]).skew().fillna(0).iloc[-1 * (day_delay + 1)])
        all_kurts.append(kurt_val := rets.rolling(periods[0]).kurt().fillna(0).iloc[-1 * (day_delay + 1)])


        # Geometric distance
        strength = (x_val**2 + y_val**2)**0.5
        # add different heuristic for cross-over opportunities
        scanner_data.append({
            "Ticker": ticker,
            "Quadrant": quadrant,
            "Signal Strength": float(strength), # ensure float for sorting
            "Valuation (X)": float(x_val),
            "Momentum (Y)": float(y_val),
            "Volume (Z)": float(vol_val),
            "Skew": float(skew_val),
            "Kurt": float(kurt_val)
        })
    kurts_skews = np.stack((all_skews, all_kurts), axis = -1)
    # Create ONE trace for all dots
    fig.add_trace(go.Scatter(
        x=all_x, 
        y=all_y,
        mode='markers+text',
        text=all_labels,
        customdata = kurts_skews,
        textposition="top center",
        marker=dict(
            size=15,
            cmin=-3,
            cmax = 3,
            color=all_volumes,       
            colorscale='Viridis', 
            showscale=True,
            colorbar=dict(title="Volume Surge (Z-Score)", tickvals=[-3, 0, 3],
                          ticktext=["-3", "0", "3"],
                          tickmode="array"),
            line=dict(width=1, color='white')
        ),
        hovertemplate=(
            "<b>%{text}</b><br>" +
            "Quadrant: %{x:.2f} | %{y:.2f}<br>" +
            "Volume: %{marker.color:.2f}<br>" +
            "---------------------<br>" +
            "Skew (x period): %{customdata[0]:.2f}<br>" +
            "Kurt (x period): %{customdata[1]:.2f}" + 
            "<extra></extra>" # Removes the secondary box
        )
    ))

    fig.update_layout(
        template="plotly_dark",
        width = 800,
        height = 800,
        xaxis=dict(
            title=f"{indics[0]}",
            gridcolor='rgba(255,255,255,0.1)', # Subtle grid lines
        ),
        yaxis=dict(
            title=f"{indics[1]}",
            gridcolor='rgba(255,255,255,0.1)',
        ),
        showlegend = False,
        shapes=[
            dict(type="line", x0=0, x1=0, y0=-chart_range[1], y1=chart_range[1], line=dict(color="Gray", dash="dash")),
            dict(type="line", x0=-chart_range[0], x1=chart_range[0], y0=0, y1=0, line=dict(color="Gray", dash="dash"))
        ],
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=list([
                    dict(
                        args=[{"mode": "markers+text"}], #
                        label="On",
                        method="restyle" 
                    ),
                    dict(
                        args=[{"mode": "markers"}],
                        label="Off",
                        method="restyle"
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                xanchor="left",
                yanchor="top"
            ),
        ]    
    )
    df = pd.DataFrame(scanner_data)
    if not df.empty:
        df = df.sort_values(by="Signal Strength", ascending=False)

    return fig, df
