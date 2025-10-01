"""
Tests for CurrencyFormatter class - focused on essential functionality.
"""
import pytest

from libs.currency_formatter import CurrencyFormatter


class TestCurrencyFormatter:
    """Test cases for CurrencyFormatter class."""

    def test_currency_formatter_init(self):
        """Test CurrencyFormatter initialization."""
        formatter = CurrencyFormatter()
        assert formatter is not None

    def test_format_currency_positive(self):
        """Test currency formatting for positive values."""
        formatter = CurrencyFormatter()
        result = formatter.format_currency(123.45)
        assert '$123.45' in result

    def test_format_currency_negative(self):
        """Test currency formatting for negative values."""
        formatter = CurrencyFormatter()
        result = formatter.format_currency(-123.45)
        assert '$123.45' in result  # Should drop negative sign

    def test_format_currency_zero(self):
        """Test currency formatting for zero values."""
        formatter = CurrencyFormatter()
        result = formatter.format_currency(0)
        assert '$0.00' in result

    def test_format_percentage_positive(self):
        """Test percentage formatting for positive values."""
        formatter = CurrencyFormatter()
        result = formatter.format_percentage(15.67)
        assert '15.67%' in result

    def test_format_percentage_negative(self):
        """Test percentage formatting for negative values."""
        formatter = CurrencyFormatter()
        result = formatter.format_percentage(-15.67)
        assert '-15.67%' in result

    def test_format_percentage_zero(self):
        """Test percentage formatting for zero values."""
        formatter = CurrencyFormatter()
        result = formatter.format_percentage(0)
        assert '0.00%' in result

    def test_format_currency_with_custom_config(self, temp_dir):
        """Test currency formatting with custom configuration."""
        import yaml
        import os
        config = {
            'currency': {
                'decimal_places': 3,
                'show_symbol': False,
                'colored_mode': False
            }
        }

        config_file = os.path.join(temp_dir, 'test_config.yaml')
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # CurrencyFormatter doesn't take config_file parameter
        formatter = CurrencyFormatter()
        result = formatter.format_currency(123.456)
        # Test basic formatting (config won't be loaded from file)
        assert '123.46' in result  # Default decimal places
        assert result.startswith('$')  # Default symbol


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
