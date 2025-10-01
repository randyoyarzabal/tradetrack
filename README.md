# TradeTrack

**A modern CLI stock portfolio tracker with real-time data, beautiful displays, and comprehensive analytics.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Rich](https://img.shields.io/badge/rich-terminal%20display-green.svg)](https://github.com/Textualize/rich)

TradeTrack is a feature-rich command-line tool for tracking and analyzing your stock and cryptocurrency portfolios. Built with Python and the Rich library, it offers real-time data from Yahoo Finance, beautiful table displays, and comprehensive portfolio management.

## 🚀 Getting Started

### Step 1: Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/randyoyarzabal/stocks.git
   cd stocks
   ```

2. **Set up Python environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Verify installation:**

   ```bash
   python ttrack.py --help
   ```

### Step 2: Create Your First Portfolio

1. **Create a new portfolio:**

   ```bash
   python ttrack.py --create-portfolio my_stocks "My Stock Portfolio"
   ```

2. **Add your first stock:**

   ```bash
   # Add Apple stock (10 shares at $150 each on 2024-01-15)
   python ttrack.py --add-lot my_stocks AAPL 2024-01-15 10 150.0
   ```

3. **Add more stocks:**

   ```bash
   # Add Microsoft stock (5 shares at $300 each today)
   python ttrack.py --add-lot my_stocks MSFT today 5 300.0
   
   # Add Tesla stock (2 shares at $200 each with current price override)
   python ttrack.py --add-lot my_stocks TSLA 2024-02-01 2 200.0 250.0
   ```

### Step 3: View Your Portfolio

1. **Display your portfolio:**

   ```bash
   python ttrack.py -p my_stocks
   ```

2. **View with beautiful borders:**

   ```bash
   python ttrack.py -p my_stocks -b
   ```

3. **See all your portfolios:**

   ```bash
   python ttrack.py --all
   ```

### Step 4: Advanced Usage

1. **Create multiple portfolios:**

   ```bash
   # Create a crypto portfolio
   python ttrack.py --create-portfolio crypto "My Crypto Portfolio"
   python ttrack.py --add-lot crypto BTC-USD 2024-01-01 0.5 45000.0
   python ttrack.py --add-lot crypto ETH-USD 2024-01-15 2.0 2500.0
   
   # Create an ETF portfolio
   python ttrack.py --create-portfolio etfs "My ETF Portfolio"
   python ttrack.py --add-lot etfs VOO 2024-01-01 10 400.0
   python ttrack.py --add-lot etfs QQQ 2024-01-01 5 350.0
   ```

2. **View comprehensive statistics:**

   ```bash
   python ttrack.py --stats
   ```

3. **Export your data:**

   ```bash
   python ttrack.py --all -c my_portfolio_export.csv
   ```

## 📊 Key Features

- **Real-time Data** - Live stock and crypto prices via Yahoo Finance
- **Beautiful Displays** - Rich tables with borders or clean columnar layout  
- **Portfolio Management** - Track multiple portfolios with YAML configuration
- **Comprehensive Analytics** - Detailed statistics, gains/losses, and performance metrics
- **Lot Tracking** - Track individual purchase lots with dates and cost basis
- **Tax Analysis** - Analyze lot aging and capital gains for tax optimization
- **Manual Price Overrides** - Override API prices for delisted or custom assets
- **Backup & Restore** - Automatic portfolio backups and restore functionality

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

### Common Display Commands

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
│   └── version.py               # Application version information
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
- **[Development Guide](docs/development.md)** - Development setup, testing, and contributing

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
