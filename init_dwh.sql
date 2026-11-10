CREATE TABLE dim_assets(
    asset_code VARCHAR(10) PRIMARY KEY, 
    asset_name VARCHAR(50) NOT NULL,
    asset_group VARCHAR(50) NOT NULL
);

INSERT INTO dim_assets(asset_code, asset_name, asset_group) VALUES
('GOLD', 'Gold', 'Precious Metals'), 
('SILVER', 'Silver', 'Precious Metals'),
('SP500', 'S&P 500', 'Equities (S&P 500)'),
('BTC', 'Bitcoin', 'Crypto'),
('ETH', 'Ethereum', 'Crypto');

CREATE TABLE fact_daily_asset_prices(
    date DATE NOT NULL,
    asset_code VARCHAR(10) NOT NULL REFERENCES dim_assets(asset_code),
    asset_name VARCHAR(50),
    asset_group VARCHAR(50),
    open NUMERIC(14, 4),
    high NUMERIC(14, 4),
    low NUMERIC(14, 4),
    close NUMERIC(14, 4),
    volume NUMERIC(20, 2),
    PRIMARY KEY (date, asset_code)
);

CREATE TABLE fact_macro_group_comparison (
    date DATE PRIMARY KEY,
    trading_day_flag SMALLINT NOT NULL,
    metals_return NUMERIC(10, 6),
    sp500_return NUMERIC(10, 6),
    crypto_return NUMERIC(10, 6),
    metals_index_100 NUMERIC(14, 4),
    sp500_index_100 NUMERIC(14, 4),
    crypto_index_100 NUMERIC(14, 4),
    corr_30d_metals_sp500 NUMERIC(10, 6),
    corr_30d_crypto_sp500 NUMERIC(10, 6),
    corr_30d_crypto_metals NUMERIC(10, 6)
);

/*CREATE INDEX idx_fact_prices_asset_date ON fact_daily_asset_prices(asset_code, date);*/