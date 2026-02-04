import pandas as pd

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
}

def to_dataframe(universe: dict):
    """
    Convert UNIVERSE dict -> pandas DataFrame for easy filtering/grouping.
    """
    rows = []
    for tkr, meta in universe.items():
        row = {"ticker": tkr}
        row.update(meta)
        rows.append(row)
    df = pd.DataFrame(rows)
    cols = ["ticker", "asset_class", "group", "region", "sector", "name"]
    return df[cols].sort_values(["asset_class", "group", "region", "sector", "ticker"], na_position="last").reset_index(drop=True)


def get_tickers():
    """
    Return a sorted list of tickers for yfinance download.
    """
    return sorted(UNIVERSE.keys())

def get_data():
    df_universe = to_dataframe(UNIVERSE)
    tickers = get_tickers(UNIVERSE)
    print(df_universe.head())
    print(len(tickers), tickers[:20])

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
        while breaker < 5:
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
    while breaker < 5:
        if curr["Close"] < min_price:
            min_price = curr["Close"]
            breaker = 0
        if curr["lowess_gradient"] < 0:
            breaker += 1
        loc -= 1
        curr = data.iloc[loc]
        days += 1
    return min_price, days



if __name__ == "__main__":
    get_data()
