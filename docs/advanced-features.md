# Advanced Features Guide

This guide covers advanced features and techniques for power users of TradeTrack.

## Table of Contents

- [Advanced Display Options](#advanced-display-options)
- [Automation and Scripting](#automation-and-scripting)
- [Custom Price Sources](#custom-price-sources)
- [Performance Optimization](#performance-optimization)
- [Integration Examples](#integration-examples)
- [Troubleshooting Advanced Features](#troubleshooting-advanced-features)

## Advanced Display Options

### Custom Terminal Width

Control table width for different terminal sizes:

```bash
# Set specific width
python ttrack.py -p portfolio -t 120

# Stretch to full terminal width
python ttrack.py -p portfolio -t 0

# Use default width from config
python ttrack.py -p portfolio
```

### Sorting and Filtering

#### Multi-Column Sorting

Sort by multiple columns for complex analysis:

```bash
# Sort by portfolio, then by gain percentage
python ttrack.py --all --sort-multi portfolio,gain_pct

# Sort by cost descending, then by symbol ascending
python ttrack.py --all --sort-multi cost,symbol --sort-desc
```

#### Available Sort Columns

- `portfolio` - Portfolio name
- `symbol` - Asset symbol
- `description` - Asset description
- `qty` - Quantity
- `ave` - Average cost
- `price` - Current price
- `gain_pct` - Gain percentage
- `cost` - Total cost
- `gain_dollars` - Gain in dollars
- `value` - Current value

### Display Modes

#### Day Gains vs Average Cost

Switch between day gains and average cost display:

```bash
# Show day gains (price change from previous close)
python ttrack.py -p portfolio -d

# Show average cost (default)
python ttrack.py -p portfolio
```

#### Include Cryptocurrency

Include crypto in all-portfolio view:

```bash
# Include crypto in --all view
python ttrack.py --all -ic

# Exclude crypto (default)
python ttrack.py --all
```

## Data Management

### Live Data Fetching

Force fresh data from Yahoo Finance:

```bash
# Bypass cache and fetch live data
python ttrack.py -p portfolio --live

# Use cached data (default, faster)
python ttrack.py -p portfolio
```

### Export and Import

#### CSV Export

Export portfolio data for external analysis:

```bash
# Export single portfolio
python ttrack.py -p portfolio -c portfolio_export.csv

# Export all portfolios
python ttrack.py --all -c all_portfolios.csv

# Export with specific sorting
python ttrack.py --all --sort gain_dollars --sort-desc -c sorted_export.csv
```

#### CSV Format

Exported CSV includes all displayed columns:

```csv
Portfolio,Symbol,Description,Qty,Ave$,Price,Change,Gain%,Cost,Gain$,Value
STOCKS,AAPL,Apple Inc.,10,150.00,175.50,2.50,16.67,1500.00,255.00,1755.00
```

### Backup and Restore

#### Portfolio Backup

Create timestamped backups:

```bash
# Backup single portfolio
python ttrack.py --backup-portfolio stocks

# Backup creates: backups/stocks_20241201_120000.yaml
```

#### Portfolio Restore

Restore from backup:

```bash
# Restore from backup
python ttrack.py --restore-portfolio backups/stocks_20241201_120000.yaml restored_stocks
```

## Advanced Portfolio Management

### Symbol Management

#### Add Symbols

Add new symbols to existing portfolios:

```bash
# Add symbol with description
python ttrack.py --add-symbol portfolio SYMBOL "Description"

# Example
python ttrack.py --add-symbol stocks NVDA "NVIDIA Corporation"
```

#### Remove Symbols

Remove symbols and all associated lots:

```bash
# Remove symbol completely
python ttrack.py --remove-symbol portfolio SYMBOL

# Example
python ttrack.py --remove-symbol stocks OLD_SYMBOL
```

### Lot Management

#### List Lots

View all lots for a specific symbol:

```bash
# List all lots for a symbol
python ttrack.py --list-lots portfolio SYMBOL

# Example
python ttrack.py --list-lots stocks AAPL
```

#### Remove Lots

Remove specific lots by index:

```bash
# Remove lot by index (0-based)
python ttrack.py --remove-lot portfolio SYMBOL INDEX

# Example: Remove first lot of AAPL
python ttrack.py --remove-lot stocks AAPL 0
```

## Configuration Advanced

### Environment Variables

Override configuration with environment variables:

```bash
# Override config file location
export TTRACK_CONFIG_FILE="/path/to/custom/config.yaml"
python ttrack.py -p portfolio

# Override portfolio directory
export TTRACK_PORTFOLIOS_DIR="/path/to/portfolios"
python ttrack.py --list
```

### Custom Configuration

#### Advanced Display Settings

```yaml
display:
  terminal_width: 0              # 0 = stretch to full width
  borders: true                  # Always use Rich tables
  show_totals: true              # Show totals row
  include_crypto: true           # Include crypto by default
  max_description_length: 50     # Longer descriptions
  stretch_to_terminal: true      # Stretch tables to full width
```

#### Currency Formatting

```yaml
currency:
  decimal_places: 4              # More decimal places
  show_symbol: false             # Hide currency symbol
  colored_mode: true             # Enable color coding
  negative_format: "minus"       # Use minus sign instead of parentheses
```

#### Sorting Configuration

```yaml
display:
  default_sort_column: "gain_dollars"  # Default sort by gain
  default_sort_descending: true        # Default to descending order
  available_sort_columns:              # Custom sort options
    - "portfolio"
    - "symbol"
    - "gain_dollars"
    - "value"
```

## Performance Optimization

### Large Portfolio Handling

For portfolios with many lots:

1. **Split portfolios**: Break large portfolios into smaller ones
2. **Use caching**: Avoid `--live` flag unless necessary
3. **Optimize sorting**: Use efficient sort columns
4. **Regular cleanup**: Remove old or unnecessary lots

### Memory Management

```bash
# Process one portfolio at a time
python ttrack.py -p portfolio1
python ttrack.py -p portfolio2

# Instead of processing all at once
python ttrack.py --all
```

### Network Optimization

```bash
# Use cached data when possible
python ttrack.py -p portfolio

# Only use --live when necessary
python ttrack.py -p portfolio --live
```

## Automation and Scripting

### Batch Operations

Create scripts for common operations:

```bash
#!/bin/bash
# daily_portfolio_check.sh

# Check all portfolios
python ttrack.py --all -b

# Export daily backup
python ttrack.py --all -c "backups/daily_$(date +%Y%m%d).csv"

# Create portfolio backup
python ttrack.py --backup-portfolio main
```

### Cron Jobs

Set up automated tasks:

```bash
# Add to crontab for daily portfolio check at 9 AM
0 9 * * * cd /path/to/tradetrack && python ttrack.py --all -c "backups/daily_$(date +\%Y\%m\%d).csv"
```

### Integration with Other Tools

#### Combine with jq for JSON processing

```bash
# Export to CSV and process with other tools
python ttrack.py --all -c data.csv
cat data.csv | cut -d',' -f1,2,9 | sort -t',' -k3 -nr
```

#### Use with other portfolio tools

```bash
# Export for import into other systems
python ttrack.py --all -c portfolio_export.csv
```

## Troubleshooting Advanced Issues

### Debug Mode

Enable detailed debugging:

```bash
# Show debug information
python ttrack.py --debug -p portfolio

# Debug with live data
python ttrack.py --debug -p portfolio --live
```

### Performance Profiling

```bash
# Time command execution
time python ttrack.py --all

# Profile memory usage
python -m memory_profiler ttrack.py --all
```

### Log Analysis

Check for detailed error information in log files and debug output.

## Best Practices

### Portfolio Organization

1. **Logical grouping**: Group related assets in same portfolio
2. **Consistent naming**: Use consistent naming conventions
3. **Regular maintenance**: Clean up old data regularly
4. **Backup strategy**: Implement regular backup procedures

### Data Quality

1. **Accurate symbols**: Verify all symbols on Yahoo Finance
2. **Correct dates**: Use actual purchase dates
3. **Valid quantities**: Ensure all quantities are positive
4. **Consistent currency**: Use same currency per portfolio

### Performance

1. **Efficient sorting**: Use appropriate sort columns
2. **Cache utilization**: Minimize use of `--live` flag
3. **Portfolio size**: Keep portfolios reasonably sized
4. **Regular updates**: Update dependencies regularly

---

**Need more help?** Check the [Troubleshooting Guide](troubleshooting.md) or [Development Guide](development.md).
