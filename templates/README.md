# Templates

This folder contains example configuration files and portfolio templates to help you get started with TradeTrack.

## Portfolio Templates

### stocks.yaml
Example stock portfolio with major tech companies:
- Apple (AAPL)
- Microsoft (MSFT)
- Google (GOOGL)
- Tesla (TSLA)
- NVIDIA (NVDA)

### crypto.yaml
Example cryptocurrency portfolio with major coins:
- Bitcoin (BTC-USD)
- Ethereum (ETH-USD)
- Dogecoin (DOGE-USD)
- Cardano (ADA-USD)
- Solana (SOL-USD)
- Example of manual price override for delisted assets

### etfs.yaml
Example ETF portfolio for diversification:
- VTI (Total Stock Market)
- VXUS (International Stocks)
- BND (Bonds)
- QQQ (NASDAQ-100)
- ARKK (Innovation)
- SPY (S&P 500)

### rsu.yaml
Example RSU (Restricted Stock Units) portfolio:
- Company stock awards
- Stock options that have been exercised
- Examples of zero cost basis entries

### empty.yaml
Empty portfolio template with comments showing the format.

## Configuration Template

### config.yaml
Single configuration template with all essential settings:
- Terminal width: 120 (adjustable)
- Columnar display by default (use `-b` flag for borders)
- Standard currency formatting
- Comprehensive sorting options
- Crypto symbols auto-detected at runtime

## Usage

1. Copy the desired portfolio template to your portfolios directory
2. Edit the template with your actual holdings
3. Copy `config.yaml` to `conf/config.yaml`
4. Customize the configuration for your needs

## Getting Started

1. Copy `empty.yaml` to your portfolios directory
2. Rename it to your portfolio name (e.g., `my_portfolio.yaml`)
3. Add your stocks following the format shown in the comments
4. Copy `config.yaml` to `conf/config.yaml` (default location)
   - Or set `CONFIG_FILE` environment variable to use a custom location
5. Update the `portfolios_dir` path in the config to point to your portfolios directory
