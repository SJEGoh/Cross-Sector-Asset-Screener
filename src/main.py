import streamlit as st
import pandas as pd
import yfinance as yf
from helper import get_dma, get_smoothed, get_tickers, get_volume

import plotly.graph_objects as go
import pandas as pd

tickers = get_tickers()

fig = go.Figure()
all_x = []
all_y = []
all_volumes = []
all_labels = []

for ticker in tickers:
    data = yf.Ticker(ticker).history(period="2y")[["Close", "Volume"]]
    if data.empty:
        continue
        
    all_x.append(get_dma(data[["Close"]]).iloc[-1])
    all_y.append(get_smoothed(data[["Close"]]))
    all_volumes.append(get_volume(data).iloc[-1]) # This should be a Z-score
    all_labels.append(ticker)

# Create ONE trace for all dots
fig.add_trace(go.Scatter(
    x=all_x, 
    y=all_y,
    mode='markers',
    text=all_labels,
    textposition="top center",
    marker=dict(
        size=15,
        color=all_volumes,       # Now Plotly sees the full range
        colorscale='Viridis', 
        showscale=True,
        colorbar=dict(title="Volume Surge (Z-Score)"),
        line=dict(width=1, color='white')
    ),
))

fig.update_layout(
    template="plotly_dark",
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
    showlegend = False
)

fig.show()
