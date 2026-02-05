import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf

UNIVERSE = {
    # =========================
    # EQUITIES — Broad beta / geography
    # =========================
    "SPY":  {"asset_class": "equity", "group": "broad", "region": "US", "sector": None, "name": "S&P 500"},
    "IVV":  {"asset_class": "equity", "group": "broad", "region": "US", "sector": None, "name": "S&P 500"},
    "VOO":  {"asset_class": "equity", "group": "broad", "region": "US", "sector": None, "name": "S&P 500"},
    "QQQ":  {"asset_class": "equity", "group": "broad", "region": "US", "sector": None, "name": "Nasdaq 100"},
    "IWM":  {"asset_class": "equity", "group": "broad", "region": "US", "sector": None, "name": "Russell 2000 (Small Cap)"},
    "DIA":  {"asset_class": "equity", "group": "broad", "region": "US", "sector": None, "name": "Dow Jones Industrial Average"},
    "MDY":  {"asset_class": "equity", "group": "broad", "region": "US", "sector": None, "name": "US Mid Cap"},
    "VTI":  {"asset_class": "equity", "group": "broad", "region": "US", "sector": None, "name": "US Total Market"},
    "VT":   {"asset_class": "equity", "group": "broad", "region": "Global", "sector": None, "name": "Global Total Market"},
    "ACWI": {"asset_class": "equity", "group": "broad", "region": "Global", "sector": None, "name": "MSCI ACWI"},
    "VXUS": {"asset_class": "equity", "group": "broad", "region": "Global ex-US", "sector": None, "name": "Total International ex-US"},
    "EFA":  {"asset_class": "equity", "group": "broad", "region": "Developed ex-US", "sector": None, "name": "MSCI EAFE"},
    "EEM":  {"asset_class": "equity", "group": "broad", "region": "Emerging", "sector": None, "name": "MSCI EM"},
    "VEA":  {"asset_class": "equity", "group": "broad", "region": "Developed ex-US", "sector": None, "name": "Developed ex-US (broad)"},
    "VWO":  {"asset_class": "equity", "group": "broad", "region": "Emerging", "sector": None, "name": "Emerging Markets (broad)"},

    # =========================
    # EQUITIES — US sectors (Select Sector SPDRs)
    # =========================
    "XLC":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Communication Services", "name": "Communication Services Select Sector"},
    "XLY":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Consumer Discretionary", "name": "Consumer Discretionary Select Sector"},
    "XLP":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Consumer Staples", "name": "Consumer Staples Select Sector"},
    "XLE":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Energy", "name": "Energy Select Sector"},
    "XLF":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Financials", "name": "Financial Select Sector"},
    "XLV":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Health Care", "name": "Health Care Select Sector"},
    "XLI":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Industrials", "name": "Industrial Select Sector"},
    "XLK":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Information Technology", "name": "Technology Select Sector"},
    "XLB":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Materials", "name": "Materials Select Sector"},
    "XLRE": {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Real Estate", "name": "Real Estate Select Sector"},
    "XLU":  {"asset_class": "equity", "group": "sector", "region": "US", "sector": "Utilities", "name": "Utilities Select Sector"},
    # =========================
    # EQUITIES — Vanguard sector equivalents (optional 2nd family)
    # =========================
    "VCR": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Consumer Discretionary", "name": "Vanguard Consumer Discretionary"},
    "VDC": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Consumer Staples", "name": "Vanguard Consumer Staples"},
    "VDE": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Energy", "name": "Vanguard Energy"},
    "VFH": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Financials", "name": "Vanguard Financials"},
    "VHT": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Health Care", "name": "Vanguard Health Care"},
    "VIS": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Industrials", "name": "Vanguard Industrials"},
    "VGT": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Information Technology", "name": "Vanguard Information Technology"},
    "VAW": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Materials", "name": "Vanguard Materials"},
    "VNQ": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Real Estate", "name": "Vanguard Real Estate (REITs)"},
    "VOX": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Communication Services", "name": "Vanguard Communication Services"},
    "VPU": {"asset_class": "equity", "group": "sector_alt", "region": "US", "sector": "Utilities", "name": "Vanguard Utilities"},

    # =========================
    # EQUITIES — factors / styles (leadership vs laggards)
    # =========================
    "MTUM": {"asset_class": "equity", "group": "factor", "region": "US", "sector": None, "name": "Momentum"},
    "QUAL": {"asset_class": "equity", "group": "factor", "region": "US", "sector": None, "name": "Quality"},
    "USMV": {"asset_class": "equity", "group": "factor", "region": "US", "sector": None, "name": "Min Volatility"},
    "VLUE": {"asset_class": "equity", "group": "factor", "region": "US", "sector": None, "name": "Value"},
    "VTV":  {"asset_class": "equity", "group": "style",  "region": "US", "sector": None, "name": "Value (broad)"},
    "VUG":  {"asset_class": "equity", "group": "style",  "region": "US", "sector": None, "name": "Growth (broad)"},
    "IWD":  {"asset_class": "equity", "group": "style",  "region": "US", "sector": None, "name": "Value (Russell 1000)"},
    "IWF":  {"asset_class": "equity", "group": "style",  "region": "US", "sector": None, "name": "Growth (Russell 1000)"},
    "RSP":  {"asset_class": "equity", "group": "style",  "region": "US", "sector": None, "name": "S&P 500 Equal Weight"},
    "VYM":  {"asset_class": "equity", "group": "style",  "region": "US", "sector": None, "name": "High Dividend"},
    "SCHD": {"asset_class": "equity", "group": "style",  "region": "US", "sector": None, "name": "Dividend (Quality tilt)"},
    # =========================
    # EQUITIES — country / single-market ETFs
    # =========================
    # Developed
    "EWJ": {"asset_class": "equity", "group": "country", "region": "Japan", "sector": None, "name": "Japan"},
    "EWG": {"asset_class": "equity", "group": "country", "region": "Germany", "sector": None, "name": "Germany"},
    "EWU": {"asset_class": "equity", "group": "country", "region": "United Kingdom", "sector": None, "name": "United Kingdom"},
    "EWQ": {"asset_class": "equity", "group": "country", "region": "France", "sector": None, "name": "France"},
    "EWI": {"asset_class": "equity", "group": "country", "region": "Italy", "sector": None, "name": "Italy"},
    "EWP": {"asset_class": "equity", "group": "country", "region": "Spain", "sector": None, "name": "Spain"},
    "EWL": {"asset_class": "equity", "group": "country", "region": "Switzerland", "sector": None, "name": "Switzerland"},
    "EWN": {"asset_class": "equity", "group": "country", "region": "Netherlands", "sector": None, "name": "Netherlands"},
    "EWA": {"asset_class": "equity", "group": "country", "region": "Australia", "sector": None, "name": "Australia"},
    "EWC": {"asset_class": "equity", "group": "country", "region": "Canada", "sector": None, "name": "Canada"},
    "EWD": {"asset_class": "equity", "group": "country", "region": "Sweden", "sector": None, "name": "Sweden"},
    "EWS": {"asset_class": "equity", "group": "country", "region": "Singapore", "sector": None, "name": "Singapore"},
    "EWH": {"asset_class": "equity", "group": "country", "region": "Hong Kong", "sector": None, "name": "Hong Kong"},
    # Emerging / thematic
    "FXI":  {"asset_class": "equity", "group": "country", "region": "China", "sector": None, "name": "China Large Cap"},
    "MCHI": {"asset_class": "equity", "group": "country", "region": "China", "sector": None, "name": "China Broad"},
    "KWEB": {"asset_class": "equity", "group": "theme",   "region": "China", "sector": "Internet", "name": "China Internet"},
    "INDA": {"asset_class": "equity", "group": "country", "region": "India", "sector": None, "name": "India"},
    "EWZ":  {"asset_class": "equity", "group": "country", "region": "Brazil", "sector": None, "name": "Brazil"},
    "EWW":  {"asset_class": "equity", "group": "country", "region": "Mexico", "sector": None, "name": "Mexico"},
    "EWT":  {"asset_class": "equity", "group": "country", "region": "Taiwan", "sector": None, "name": "Taiwan"},
    "EWY":  {"asset_class": "equity", "group": "country", "region": "South Korea", "sector": None, "name": "South Korea"},
    "EZA":  {"asset_class": "equity", "group": "country", "region": "South Africa", "sector": None, "name": "South Africa"},
    "TUR":  {"asset_class": "equity", "group": "country", "region": "Turkey", "sector": None, "name": "Turkey"},
    "GREK": {"asset_class": "equity", "group": "country", "region": "Greece", "sector": None, "name": "Greece"},
    "VNM":  {"asset_class": "equity", "group": "country", "region": "Vietnam", "sector": None, "name": "Vietnam"},
    "RSX":  {"asset_class": "equity", "group": "country", "region": "Russia", "sector": None, "name": "Russia (check tradability/liquidity)"},
    # =========================
    # BONDS — core + curve + credit
    # =========================
    "BND":  {"asset_class": "rates", "group": "broad", "region": "US", "sector": None, "name": "US Total Bond Market"},
    "AGG":  {"asset_class": "rates", "group": "broad", "region": "US", "sector": None, "name": "US Aggregate Bonds"},
    "BIL":  {"asset_class": "rates", "group": "curve", "region": "US", "sector": None, "name": "T-Bills (1-3m)"},
    "SGOV": {"asset_class": "rates", "group": "curve", "region": "US", "sector": None, "name": "Treasuries (0-3m)"},
    "SHY":  {"asset_class": "rates", "group": "curve", "region": "US", "sector": None, "name": "Treasuries (1-3y)"},
    "IEF":  {"asset_class": "rates", "group": "curve", "region": "US", "sector": None, "name": "Treasuries (7-10y)"},
    "TLT":  {"asset_class": "rates", "group": "curve", "region": "US", "sector": None, "name": "Treasuries (20+y)"},
    "TIP":  {"asset_class": "rates", "group": "inflation", "region": "US", "sector": None, "name": "TIPS"},
    "LQD":  {"asset_class": "credit", "group": "spread", "region": "US", "sector": None, "name": "IG Corporates"},
    "HYG":  {"asset_class": "credit", "group": "spread", "region": "US", "sector": None, "name": "High Yield"},
    "JNK":  {"asset_class": "credit", "group": "spread", "region": "US", "sector": None, "name": "High Yield (alt)"},
    "EMB":  {"asset_class": "credit", "group": "em", "region": "EM", "sector": None, "name": "EM USD Sovereign Debt"},
    "BWX":  {"asset_class": "rates", "group": "broad", "region": "Developed ex-US", "sector": None, "name": "Intl Treasuries (developed)"},
    "IAGG": {"asset_class": "rates", "group": "broad", "region": "Global", "sector": None, "name": "Global Aggregate Bonds"},

    # =========================
    # COMMODITIES — baskets + single-commodity ETFs
    # =========================
    "DBC":  {"asset_class": "commodity", "group": "broad", "region": "Global", "sector": None, "name": "Broad Commodities (futures basket)"},
    "PDBC": {"asset_class": "commodity", "group": "broad", "region": "Global", "sector": None, "name": "Broad Commodities (rules-based)"},
    "GSG":  {"asset_class": "commodity", "group": "broad", "region": "Global", "sector": None, "name": "Broad Commodities (alt)"},
    "GLD":  {"asset_class": "commodity", "group": "metals", "region": "Global", "sector": "Gold", "name": "Gold"},
    "IAU":  {"asset_class": "commodity", "group": "metals", "region": "Global", "sector": "Gold", "name": "Gold (alt)"},
    "SLV":  {"asset_class": "commodity", "group": "metals", "region": "Global", "sector": "Silver", "name": "Silver"},
    "USO":  {"asset_class": "commodity", "group": "energy", "region": "Global", "sector": "WTI", "name": "WTI crude (ETF proxy)"},
    "BNO":  {"asset_class": "commodity", "group": "energy", "region": "Global", "sector": "Brent", "name": "Brent crude (ETF proxy)"},
    "UNG":  {"asset_class": "commodity", "group": "energy", "region": "Global", "sector": "Natural Gas", "name": "Natural Gas (ETF proxy)"},
    "CPER": {"asset_class": "commodity", "group": "metals", "region": "Global", "sector": "Copper", "name": "Copper (ETF proxy)"},
    "JJC":  {"asset_class": "commodity", "group": "metals", "region": "Global", "sector": "Copper", "name": "Copper (alt/older)"},
    "PPLT": {"asset_class": "commodity", "group": "metals", "region": "Global", "sector": "Platinum", "name": "Platinum"},
    "PALL": {"asset_class": "commodity", "group": "metals", "region": "Global", "sector": "Palladium", "name": "Palladium"},
    "DBA":  {"asset_class": "commodity", "group": "agri", "region": "Global", "sector": "Agriculture", "name": "Agriculture basket"},
    "CORN": {"asset_class": "commodity", "group": "agri", "region": "Global", "sector": "Corn", "name": "Corn"},
    "WEAT": {"asset_class": "commodity", "group": "agri", "region": "Global", "sector": "Wheat", "name": "Wheat"},
    "SOYB": {"asset_class": "commodity", "group": "agri", "region": "Global", "sector": "Soybeans", "name": "Soybeans"},
    "JO":   {"asset_class": "commodity", "group": "agri", "region": "Global", "sector": "Coffee", "name": "Coffee"},
    "SGG":  {"asset_class": "commodity", "group": "agri", "region": "Global", "sector": "Sugar", "name": "Sugar (availability varies)"},

    # =========================
    # COMMODITIES — futures tickers on Yahoo (pure price series)
    # =========================
    "CL=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "WTI", "name": "WTI Crude (futures)"},
    "BZ=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Brent", "name": "Brent Crude (futures)"},
    "NG=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Natural Gas", "name": "Natural Gas (futures)"},
    "GC=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Gold", "name": "Gold (futures)"},
    "SI=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Silver", "name": "Silver (futures)"},
    "HG=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Copper", "name": "Copper (futures)"},
    "ZC=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Corn", "name": "Corn (futures)"},
    "ZW=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Wheat", "name": "Wheat (futures)"},
    "ZS=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Soybeans", "name": "Soybeans (futures)"},
    "KC=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Coffee", "name": "Coffee (futures)"},
    "SB=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Sugar", "name": "Sugar (futures)"},
    "CT=F": {"asset_class": "commodity", "group": "futures", "region": "Global", "sector": "Cotton", "name": "Cotton (futures)"},

    # =========================
    # CRYPTO — spot (Yahoo format)
    # =========================
    "BTC-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Bitcoin"},
    "ETH-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Ethereum"},
    "SOL-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Solana"},
    "BNB-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "BNB"},
    "XRP-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "XRP"},
    "ADA-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Cardano"},
    "DOGE-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Dogecoin"},
    "AVAX-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Avalanche"},
    "LINK-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Chainlink"},
    "DOT-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Polkadot"},
    "MATIC-USD": {"asset_class": "crypto", "group": "spot", "region": "Global", "sector": None, "name": "Polygon (may vary by feed)"},
    "TOTAL-USD": {"asset_class": "crypto", "group": "macro", "region": "Global", "sector": None, "name": "Total crypto market cap (availability varies)"},
    # =========================
    # CRYPTO — ETFs (optional: tradfi flow lens)
    # =========================
    # Spot BTC ETFs
    "IBIT": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "iShares Bitcoin Trust"},
    "FBTC": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "Fidelity Wise Origin Bitcoin Fund"},
    "GBTC": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "Grayscale Bitcoin Trust"},
    "ARKB": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "ARK 21Shares Bitcoin ETF"},
    "BITB": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "Bitwise Bitcoin ETF"},
    "HODL": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "VanEck Bitcoin Trust"},
    "BRRR": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "Valkyrie/CoinShares Bitcoin ETF"},
    "BTCO": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "Invesco Galaxy Bitcoin ETF"},
    "EZBC": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "Franklin Bitcoin ETF"},
    "BTCW": {"asset_class": "crypto_etf", "group": "spot_btc_etf", "region": "US", "sector": None, "name": "WisdomTree Bitcoin ETF"},
    # Spot ETH ETFs
    "ETHA": {"asset_class": "crypto_etf", "group": "spot_eth_etf", "region": "US", "sector": None, "name": "iShares Ethereum Trust"},
    "FETH": {"asset_class": "crypto_etf", "group": "spot_eth_etf", "region": "US", "sector": None, "name": "Fidelity Ethereum Fund"},
    "QETH": {"asset_class": "crypto_etf", "group": "spot_eth_etf", "region": "US", "sector": None, "name": "Invesco Galaxy Ethereum ETF"},
    "EZET": {"asset_class": "crypto_etf", "group": "spot_eth_etf", "region": "US", "sector": None, "name": "Franklin Ethereum ETF"},
    "ETHW": {"asset_class": "crypto_etf", "group": "spot_eth_etf", "region": "US", "sector": None, "name": "Bitwise Ethereum ETF"},
    "ETHE": {"asset_class": "crypto_etf", "group": "spot_eth_etf", "region": "US", "sector": None, "name": "Grayscale Ethereum Trust"},
    "ETH":  {"asset_class": "crypto_etf", "group": "spot_eth_etf", "region": "US", "sector": None, "name": "Grayscale Ethereum Mini Trust"},
}

def get_dataframe():
    """
    Convert UNIVERSE dict -> pandas DataFrame for easy filtering/grouping.
    """
    rows = []
    for tkr, meta in UNIVERSE.items():
        row = {"ticker": tkr}
        row.update(meta)
        rows.append(row)
    df = pd.DataFrame(rows)
    cols = ["ticker", "asset_class", "group", "region", "sector", "name"]
    return df[cols].sort_values(["asset_class", "group", "region", "sector", "ticker"], na_position="last").reset_index(drop=True)

def get_filtered_universe(df):
    temp_df = df.copy()

    c1, c2, c3 = st.columns(3)

    with c1:
        region = st.multiselect("Choose Region", temp_df["region"].unique().tolist())
        if region:
            temp_df = temp_df[temp_df["region"].isin(region)]

        asset_class = st.multiselect("Choose Asset Class", temp_df["asset_class"].unique().tolist())
        if asset_class:
            temp_df = temp_df[temp_df["asset_class"].isin(asset_class)]

    with c2:
        group = st.multiselect("Choose Group", temp_df["group"].unique().tolist())
        if group:
            temp_df = temp_df[temp_df["group"].isin(group)]

        sector = st.multiselect("Choose Sector", temp_df["sector"].unique().tolist())
        if sector:
            temp_df = temp_df[temp_df["sector"].isin(sector)]

    with c3:
        name = st.multiselect("Select Name", temp_df["name"].unique().tolist())
        if name:
            temp_df = temp_df[temp_df["name"].isin(name)]

        ticker = st.multiselect("Select Tickers", temp_df["ticker"].unique().tolist())
        if ticker:
            temp_df = temp_df[temp_df["ticker"].isin(ticker)]

    return temp_df

def get_tickers(universe):
    """
    Return a sorted list of tickers for yfinance download.
    """
    return sorted(universe["ticker"])

def get_data():
    df_universe = get_dataframe()
    tickers = get_tickers(UNIVERSE)
    print(df_universe.head())
    print(len(tickers), tickers[:20])

# For dashboard
def get_dma(data):
    data["100dma"] = data[["Close"]].rolling("30D").mean()
    data["100dms"] = data[["Close"]].rolling("90D").std()

    data["z"] = (data["Close"] - data["100dma"])/data["100dms"]
    return data["z"]


def get_smoothed(data):
    data = data.dropna().tail(75) 
    
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
        # Prediction
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
    
    # 1. Rolling 5-day Sum of Innovations
    rolling_sums = innovations_series.rolling(window=5).sum()
    
    rolling_std = rolling_sums.rolling(window=63).std()

    z_scores = rolling_sums / rolling_std.replace(0, 1.0)

    return z_scores.fillna(0).tail(10).tolist()

def get_volume(data):
    data['vol_ma'] = data['Volume'].rolling(20).mean()
    data['vol_std'] = data['Volume'].rolling(20).std()
    data['vol_z'] = (data['Volume'] - data['vol_ma']) / data['vol_std']

    return pd.Series(data["vol_z"])

def get_extreme(data):
    count = 0
    for val in data.tail(5)["lowess_gradient"]:
        
        if val > 0:
            count += 1
            continue
        count -= 1
    loc = -1
    curr = data.iloc[-1]
    breaker = 0
    days = 0
    if count < 0:
        max_price = 0
        while breaker < 5 and loc < data.shape[0]-1:
            if curr["Close"] > max_price:
                max_price = curr["Close"]
                breaker = 0
            if curr["lowess_gradient"] > 0:
                breaker += 1
            loc -= 1
            curr = data.iloc[loc]
            days += 1

        return max_price, days
    min_price = float("inf")
    while breaker < 5 and loc < data.shape[0]-1:
        if curr["Close"] < min_price:
            min_price = curr["Close"]
            breaker = 0
        if curr["lowess_gradient"] < 0:
            breaker += 1
        loc -= 1
        curr = data.iloc[loc]
        days += 1
    return min_price, days

from datetime import date, timedelta
from polygon import RESTClient
import os

client = RESTClient(os.getenv("API"))
def get_polygon_data(ticker, days_back=730):
    """
    Fetches historical data from Polygon and returns a DataFrame 
    structured EXACTLY like yfinance (Date Index, Close, Volume).
    """
    # 1. Define Date Range
    to_date = date.today()
    from_date = to_date - timedelta(days=days_back)

    try:
        # 2. Fetch Aggregates (Bars)
        # 1 = multiplier, "day" = timespan
        aggs = client.get_aggs(
            ticker=ticker, 
            multiplier=1, 
            timespan="day", 
            from_=from_date, 
            to=to_date
        )
        
        # 3. Handle Empty Responses
        if not aggs:
            return pd.DataFrame() # Return empty if no data

        # 4. Convert to DataFrame
        # Polygon returns a list of objects, we need to extract the values
        data = [
            {
                "Date": pd.to_datetime(a.timestamp, unit="ms"),
                "Close": a.close,
                "Volume": a.volume
            } 
            for a in aggs
        ]
        
        df = pd.DataFrame(data)
        
        # 5. Format to match YFinance structure
        df.set_index("Date", inplace=True)
        
        # Ensure columns are floats (Polygon uses precise Decimals sometimes)
        df["Close"] = df["Close"].astype(float)
        df["Volume"] = df["Volume"].astype(float)
        
        return df[["Close", "Volume"]]

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    get_data()
