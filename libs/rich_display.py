"""
Rich table display utilities for the Stock Portfolio Tracker.
Provides modern table display with borders and columnar options.
"""

from typing import List, Dict, Any, Optional, Union
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from columnar import columnar
from .config_loader import get_config_loader
from .currency_formatter import get_currency_formatter


class RichDisplay:
    """Handles Rich-based table display with configuration support."""

    def __init__(self):
        """Initialize the Rich display with configuration."""
        self.config_loader = get_config_loader()
        self.table_config = self.config_loader.get_table_config()
        self.currency_formatter = get_currency_formatter()
        self.console = Console()

    def create_table(
        self,
        headers: List[str],
        data: List[List[Any]],
        bordered: bool = False,
        title: Optional[str] = None
    ) -> Table:
        """
        Create a Rich table with the specified configuration.

        Args:
            headers: List of column headers
            data: List of rows, each row is a list of values
            bordered: Whether to show borders
            title: Optional table title

        Returns:
            Rich Table object
        """
        # Create table
        table = Table(title=title, show_header=True,
                      header_style=self.table_config['header_style'],
                      expand=True)

        # Configure borders
        if bordered:
            border_style = self.table_config['bordered_style']
            if border_style == "light":
                table.box = box.ROUNDED
            elif border_style == "heavy":
                table.box = box.HEAVY
            elif border_style == "double":
                table.box = box.DOUBLE
            else:
                table.box = box.ROUNDED
        else:
            table.box = box.MINIMAL

        # Add columns with colored headers
        for header in headers:
            # Determine alignment based on content type
            justify = self._get_column_alignment(header, data)

            # Color the headers
            if header.upper() in ['SYMBOL', 'TICKER']:
                header_text = Text(header, style="bold bright_cyan")
            elif header.upper() in ['PORTFOLIO', 'NAME']:
                header_text = Text(header, style="bold bright_magenta")
            elif header.upper() in ['DESCRIPTION', 'DESC']:
                header_text = Text(header, style="bold bright_blue")
            elif header.upper() in ['QTY', 'QUANTITY', 'SHARES']:
                header_text = Text(header, style="bold bright_yellow")
            elif header.upper() in ['PRICE', 'COST', 'VALUE', 'GAIN$', 'AVE$', 'DAY$']:
                header_text = Text(header, style="bold bright_green")
            elif header.upper() in ['GAIN%', 'PERCENTAGE']:
                header_text = Text(header, style="bold bright_red")
            else:
                header_text = Text(header, style="bold white")

            table.add_column(header_text, justify=justify)

        # Add rows
        for row in data:
            # Convert row data to Rich Text objects for proper coloring
            formatted_row = []
            for i, cell in enumerate(row):
                header = headers[i] if i < len(headers) else ""

                if isinstance(cell, (int, float)):
                    # Special handling for VALUE column - color based on Gain$
                    # Ensure we have Gain$ column
                    if header == 'Value' and len(row) > 7:
                        gain_dollars = row[7]  # Gain$ is typically at index 7
                        formatted_cell = self._format_value_with_rich_gain_color(
                            cell, gain_dollars)
                    else:
                        # Use Rich colors for numeric cells
                        formatted_cell = self._format_cell_with_rich_color(
                            cell, header)
                else:
                    # Color text cells based on column type
                    cell_str = str(cell) if cell is not None else ""
                    if header.upper() in ['SYMBOL', 'TICKER']:
                        formatted_cell = Text(
                            cell_str, style="bright_cyan bold")
                    elif header.upper() in ['PORTFOLIO', 'NAME']:
                        formatted_cell = Text(cell_str, style="bright_magenta")
                    elif header.upper() in ['DESCRIPTION', 'DESC']:
                        formatted_cell = Text(cell_str, style="bright_blue")
                    else:
                        formatted_cell = Text(cell_str, style="white")

                formatted_row.append(formatted_cell)

            table.add_row(*formatted_row)

        return table

    def _get_column_alignment(self, header: str, data: List[List[Any]]) -> str:
        """
        Determine column alignment based on header and data.

        Args:
            header: Column header
            data: Table data

        Returns:
            Alignment string: "left", "right", or "center"
        """
        # Default alignment from config
        default_alignment = self.table_config['number_alignment']

        # Check if this is a numeric column
        numeric_headers = ['Qty', 'Price', 'Cost',
                           'Gain$', 'Value', 'Gain%', 'Ave$', 'Day$']
        if any(numeric in header for numeric in numeric_headers):
            return default_alignment

        # Check if data in this column is mostly numeric
        if data:
            col_index = 0  # This would need to be determined based on header position
            numeric_count = 0
            total_count = 0

            for row in data:
                if col_index < len(row):
                    cell = row[col_index]
                    if isinstance(cell, (int, float)):
                        numeric_count += 1
                    total_count += 1

            if total_count > 0 and numeric_count / total_count > 0.5:
                return default_alignment

        return "left"

    def _format_value_with_rich_gain_color(self, value: Union[int, float], gain_dollars: Union[int, float]) -> Text:
        """
        Format VALUE column with Rich color based on Gain$ value.

        Args:
            value: The VALUE amount
            gain_dollars: The Gain$ amount to determine color

        Returns:
            Rich Text object with appropriate color
        """
        # Format the value as currency
        formatted_text = self.currency_formatter.format_currency(
            value,
            rich_mode=True,
            colored_mode=False  # We'll handle coloring manually
        )

        # Create Rich Text with colors based on gain/loss
        text = Text(formatted_text)
        if gain_dollars > 0:
            text.stylize("green")
        elif gain_dollars < 0:
            text.stylize("red")
        # If gain_dollars == 0, use default color

        return text

    def _format_cell_with_rich_color(self, value: Union[int, float], column_type: str) -> Text:
        """
        Format a cell with Rich colors based on value and column type.

        Args:
            value: The numeric value to format
            column_type: Type of column (e.g., 'Gain$', 'Gain%', 'Value')

        Returns:
            Rich Text object with appropriate colors
        """
        # For Rich display, use colored_mode from config
        # If colored_mode is true, use colors and drop negative sign
        # If colored_mode is false, use parentheses for negative values
        currency_config = self.config_loader.get_currency_config()
        use_colors = currency_config['colored_mode']
        is_gain_loss_column = column_type in ['Gain$', 'Gain%', 'Value']
        drop_negative_sign = use_colors  # Drop negative sign when using colors

        # Format the value using currency formatter
        if 'Gain%' in column_type or '%' in column_type:
            formatted_text = self.currency_formatter.format_percentage(
                value,
                rich_mode=True,
                colored_mode=False,  # Rich handles its own coloring
                drop_negative_sign=drop_negative_sign
            )
        elif column_type in ['Cost', 'Gain$', 'Value', 'Ave$', 'Day$', 'Price']:
            formatted_text = self.currency_formatter.format_currency(
                value,
                rich_mode=True,
                colored_mode=False,  # Rich handles its own coloring
                drop_negative_sign=drop_negative_sign
            )
        else:
            formatted_text = self.currency_formatter.format_number(
                value, rich_mode=True)

        # Create Rich Text with colors
        text = Text(formatted_text)

        # Apply colors based on value and column type
        if use_colors:
            # Use Rich colors when colored_mode is enabled
            if value < 0:
                text.stylize("red")
            elif value > 0 and is_gain_loss_column:
                text.stylize("green")
        else:
            # No colors when colored_mode is disabled
            pass

        return text

    def display_columnar_table(
        self,
        headers: List[str],
        data: List[List[Any]],
        title: Optional[str] = None,
        width: Optional[int] = None
    ):
        """
        Display a table using columnar (non-Rich) with termcolor formatting.

        Args:
            headers: List of column headers
            data: List of rows
            title: Optional table title
            width: Terminal width override
        """
        # Format data with termcolor for columnar display
        formatted_data = []
        for row in data:
            formatted_row = []
            for i, cell in enumerate(row):
                if isinstance(cell, (int, float)):
                    # Use termcolor formatting for numeric cells
                    header = headers[i] if i < len(headers) else ""

                    # Special handling for VALUE column - color based on Gain$
                    # Ensure we have Gain$ column
                    if header == 'Value' and len(row) > 8:
                        # Gain$ is now at index 8 (after adding Portfolio column)
                        gain_dollars = row[8]
                        formatted_cell = self._format_value_with_gain_color(
                            cell, gain_dollars)
                    else:
                        formatted_cell = self._format_cell_with_termcolor(
                            cell, header)
                else:
                    # Plain text for non-numeric cells
                    formatted_cell = str(cell) if cell is not None else ""

                    # Colorize symbols (second column) in cyan to match rich display
                    # Symbol is now at index 1 (Portfolio is at index 0)
                    if i == 1 and cell:
                        from termcolor import colored
                        formatted_cell = colored(
                            str(cell), 'cyan', force_color=True)

                formatted_row.append(formatted_cell)
            formatted_data.append(formatted_row)

        # Display using columnar
        if title:
            print(title)

        # Determine terminal width based on stretch setting
        if width:
            # Use provided width (explicit override)
            terminal_width = width
        elif self.config_loader.should_stretch_to_terminal():
            # Stretch to full terminal width - ignore terminal_width setting
            terminal_width = self.console.width
        else:
            # Use configured terminal width (don't stretch)
            terminal_width = self.config_loader.get_terminal_width()

        table = columnar(
            formatted_data,
            headers=headers,
            no_borders=True,
            terminal_width=terminal_width
        )
        # Strip trailing spaces from each line
        lines = table.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        print('\n'.join(cleaned_lines))

    def _format_value_with_gain_color(self, value: Union[int, float], gain_dollars: Union[int, float]) -> str:
        """
        Format VALUE column with color based on Gain$ value.

        Args:
            value: The VALUE amount
            gain_dollars: The Gain$ amount to determine color

        Returns:
            Formatted string with termcolor
        """
        from termcolor import colored

        # Format the value as currency
        formatted_value = self.currency_formatter.format_currency(
            value,
            rich_mode=False,
            colored_mode=False  # We'll handle coloring manually
        )

        # Color based on gain/loss
        if gain_dollars > 0:
            return colored(formatted_value, 'green', force_color=True)
        elif gain_dollars < 0:
            return colored(formatted_value, 'red', force_color=True)
        else:
            return formatted_value

    def _format_cell_with_termcolor(self, value: Union[int, float], column_type: str) -> str:
        """
        Format a cell with termcolor for columnar display.

        Args:
            value: The numeric value to format
            column_type: Type of column (e.g., 'Gain$', 'Gain%', 'Value')

        Returns:
            Formatted string with termcolor
        """
        # Only apply gain/loss coloring to specific columns
        is_gain_loss_column = column_type in ['Gain$', 'Gain%', 'Value']

        # For columnar display, use colored_mode from config
        # If colored_mode is false, use parentheses for negative values
        # If colored_mode is true, drop negative sign and use color
        currency_config = self.config_loader.get_currency_config()
        use_colors = currency_config['colored_mode']
        drop_negative_sign = use_colors  # Drop negative sign when using colors

        # Format the value using currency formatter
        if 'Gain%' in column_type or '%' in column_type:
            formatted_text = self.currency_formatter.format_percentage(
                value,
                rich_mode=False,
                colored_mode=False,  # Don't use formatter colors, apply our own
                drop_negative_sign=drop_negative_sign
            )
        elif column_type in ['Cost', 'Gain$', 'Value', 'Ave$', 'Day$', 'Price']:
            formatted_text = self.currency_formatter.format_currency(
                value,
                rich_mode=False,
                colored_mode=False,  # Don't use formatter colors, apply our own
                drop_negative_sign=drop_negative_sign
            )
        else:
            formatted_text = self.currency_formatter.format_number(
                value, rich_mode=False)

        # Apply colors if enabled and this is a gain/loss column
        if use_colors and is_gain_loss_column:
            from termcolor import colored
            if value < 0:
                return colored(formatted_text, 'red', force_color=True)
            elif value > 0:
                return colored(formatted_text, 'green', force_color=True)

        return formatted_text

    def _format_numeric_cell(self, value: Union[int, float], header: str) -> str:
        """
        Format a numeric cell based on its type and header.

        Args:
            value: Numeric value to format
            header: Column header to determine formatting

        Returns:
            Formatted string
        """
        if isinstance(value, float):
            if 'Gain%' in header or 'Gain' in header and '%' in header:
                return f"{value:.2f}%"
            elif 'Qty' in header and value.is_integer():
                return f"{int(value):,}"
            else:
                return f"{value:,.2f}"
        else:
            return f"{value:,}"

    def display_table(
        self,
        headers: List[str],
        data: List[List[Any]],
        bordered: bool = False,
        title: Optional[str] = None,
        width: Optional[int] = None
    ):
        """
        Display a table using Rich.

        Args:
            headers: List of column headers
            data: List of rows
            bordered: Whether to show borders
            title: Optional table title
            width: Terminal width override
        """
        table = self.create_table(headers, data, bordered, title)

        # Determine console width based on stretch setting
        if width:
            # Use provided width (explicit override)
            console = Console(width=width)
            console.print(table)
        elif self.config_loader.should_stretch_to_terminal():
            # Stretch to full terminal width - ignore terminal_width setting
            self.console.print(table)
        else:
            # Use configured terminal width (don't stretch)
            configured_width = self.config_loader.get_terminal_width()
            console = Console(width=configured_width)
            console.print(table)

    def display_portfolio_table(
        self,
        portfolio_name: str,
        headers: List[str],
        data: List[List[Any]],
        bordered: bool = False,
        show_totals: bool = True,
        width: Optional[int] = None,
        title: Optional[str] = None
    ):
        """
        Display a portfolio table with proper formatting.

        Args:
            portfolio_name: Name of the portfolio
            headers: List of column headers
            data: List of rows
            bordered: Whether to show borders
            show_totals: Whether to show totals row
            width: Terminal width override
            title: Optional custom title (if not provided, uses default)
        """
        # Use provided title or create default
        if title is None:
            title = f"Portfolio: {portfolio_name}"

        # Display the table
        self.display_table(headers, data, bordered, title, width)

    def display_stats_table(
        self,
        stats_type: str,
        headers: List[str],
        data: List[List[Any]],
        bordered: bool = False,
        width: Optional[int] = None
    ):
        """
        Display a statistics table.

        Args:
            stats_type: Type of statistics (e.g., "Totals", "Averages")
            headers: List of column headers
            data: List of rows
            bordered: Whether to show borders
            width: Terminal width override
        """
        title = f"{stats_type} Statistics"
        self.display_table(headers, data, bordered, title, width)

    def display_minmax_table(
        self,
        headers: List[str],
        data: List[List[Any]],
        bordered: bool = False,
        width: Optional[int] = None
    ):
        """
        Display a min/max statistics table.

        Args:
            headers: List of column headers
            data: List of rows
            bordered: Whether to show borders
            width: Terminal width override
        """
        title = "Min/Max Statistics"
        self.display_table(headers, data, bordered, title, width)


# Global Rich display instance
_rich_display: Optional[RichDisplay] = None


def get_rich_display() -> RichDisplay:
    """Get the global Rich display instance."""
    global _rich_display
    if _rich_display is None:
        _rich_display = RichDisplay()
    return _rich_display


def display_table(headers: List[str], data: List[List[Any]], **kwargs):
    """Display a table using the global Rich display instance."""
    get_rich_display().display_table(headers, data, **kwargs)


def display_portfolio_table(portfolio_name: str, headers: List[str], data: List[List[Any]], **kwargs):
    """Display a portfolio table using the global Rich display instance."""
    get_rich_display().display_portfolio_table(
        portfolio_name, headers, data, **kwargs)


def display_stats_table(stats_type: str, headers: List[str], data: List[List[Any]], **kwargs):
    """Display a statistics table using the global Rich display instance."""
    get_rich_display().display_stats_table(stats_type, headers, data, **kwargs)


def display_minmax_table(headers: List[str], data: List[List[Any]], **kwargs):
    """Display a min/max table using the global Rich display instance."""
    get_rich_display().display_minmax_table(headers, data, **kwargs)
