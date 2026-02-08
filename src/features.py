import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
import streamlit as st

'''
For any features use format
def feature(data, period)
only need to return up to 5 days
max days is 2 * period
'''

# First order 
def get_dma(data, period = 30):
    time = str(period) + "D"
    time_sd = str(2 * period) + "D"
    data["100dma"] = data[["Close"]].rolling(time).mean()
    data["100dms"] = data[["Close"]].rolling(time_sd).std()

    data["z"] = (data["Close"] - data["100dma"])/data["100dms"]
    return data["z"]

def get_dma_second(data, period=20):

    ma = data["Close"].rolling(period).mean()
    dma_pct = (data["Close"] - ma) / ma
    
    dma_velocity = dma_pct.diff()
    dma_accel = dma_velocity.diff()
    

    sigma = dma_accel.rolling(period * 2).std()
    
    scaled_accel = dma_accel / sigma
    
    return scaled_accel


def get_rolling_retrac(data, period=14, raw=False):
    # 1. Prepare Data
    prices = data["Close"].to_numpy()
    
    # 2. Create Rolling Windows
    windows = sliding_window_view(prices, window_shape=period)
    
    # 3. Find Indices of Max and Min
    max_idx_rel = np.argmax(windows, axis=1)
    min_idx_rel = np.argmin(windows, axis=1)
    
    # 4. Get Values
    row_indices = np.arange(windows.shape[0])
    roll_max = windows[row_indices, max_idx_rel]
    roll_min = windows[row_indices, min_idx_rel]
    curr_price = windows[:, -1]
    

    price_range = roll_max - roll_min
    
    with np.errstate(divide='ignore', invalid='ignore'):
        raw_retracement = (curr_price - roll_min) / price_range
        raw_retracement = np.nan_to_num(raw_retracement, nan=0.0)

    if raw:
        pad = np.full(period - 1, np.nan)
        full_result = np.concatenate([pad, raw_retracement])
        return pd.Series(full_result, index=data.index)

    final_values = np.where(
        max_idx_rel < min_idx_rel,
        raw_retracement,      
        -raw_retracement      
    )
    
    pad = np.full(period - 1, np.nan)
    full_result = np.concatenate([pad, final_values])
    
    return pd.Series(full_result, index=data.index)

def kalman_first(data, period = 10):
    data = data.dropna().tail(period * 2) 
    
    data["pct_change"] = data["Close"].pct_change()
    data = data.dropna()
    
    q = 0.05
    r = 1.0

    if data.empty:
        return [0] * 10
        
    x = np.array([[data["pct_change"].iloc[0]], [0.0]])
    P = np.eye(2)
    F = np.array([[1, 1.0],
                  [0, 1]])
    H = np.array([[1, 0]])
    Q = np.eye(2) * q
    R = np.array([[r]])
    
    smoothed_innovations = []
    
    for z in data["pct_change"]:
        x = F @ x
        P = F @ P @ F.T + Q
        
        # Update
        y = z - (H @ x) # Innovation
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        x = x + K @ y
        P = (np.eye(2) - K @ H) @ P
    
        smoothed_innovations.append(x[0][0])
    
    innovations_series = pd.Series(smoothed_innovations)

    z_scores = (innovations_series - innovations_series.rolling(period).mean()) / innovations_series.rolling(period).std()

    return z_scores.fillna(0).tail(10)

# kalman innovation
def get_smoothed(data, period = 10):
    data = data.dropna().tail(period * 2) 
    
    data["pct_change"] = data["Close"].pct_change()
    data = data.dropna()
    
    q = 0.05
    r = 1.0

    if data.empty:
        return [0] * 10
        
    x = np.array([[data["pct_change"].iloc[0]], [0.0]])
    P = np.eye(2)
    F = np.array([[1, 1.0],
                  [0, 1]])
    H = np.array([[1, 0]])
    Q = np.eye(2) * q
    R = np.array([[r]])
    
    smoothed_innovations = []
    
    for z in data["pct_change"]:
        x = F @ x
        P = F @ P @ F.T + Q
        
        # Update
        y = z - (H @ x) # Innovation
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        x = x + K @ y
        P = (np.eye(2) - K @ H) @ P
    
        smoothed_innovations.append(y[0][0])
    
    innovations_series = pd.Series(smoothed_innovations)

    z_scores = (innovations_series - innovations_series.rolling(period).mean()) / innovations_series.rolling(period).std()

    return z_scores.fillna(0).tail(10)


# Second order 
def kalman_second(data, period = 10):
    data = data.dropna().tail(period * 2) 
    
    data["pct_change"] = data["Close"].pct_change()
    data = data.dropna()
    
    q = 0.05
    r = 1.0

    if data.empty:
        return [0] * 10
        
    x = np.array([[data["pct_change"].iloc[0]], [0.0]])
    P = np.eye(2)
    F = np.array([[1, 1.0],
                  [0, 1]])
    H = np.array([[1, 0]])
    Q = np.eye(2) * q
    R = np.array([[r]])
    
    smoothed_innovations = []
    
    for z in data["pct_change"]:
        x = F @ x
        P = F @ P @ F.T + Q
        
        # Update
        y = z - (H @ x) # Innovation
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        x = x + K @ y
        P = (np.eye(2) - K @ H) @ P
    
        smoothed_innovations.append(x[1][0])
    
    innovations_series = pd.Series(smoothed_innovations)

    z_scores = (innovations_series - innovations_series.rolling(period).mean()) / innovations_series.rolling(period).std()

    return z_scores.fillna(0).tail(10)



def perc_retrac_second(data, period):
    # 1. Get the RAW (Unsigned) Position (0.0 to 1.0)
    # We do NOT want the trend logic interfering with the derivative
    raw_position = get_rolling_retrac(data, period, raw=True)
    
    # 2. Calculate "Velocity" (Change in Position)
    velocity = raw_position.diff()
    
    # 3. Calculate "Acceleration" (Change in Velocity)
    acceleration = velocity.diff()
    
    # 4. Smooth it (Sum/Mean) to create the "Net Force"
    # This removes the day-to-day noise
    return acceleration.rolling(window=5).mean()


def get_lag_and_corr(data, benchmark, period=20, max_lag=5):
    s_vals = data["Close"] if isinstance(data, pd.DataFrame) else data
    b_vals = benchmark["Close"] if isinstance(benchmark, pd.DataFrame) else benchmark

    df = pd.DataFrame({
        "stock": s_vals.pct_change(),
        "bench": b_vals.pct_change()
    }).dropna()

    list_lags = []
    list_corrs = []
    dates = []
    lags = list(range(-max_lag, max_lag + 1))

    # 2. Loop with Error Silencing
    for t in range(period, len(df)):
        window = df.iloc[t-period : t]
        
        # Check if window is valid (has variance)
        if window['stock'].std() == 0 or window['bench'].std() == 0:
            # If flat line, correlation is 0 (or undefined)
            list_lags.append(0)
            list_corrs.append(0.0)
            dates.append(df.index[t])
            continue

        window_corrs = []
        for lag in lags:
            series_stock = window['stock']
            series_bench = window['bench'].shift(lag)
            
            # SILENCE THE WARNINGS
            with np.errstate(all='ignore'):
                val = series_stock.corr(series_bench)
            
            window_corrs.append(val if not np.isnan(val) else 0.0)

        # 3. Extract Best
        best_idx = np.argmax(window_corrs)
        
        best_lag_day = lags[best_idx]          # Integer (e.g. -2)
        best_corr_score = window_corrs[best_idx] # Float (e.g. 0.85)

        list_lags.append(best_lag_day)
        list_corrs.append(best_corr_score)
        dates.append(df.index[t])

    return pd.Series(list_lags, index=dates), pd.Series(list_corrs, index=dates)

# --- WRAPPERS (Debug Mode) ---

def get_lag_days(data, benchmark, period=20):
    lags, corrs = get_lag_and_corr(data, benchmark, period)
    # Debug: Print one value to prove it's an Integer
    return lags

def get_lag_corr(data, benchmark, period=20):
    lags, corrs = get_lag_and_corr(data, benchmark, period)
    # Debug: Print one value to prove it's a Float
    return corrs

def get_indic(indic):
    # First order
    if indic == "DMA":
        return get_dma
    if indic == "First Order Kalman":
        return kalman_first
    if indic == "Kalman Innovation":
        return get_smoothed
    if indic == "Percentage Retracement":
        return get_rolling_retrac
    if indic == "Lag/Lead Days":
        return get_lag_days

    # Second order
    if indic == "Second Order Kalman":
        return kalman_second
    if indic == "Second Order Percentage Retracement":
        return perc_retrac_second
    if indic == "Second Order DMA":
        return get_dma_second
    if indic == "Rolling Alpha":
        return get_rolling_alpha
    if indic == "Lag/Lead Corr":
        return get_lag_corr
