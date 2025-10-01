# Configuration Guide

This guide covers all configuration options available in TradeTrack.

## Main Configuration File

The main configuration is stored in `conf/config.yaml`. This file controls all aspects of the application behavior.

## Configuration Sections

### Application Information

```yaml
app:
  name: "Stock Portfolio Tracker"
  version: "v1.0"
```

### File Paths

```yaml
paths:
  portfolios_dir: "/Users/royarzab/chief_plugins/stocks/portfolios"  # Directory containing portfolio YAML files
  log_file: "logs/portfolio.log"    # Log file path (optional)
```

**Note**: The config file path is automatically detected and can be overridden with the `CONFIG_FILE` environment variable. Default is `conf/config.yaml`.

### Display Configuration

```yaml
display:
  terminal_width: 120             # Default terminal width
  borders: false                  # Default border setting for tables
  show_totals: true               # Show totals row by default
  include_crypto: false           # Include crypto by default
  max_description_length: 28      # Maximum characters for company descriptions
  stretch_to_terminal: false      # Stretch tables to full terminal width (true) or respect terminal_width (false)
  
  # Sorting Configuration
  default_sort_column: "symbol"   # Default column to sort by
  default_sort_descending: false  # Default sort order (false = ascending, true = descending)
  
  # Available sort columns (for reference and validation)
  available_sort_columns:
    - "portfolio"      # Portfolio name
    - "symbol"         # Stock symbol
    - "description"    # Company description
    - "qty"            # Quantity/shares
    - "ave"            # Average cost (or day cost in day mode)
    - "price"          # Current price
    - "gain_pct"       # Gain percentage
    - "cost"           # Total cost
    - "gain_dollars"   # Gain in dollars
    - "value"          # Current value
```

### Currency Formatting

```yaml
currency:
  decimal_places: 2               # Number of decimal places for currency
  show_symbol: true               # Show $ symbol
  colored_mode: true              # Use colors for positive/negative values
  negative_format: "parentheses"  # Format for negative values: "parentheses" or "minus"
```

### Table Display Options

```yaml
tables:
  bordered_style: "heavy"         # Border style for -b flag: "light", "heavy", "double"
  columnar_style: "clean"         # Style for columnar display
  header_style: "bold"            # Header text style
  number_alignment: "right"       # Number alignment: "left", "center", "right"
```

### API Configuration

```yaml
api:
  yahoo:
    timeout: 30                   # Request timeout in seconds
    retries: 3                    # Number of retry attempts
    cache_duration: 300           # Cache duration in seconds (5 minutes)
  td_ameritrade:
    enabled: false                # Enable TD Ameritrade API (not implemented)
    client_id: ""                 # TD Ameritrade client ID
    redirect_uri: ""              # TD Ameritrade redirect URI
```

### Portfolio Configuration

```yaml
portfolio:
  crypto_symbols:                 # List of known crypto symbols
    - "BTC-USD"
    - "ETH-USD"
    - "DOGE-USD"
    - "SHIB-USD"
    - "XRP-USD"
    - "XLM-USD"
    - "PEPE-USD"
```

## Configuration Examples

### Minimal Configuration

```yaml
paths:
  portfolios_dir: "portfolios"

display:
  terminal_width: 120
  borders: false
  show_totals: true
```

### Rich Display Configuration

```yaml
display:
  terminal_width: 140
  borders: true
  show_totals: true
  stretch_to_terminal: true

tables:
  bordered_style: "heavy"
  header_style: "bold"
```

### Crypto-Focused Configuration

```yaml
display:
  include_crypto: true
  terminal_width: 120
  max_description_length: 35

currency:
  decimal_places: 6  # More precision for crypto
  colored_mode: true
```

### Sorting Configuration

```yaml
display:
  default_sort_column: "gain_dollars"
  default_sort_descending: true
  available_sort_columns:
    - "symbol"
    - "gain_dollars"
    - "gain_pct"
    - "value"
```

## Environment Variables

You can override configuration values using environment variables:

```bash
# Override config file path

export CONFIG_FILE="/path/to/custom/config.yaml"

# Override portfolios directory

export TRADETRACK_PORTFOLIOS_DIR="/path/to/portfolios"

# Override terminal width

export TRADETRACK_TERMINAL_WIDTH="140"

# Override cache duration

export TRADETRACK_CACHE_DURATION="600"
```

### Config File Path

The configuration file path is automatically detected with the following priority:

1. **Environment Variable**: `CONFIG_FILE` environment variable
2. **Default**: `conf/config.yaml` (relative to the application directory)

This means you can:
- Use the default `conf/config.yaml` (most common)
- Override with `CONFIG_FILE` environment variable for custom locations
- No need to specify the path in the config file itself

## Configuration Validation

TradeTrack validates configuration on startup and will:

1. Check that required paths exist
2. Validate numeric values are within reasonable ranges
3. Ensure boolean values are properly formatted
4. Verify that sort columns are valid

## Troubleshooting Configuration

### Common Issues

1. **Portfolios directory not found**
   - Ensure the path exists and is accessible
   - Use absolute paths for better reliability

2. **Invalid sort column**
   - Check that the column name is in `available_sort_columns`
   - Use lowercase column names

3. **Terminal width not respected**
   - Set `stretch_to_terminal: false`
   - Ensure `terminal_width` is set to a reasonable value

4. **Currency formatting issues**
   - Check that `decimal_places` is a positive integer
   - Ensure `negative_format` is either "parentheses" or "minus"

### Debug Mode

Enable debug mode to see configuration loading:

```bash
python ttrack.py --debug -p crypto
```

This will show:
- Configuration file loading
- Default value application
- Validation results
- Final configuration values
