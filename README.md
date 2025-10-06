# TradeTrack

> **A modern CLI stock portfolio tracker with real-time data and beautiful displays**

Track and analyze your stock and cryptocurrency portfolios with real-time data from Yahoo Finance, beautiful table displays, and comprehensive portfolio management. Built with Python and the Rich library.

## Quick Start (3 Steps)

### 1. Clone & Setup
```bash
git clone https://github.com/randyoyarzabal/tradetrack.git
cd tradetrack

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Tracking
```bash
# Create your first portfolio
python ttrack.py create my-portfolio

# Add some stocks
python ttrack.py add AAPL 10 150.00 my-portfolio
python ttrack.py add MSFT 5 300.00 my-portfolio

# View your portfolio
python ttrack.py view my-portfolio
```

**That's it!** Your portfolio is ready. See [Complete Documentation](docs/index.md) for advanced features.

## System Requirements

- **Python 3.8+** with pip support
- **Internet connection** for real-time data
- **Git** (for cloning repository)

**Supported OS**: Windows, macOS, Linux

> **Need detailed setup instructions?** See [Dependencies](docs/dependencies.md) and [Configuration](docs/configuration.md) for comprehensive installation steps.

## Production Setup

### Portfolio Management
```bash
# Create portfolio
python ttrack.py --create-portfolio my_stocks "My Stock Portfolio"

# Add stocks with lots
python ttrack.py --add-lot my_stocks AAPL today 10 150.0
python ttrack.py --add-lot my_stocks MSFT 2024-01-15 5 300.0

# View portfolio
python ttrack.py -p my_stocks -b  # Beautiful bordered view
```

### Advanced Operations
```bash
# View all portfolios
python ttrack.py --all

# Get statistics
python ttrack.py --stats

# Export data
python ttrack.py --all -c export.csv
```

> **Advanced portfolio management?** See [Portfolio Format](docs/portfolio-format.md) and [Advanced Features](docs/advanced-features.md) for comprehensive usage.

## Key Commands

```bash
# Portfolio Management
python ttrack.py --create-portfolio|--delete-portfolio|--list

# Lot Management
python ttrack.py --add-lot|--remove-lot|--list-lots

# Viewing & Analysis
python ttrack.py -p|--all|--stats|--export
```

## Features

- **Deploy in Minutes** - 3-step setup process
- **Real-time Data** - Live stock and crypto prices via Yahoo Finance
- **Beautiful Displays** - Rich tables with borders or clean columnar layout
- **Portfolio Management** - Track multiple portfolios with YAML configuration
- **Comprehensive Analytics** - Detailed statistics, gains/losses, and performance metrics
- **Lot Tracking** - Track individual purchase lots with dates and cost basis
- **Tax Analysis** - Analyze lot aging and capital gains for tax optimization
- **Manual Price Overrides** - Override API prices for delisted or custom assets
- **Backup & Restore** - Automatic portfolio backups and restore functionality

## Documentation

- **[Complete Guide](docs/index.md)** - Full documentation index
- **[Dependencies](docs/dependencies.md)** - System requirements and setup
- **[Configuration](docs/configuration.md)** - Portfolio configuration and management
- **[Advanced Features](docs/advanced-features.md)** - Advanced usage and customization
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## Troubleshooting

### Common Issues

**"pip externally managed" Error**
```bash
# Solution: Use virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**No data from Yahoo Finance**
```bash
# Check internet connection and try again
# Some symbols may be delisted or unavailable
```

**Portfolio not found**
```bash
# List all portfolios
python ttrack.py --list

# Create new portfolio if needed
python ttrack.py --create-portfolio my_portfolio "My Portfolio"
```

> **Need more troubleshooting help?** See [Troubleshooting Guide](docs/troubleshooting.md) for detailed solutions and advanced configuration.

## Contributing

Issues and pull requests welcome! See our [GitHub repository](https://github.com/randyoyarzabal/tradetrack).

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**TradeTrack** - Track your investments with confidence