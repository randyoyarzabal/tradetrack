# Dependencies and Requirements

This document provides detailed information about TradeTrack's dependencies and requirements.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, Linux
- **Terminal**: Any terminal emulator (PuTTY, Windows Terminal, macOS Terminal, etc.)

## Core Dependencies

### Rich (>=14.1.0)

**Purpose**: Beautiful terminal displays and tables
- Provides bordered tables with `-b` flag
- Handles text coloring and formatting
- Creates professional-looking terminal output
- **Why**: Essential for the Rich display mode and enhanced user experience

### yfinance (>=0.2.66)

**Purpose**: Real-time stock and cryptocurrency data
- Fetches live prices from Yahoo Finance
- Handles both stocks and crypto symbols
- Provides company descriptions and metadata
- **Why**: Free, reliable source of financial data

### PyYAML (>=6.0)

**Purpose**: Configuration and portfolio file parsing
- Reads `config.yaml` configuration file
- Parses portfolio YAML files
- Handles complex data structures
- **Why**: Human-readable configuration format

### pandas (>=2.3.0)

**Purpose**: Data manipulation and analysis
- Processes portfolio data into DataFrames
- Handles calculations and aggregations
- Manages sorting and filtering
- **Why**: Powerful data analysis capabilities

### termcolor (>=3.1.0)

**Purpose**: Terminal text coloring for columnar display
- Colors positive/negative values
- Highlights important information
- Works across different terminals
- **Why**: Visual feedback in columnar mode

### python-dotenv (>=1.1.0)

**Purpose**: Environment variable management
- Loads configuration from `.env` files
- Manages sensitive data like API keys
- Provides fallback configuration
- **Why**: Secure configuration management

### requests (>=2.32.0)

**Purpose**: HTTP requests (used by yfinance)
- Handles API communication
- Manages timeouts and retries
- **Why**: Required by yfinance for data fetching

### numpy (>=2.3.0)

**Purpose**: Numerical computing
- Required by pandas for data operations
- Handles mathematical calculations
- **Why**: Core dependency of pandas

### columnar (>=1.4.0)

**Purpose**: Columnar table display
- Creates clean, borderless tables
- Handles text wrapping and alignment
- Provides alternative to Rich display
- **Why**: Lightweight table display option

## Installation

### Basic Installation

```bash
pip install -r requirements.txt
```

### Development Installation

```bash
# Install core dependencies

pip install -r requirements.txt

# Install development dependencies

pip install pytest black flake8 mypy
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment

python3 -m venv .venv

# Activate virtual environment

source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt
```

## Version Compatibility

### Python Version Support

- **Python 3.8**: Minimum supported version
- **Python 3.9+**: Recommended for best performance
- **Python 3.11+**: Latest features and optimizations

### Package Version Ranges

All packages use `>=` version constraints to ensure compatibility:
- Allows patch and minor version updates
- Prevents breaking changes from major version updates
- Ensures security updates are included

## Optional Dependencies

### Development Tools

```bash
# Testing

pytest>=7.0.0

# Code formatting

black>=23.0.0

# Linting

flake8>=6.0.0

# Type checking

mypy>=1.0.0
```

### Enhanced Functionality

- **matplotlib**: For future charting features
- **plotly**: For interactive visualizations
- **jupyter**: For notebook-based analysis

## Troubleshooting Dependencies

### Common Issues

1. **yfinance errors**
   - Update to latest version: `pip install --upgrade yfinance`
   - Check internet connection
   - Verify symbol format (e.g., "AAPL", "BTC-USD")

2. **Rich display issues**
   - Update Rich: `pip install --upgrade rich`
   - Check terminal compatibility
   - Try columnar mode: `python ttrack.py -p crypto` (without `-b`)

3. **Pandas warnings**
   - Update pandas: `pip install --upgrade pandas`
   - Check data types in portfolio files

4. **YAML parsing errors**
   - Validate YAML syntax in config and portfolio files
   - Check indentation (use spaces, not tabs)
   - Verify file encoding (UTF-8)

### Platform-Specific Issues

#### Windows

- Use Windows Terminal or PowerShell for best experience
- PuTTY works but may have limited Unicode support
- Consider using WSL for Linux-like experience

#### macOS

- Terminal.app works well
- iTerm2 provides enhanced features
- Homebrew Python recommended

#### Linux

- Most terminals work well
- Ensure UTF-8 locale is set
- Install system dependencies if needed

## Security Considerations

### API Keys

- Never commit API keys to version control
- Use environment variables for sensitive data
- Consider using `.env` files (excluded from git)

### Data Privacy

- Portfolio data is stored locally
- No data is sent to external servers (except Yahoo Finance)
- Cache files contain only public market data

### Package Security

- Regularly update dependencies: `pip install --upgrade -r requirements.txt`
- Use `pip-audit` to check for vulnerabilities
- Consider using `pip-tools` for dependency management

## Performance Considerations

### Memory Usage

- pandas DataFrames are memory-efficient
- Large portfolios may require more RAM
- Consider chunking for very large datasets

### Network Usage

- yfinance caches data locally
- Live data fetches are minimal
- Offline mode available with cached data

### CPU Usage

- Calculations are optimized with pandas/numpy
- Rich rendering is efficient
- Consider terminal size for large tables

## Updating Dependencies

### Check for Updates

```bash
pip list --outdated
```

### Update All Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Update Specific Package

```bash
pip install --upgrade package_name
```

### Pin Versions (Production)

For production deployments, consider pinning exact versions:
```txt
rich==14.1.0
yfinance==0.2.66
pandas==2.3.3
```

## Contributing

When adding new dependencies:

1. Add to `requirements.txt` with appropriate version constraint
2. Update this documentation
3. Test on multiple Python versions
4. Consider security implications
5. Document the purpose and usage
