# Portfolio Format Guide

This guide explains the YAML format used for TradeTrack portfolios and provides examples for different types of investments.

## Table of Contents

- [Basic Portfolio Structure](#basic-portfolio-structure)
- [Field Descriptions](#field-descriptions)
- [Portfolio Examples](#portfolio-examples)
- [Advanced Features](#advanced-features)
- [Validation Rules](#validation-rules)
- [Best Practices](#best-practices)

## Basic Portfolio Structure

A TradeTrack portfolio is a YAML file with the following structure:

```yaml
name: PORTFOLIO_NAME
description: "Portfolio Description"
currency: USD
lots:
  - symbol: SYMBOL
    description: "Asset Description"
    qty: 10
    cost_per_share: 150.00
    date: "2024-01-15"
    manual_price: null  # Optional: override current price
```

## Required Fields

### Portfolio Level Fields

- **`name`**: Unique portfolio identifier (uppercase, no spaces)
- **`description`**: Human-readable portfolio description
- **`currency`**: Currency code (USD, EUR, etc.)

### Lot Level Fields

- **`symbol`**: Yahoo Finance symbol (e.g., AAPL, BTC-USD, VOO)
- **`description`**: Human-readable asset description
- **`qty`**: Number of shares/units
- **`cost_per_share`**: Purchase price per share/unit
- **`date`**: Purchase date in YYYY-MM-DD format or "today"

## Optional Fields

### Lot Level Optional Fields

- **`manual_price`**: Override current market price (useful for delisted stocks)

## Portfolio Examples

### Stock Portfolio

```yaml
name: STOCKS
description: "Individual Stock Portfolio"
currency: USD
lots:
  - symbol: AAPL
    description: "Apple Inc."
    qty: 10
    cost_per_share: 150.00
    date: "2024-01-15"
    manual_price: null
  - symbol: MSFT
    description: "Microsoft Corporation"
    qty: 5
    cost_per_share: 300.00
    date: "2024-02-01"
    manual_price: null
  - symbol: GOOGL
    description: "Alphabet Inc. Class A"
    qty: 3
    cost_per_share: 2800.00
    date: "today"
    manual_price: null
```

### Cryptocurrency Portfolio

```yaml
name: CRYPTO
description: "Cryptocurrency Portfolio"
currency: USD
lots:
  - symbol: BTC-USD
    description: "Bitcoin USD"
    qty: 0.5
    cost_per_share: 45000.00
    date: "2024-01-01"
    manual_price: null
  - symbol: ETH-USD
    description: "Ethereum USD"
    qty: 2.0
    cost_per_share: 2500.00
    date: "2024-01-15"
    manual_price: 2600.00
  - symbol: ADA-USD
    description: "Cardano USD"
    qty: 1000
    cost_per_share: 0.45
    date: "today"
    manual_price: null
```

### ETF Portfolio

```yaml
name: ETFS
description: "Exchange-Traded Fund Portfolio"
currency: USD
lots:
  - symbol: VOO
    description: "Vanguard S&P 500 ETF"
    qty: 10
    cost_per_share: 400.00
    date: "2024-01-01"
    manual_price: null
  - symbol: QQQ
    description: "Invesco QQQ Trust"
    qty: 5
    cost_per_share: 350.00
    date: "2024-01-01"
    manual_price: null
  - symbol: VTI
    description: "Vanguard Total Stock Market ETF"
    qty: 8
    cost_per_share: 220.00
    date: "2024-02-01"
    manual_price: null
```

### RSU/ESPP Portfolio

```yaml
name: RSU
description: "Restricted Stock Units"
currency: USD
lots:
  - symbol: AAPL
    description: "Apple Inc. RSU"
    qty: 50
    cost_per_share: 0.00
    date: "2024-01-15"
    manual_price: 150.00
  - symbol: MSFT
    description: "Microsoft Corporation ESPP"
    qty: 25
    cost_per_share: 250.00
    date: "2024-02-01"
    manual_price: null
```

## Symbol Formats

### Stock Symbols

Use standard ticker symbols as they appear on Yahoo Finance:

- **Apple**: `AAPL`
- **Microsoft**: `MSFT`
- **Google**: `GOOGL` (Class A) or `GOOG` (Class C)
- **Tesla**: `TSLA`

### Cryptocurrency Symbols

Use Yahoo Finance crypto format:

- **Bitcoin**: `BTC-USD`
- **Ethereum**: `ETH-USD`
- **Cardano**: `ADA-USD`
- **Solana**: `SOL-USD`

### International Symbols

Include exchange suffixes:

- **Toyota (Tokyo)**: `7203.T`
- **Samsung (Korea)**: `005930.KS`
- **Nestle (Switzerland)**: `NESN.SW`

## Date Formats

### Supported Date Formats

- **ISO Format**: `2024-01-15`
- **Today**: `today` (uses current date)
- **Relative dates**: Not supported (use specific dates)

### Examples

```yaml
date: "2024-01-15"  # January 15, 2024
date: "today"       # Current date
date: "2023-12-31"  # December 31, 2023
```

## Manual Price Overrides

Use `manual_price` to override current market prices:

### When to Use

- **Delisted stocks**: Assets no longer traded
- **Private companies**: Non-public securities
- **Custom valuations**: Your own price estimates
- **Testing**: Override prices for testing purposes

### Manual Price Examples

```yaml
# Delisted stock with manual price
- symbol: DELISTED
  description: "Delisted Company"
  qty: 100
  cost_per_share: 10.00
  date: "2023-01-01"
  manual_price: 5.00  # Override current price

# RSU with current market price
- symbol: AAPL
  description: "Apple RSU"
  qty: 50
  cost_per_share: 0.00
  date: "2024-01-15"
  manual_price: 150.00  # Current market price
```

## Best Practices

### File Organization

1. **One portfolio per file**: Keep each portfolio in its own YAML file
2. **Descriptive names**: Use clear, descriptive portfolio names
3. **Consistent naming**: Use uppercase for portfolio names, proper case for descriptions

### Data Quality

1. **Accurate dates**: Use actual purchase dates when possible
2. **Correct symbols**: Verify symbols on Yahoo Finance before adding
3. **Consistent currency**: Use the same currency for all lots in a portfolio
4. **Valid quantities**: Ensure quantities are positive numbers

### Maintenance

1. **Regular updates**: Update manual prices when needed
2. **Clean data**: Remove old or incorrect lots
3. **Backup files**: Keep backups of your portfolio files
4. **Version control**: Consider using Git for portfolio file versioning

## Common Mistakes

### Symbol Errors

```yaml
# Wrong
symbol: "Apple"     # Use ticker symbol, not company name
symbol: "BTC"       # Use full crypto symbol

# Correct
symbol: "AAPL"      # Apple ticker
symbol: "BTC-USD"   # Bitcoin crypto symbol
```

### Date Errors

```yaml
# Wrong
date: "1/15/2024"   # Wrong format
date: "yesterday"   # Not supported

# Correct
date: "2024-01-15"  # ISO format
date: "today"       # Current date
```

### Quantity Errors

```yaml
# Wrong
qty: "10"           # String instead of number
qty: -5             # Negative quantity

# Correct
qty: 10             # Positive number
qty: 0.5            # Decimal for fractional shares
```

## Template Files

Use the template files in `/templates/portfolios/` as starting points:

- **`empty.yaml`**: Basic empty portfolio template
- **`stocks.yaml`**: Example stock portfolio
- **`crypto.yaml`**: Example cryptocurrency portfolio
- **`etfs.yaml`**: Example ETF portfolio
- **`rsu.yaml`**: Example RSU/ESPP portfolio

## Validation

TradeTrack validates portfolio files when loading them. Common validation errors:

1. **Missing required fields**: Ensure all required fields are present
2. **Invalid date format**: Use YYYY-MM-DD or "today"
3. **Invalid symbols**: Check symbols on Yahoo Finance
4. **YAML syntax errors**: Ensure proper indentation and formatting

---

**Need help?** Check the [Troubleshooting Guide](troubleshooting.md) or create an issue on GitHub.
