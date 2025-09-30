# TradeTrack

**A personal CLI stock trading management and analysis tool.**

TradeTrack is a modern, feature-rich command-line tool for tracking and analyzing your stock and cryptocurrency portfolios. Built with Python, it offers a clean interface, real-time data from Yahoo Finance, and beautiful table displays using the Rich library.

## ✨ Features

- **📊 Portfolio Management**: Track multiple portfolios with YAML configuration
- **💰 Real-time Data**: Live stock and crypto prices via Yahoo Finance API
- **🎨 Beautiful Display**: Rich tables with borders or clean columnar layout
- **📈 Comprehensive Analytics**: Detailed statistics, gains/losses, and performance metrics
- **🔧 Highly Configurable**: Customizable currency formatting, display options, and more
- **📝 Lot Tracking**: Track individual purchase lots with dates and cost basis
- **💱 Multi-currency Support**: Handle different currencies and manual price overrides
- **📊 Export Capabilities**: Export portfolio data to CSV format
- **🛠️ CRUD Operations**: Create, read, update, and delete portfolios, symbols, and lots
- **📊 Tax Analysis**: Analyze lot aging and capital gains for tax optimization
- **🔄 Backup & Restore**: Automatic portfolio backups and restore functionality

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

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
   - Update `conf/config.yaml` to point to your portfolio directory
   - Create your portfolio YAML files in the specified directory
   - Example: Set `portfolios_dir` to `/path/to/your/portfolios`

### Basic Usage

```bash
# Display a specific portfolio
python stocks.py -p crypto

# Display with borders (Rich mode)
python stocks.py -p stocks -b

# Display with full terminal width
python stocks.py -p crypto -t 0

# Show all portfolios
python stocks.py --all

# Show all portfolios including crypto
python stocks.py --all -ic

# Display statistics
python stocks.py --stats

# Export to CSV
python stocks.py --all -c portfolio_export.csv
```

## 🛠️ CRUD Operations

TradeTrack now includes comprehensive CRUD (Create, Read, Update, Delete) operations for managing your portfolios:

### Portfolio Management

```bash
# Create a new portfolio
python stocks.py --create-portfolio new_portfolio "My new portfolio"

# Delete a portfolio
python stocks.py --delete-portfolio old_portfolio

# List all portfolios
python stocks.py --list
```

### Symbol Management

```bash
# Add a new symbol to a portfolio
python stocks.py --add-symbol crypto ETH-USD "Ethereum"

# Remove a symbol and all its lots
python stocks.py --remove-symbol crypto BTC-USD
```

### Lot Management

```bash
# Add a new lot (uses current date if not specified)
python stocks.py --add-lot crypto BTC-USD today 0.5 45000.0

# Add a lot with specific date and manual price
python stocks.py --add-lot robinhood AAPL 2024-01-15 10 150.0 155.0

# Remove a lot by index
python stocks.py --remove-lot crypto BTC-USD 0

# List all lots for a symbol
python stocks.py --list-lots crypto BTC-USD
```

### Tax Analysis

```bash
# Analyze tax implications for all symbols in a portfolio
python stocks.py --tax-analysis crypto all

# Analyze tax implications for a specific symbol
python stocks.py --tax-analysis crypto BTC-USD
```

### Backup & Restore

```bash
# Create a backup of a portfolio
python stocks.py --backup-portfolio crypto

# Restore a portfolio from backup
python stocks.py --restore-portfolio backups/crypto_20241201_120000.yaml restored_crypto
```

### Key Features

- **Automatic Sorting**: Portfolios are kept in alphabetical order, lots sorted by date (newest first)
- **Default Values**: New lots default to current date if not specified
- **Tax Analysis**: Track lot aging and capital gains for tax optimization
- **Backup System**: Automatic timestamped backups before major changes
- **Validation**: Comprehensive input validation and error handling

## 📁 Project Structure

```
tradetrack/
├── conf/
│   ├── config.yaml              # Main configuration file
│   └── portfolios/              # Portfolio YAML files
│       ├── crypto.yaml
│       ├── stocks.yaml
│       └── ...
├── libs/
│   ├── config_loader.py         # Configuration management
│   ├── currency_formatter.py    # Currency formatting utilities
│   ├── lot_analysis.py          # Lot analysis and performance tracking
│   ├── portfolio_loader.py      # YAML portfolio loading
│   ├── portfolio_library.py     # Main portfolio logic
│   ├── rich_display.py          # Rich table display
│   ├── tax_analysis.py          # Tax analysis and lot aging
│   └── yahoo_quotes.py          # Yahoo Finance API integration
├── stocks.py                    # Main CLI application with CRUD operations
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## ⚙️ Configuration

### Main Configuration (`conf/config.yaml`)

The main configuration file controls all aspects of the application:

```yaml
# Application Information
app:
  name: "Stock Portfolio Tracker"
  version: "v1.0"

# File Paths
paths:
  portfolios_dir: "conf/portfolios"
  config_file: "conf/config.yaml"

# Display Options
display:
  terminal_width: 120
  borders: false
  show_totals: true
  include_crypto: false

# Currency Formatting
currency:
  decimal_places: 2
  show_symbol: true
  colored_mode: true
  negative_format: "parentheses"

# Table Display
tables:
  bordered_style: "heavy"
  columnar_style: "clean"
  header_style: "bold"
  number_alignment: "right"
```

### Portfolio Format (`conf/portfolios/your_portfolio.yaml`)

Portfolios are defined in YAML format with the following structure:

```yaml
name: PORTFOLIO_NAME
description: "Portfolio description"
stocks:
  SYMBOL:
    description: "Company/Asset description"
    notes: "Your notes about this investment"
    lots:
      - date: "YYYY-MM-DD"
        shares: 10.5
        cost_basis: 150.25
        manual_price: null  # Optional override price
      - date: "YYYY-MM-DD"
        shares: 5.0
        cost_basis: 160.00
        manual_price: 155.50
```

## 🎯 Command Line Options

The command line options are organized into logical groups for better usability:

### General Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help message |
| `-v, --version` | Show version information |
| `--debug` | Enable debug mode |

### Screen Display Options

| Option | Description |
|--------|-------------|
| `-b, --borders` | Use Rich tables with borders |
| `-t WIDTH` | Set terminal width (0 = stretch to full width) |
| `-n, --no_totals` | Hide totals row |

### Portfolio Display Options

| Option | Description |
|--------|-------------|
| `-p PORTFOLIO` | Display specific portfolio |
| `--all` | Display all portfolios combined |
| `--list` | List available portfolios |
| `-s, --stats` | Show portfolio statistics |
| `-c FILE` | Export to CSV file |
| `-ic, --crypto` | Include cryptocurrency (--all only) |
| `-d, --day` | Show day gains instead of average cost |

### Lot Management Options

| Option | Description |
|--------|-------------|
| `--add-lot PORTFOLIO SYMBOL DATE SHARES COST_BASIS [MANUAL_PRICE]` | Add a new lot to a portfolio |
| `--remove-lot PORTFOLIO SYMBOL LOT_INDEX` | Remove a lot from a portfolio |
| `--update-lot PORTFOLIO SYMBOL LOT_INDEX FIELD` | Update a lot field |
| `--list-lots PORTFOLIO SYMBOL` | List all lots for a symbol |

### Symbol Management Options

| Option | Description |
|--------|-------------|
| `--add-symbol PORTFOLIO SYMBOL DESCRIPTION` | Add a new symbol to a portfolio |
| `--remove-symbol PORTFOLIO SYMBOL` | Remove a symbol and all its lots |

### Portfolio Management Options

| Option | Description |
|--------|-------------|
| `--create-portfolio PORTFOLIO DESCRIPTION` | Create a new portfolio |
| `--delete-portfolio PORTFOLIO` | Delete a portfolio |
| `--backup-portfolio PORTFOLIO` | Create a backup of a portfolio |
| `--restore-portfolio BACKUP_FILE PORTFOLIO` | Restore a portfolio from backup |

### Analysis Options

| Option | Description |
|--------|-------------|
| `--tax-analysis PORTFOLIO SYMBOL` | Show tax analysis for portfolio/symbol |

### Data Options

| Option | Description |
|--------|-------------|
| `--live` | Force live data fetch (bypass cache) |

## 📊 Display Modes

### Columnar Mode (Default)
Clean, borderless tables perfect for quick viewing:
```bash
python stocks.py -p crypto
```

### Rich Mode (Bordered)
Beautiful tables with borders and enhanced formatting:
```bash
python stocks.py -p crypto -b
```

## 💰 Currency Formatting

TradeTrack offers flexible currency formatting:

- **Decimal Places**: Configurable precision (default: 2)
- **Symbol Display**: Toggle $ symbol on/off
- **Color Coding**: Red for losses, green for gains
- **Negative Format**: Parentheses or minus sign
- **Rich Integration**: Proper color handling in both display modes

## 🔧 Advanced Features

### Manual Price Overrides
Override API prices for specific lots:
```yaml
lots:
  - date: "2023-01-15"
    shares: 10
    cost_basis: 150.00
    manual_price: 155.50  # Override current price
```

### Lot Tracking
Track multiple purchase lots with different dates and costs:
```yaml
stocks:
  AAPL:
    lots:
      - date: "2023-01-10"
        shares: 10
        cost_basis: 150.25
      - date: "2023-06-15"
        shares: 5
        cost_basis: 175.50
```

### Statistics and Analytics
Comprehensive portfolio analysis:
- Total cost, value, and gains
- Average performance metrics
- Min/max values across all holdings
- Individual stock performance

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and setup:**
   ```bash
   git clone https://github.com/randyoyarzabal/stocks.git
   cd stocks
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run tests:**
   ```bash
   python -m pytest tests/
   ```

3. **Debug mode:**
   ```bash
   python stocks.py --debug -p crypto
   ```

### Adding New Features

1. **Configuration**: Add new options to `conf/config.yaml`
2. **Portfolio Logic**: Extend `libs/portfolio_library.py`
3. **Display**: Modify `libs/rich_display.py`
4. **Data Sources**: Update `libs/yahoo_quotes.py`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/randyoyarzabal/stocks/issues) page
2. Create a new issue with detailed information
3. Include your configuration and error messages

## 🙏 Acknowledgments

- **Yahoo Finance**: For providing free financial data
- **Rich Library**: For beautiful terminal displays
- **Python Community**: For excellent libraries and tools

---

**TradeTrack** - Making portfolio management simple and beautiful! 📈✨