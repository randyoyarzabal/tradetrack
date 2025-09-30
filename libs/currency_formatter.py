"""
Currency formatting utilities for the Stock Portfolio Tracker.
Provides configurable currency formatting with color support for both Rich and terminal display.
"""

from typing import Union, Optional
from termcolor import colored
from .config_loader import get_config_loader


class CurrencyFormatter:
    """Handles currency formatting with configuration support."""

    def __init__(self):
        """Initialize the currency formatter with configuration."""
        self.config_loader = get_config_loader()
        self.currency_config = self.config_loader.get_currency_config()

    def format_currency(
        self,
        value: Union[float, int],
        show_symbol: Optional[bool] = None,
        decimal_places: Optional[int] = None,
        colored_mode: Optional[bool] = None,
        negative_format: Optional[str] = None,
        rich_mode: bool = False,
        drop_negative_sign: bool = False
    ) -> str:
        """
        Format a currency value according to configuration.

        Args:
            value: The numeric value to format
            show_symbol: Override symbol display (uses config if None)
            decimal_places: Override decimal places (uses config if None)
            colored_mode: Override color mode (uses config if None)
            negative_format: Override negative format (uses config if None)
            rich_mode: If True, returns plain text for Rich formatting
            drop_negative_sign: If True, removes negative sign and uses color instead

        Returns:
            Formatted currency string
        """
        # Use provided values or fall back to config
        show_symbol = show_symbol if show_symbol is not None else self.currency_config[
            'show_symbol']
        decimal_places = decimal_places if decimal_places is not None else self.currency_config[
            'decimal_places']
        colored_mode = colored_mode if colored_mode is not None else self.currency_config[
            'colored_mode']
        negative_format = negative_format if negative_format is not None else self.currency_config[
            'negative_format']

        # Format the number
        if decimal_places == 0:
            formatted_value = f"{int(round(value)):,}"
        else:
            formatted_value = f"{value:,.{decimal_places}f}"

        # Handle negative values
        is_negative = value < 0
        if is_negative:
            if drop_negative_sign:
                # Remove the negative sign - will be indicated by color instead
                formatted_value = formatted_value[1:]  # Remove minus sign
            elif negative_format == "parentheses":
                # Remove minus sign and add parentheses
                formatted_value = f"({formatted_value[1:]})"
            # If negative_format is "minus", keep the minus sign (default behavior)

        # Add currency symbol
        if show_symbol:
            formatted_value = f"${formatted_value}"

        # Apply colors if enabled and not in Rich mode
        if colored_mode and not rich_mode and is_negative:
            formatted_value = colored(formatted_value, 'red')
        elif colored_mode and not rich_mode and value > 0:
            formatted_value = colored(formatted_value, 'green')

        return formatted_value

    def format_percentage(
        self,
        value: Union[float, int],
        decimal_places: Optional[int] = None,
        colored_mode: Optional[bool] = None,
        rich_mode: bool = False,
        drop_negative_sign: bool = False
    ) -> str:
        """
        Format a percentage value.

        Args:
            value: The percentage value to format
            decimal_places: Override decimal places (uses config if None)
            colored_mode: Override color mode (uses config if None)
            rich_mode: If True, returns plain text for Rich formatting
            drop_negative_sign: If True, removes negative sign and uses color instead

        Returns:
            Formatted percentage string
        """
        decimal_places = decimal_places if decimal_places is not None else self.currency_config[
            'decimal_places']
        colored_mode = colored_mode if colored_mode is not None else self.currency_config[
            'colored_mode']

        # Format the percentage
        if decimal_places == 0:
            formatted_value = f"{int(round(value))}%"
        else:
            formatted_value = f"{value:.{decimal_places}f}%"

        # Handle negative values
        is_negative = value < 0
        if is_negative and drop_negative_sign:
            # Remove the negative sign - will be indicated by color instead
            formatted_value = formatted_value[1:]  # Remove minus sign

        # Apply colors if enabled and not in Rich mode
        if colored_mode and not rich_mode and is_negative:
            formatted_value = colored(formatted_value, 'red')
        elif colored_mode and not rich_mode and value > 0:
            formatted_value = colored(formatted_value, 'green')

        return formatted_value

    def format_number(
        self,
        value: Union[float, int],
        decimal_places: Optional[int] = None,
        colored_mode: Optional[bool] = None,
        rich_mode: bool = False
    ) -> str:
        """
        Format a number without currency symbol.

        Args:
            value: The numeric value to format
            decimal_places: Override decimal places (uses config if None)
            colored_mode: Override color mode (uses config if None)
            rich_mode: If True, returns plain text for Rich formatting

        Returns:
            Formatted number string
        """
        decimal_places = decimal_places if decimal_places is not None else self.currency_config[
            'decimal_places']
        colored_mode = colored_mode if colored_mode is not None else self.currency_config[
            'colored_mode']

        # Format the number
        if decimal_places == 0:
            formatted_value = f"{int(round(value)):,}"
        else:
            formatted_value = f"{value:,.{decimal_places}f}"

        # Apply colors if enabled and not in Rich mode
        if colored_mode and not rich_mode and value < 0:
            formatted_value = colored(formatted_value, 'red')
        elif colored_mode and not rich_mode and value > 0:
            formatted_value = colored(formatted_value, 'green')

        return formatted_value


# Global currency formatter instance
_currency_formatter: Optional[CurrencyFormatter] = None


def get_currency_formatter() -> CurrencyFormatter:
    """Get the global currency formatter instance."""
    global _currency_formatter
    if _currency_formatter is None:
        _currency_formatter = CurrencyFormatter()
    return _currency_formatter


def format_currency(value: Union[float, int], **kwargs) -> str:
    """Format currency using the global formatter."""
    return get_currency_formatter().format_currency(value, **kwargs)


def format_percentage(value: Union[float, int], **kwargs) -> str:
    """Format percentage using the global formatter."""
    return get_currency_formatter().format_percentage(value, **kwargs)


def format_number(value: Union[float, int], **kwargs) -> str:
    """Format number using the global formatter."""
    return get_currency_formatter().format_number(value, **kwargs)
