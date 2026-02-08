import numpy as np
import pandas as pd

def get_dma(data, period = 30):
    time = str(period) + "D"
    time_sd = str(2 * period) + "D"
    data["100dma"] = data[["Close"]].rolling(time).mean()
    data["100dms"] = data[["Close"]].rolling(time_sd).std()

    data["z"] = (data["Close"] - data["100dma"])/data["100dms"]
    return data["z"]


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
        
        # We collect the innovation 'y', as per your logic
        smoothed_innovations.append(y[0][0])
    
    # Convert to Series for vectorized rolling math
    innovations_series = pd.Series(smoothed_innovations)

    z_scores = (innovations_series - innovations_series.rolling(period).mean()) / innovations_series.rolling(period).std()

    return z_scores.fillna(0).tail(10).tolist()

def get_indic(indic):
    if indic == "DMA":
        return get_dma
    if indic == "Kalman Innovation":
        return get_smoothed
