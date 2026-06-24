/* =========================================================
   1) Create Bronze / Silver / Gold schemas if not exist
========================================================= */
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'bronze')
    EXEC('CREATE SCHEMA bronze');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'silver')
    EXEC('CREATE SCHEMA silver');
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'gold')
    EXEC('CREATE SCHEMA gold');
GO

/* =========================================================
   2) bronze.sp500_tickers
========================================================= */
IF OBJECT_ID('bronze.sp500_tickers', 'U') IS NOT NULL
    DROP TABLE bronze.sp500_tickers;
GO

CREATE TABLE bronze.sp500_tickers (
    ticker              VARCHAR(20)   NOT NULL PRIMARY KEY,
    company_name        VARCHAR(255)  NULL,
    source              VARCHAR(100)  NOT NULL DEFAULT 'Wikipedia',
    load_date           DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    load_ts             DATETIME2     NOT NULL DEFAULT GETDATE()
);
GO

/* =========================================================
   3) bronze.profile
========================================================= */
IF OBJECT_ID('bronze.profile', 'U') IS NOT NULL
    DROP TABLE bronze.profile;
GO

CREATE TABLE bronze.profile (
    ticker                  VARCHAR(20)   NOT NULL,
    company_name            VARCHAR(255)  NULL,
    sector                  VARCHAR(255)  NULL,
    industry                VARCHAR(255)  NULL,
    current_price           DECIMAL(18,4) NULL,
    market_cap              BIGINT        NULL,
    beta                    DECIMAL(18,6) NULL,
    country                 VARCHAR(100)  NULL,
    currency                VARCHAR(50)   NULL,
    website                 VARCHAR(500)  NULL,
    ceo                     VARCHAR(255)  NULL,
    ipo_date                DATE          NULL,
    is_etf                  BIT           NULL,
    is_actively_trading     BIT           NULL,
    fmp_fetch_date          DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    load_ts                 DATETIME2     NOT NULL DEFAULT GETDATE()
);
GO

/* =========================================================
   4) bronze.income_statement
========================================================= */
IF OBJECT_ID('bronze.income_statement', 'U') IS NOT NULL
    DROP TABLE bronze.income_statement;
GO

CREATE TABLE bronze.income_statement (
    ticker                          VARCHAR(20)   NOT NULL,
    statement_date                  DATE          NULL,
    fiscal_year                     VARCHAR(20)   NULL,
    period                          VARCHAR(20)   NULL,
    revenue                         BIGINT        NULL,
    gross_profit                    BIGINT        NULL,
    operating_income                BIGINT        NULL,
    net_income                      BIGINT        NULL,
    eps                             DECIMAL(18,6) NULL,
    weighted_avg_shares_diluted     BIGINT        NULL,
    reported_currency               VARCHAR(20)   NULL,
    fmp_fetch_date                  DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    load_ts                         DATETIME2     NOT NULL DEFAULT GETDATE()
);
GO

/* =========================================================
   5) bronze.balance_sheet
========================================================= */
IF OBJECT_ID('bronze.balance_sheet', 'U') IS NOT NULL
    DROP TABLE bronze.balance_sheet;
GO

CREATE TABLE bronze.balance_sheet (
    ticker                              VARCHAR(20)   NOT NULL,
    statement_date                      DATE          NULL,
    fiscal_year                         VARCHAR(20)   NULL,
    period                              VARCHAR(20)   NULL,
    cash_and_short_term_investments     BIGINT        NULL,
    total_assets                        BIGINT        NULL,
    total_debt                          BIGINT        NULL,
    net_debt                            BIGINT        NULL,
    total_equity                        BIGINT        NULL,
    reported_currency                   VARCHAR(20)   NULL,
    fmp_fetch_date                      DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    load_ts                             DATETIME2     NOT NULL DEFAULT GETDATE()
);
GO

/* =========================================================
   6) bronze.cashflow
========================================================= */
IF OBJECT_ID('bronze.cashflow', 'U') IS NOT NULL
    DROP TABLE bronze.cashflow;
GO

CREATE TABLE bronze.cashflow (
    ticker                          VARCHAR(20)   NOT NULL,
    statement_date                  DATE          NULL,
    fiscal_year                     VARCHAR(20)   NULL,
    period                          VARCHAR(20)   NULL,
    operating_cash_flow             BIGINT        NULL,
    capital_expenditure             BIGINT        NULL,
    free_cash_flow                  BIGINT        NULL,
    net_income                      BIGINT        NULL,
    reported_currency               VARCHAR(20)   NULL,
    fmp_fetch_date                  DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    load_ts                         DATETIME2     NOT NULL DEFAULT GETDATE()
);
GO

/* =========================================================
   7) bronze.ratios_ttm
========================================================= */
IF OBJECT_ID('bronze.ratios_ttm', 'U') IS NOT NULL
    DROP TABLE bronze.ratios_ttm;
GO

CREATE TABLE bronze.ratios_ttm (
    ticker                  VARCHAR(20)   NOT NULL,
    pe_ratio                DECIMAL(18,6) NULL,
    pb_ratio                DECIMAL(18,6) NULL,
    ps_ratio                DECIMAL(18,6) NULL,
    current_ratio           DECIMAL(18,6) NULL,
    debt_to_equity          DECIMAL(18,6) NULL,
    gross_margin            DECIMAL(18,6) NULL,
    operating_margin        DECIMAL(18,6) NULL,
    net_margin              DECIMAL(18,6) NULL,
    roe                     DECIMAL(18,6) NULL,
    roa                     DECIMAL(18,6) NULL,
    fmp_fetch_date          DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    load_ts                 DATETIME2     NOT NULL DEFAULT GETDATE()
);
GO

/* =========================================================
   8) bronze.api_run_log
========================================================= */
IF OBJECT_ID('bronze.api_run_log', 'U') IS NOT NULL
    DROP TABLE bronze.api_run_log;
GO

CREATE TABLE bronze.api_run_log (
    log_id               INT IDENTITY(1,1) PRIMARY KEY,
    run_ts               DATETIME2      NOT NULL DEFAULT GETDATE(),
    ticker               VARCHAR(20)    NULL,
    endpoint_name        VARCHAR(100)   NOT NULL,
    request_url          VARCHAR(1000)  NULL,
    http_status_code     INT            NULL,
    success_flag         BIT            NOT NULL,
    error_message        VARCHAR(2000)  NULL
);
GO