import yfinance as yf
import pandas as pd
import numpy as np

ASSETS = {
    "GC=F" : {"name": "Gold", "code": "GOLD", "group": "Precious Metals"},
    "SI=F" : {"name": "Silver", "code": "SILVER", "group": "Precious Metals"},
    "^GSPC" : {"name": "S&P 500", "code": "SP500", "group": "Equities (S&P 500)"},
    "BTC-USD" : {"name": "Bitcoin", "code": "BTC", "group": "Crypto"},
    "ETH-USD" : {"name": "Ethereum", "code": "ETH", "group": "Crypto"}
}
START_DATE="2018-01-01"

print("Loading data...")

raw_frames=[]

for ticker, meta in ASSETS.items():
    df=yf.download(ticker, start=START_DATE, interval="1d", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df = df.reset_index()


    df["Ticker"] = ticker
    df["Asset_Code"] = meta["code"]
    df["Asset_Name"] = meta["name"]
    df["Asset_Group"] = meta["group"]

    df = df[["Date", "Asset_Code", "Asset_Name", "Asset_Group", "Open", "High", "Low", "Close", "Volume"]]
    raw_frames.append(df)

fact_prices = pd.concat(raw_frames, ignore_index=True)
fact_prices["Date"] = pd.to_datetime(fact_prices["Date"]).dt.tz_localize(None)


pivot_close = fact_prices.pivot(index="Date", columns="Asset_Code", values="Close").sort_index()

expected_codes = ["GOLD", "SILVER", "SP500", "BTC", "ETH"]
missing_cols = [c for c in expected_codes if c not in pivot_close.columns]
if missing_cols:
    raise ValueError(f"Missing columns: {missing_cols}")

is_trading_day = pivot_close["SP500"].notna().astype(int)

pivot_aligned = pivot_close.ffill().dropna()

returns_df = pivot_aligned.pct_change().dropna()

macro_groups = pd.DataFrame(index=returns_df.index)
macro_groups["Trading_Day_Flag"] = is_trading_day.loc[returns_df.index]


macro_groups["Metals_Return"] = (returns_df["GOLD"] + returns_df["SILVER"]) / 2
macro_groups["SP500_Return"] = returns_df["SP500"]
macro_groups["Crypto_Return"] = (returns_df["BTC"] + returns_df["ETH"]) / 2

macro_groups["Metals_Index_100"] = 100 * (1 + macro_groups["Metals_Return"]).cumprod()
macro_groups["SP500_Index_100"] = 100 * (1 + macro_groups["SP500_Return"]).cumprod()
macro_groups["Crypto_Index_100"] = 100 * (1 + macro_groups["Crypto_Return"]).cumprod()

macro_groups["Corr_30D_Metals_SP500"] = macro_groups["Metals_Return"].rolling(30).corr(macro_groups["SP500_Return"])
macro_groups["Corr_30D_Crypto_SP500"] = macro_groups["Crypto_Return"].rolling(30).corr(macro_groups["SP500_Return"])
macro_groups["Corr_30D_Crypto_Metals"] = macro_groups["Crypto_Return"].rolling(30).corr(macro_groups["Metals_Return"])

fact_prices.to_csv("fact_daily_asset_prices.csv", index=False, encoding="utf-8")
macro_groups.reset_index().to_csv("fact_macro_group_comparison.csv", index=False, encoding="utf-8")

print(f"done {len(fact_prices)} rows in fact_daily_asset_prices.csv")
print(f"Comparison table of ({len(macro_groups)} days) saved in fact_macro_group_comparison.csv")    

