"""
Modern Portfolio Library for the Stock Portfolio Tracker.
Integrates YAML portfolios, Yahoo Finance API, Rich display, and currency formatting.
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from .config_loader import get_config_loader
from .portfolio_loader import get_portfolio_loader
from .yahoo_quotes import get_yahoo_quotes
from .rich_display import get_rich_display
from .currency_formatter import get_currency_formatter


class PortfolioLibrary:
    """Modern portfolio management with YAML, Yahoo Finance, and Rich display."""

    def __init__(self):
        """Initialize the portfolio library."""
        self.config_loader = get_config_loader()
        self.portfolio_loader = get_portfolio_loader()
        self.yahoo_quotes = get_yahoo_quotes()
        self.rich_display = get_rich_display()
        self.currency_formatter = get_currency_formatter()

        # Display settings
        self.borders = False
        self.show_totals = True
        self.include_crypto = False
        self.terminal_width = self.config_loader.get_terminal_width()
        self.day_mode = False

        # Data storage
        self.portfolios: Dict[str, Dict[str, Any]] = {}
        self.all_stocks: Dict[str, Dict[str, Any]] = {}
        self.quotes: Dict[str, Dict[str, Any]] = {}
        self.df: Optional[pd.DataFrame] = None
        self.stats: Dict[str, Any] = {}
        self._show_cache_message = False

        # Headers for display
        self.headers = ['Portfolio', 'Symbol', 'Description',
                        'Qty', 'Ave$', 'Price', 'Gain%', 'Cost', 'Gain$', 'Value']

        # Sorting configuration
        self.sort_column = self.config_loader.get_default_sort_column()
        self.sort_descending = self.config_loader.get_default_sort_descending()
        self.sort_columns = []  # For multi-column sorting

        # Column mapping for sorting
        self.sort_column_map = {
            'portfolio': 'Portfolio',
            'symbol': 'Symbol',
            'description': 'Description',
            'qty': 'Qty',
            'ave': 'Ave$',  # Will be 'Day$' in day mode
            'price': 'Price',
            'gain_pct': 'Gain%',
            'cost': 'Cost',
            'gain_dollars': 'Gain$',
            'value': 'Value'
        }

    def load_portfolios(self, live_data=False):
        """Load all portfolios and prepare data."""
        self.portfolios = self.portfolio_loader.load_portfolios()
        self.all_stocks = self.portfolio_loader.get_all_stocks()

        # Filter stocks based on settings
        filtered_stocks = self._filter_stocks()

        # Get quotes for all symbols, but exclude those with manual prices
        # Extract actual symbols from the composite keys
        all_symbols = [stock_data['symbol']
                       for stock_data in filtered_stocks.values()]
        manual_price_symbols = self._get_symbols_with_manual_prices(
            filtered_stocks)
        symbols_to_fetch = [
            s for s in all_symbols if s not in manual_price_symbols]

        # Reinitialize YahooQuotes based on live_data flag
        if live_data:
            # For live data, clear global cache and don't load from file
            from .yahoo_quotes import _global_cache, _global_cache_timestamps
            _global_cache.clear()
            _global_cache_timestamps.clear()
            from .yahoo_quotes import YahooQuotes
            self.yahoo_quotes = YahooQuotes(load_from_file=False)
            # print("DEBUG: Live data requested - cleared cache and not loading from file")
        else:
            # For cached data, load from file
            from .yahoo_quotes import YahooQuotes
            self.yahoo_quotes = YahooQuotes(load_from_file=True)

        # Check if we have valid cached data for symbols that need fetching
        if not live_data and self._has_valid_cache(symbols_to_fetch):
            self.quotes = self._get_cached_quotes(symbols_to_fetch)
            self._show_cache_message = True
        else:
            # Only fetch live data for symbols that don't have manual prices
            if symbols_to_fetch:
                # Determine the reason for live fetch
                if live_data:
                    reason = "live data requested"
                else:
                    reason = "cache expired"

                # Show progress spinner for live data fetch
                self._fetch_quotes_with_spinner(symbols_to_fetch, reason)
            self._show_cache_message = False

        # Process data into pandas DataFrame
        self._process_data(filtered_stocks)

        # Calculate statistics
        self._calculate_statistics()

    def _has_valid_cache(self, symbols: List[str]) -> bool:
        """Check if we have valid cached data for all symbols."""
        if not symbols:
            return False

        for symbol in symbols:
            if symbol not in self.yahoo_quotes.cache or not self.yahoo_quotes._is_cache_valid(symbol):
                return False

        return True

    def _get_cached_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get cached quotes for symbols."""
        quotes = {}
        for symbol in symbols:
            if symbol in self.yahoo_quotes.cache:
                quotes[symbol] = self.yahoo_quotes.cache[symbol]
        return quotes

    def _fetch_quotes_with_spinner(self, symbols: List[str], reason: str):
        """Fetch quotes with a progress spinner."""
        import sys
        import time
        import threading
        import io
        from contextlib import redirect_stderr, redirect_stdout

        # Create message based on reason
        if reason == "live data requested":
            message = "Fetching live data"
        elif reason == "cache expired":
            message = "Cache expired, fetching fresh data"
        else:
            message = "Loading data"

        # Classic ASCII spinner compatible with PuTTY and other terminals
        spinner_chars = "|/-\\"  # Classic ASCII spinner: | / - \
        spinner_running = True
        spinner_index = 0

        def spinner_worker():
            nonlocal spinner_index
            while spinner_running:
                print(
                    f"\r{message} {spinner_chars[spinner_index % len(spinner_chars)]}", end="", flush=True, file=sys.stderr)
                time.sleep(0.1)
                spinner_index += 1

        # Start spinner in a separate thread
        spinner_thread = threading.Thread(target=spinner_worker)
        spinner_thread.daemon = True
        spinner_thread.start()

        try:
            # Suppress stdout to hide yfinance output but keep stderr for spinner
            with redirect_stdout(io.StringIO()):
                self.quotes = self.yahoo_quotes.get_quotes(symbols)
        finally:
            # Stop spinner
            spinner_running = False
            spinner_thread.join(timeout=0.2)
            # Clear the spinner line completely
            print(f"\r{' ' * 50}\r", end="", flush=True, file=sys.stderr)

    def _filter_stocks(self) -> Dict[str, Dict[str, Any]]:
        """Filter stocks based on current settings."""
        filtered = {}

        for portfolio_symbol, stock_data in self.all_stocks.items():
            # Extract the actual symbol from the portfolio_symbol key
            symbol = stock_data['symbol']

            # Check crypto inclusion
            if not self.include_crypto and self.yahoo_quotes.is_crypto(symbol):
                continue

            filtered[portfolio_symbol] = stock_data

        return filtered

    def _get_symbols_with_manual_prices(self, stocks: Dict[str, Dict[str, Any]]) -> List[str]:
        """Get list of symbols that have manual prices in their lots."""
        manual_price_symbols = []

        for portfolio_symbol, stock_data in stocks.items():
            # Check if any lot has a manual_price
            manual_prices = [lot.get(
                'manual_price') for lot in stock_data['lots'] if lot.get('manual_price')]
            if manual_prices:
                # Extract the actual symbol from the portfolio_symbol key
                symbol = stock_data['symbol']
                manual_price_symbols.append(symbol)

        return manual_price_symbols

    def _process_data(self, stocks: Dict[str, Dict[str, Any]]):
        """Process stock data into pandas DataFrame."""
        rows = []

        for portfolio_symbol, stock_data in stocks.items():
            # Extract the actual symbol from the portfolio_symbol key
            symbol = stock_data['symbol']

            # Check if we have quote data, if not, try to use manual prices
            if symbol not in self.quotes:
                # Try to use manual price as fallback
                manual_prices = [lot.get(
                    'manual_price') for lot in stock_data['lots'] if lot.get('manual_price')]
                if not manual_prices:
                    continue  # Skip if no manual price available

                # Create a mock quote with manual price
                quote = {
                    'description': stock_data.get('description', symbol),
                    # Use most recent manual price
                    'current_price': manual_prices[-1]
                }
            else:
                quote = self.quotes[symbol]

            portfolio = stock_data['portfolio']
            # Use Yahoo description instead of portfolio description, truncate if too long
            description = quote.get('description', symbol)
            max_length = self.config_loader.get_max_description_length()
            if len(description) > max_length:
                description = description[:max_length-3] + "..."

            # Calculate totals across all lots
            total_shares = sum(lot['shares'] for lot in stock_data['lots'])
            total_cost = sum(lot['shares'] * lot['cost_basis']
                             for lot in stock_data['lots'])
            average_cost = total_cost / total_shares if total_shares > 0 else 0

            # Get current price
            current_price = quote['current_price']

            # Use manual price if available and current price is 0 or very small
            if current_price <= 0 and stock_data['lots']:
                manual_prices = [lot.get(
                    'manual_price') for lot in stock_data['lots'] if lot.get('manual_price')]
                if manual_prices:
                    # Use the most recent manual price
                    current_price = manual_prices[-1]

            # Determine cost label and cost basis for calculations
            cost_label = 'Day$' if self.day_mode else 'Ave$'
            cost_value = quote['open_price'] if self.day_mode else average_cost

            # Calculate gains based on the appropriate cost basis
            if self.day_mode:
                # For daily mode, calculate gains based on opening price
                daily_cost = total_shares * quote['open_price']
                total_value = total_shares * current_price
                gain_dollars = total_value - daily_cost
                gain_percent = (gain_dollars / daily_cost *
                                100) if daily_cost > 0 else 0
            else:
                # For average mode, calculate gains based on average cost
                total_value = total_shares * current_price
                gain_dollars = total_value - total_cost
                gain_percent = (gain_dollars / total_cost *
                                100) if total_cost > 0 else 0

            # Format quantities - add asterisk for fractional, remove decimals
            if total_shares.is_integer():
                total_shares = f"{int(total_shares)}"
            else:
                # For fractional quantities, add asterisk and remove decimals
                total_shares = f"{int(total_shares)}*"

            # Create row data
            row = {
                'Portfolio': portfolio,
                'Symbol': symbol,
                'Description': description,
                'Qty': total_shares,
                cost_label: cost_value,
                'Price': current_price,
                'Gain%': gain_percent,
                'Cost': total_cost,
                'Gain$': gain_dollars,
                'Value': total_value
            }

            rows.append(row)

        # Create DataFrame
        self.df = pd.DataFrame(rows)

        # Update headers
        self.headers = ['Portfolio', 'Symbol', 'Description', 'Qty',
                        'Day$' if self.day_mode else 'Ave$', 'Price', 'Gain%', 'Cost', 'Gain$', 'Value']

    def _calculate_statistics(self):
        """Calculate portfolio statistics."""
        if self.df is None or self.df.empty:
            self.stats = {}
            return

        # Calculate totals
        totals = {
            'Cost': self.df['Cost'].sum(),
            'Gain$': self.df['Gain$'].sum(),
            'Value': self.df['Value'].sum(),
            'Gain%': (self.df['Gain$'].sum() / self.df['Cost'].sum() * 100) if self.df['Cost'].sum() > 0 else 0
        }

        # Calculate averages
        averages = {
            'Gain%': self.df['Gain%'].mean(),
            'Cost': self.df['Cost'].mean(),
            'Gain$': self.df['Gain$'].mean(),
            'Value': self.df['Value'].mean()
        }

        # Find min/max values
        min_max = {}
        for column in ['Value', 'Gain$', 'Gain%', 'Cost', 'Qty']:
            if column in self.df.columns:
                min_idx = self.df[column].idxmin()
                max_idx = self.df[column].idxmax()

                min_max[f'Min {column}'] = (
                    self.df.loc[min_idx, 'Portfolio'],
                    self.df.loc[min_idx, 'Symbol'],
                    self.df.loc[min_idx, column]
                )
                min_max[f'Max {column}'] = (
                    self.df.loc[max_idx, 'Portfolio'],
                    self.df.loc[max_idx, 'Symbol'],
                    self.df.loc[max_idx, column]
                )

        self.stats = {
            'Totals': totals,
            'Averages': averages,
            **min_max
        }

    def display_portfolio(self, portfolio_name: str):
        """Display a specific portfolio."""
        if portfolio_name not in self.portfolios:
            print(f"Portfolio '{portfolio_name}' not found")
            return

        # Filter data for this portfolio
        portfolio_data = self.df[self.df['Portfolio'] ==
                                 portfolio_name] if self.df is not None else pd.DataFrame()

        if portfolio_data.empty:
            print(f"No data found for portfolio '{portfolio_name}'")
            return

        # Apply configurable sorting to filtered data
        sorted_portfolio_data = self._apply_sorting(portfolio_data)

        # Convert to display format
        display_data = self._format_display_data(sorted_portfolio_data)

        # Prepare footer data if totals are enabled
        footer_data = None
        if self.show_totals:
            footer_data = self._create_footer_data(sorted_portfolio_data)
            # Remove Portfolio column from footer data for single portfolio display
            footer_data = footer_data[1:] if footer_data else None

        # Generate portfolio title with average gain percentage
        portfolio_title = self._generate_portfolio_title(
            portfolio_name, portfolio_data)

        # Display the table using appropriate method
        if self.borders:
            # Use Rich table with borders and footer
            # Remove Portfolio column from both headers and data for single portfolio display
            # Remove Portfolio column
            headers_without_portfolio = self.headers[1:]
            # Remove Portfolio column from each row
            data_without_portfolio = [row[1:] for row in display_data]

            self.rich_display.display_portfolio_table(
                portfolio_name=portfolio_name,
                headers=headers_without_portfolio,
                data=data_without_portfolio,
                bordered=True,
                title=portfolio_title,
                footer_data=footer_data
            )
        else:
            # Use columnar table without borders
            # Remove Portfolio column from both headers and data for single portfolio display
            # Remove Portfolio column
            headers_without_portfolio = self.headers[1:]
            # Remove Portfolio column from each row
            data_without_portfolio = [row[1:] for row in display_data]

            # Add totals row for columnar display if enabled
            if self.show_totals:
                totals_row = self._create_totals_row(sorted_portfolio_data)
                # Remove Portfolio column from totals row
                totals_row_without_portfolio = totals_row[1:]
                data_without_portfolio.append(totals_row_without_portfolio)

            self.rich_display.display_columnar_table(
                headers=headers_without_portfolio,
                data=data_without_portfolio,
                title=portfolio_title
            )

        # Show cache message if applicable
        self._show_cache_status_message()

    def display_all_portfolios(self):
        """Display all portfolios combined."""
        if self.df is None or self.df.empty:
            print("No portfolio data available")
            return

        # Apply configurable sorting
        sorted_data = self._apply_sorting(self.df)

        # Convert to display format
        display_data = self._format_display_data(sorted_data)

        # Prepare footer data if totals are enabled
        footer_data = None
        if self.show_totals:
            footer_data = self._create_footer_data(self.df)

        # Display the table using appropriate method
        if self.borders:
            # Use Rich table with borders and footer
            self.rich_display.display_table(
                headers=self.headers,
                data=display_data,
                bordered=True,
                title="All Portfolios",
                footer_data=footer_data
            )
        else:
            # Use columnar table without borders (still use totals row for columnar)
            if self.show_totals:
                totals_row = self._create_totals_row(self.df)
                display_data.append(totals_row)

            self.rich_display.display_columnar_table(
                headers=self.headers,
                data=display_data,
                title="All Portfolios"
            )

        # Show cache message if applicable
        self._show_cache_status_message()

    def display_statistics(self):
        """Display portfolio statistics."""
        if not self.stats:
            print("No statistics available")
            return

        # Display totals
        self._display_totals_table()

        # Display averages
        self._display_averages_table()

        # Display min/max
        self._display_minmax_table()

        # Show cache message if applicable
        self._show_cache_status_message()

    def _display_totals_table(self):
        """Display totals statistics table."""
        totals = self.stats['Totals']

        headers = ['', 'Cost', 'Gain$', 'Value']
        data = [['TOTAL',
                totals['Cost'],  # Pass raw value for Rich coloring
                totals['Gain$'],
                totals['Value']]]

        if self.borders:
            self.rich_display.display_stats_table(
                stats_type="Totals",
                headers=headers,
                data=data,
                bordered=True,
                width=self.terminal_width
            )
        else:
            self.rich_display.display_columnar_table(
                headers=headers,
                data=data,
                title="Totals Statistics",
                width=self.terminal_width
            )

    def _display_averages_table(self):
        """Display averages statistics table."""
        averages = self.stats['Averages']

        headers = ['', 'Gain%', 'Cost', 'Gain$', 'Value']
        data = [['AVERAGE',
                averages['Gain%'],  # Pass raw value for Rich coloring
                averages['Cost'],
                averages['Gain$'],
                averages['Value']]]

        if self.borders:
            self.rich_display.display_stats_table(
                stats_type="Averages",
                headers=headers,
                data=data,
                bordered=True,
                width=self.terminal_width
            )
        else:
            self.rich_display.display_columnar_table(
                headers=headers,
                data=data,
                title="Averages Statistics",
                width=self.terminal_width
            )

    def _display_minmax_table(self):
        """Display min/max statistics table."""
        headers = ['', 'Min', 'Symbol', 'Portfolio',
                   '', 'Max', 'Symbol', 'Portfolio']
        data = []

        columns = ['Qty', 'Ave$' if not self.day_mode else 'Day$',
                   'Gain%', 'Cost', 'Gain$', 'Value']

        for col in columns:
            if col in self.df.columns:
                min_key = f'Min {col}'
                max_key = f'Max {col}'

                if min_key in self.stats and max_key in self.stats:
                    min_data = self.stats[min_key]
                    max_data = self.stats[max_key]

                    # Pass raw values for Rich coloring
                    min_value = min_data[2]
                    max_value = max_data[2]

                    row = [col, min_value, min_data[1], min_data[0],
                           '', max_value, max_data[1], max_data[0]]
                    data.append(row)

        if self.borders:
            self.rich_display.display_minmax_table(
                headers=headers,
                data=data,
                bordered=True,
                width=self.terminal_width
            )
        else:
            self.rich_display.display_columnar_table(
                headers=headers,
                data=data,
                title="Min/Max Statistics",
                width=self.terminal_width
            )

    def _format_stat_value(self, column: str, value: float) -> str:
        """Format a statistic value based on column type."""
        if 'Gain%' in column or '%' in column:
            return self.currency_formatter.format_percentage(value)
        elif column in ['Cost', 'Gain$', 'Value', 'Ave$', 'Day$']:
            return self.currency_formatter.format_currency(value)
        else:
            return self.currency_formatter.format_number(value)

    def _format_display_data(self, df: pd.DataFrame) -> List[List[Any]]:
        """Format DataFrame data for display."""
        display_data = []

        for _, row in df.iterrows():
            display_row = [
                row['Portfolio'],
                row['Symbol'],
                row['Description'],
                row['Qty'],
                # Ave$/Day$ - pass raw value for Rich coloring
                row[self.headers[4]],
                row['Price'],
                row['Gain%'],
                row['Cost'],
                row['Gain$'],
                row['Value']
            ]
            display_data.append(display_row)

        return display_data

    def _create_totals_row(self, df: pd.DataFrame) -> List[Any]:
        """Create a totals row for display."""
        totals = df.sum()

        # Create totals row matching display data format (10 columns including Portfolio)
        return [
            '',  # Portfolio
            '',  # Symbol
            '',  # Description
            '',  # Qty
            '',  # Ave$/Day$
            '',  # Price
            '',  # Gain%
            totals['Cost'],  # Pass raw value for Rich coloring
            totals['Gain$'],
            totals['Value']
        ]

    def _create_footer_data(self, df: pd.DataFrame) -> List[str]:
        """Create footer data for Rich table display."""
        totals = df.sum()

        # Format footer data for each column
        return [
            '',  # Portfolio
            '',  # Symbol
            '',  # Description
            '',  # Qty
            '',  # Ave$/Day$
            '',  # Price
            '',  # Gain%
            self.currency_formatter.format_currency(
                totals.get('Cost', 0), rich_mode=True),
            self.currency_formatter.format_currency(
                totals.get('Gain$', 0), rich_mode=True),
            self.currency_formatter.format_currency(
                totals.get('Value', 0), rich_mode=True)
        ]

    def export_to_csv(self, filename: str):
        """Export portfolio data to CSV."""
        if self.df is not None:
            self.df.to_csv(filename, index=False,
                           header=True, encoding='utf-8')
            print(f'Exported data to CSV file: {filename}')
        else:
            print("No data available to export")

    def load_portfolio_names_only(self):
        """Load only portfolio names without fetching quotes."""
        self.portfolios = self.portfolio_loader.load_portfolios()
        self.all_stocks = self.portfolio_loader.get_all_stocks()

    def get_portfolio_names(self) -> List[str]:
        """Get list of portfolio names."""
        return self.portfolio_loader.get_portfolio_names()

    def set_sorting(self, column: str = None, descending: bool = False, multi_columns: List[str] = None):
        """
        Configure sorting options.

        Args:
            column: Single column to sort by
            descending: Sort in descending order
            multi_columns: List of columns for multi-column sorting
        """
        if multi_columns:
            self.sort_columns = multi_columns
            self.sort_column = None
        elif column:
            self.sort_column = column
            self.sort_columns = []

        self.sort_descending = descending

    def _validate_sort_column(self, column: str) -> str:
        """
        Validate and normalize sort column names.

        Args:
            column: Column name to validate

        Returns:
            Validated DataFrame column name

        Raises:
            ValueError: If column name is invalid
        """
        if column not in self.sort_column_map:
            available = list(self.sort_column_map.keys())
            raise ValueError(
                f"Invalid sort column '{column}'. Available columns: {', '.join(available)}")

        # Handle day mode for ave column
        if column == 'ave' and self.day_mode:
            return 'Day$'

        return self.sort_column_map[column]

    def _apply_sorting(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply sorting to DataFrame based on current settings.

        Args:
            df: DataFrame to sort

        Returns:
            Sorted DataFrame
        """
        if df is None or df.empty:
            return df

        try:
            if self.sort_columns:
                # Multi-column sorting
                columns = [self._validate_sort_column(
                    col) for col in self.sort_columns]
                ascending = [not self.sort_descending] * len(columns)
                return df.sort_values(columns, ascending=ascending)
            else:
                # Single column sorting
                column = self._validate_sort_column(self.sort_column)
                return df.sort_values(column, ascending=not self.sort_descending)
        except ValueError as e:
            print(f"Warning: {e}. Using default sorting by symbol.")
            return df.sort_values('Symbol')

    def _portfolio_contains_crypto(self, portfolio_name: str) -> bool:
        """Check if a portfolio contains crypto symbols."""
        if portfolio_name not in self.portfolios:
            return False

        portfolio = self.portfolios[portfolio_name]
        if 'stocks' not in portfolio:
            return False

        # Check if any symbol in the portfolio is crypto
        for symbol in portfolio['stocks'].keys():
            if self.yahoo_quotes.is_crypto(symbol):
                return True

        return False

    def _generate_portfolio_title(self, portfolio_name: str, portfolio_data: pd.DataFrame) -> str:
        """Generate portfolio title with average gain percentage and color coding."""
        if portfolio_data.empty:
            return f"Portfolio: {portfolio_name}"

        # Use existing statistics from pandas dataset
        if hasattr(self, 'stats') and 'totals' in self.stats:
            total_gain_percent = self.stats['totals']['Gain%']
            total_gain_dollars = self.stats['totals']['Gain$']
        else:
            # Fallback to manual calculation if stats not available
            total_cost = portfolio_data['Cost'].sum()
            total_gain_dollars = portfolio_data['Gain$'].sum()
            total_gain_percent = (total_gain_dollars /
                                  total_cost * 100) if total_cost > 0 else 0

        # Format the gain percentage
        gain_percent_str = f"{total_gain_percent:+.1f}%"

        # Create colored title based on gain/loss
        from termcolor import colored
        if total_gain_dollars > 0:
            colored_gain = colored(gain_percent_str, 'green', force_color=True)
        elif total_gain_dollars < 0:
            colored_gain = colored(gain_percent_str, 'red', force_color=True)
        else:
            colored_gain = gain_percent_str

        # Add mode indicator to title
        mode_indicator = "Daily" if self.day_mode else "All-Time"
        return f"Portfolio: {portfolio_name} ({mode_indicator} {colored_gain})"

    def _show_cache_status_message(self):
        """Show cache status message at the bottom of display."""
        if self._show_cache_message:
            print("\nUsing cached data. Use --live to force fresh data fetch.")
        else:
            print("\nLive data fetched successfully.")

        # Add notes about manual_price and fractional quantities
        print(
            "- Use manual_price in --add-lot to suppress warnings for delisted symbols.")
        print("- * indicates fractional quantities (e.g., crypto or ETF shares).")
