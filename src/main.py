import yfinance as yf
from helper import get_dma, get_smoothed, get_volume
import plotly.graph_objects as go
import time
import random
# Ok just make this into a giant function. Inputs: (day, universe, )
def get_fig(tickers, day_delay):
    fig = go.Figure()
    all_x = []
    all_y = []
    all_volumes = []
    all_labels = []

    for ticker in tickers:
        data = yf.Ticker(ticker).history(period="2y")[["Close", "Volume"]]
        if data.empty or data.shape[0] < 100:
            continue
        
        all_x.append(get_dma(data[["Close"]]).iloc[-1 * (day_delay + 1)])
        all_y.append(get_smoothed(data[["Close"]])[-1 * (day_delay + 1)])
        all_volumes.append(get_volume(data).iloc[-1 * (day_delay + 1)]) 
        all_labels.append(ticker)
        time.sleep(random.uniform(0.05, 0.1))
    # Create ONE trace for all dots
    fig.add_trace(go.Scatter(
        x=all_x, 
        y=all_y,
        mode='markers+text',
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

    return fig
