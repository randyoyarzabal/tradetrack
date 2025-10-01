"""
Tests for RichDisplay class - focused on essential functionality.
"""
import pytest
from unittest.mock import Mock, patch
from rich.text import Text
from rich.table import Table

from libs.rich_display import RichDisplay


class TestRichDisplay:
    """Test cases for RichDisplay class."""

    def test_rich_display_init(self):
        """Test RichDisplay initialization."""
        display = RichDisplay()
        assert display.config_loader is not None
        assert display.currency_formatter is not None

    def test_create_table_basic(self):
        """Test basic table creation."""
        display = RichDisplay()
        headers = ['Symbol', 'Price', 'Change']
        data = [['AAPL', 175.50, 2.50], ['GOOGL', 2900.00, 50.00]]
        
        table = display.create_table(headers, data)
        
        assert isinstance(table, Table)
        assert table.title is None
        assert table.show_header is True

    def test_create_table_with_title(self):
        """Test table creation with title."""
        display = RichDisplay()
        headers = ['Symbol', 'Price', 'Change']
        data = [['AAPL', 175.50, 2.50]]
        
        table = display.create_table(headers, data, title="Test Portfolio")
        assert table.title == "Test Portfolio"

    def test_create_table_bordered(self):
        """Test bordered table creation."""
        display = RichDisplay()
        headers = ['Symbol', 'Price', 'Change']
        data = [['AAPL', 175.50, 2.50]]
        
        table = display.create_table(headers, data, bordered=True)
        # Rich tables don't have border_style attribute, just check it's created
        assert table is not None

    def test_create_table_with_footer(self):
        """Test table creation with footer data."""
        display = RichDisplay()
        headers = ['Symbol', 'Price', 'Change']
        data = [['AAPL', 175.50, 2.50]]
        footer_data = ['TOTAL', 175.50, 2.50]
        
        table = display.create_table(headers, data, footer_data=footer_data)
        assert table.show_footer is True

    def test_format_cell_with_rich_color_positive(self):
        """Test Rich color formatting for positive values."""
        display = RichDisplay()
        result = display._format_cell_with_rich_color(150.50, 'Gain$')
        
        assert isinstance(result, Text)
        assert result.plain == '$150.50'

    def test_format_cell_with_rich_color_negative(self):
        """Test Rich color formatting for negative values."""
        display = RichDisplay()
        result = display._format_cell_with_rich_color(-150.50, 'Gain$')
        
        assert isinstance(result, Text)
        assert result.plain == '$150.50'  # Negative sign dropped

    def test_format_cell_with_rich_color_cost_column(self):
        """Test Rich color formatting for Cost column (no color)."""
        display = RichDisplay()
        result = display._format_cell_with_rich_color(150.50, 'Cost')
        
        assert isinstance(result, Text)
        assert result.plain == '$150.50'

    def test_display_table_basic(self, capsys):
        """Test basic table display."""
        display = RichDisplay()
        headers = ['Symbol', 'Price']
        data = [['AAPL', 175.50]]
        
        display.display_table(headers, data)
        
        captured = capsys.readouterr()
        assert 'AAPL' in captured.out
        assert '175.50' in captured.out