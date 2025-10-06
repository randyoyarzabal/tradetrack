# Development Guide

This document provides comprehensive information for developers working on TradeTrack.

## Table of Contents

- [Getting Started for Developers](#getting-started-for-developers)
- [Project Structure](#project-structure)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Building and Distribution](#building-and-distribution)
- [Contributing Guidelines](#contributing-guidelines)

## Getting Started for Developers

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment (recommended)

### Development Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/randyoyarzabal/stocks.git
   cd stocks
   ```

2. **Set up development environment:**

   ```bash
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r tests/requirements.txt
   ```

3. **Verify development setup:**

   ```bash
   # Run the automated test setup
   python tests/setup_tests.py
   
   # Run basic tests
   python tests/run_tests.py --syntax
   ```

## 🧪 Testing

### Test Structure

The test suite is located in the `tests/` directory and follows a **practical approach** for a small CLI project:

```
tests/
├── __init__.py
├── conftest.py
├── requirements.txt          # Test dependencies
├── setup_tests.py           # Automated test setup
├── run_tests.py             # Test runner script
├── README.md                # Test documentation
├── test_basic.py            # Core functionality tests
├── test_config_loader.py    # Configuration tests
├── test_currency_formatter.py
├── test_portfolio_loader.py
├── test_yahoo_quotes.py
├── test_rich_display.py
└── test_portfolio_library.py
```

### Test Philosophy

This test suite follows a **focused approach**:

- **Essential functionality only** - Tests core features that users depend on
- **Simple and maintainable** - Easy to understand and update
- **Fast execution** - Quick feedback during development
- **Practical coverage** - Tests what matters most, not everything

### Running Tests

#### Quick Test Commands

```bash
# Run all tests

python tests/run_tests.py

# Run specific test categories

python tests/run_tests.py --basic
python tests/run_tests.py --component

# Run tests with pattern matching

python tests/run_tests.py --pattern "test_config"

# Enable debug mode for detailed error output

python tests/run_tests.py --debug
python tests/run_tests.py --component --debug

# Run with pytest directly

pytest tests/ -v
pytest tests/test_config_loader.py -v
```

#### Test Categories

- **Basic Tests**: Core functionality and imports
- **Component Tests**: Individual module testing

#### Debug Mode

The test runner includes a debug mode that provides detailed error information when tests fail. This is particularly useful during development and troubleshooting.

**Usage:**
```bash
# Enable debug mode for all tests
python tests/run_tests.py --debug

# Enable debug mode for specific test categories
python tests/run_tests.py --basic --debug
python tests/run_tests.py --component --debug

# Enable debug mode for pattern matching
python tests/run_tests.py --pattern "test_config" --debug
```

**Debug Output Includes:**
- Return code from failed test commands
- Execution duration
- Complete STDOUT output (test results)
- Complete STDERR output (error messages)
- Clear visual separation between debug sections

**When to Use Debug Mode:**
- When tests are failing and you need to see detailed error information
- During development to understand test behavior
- When troubleshooting CI/CD issues
- When investigating test performance problems

### Test Dependencies

Test dependencies are managed in `tests/requirements.txt`:

```bash
# Install test dependencies

pip install -r tests/requirements.txt

# Or use the automated setup

python tests/setup_tests.py
```

### Writing Tests

#### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `TestClassName`
- Test methods: `test_should_do_something_when_condition`

#### Example Test Structure

```python
def test_config_loader_init_default(self):
    """✓ Test ConfigLoader initialization with default config path."""
    # Arrange
    loader = ConfigLoader()
    
    # Act
    config = loader.load_config()
    
    # Assert
    assert config is not None
    assert loader.config_path == Path('conf/config.yaml')
```

#### Best Practices

- Use descriptive test names with ✓ checkmarks
- Follow Arrange-Act-Assert pattern
- Use fixtures for reusable test data
- Mock external dependencies
- Test both success and error cases
- Include edge cases and boundary conditions

## Development Tools

### Code Quality

#### Formatting

```bash
# Format code with Black

black libs/ tests/

# Sort imports with isort

isort libs/ tests/
```

#### Linting

```bash
# Run flake8 linting

flake8 libs/ tests/

# Run type checking with mypy

mypy libs/ --ignore-missing-imports
```

#### Security Scanning

```bash
# Run security linting

bandit -r libs/

# Check for vulnerable dependencies

safety check
```

### Continuous Integration

The project uses GitHub Actions for automated testing:

- **Multi-platform**: Linux, Windows, macOS
- **Multi-version**: Python 3.9, 3.10, 3.11, 3.12, 3.13
- **Comprehensive**: All test categories
- **Scheduled**: Daily runs at 2 AM UTC

See `.github/workflows/test.yml` for CI configuration.

## 📁 Project Structure

```
tradetrack/
├── libs/                    # Core application modules
│   ├── config_loader.py     # Configuration management
│   ├── currency_formatter.py
│   ├── portfolio_library.py
│   ├── portfolio_loader.py
│   ├── rich_display.py
│   ├── tax_analysis.py
│   ├── yahoo_quotes.py
│   └── lot_analysis.py
├── conf/                    # Configuration files
│   ├── config.yaml         # Default configuration
│   └── version.py          # Version information
├── docs/                   # Documentation
│   ├── configuration.md
│   ├── dependencies.md
│   └── development.md      # This file
├── tests/                  # Test suite
├── templates/              # Template files
├── ttrack.py              # Main application entry point
├── requirements.txt        # Production dependencies
└── README.md              # User documentation
```

## 🐛 Debugging

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Test Failures**: Check test data and mock configurations
3. **Performance Issues**: Use profiling tools to identify bottlenecks
4. **Memory Leaks**: Monitor memory usage in long-running tests

### Debug Commands

```bash
# Run tests with debug output

pytest tests/ -v -s --tb=long

# Run specific test with debug

pytest tests/test_config_loader.py::TestConfigLoader::test_config_loader_init_default -v -s

# Profile test performance

pytest tests/ --profile
```

## 📊 Performance Testing

### Memory Testing

```bash
# Run memory tests

python tests/run_tests.py --memory

# Monitor memory usage

python -m memory_profiler tests/test_runtime.py
```

### Performance Benchmarks

```bash
# Run performance tests

python tests/run_tests.py --performance

# Benchmark specific functions

pytest tests/ -k "performance" --benchmark-only
```

## 🔄 Contributing

### Development Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make changes and test:**
   ```bash
   # Run tests
   python tests/run_tests.py
   
   # Check code quality
   black libs/ tests/
   flake8 libs/ tests/
   ```

3. **Commit changes:**
   ```bash
   git add .
   git commit -m "Add new feature with tests"
   ```

4. **Push and create PR:**
   ```bash
   git push origin feature/new-feature
   ```

### Code Review Checklist

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact is acceptable

## 📚 Learning Resources

### Python Testing

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Python Testing with pytest](https://pythontest.com/pytest/)
- [Effective Python Testing](https://realpython.com/python-testing/)

### Development Tools

- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linting](https://flake8.pycqa.org/)
- [MyPy Type Checking](https://mypy.readthedocs.io/)
- [Bandit Security Linting](https://bandit.readthedocs.io/)

## 🆘 Getting Help

### Internal Resources

- Check `tests/README.md` for detailed test documentation
- Review existing tests for examples
- Check CI logs for test failures

### External Resources

- Python documentation
- pytest documentation
- Rich library documentation
- Yahoo Finance API documentation

---

**Note**: This development guide is maintained alongside the codebase. Please update it when adding new features or changing the development process.
