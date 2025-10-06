# Troubleshooting Guide

This guide helps you resolve common issues when using TradeTrack.

## Table of Contents

- [Common Issues](#common-issues)
- [Data and API Issues](#data-and-api-issues)
- [Performance Issues](#performance-issues)
- [Configuration Issues](#configuration-issues)
- [Getting Additional Help](#getting-additional-help)

## Common Issues

### Installation Problems

#### Python Not Found

**Error**: `python: command not found` or `python3: command not found`

**Solution**:

- **Windows**: Download Python from [python.org](https://www.python.org/downloads/) and ensure "Add Python to PATH" is checked
- **macOS**: Install via Homebrew: `brew install python3`
- **Linux**: Install via package manager: `sudo apt install python3` (Ubuntu/Debian) or `sudo yum install python3` (RHEL/CentOS)

#### Virtual Environment Issues

**Error**: `venv: command not found`

**Solution**:

```bash
# Ensure you're using the correct Python command for your OS
python -m venv .venv    # Windows
python3 -m venv .venv   # macOS/Linux
```

#### Permission Denied on Activation
**Error**: `Permission denied` when running activation script

**Solution**:
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
chmod +x .venv/bin/activate
source .venv/bin/activate
```

### Runtime Issues

#### Module Not Found
**Error**: `ModuleNotFoundError: No module named 'rich'`

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Yahoo Finance API Issues
**Error**: No data returned or connection timeouts

**Solutions**:
1. **Check internet connection**
2. **Try with `--live` flag**: `python ttrack.py -p portfolio --live`
3. **Verify symbol format**: Use correct Yahoo Finance symbols (e.g., `BTC-USD` not `BTC`)
4. **Check if market is open**: Some data may not be available outside market hours

#### Configuration File Issues
**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'conf/config.yaml'`

**Solution**:
```bash
# Ensure you're running from the project root directory
cd /path/to/tradetrack
python ttrack.py --help
```

#### Portfolio File Issues
**Error**: `YAML parsing errors` or `Invalid portfolio format`

**Solutions**:
1. **Check YAML syntax**: Ensure proper indentation and formatting
2. **Validate dates**: Use `YYYY-MM-DD` format or `today`
3. **Check numeric values**: Ensure shares and prices are numbers, not strings
4. **Use templates**: Copy from `/templates/portfolios/` as starting point

### Display Issues

#### Terminal Width Problems
**Issue**: Tables not displaying correctly

**Solution**:
```bash
# Set terminal width explicitly
python ttrack.py -p portfolio -t 120

# Or stretch to full width
python ttrack.py -p portfolio -t 0
```

#### Color Display Issues
**Issue**: Colors not showing or displaying incorrectly

**Solution**:
1. **Check terminal support**: Ensure your terminal supports ANSI colors
2. **Disable colors**: Set `colored_mode: false` in `conf/config.yaml`
3. **Use bordered mode**: `python ttrack.py -p portfolio -b`

#### Unicode/Character Issues
**Issue**: Special characters not displaying correctly

**Solution**:
1. **Set UTF-8 encoding**: `export LANG=en_US.UTF-8` (Linux/macOS)
2. **Use Windows Terminal**: For Windows, use Windows Terminal instead of Command Prompt
3. **Check font**: Ensure terminal font supports Unicode characters

### Performance Issues

#### Slow Data Fetching
**Issue**: Long delays when fetching stock data

**Solutions**:
1. **Use cached data**: Don't use `--live` flag unless necessary
2. **Reduce portfolio size**: Split large portfolios into smaller ones
3. **Check network**: Ensure stable internet connection
4. **Update dependencies**: `pip install --upgrade -r requirements.txt`

#### Memory Issues
**Issue**: High memory usage with large portfolios

**Solutions**:
1. **Split portfolios**: Break large portfolios into smaller ones
2. **Remove old lots**: Clean up historical data you don't need
3. **Check system resources**: Ensure adequate RAM available

## Getting Help

### Debug Mode
Enable debug mode for detailed error information:
```bash
python ttrack.py --debug -p portfolio
```

### Log Files
Check for log files in the project directory for detailed error information.

### System Information
When reporting issues, include:
- Operating system and version
- Python version: `python --version`
- TradeTrack version: `python ttrack.py --version`
- Error messages and stack traces
- Configuration file contents (remove sensitive data)

### Community Support
- **GitHub Issues**: [Create an issue](https://github.com/randyoyarzabal/stocks/issues)
- **Documentation**: Check this guide and other docs in `/docs/`
- **Examples**: Review files in `/templates/` directory

## Prevention Tips

1. **Keep dependencies updated**: Regularly run `pip install --upgrade -r requirements.txt`
2. **Backup portfolios**: Use `--backup-portfolio` command regularly
3. **Test configurations**: Validate YAML files before using them
4. **Use virtual environments**: Always use virtual environments to avoid conflicts
5. **Check system requirements**: Ensure Python 3.8+ and adequate system resources

---

**Still having issues?** Create a detailed issue on GitHub with the information above.
