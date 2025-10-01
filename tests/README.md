# TradeTrack Test Suite

This directory contains a focused test suite for the TradeTrack CLI application, designed to be practical and maintainable for a small project.

> **For development setup and contributing guidelines, see [docs/development.md](../docs/development.md)**

## 🧪 Test Structure

### Test Files

| File | Purpose | Coverage |
|------|---------|----------|
| `test_basic.py` | Core functionality tests | Main modules and basic operations |
| `test_config_loader.py` | Configuration loading | ConfigLoader class |
| `test_currency_formatter.py` | Currency formatting | CurrencyFormatter class |
| `test_portfolio_loader.py` | Portfolio data loading | PortfolioLoader class |
| `test_yahoo_quotes.py` | Yahoo Finance API | YahooQuotes class |
| `test_rich_display.py` | Rich terminal display | RichDisplay class |
| `test_portfolio_library.py` | Portfolio management | PortfolioLibrary class |
| `run_tests.py` | Test runner script | All test suites |

### Test Philosophy

This test suite follows a **practical approach** for a small CLI project:

- **Essential functionality only** - Tests core features that users depend on
- **Simple and maintainable** - Easy to understand and update
- **Fast execution** - Quick feedback during development
- **Focused coverage** - Tests what matters most, not everything

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
python tests/run_tests.py

# Run specific test file
pytest tests/test_basic.py -v

# Run with pytest directly
pytest tests/ -v
```

> **For complete development setup instructions, see [docs/development.md](../docs/development.md)**

## 📊 Test Data

### Test Portfolios

The test suite includes minimal test data:

- **`test_data/portfolios/`** - Sample portfolio files for testing
- **Fixtures** - Reusable test data in `conftest.py`

### Test Configuration

- **`conftest.py`** - pytest fixtures and configuration
- **`requirements.txt`** - Test dependencies

## 🔧 Test Features

### Python Best Practices

- **Fixtures**: Reusable test data and setup
- **Mocking**: Isolated testing with `unittest.mock`
- **Error Testing**: Basic error handling validation
- **Clear Assertions**: Obvious pass/fail criteria

### Test Coverage

- **Core Functions**: Essential functionality validation
- **Error Cases**: Basic error handling
- **Integration**: Key component interactions
- **Edge Cases**: Common boundary conditions

## 🛠️ Test Dependencies

Test dependencies are managed in `tests/requirements.txt`:

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Or use the automated setup
python tests/setup_tests.py
```

## 📋 Writing Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `TestClassName`
- Test methods: `test_should_do_something_when_condition`

### Example Test Structure

```python
def test_config_loader_init_default(self):
    """Test ConfigLoader initialization with default config path."""
    # Arrange
    loader = ConfigLoader()
    
    # Act
    config = loader.load_config()
    
    # Assert
    assert config is not None
    assert loader.config_path == Path('conf/config.yaml')
```

### Best Practices

- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Use fixtures for reusable test data
- Mock external dependencies
- Test both success and error cases
- Keep tests simple and focused

## 🎯 Test Categories

### Basic Tests (`test_basic.py`)

- Core module imports
- Basic functionality
- Syntax validation
- Main script execution

### Component Tests

- **ConfigLoader**: Configuration loading and validation
- **CurrencyFormatter**: Currency and percentage formatting
- **PortfolioLoader**: Portfolio data loading
- **YahooQuotes**: API integration
- **RichDisplay**: Terminal display
- **PortfolioLibrary**: Portfolio management

## 📈 Continuous Integration

The test suite is integrated with GitHub Actions for automated testing:

- **Multi-platform**: Linux, Windows, macOS
- **Multi-version**: Python 3.9, 3.10, 3.11, 3.12, 3.13
- **Focused**: Essential functionality only
- **Fast**: Quick execution for rapid feedback

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Test Failures**: Check test data and mock configurations
3. **Permission Errors**: Check file permissions for test data

### Debug Commands

```bash
# Run tests with debug output
pytest tests/ -v -s --tb=long

# Run specific test with debug
pytest tests/test_basic.py::TestBasic::test_config_loader_basic -v -s
```

## 📚 Learning Resources

### Python Testing

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Python Testing with pytest](https://pythontest.com/pytest/)

### Test Design Patterns

- **Arrange-Act-Assert**: Structure tests clearly
- **Test Doubles**: Mocks, stubs, and fakes
- **Data Builders**: Construct test data efficiently

## 🤝 Contributing

### Adding New Tests

1. Create test file following naming convention: `test_*.py`
2. Use descriptive test names: `test_should_do_something_when_condition`
3. Follow Arrange-Act-Assert pattern
4. Add appropriate fixtures and mocks
5. Include error cases
6. Keep tests simple and focused

### Test Quality Guidelines

- **Fast**: Tests should run quickly
- **Independent**: Tests shouldn't depend on each other
- **Repeatable**: Tests should produce consistent results
- **Self-validating**: Tests should have clear pass/fail criteria
- **Simple**: Keep tests easy to understand and maintain

## 📊 Metrics

### Current Coverage

- **Basic Tests**: Core functionality
- **Component Tests**: Individual modules
- **Integration Tests**: Key interactions
- **Error Tests**: Basic error handling

### Performance Benchmarks

- **Total Suite**: < 30 seconds
- **Individual Tests**: < 5 seconds each
- **Fast Feedback**: Quick development cycle

---

**Note**: This test suite is designed to be practical and maintainable for a small CLI project. It focuses on essential functionality rather than comprehensive coverage.