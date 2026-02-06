from helper import get_dma, get_smoothed, get_volume, get_polygon_data
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
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

def get_fig(tickers, day_delay):
    fig = go.Figure()
    all_x = []
    all_y = []
    all_volumes = []
    all_labels = []
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
        all_x.append(x_val := get_dma(data[["Close"]]).iloc[-1 * (day_delay + 1)])
        all_y.append(y_val := get_smoothed(data[["Close"]])[-1 * (day_delay + 1)])
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

        # Geometric distance
        strength = (x_val**2 + y_val**2)**0.5
        scanner_data.append({
            "Ticker": ticker,
            "Quadrant": quadrant,
            "Signal Strength": float(strength), # ensure float for sorting
            "Valuation (X)": float(x_val),
            "Momentum (Y)": float(y_val),
            "Volume (Z)": float(vol_val)
        })

    # Create ONE trace for all dots
    fig.add_trace(go.Scatter(
        x=all_x, 
        y=all_y,
        mode='markers+text',
        text=all_labels,
        textposition="top center",
        marker=dict(
            size=15,
            cmin=-3,
            cmax = 3,
            color=all_volumes,       # Now Plotly sees the full range
            colorscale='Viridis', 
            showscale=True,
            colorbar=dict(title="Volume Surge (Z-Score)", tickvals=[-3, 0, 3],
                          ticktext=["-3", "0", "3"],
                          tickmode="array"),
            line=dict(width=1, color='white')
        ),
    ))

    fig.update_layout(
        template="plotly_dark",
        width = 800,
        height = 800,
        xaxis=dict(
            title="Distance from 30DMA (Z-Score)",
            gridcolor='rgba(255,255,255,0.1)', # Subtle grid lines
            zerolinecolor='white',
            zerolinewidth=1
        ),
        yaxis=dict(
            title="Kalman Innovation (5 Day Sum)",
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='white',
            zerolinewidth=1
        ),
        showlegend = False,
        shapes=[
            dict(type="line", x0=0, x1=0, y0=-3, y1=3, line=dict(color="Gray", dash="dash")),
            dict(type="line", x0=-3, x1=3, y0=0, y1=0, line=dict(color="Gray", dash="dash"))
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
                x=0.05, 
                xanchor="left",
                y=1.1, 
                yanchor="top"
            ),
        ]    
    )
    df = pd.DataFrame(scanner_data)
    if not df.empty:
        df = df.sort_values(by="Signal Strength", ascending=False)

    return fig, df
