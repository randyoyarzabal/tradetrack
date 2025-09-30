# TradeTrack

**A modern CLI stock portfolio tracker with real-time data, beautiful displays, and comprehensive analytics.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rich](https://img.shields.io/badge/rich-terminal%20display-green.svg)](https://github.com/Textualize/rich)

TradeTrack is a feature-rich command-line tool for tracking and analyzing your stock and cryptocurrency portfolios. Built with Python and the Rich library, it offers real-time data from Yahoo Finance, beautiful table displays, and comprehensive portfolio management.

## Key Features

- **Real-time Data** - Live stock and crypto prices via Yahoo Finance
- **Beautiful Displays** - Rich tables with borders or clean columnar layout  
- **Portfolio Management** - Track multiple portfolios with YAML configuration
- **Comprehensive Analytics** - Detailed statistics, gains/losses, and performance metrics
- **Highly Configurable** - Customizable display, currency formatting, and sorting
- **Lot Tracking** - Track individual purchase lots with dates and cost basis
- **Manual Price Overrides** - Override API prices for delisted or custom assets
- **CRUD Operations** - Full create, read, update, delete functionality
- **Tax Analysis** - Analyze lot aging and capital gains for tax optimization
- **Backup & Restore** - Automatic portfolio backups and restore functionality

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Configuration File

TradeTrack automatically looks for configuration in this order:
1. **Environment Variable**: `TTRACK_CONFIG_FILE` (if set)
2. **Default**: `conf/config.yaml` (relative to application directory)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/randyoyarzabal/stocks.git
   cd stocks
   ```

2. **Create and activate virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your portfolios:**
   - Copy `templates/config.yaml` to `conf/config.yaml` (default location)
   - Or set `TTRACK_CONFIG_FILE` environment variable to use a custom config location
   - Update the `portfolios_dir` path in the config to point to your portfolio directory
   - Create your portfolio YAML files in the specified directory

### Configuration Options

**Default Configuration:**
- Config file: `conf/config.yaml` (auto-detected)
- Portfolios directory: `portfolios/` (configurable in config file)

**Custom Configuration:**
```bash
# Use custom config file location
export TTRACK_CONFIG_FILE="/path/to/custom/config.yaml"
python ttrack.py -p crypto

# Or specify directly (if supported by your setup)
python ttrack.py -p crypto --config /path/to/custom/config.yaml
```

### Basic Usage

```bash
# Display a specific portfolio
python ttrack.py -p crypto

# Display with borders (Rich mode)
python ttrack.py -p stocks -b

# Show all portfolios
python ttrack.py --all

# Show all portfolios including crypto
python ttrack.py --all -ic

# Display statistics
python ttrack.py --stats

# Export to CSV
python ttrack.py --all -c portfolio_export.csv
```

## Common Commands

### Portfolio Management

```bash
# Create a new portfolio
python ttrack.py --create-portfolio new_portfolio "My new portfolio"

# Delete a portfolio
python ttrack.py --delete-portfolio old_portfolio

# List all portfolios
python ttrack.py --list
```

### Lot Management

```bash
# Add a new lot (uses current date if not specified)
python ttrack.py --add-lot crypto BTC-USD today 0.5 45000.0

# Add a lot with specific date and manual price
python ttrack.py --add-lot robinhood AAPL 2024-01-15 10 150.0 155.0

# Remove a lot by index
python ttrack.py --remove-lot crypto BTC-USD 0

# List all lots for a symbol
python ttrack.py --list-lots crypto BTC-USD
```

### Symbol Management

```bash
# Add a new symbol to a portfolio
python ttrack.py --add-symbol crypto ETH-USD "Ethereum"

# Remove a symbol and all its lots
python ttrack.py --remove-symbol crypto BTC-USD
```

### Display Options

```bash
# Rich tables with borders
python ttrack.py -p crypto -b

# Sort by gain dollars (descending)
python ttrack.py --all --sort gain_dollars --sort-desc

# Show day gains instead of average cost
python ttrack.py -p crypto -d

# Force live data fetch
python ttrack.py -p crypto --live
```

## Project Structure

```text
tradetrack/
├── conf/
│   ├── config.yaml              # Main configuration file
│   └── constants.py             # Application constants
├── libs/
│   ├── config_loader.py         # Configuration management
│   ├── currency_formatter.py    # Currency formatting utilities
│   ├── lot_analysis.py          # Lot analysis and performance tracking
│   ├── portfolio_loader.py      # YAML portfolio loading
│   ├── portfolio_library.py     # Main portfolio logic
│   ├── rich_display.py          # Rich table display
│   ├── tax_analysis.py          # Tax analysis and lot aging
│   └── yahoo_quotes.py          # Yahoo Finance API integration
├── docs/                        # Extended documentation
│   ├── configuration.md         # Detailed configuration guide
│   ├── dependencies.md          # Requirements and dependency information
│   ├── portfolio-format.md      # Portfolio YAML format guide
│   ├── advanced-features.md     # Advanced features and tips
│   └── troubleshooting.md       # Common issues and solutions
├── templates/                   # Example files and templates
│   ├── config.yaml              # Configuration template
│   └── portfolios/              # Portfolio templates
│       ├── stocks.yaml          # Example stock portfolio
│       ├── crypto.yaml          # Example crypto portfolio
│       ├── etfs.yaml            # Example ETF portfolio
│       ├── rsu.yaml             # Example RSU portfolio
│       └── empty.yaml           # Empty portfolio template
├── ttrack.py                    # Main CLI application
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Configuration

### Quick Configuration

Edit `conf/config.yaml` to customize your experience:

```yaml
# Display Options
display:
  terminal_width: 120             # Terminal width
  borders: false                  # Default border setting
  show_totals: true               # Show totals row
  include_crypto: false           # Include crypto by default
  max_description_length: 28      # Max characters for descriptions
  stretch_to_terminal: false      # Stretch tables to full width

# Currency Formatting
currency:
  decimal_places: 2               # Number of decimal places
  show_symbol: true               # Show $ symbol
  colored_mode: true              # Use colors for positive/negative
  negative_format: "parentheses"  # Format for negative values

# Sorting Options
display:
  default_sort_column: "symbol"   # Default sort column
  default_sort_descending: false  # Default sort order
  available_sort_columns:         # Available sort options
    - "portfolio"
    - "symbol"
    - "description"
    - "qty"
    - "ave"
    - "price"
    - "gain_pct"
    - "cost"
    - "gain_dollars"
    - "value"
```

### Portfolio Format
Portfolios are defined in YAML format:

```yaml
name: CRYPTO
description: "Cryptocurrency Portfolio"
stocks:
  BTC-USD:
    description: "Bitcoin USD"
    lots:
      - date: "2024-01-15"
        shares: 0.5
        cost_basis: 45000.0
        manual_price: null  # Optional override price
  ETH-USD:
    description: "Ethereum USD"
    lots:
      - date: "2024-02-01"
        shares: 2.0
        cost_basis: 2500.0
        manual_price: 2600.0  # Override current price
```

## Command Reference

### General Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `-v, --version` | Show version information |
| `--debug` | Enable debug mode |

### Display Options

| Option | Description |
|--------|-------------|
| `-b, --borders` | Use Rich tables with borders |
| `-t WIDTH` | Set terminal width (0 = stretch to full width) |
| `-n, --no_totals` | Hide totals row |
| `-ic, --crypto` | Include cryptocurrency (--all only) |
| `-d, --day` | Show day gains instead of average cost |

### Portfolio Options

| Option | Description |
|--------|-------------|
| `-p PORTFOLIO` | Display specific portfolio |
| `--all` | Display all portfolios combined |
| `--list` | List available portfolios |
| `-s, --stats` | Show portfolio statistics |
| `-c FILE` | Export to CSV file |

### Sorting Options

| Option | Description |
|--------|-------------|
| `--sort COLUMN` | Sort by column (see available columns in config) |
| `--sort-desc` | Sort in descending order |
| `--sort-multi COL1,COL2` | Sort by multiple columns |

### Data Options

| Option | Description |
|--------|-------------|
| `--live` | Force live data fetch (bypass cache) |

## Display Modes

### Columnar Mode (Default)

Clean, borderless tables perfect for quick viewing:

```bash
python ttrack.py -p crypto
```

### Rich Mode (Bordered)

Beautiful tables with borders and enhanced formatting:

```bash
python ttrack.py -p crypto -b
```

## Advanced Features

### Manual Price Overrides

Override API prices for specific lots:

```yaml
lots:
  - date: "2023-01-15"
    shares: 10
    cost_basis: 150.00
    manual_price: 155.50  # Override current price
```

### Tax Analysis

Analyze lot aging and capital gains:

```bash
# Analyze tax implications for all symbols
python ttrack.py --tax-analysis crypto all

# Analyze tax implications for a specific symbol
python ttrack.py --tax-analysis crypto BTC-USD
```

### Backup & Restore

```bash
# Create a backup of a portfolio
python ttrack.py --backup-portfolio crypto

# Restore a portfolio from backup
python ttrack.py --restore-portfolio backups/crypto_20241201_120000.yaml restored_crypto
```

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/randyoyarzabal/stocks.git
cd stocks
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running Tests

```bash
python -m pytest tests/
```

### Debug Mode

```bash
python ttrack.py --debug -p crypto
```

## Documentation

For detailed documentation, see the `/docs` folder:

- **[Configuration Guide](docs/configuration.md)** - Detailed configuration options
- **[Portfolio Format](docs/portfolio-format.md)** - Portfolio YAML format guide
- **[Dependencies](docs/dependencies.md)** - Requirements and dependency information
- **[Advanced Features](docs/advanced-features.md)** - Advanced features and tips
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/randyoyarzabal/stocks/issues) page
2. Create a new issue with detailed information
3. Include your configuration and error messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Yahoo Finance** - For providing free financial data
- **Rich Library** - For beautiful terminal displays
- **Python Community** - For excellent libraries and tools

---

**TradeTrack** - Making portfolio management simple and beautiful!
