INSERT INTO dim_assets (asset_code, asset_name, asset_group) VALUES
('GOLD', 'Gold', 'Precious Metals'),
('SILVER', 'Silver', 'Precious Metals'),
('SP500', 'S&P 500', 'Equities (S&P 500)'),
('BTC', 'Bitcoin', 'Crypto'),
('ETH', 'Ethereum', 'Crypto')
ON CONFLICT (asset_code) DO NOTHING;

ALTER TABLE fact_daily_asset_prices
DROP CONSTRAINT IF EXISTS fk_asset_code,
ADD CONSTRAINT fk_asset_code FOREIGN KEY (asset_code) REFERENCES dim_assets(asset_code);

CREATE OR REPLACE VIEW vw_asset_risk_metrics AS
WITH daily_calc AS (
    SELECT 
        date,
        asset_code,
        close,
        LAG(close) OVER (PARTITION BY asset_code ORDER BY date) AS prev_close,
        MAX(close) OVER (
            PARTITION BY asset_code 
            ORDER BY date 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_max_close
    FROM fact_daily_asset_prices
),
returns_calc AS (
    SELECT 
        date,
        asset_code,
        close,
        (close - prev_close) / NULLIF(prev_close, 0) AS daily_return,
        (close - running_max_close) / NULLIF(running_max_close, 0) AS drawdown_pct
    FROM daily_calc
)
SELECT 
    date,
    asset_code,
    close,
    ROUND(daily_return::numeric, 6) AS daily_return,
    ROUND(drawdown_pct::numeric, 4) AS drawdown_pct,
    ROUND(
        (STDDEV(daily_return) OVER (
            PARTITION BY asset_code 
            ORDER BY date 
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) * SQRT(252))::numeric, 4
    ) AS annualized_volatility_30d
FROM returns_calc
WHERE daily_return IS NOT NULL;