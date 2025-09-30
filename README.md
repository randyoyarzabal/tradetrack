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

# Show all portfolios
python stocks.py --all

# Display statistics
python stocks.py --stats

# Export to CSV
python stocks.py --all -c portfolio_export.csv
```

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
│   ├── portfolio_loader.py      # YAML portfolio loading
│   ├── portfolio_library.py     # Main portfolio logic
│   ├── rich_display.py          # Rich table display
│   └── yahoo_quotes.py          # Yahoo Finance API integration
├── stocks.py                    # Main CLI application
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

### Basic Commands

| Option | Description |
|--------|-------------|
| `-p PORTFOLIO` | Display specific portfolio |
| `--all` | Display all portfolios combined |
| `-s, --stats` | Show portfolio statistics |
| `-c FILE` | Export to CSV file |

### Display Options

| Option | Description |
|--------|-------------|
| `-b, --borders` | Use Rich tables with borders |
| `-d, --day` | Show day gains instead of average cost |
| `-n, --no_totals` | Hide totals row |
| `-t WIDTH` | Set terminal width |

### Filter Options

| Option | Description |
|--------|-------------|
| `-ic, --crypto` | Include cryptocurrency |
| `-iu, --unvested` | Include unvested stocks |

### Utility Options

| Option | Description |
|--------|-------------|
| `--debug` | Enable debug mode |
| `-h, --help` | Show help message |
| `-v, --version` | Show version information |

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