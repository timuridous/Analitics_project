import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

print("Loading assets prices ...")
df_prices = pd.read_csv("fact_daily_asset_prices.csv")
df_prices.columns = [col.lower() for col in df_prices.columns]  
df_prices["date"] = pd.to_datetime(df_prices["date"]).dt.date
df_prices.to_sql("fact_daily_asset_prices", engine, if_exists="append", index=False)

print("Loading macrocomparison...")
df_macro = pd.read_csv("fact_macro_group_comparison.csv")
df_macro.columns = [col.lower() for col in df_macro.columns]  
df_macro["date"] = pd.to_datetime(df_macro["date"]).dt.date
df_macro.to_sql("fact_macro_group_comparison", engine, if_exists="append", index=False)

print("Done!")