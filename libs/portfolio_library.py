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

        # Headers for display
        self.headers = ['Portfolio', 'Symbol', 'Description',
                        'Qty', 'Ave$', 'Price', 'Gain%', 'Cost', 'Gain$', 'Value']

    def load_portfolios(self, live_data=False):
        """Load all portfolios and prepare data."""
        self.portfolios = self.portfolio_loader.load_portfolios()
        self.all_stocks = self.portfolio_loader.get_all_stocks()

        # Filter stocks based on settings
        filtered_stocks = self._filter_stocks()

        # Get quotes for all symbols
        symbols = list(filtered_stocks.keys())

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

        # Check if we have valid cached data
        if not live_data and self._has_valid_cache(symbols):
            print("Using cached data. Use --live to force fresh data fetch.")
            self.quotes = self._get_cached_quotes(symbols)
        else:
            # Determine the reason for live fetch
            if live_data:
                reason = "live data requested"
            else:
                reason = "cache expired"

            # Debug: Show cache status (can be removed in production)
            # print(f"DEBUG: Cache check - Cache size: {len(self.yahoo_quotes.cache)}, Symbols: {len(symbols)}")
            # print(f"DEBUG: Cache keys: {list(self.yahoo_quotes.cache.keys())[:5]}...")  # Show first 5 keys

            # Show progress spinner for live data fetch
            self._fetch_quotes_with_spinner(symbols, reason)

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

        # Check if we can use Rich console
        try:
            from rich.console import Console
            from rich.spinner import Spinner
            from rich.text import Text
            
            console = Console()
            
            # Only use Rich if we have a proper terminal
            if console.is_terminal:
                # Create spinner
                with console.status(Spinner("arc", Text(message, style="cyan")), spinner_style="cyan") as status:
                    # Suppress all output during fetch
                    with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                        self.quotes = self.yahoo_quotes.get_quotes(symbols)
                return
        except Exception:
            pass

        # Fallback: Simple text-based spinner
        print(f"{message}...", end="", flush=True)
        
        # Start spinner in a separate thread
        spinner_chars = "|/-\\"
        spinner_running = True
        
        def spinner_worker():
            i = 0
            while spinner_running:
                print(f"\r{message} {spinner_chars[i % len(spinner_chars)]}", end="", flush=True)
                time.sleep(0.1)
                i += 1
        
        spinner_thread = threading.Thread(target=spinner_worker)
        spinner_thread.daemon = True
        spinner_thread.start()
        
        try:
            # Suppress all output during fetch
            with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                self.quotes = self.yahoo_quotes.get_quotes(symbols)
        finally:
            # Stop spinner
            spinner_running = False
            spinner_thread.join(timeout=0.2)
            print(f"\r{message} complete!    ", flush=True)

    def _filter_stocks(self) -> Dict[str, Dict[str, Any]]:
        """Filter stocks based on current settings."""
        filtered = {}

        for symbol, stock_data in self.all_stocks.items():
            # Check crypto inclusion
            if not self.include_crypto and self.yahoo_quotes.is_crypto(symbol):
                continue


            filtered[symbol] = stock_data

        return filtered

    def _process_data(self, stocks: Dict[str, Dict[str, Any]]):
        """Process stock data into pandas DataFrame."""
        rows = []

        for symbol, stock_data in stocks.items():
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

            # Calculate gains
            total_value = total_shares * current_price
            gain_dollars = total_value - total_cost
            gain_percent = (gain_dollars / total_cost *
                            100) if total_cost > 0 else 0

            # Determine cost label
            cost_label = 'Day$' if self.day_mode else 'Ave$'
            cost_value = quote['open_price'] if self.day_mode else average_cost

            # Format quantities
            if total_shares.is_integer():
                total_shares = int(total_shares)

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

        # Convert to display format
        display_data = self._format_display_data(portfolio_data)

        # Add totals row if enabled
        if self.show_totals:
            totals_row = self._create_totals_row(portfolio_data)
            display_data.append(totals_row)

        # Display the table using appropriate method
        if self.borders:
            # Use Rich table with borders
            self.rich_display.display_portfolio_table(
                portfolio_name=portfolio_name,
                headers=self.headers[1:],  # Remove Portfolio column
                data=display_data,
                bordered=True,
                width=self.terminal_width
            )
        else:
            # Use columnar table without borders
            self.rich_display.display_columnar_table(
                headers=self.headers[1:],  # Remove Portfolio column
                data=display_data,
                title=f"Portfolio: {portfolio_name}",
                width=self.terminal_width
            )

    def display_all_portfolios(self):
        """Display all portfolios combined."""
        if self.df is None or self.df.empty:
            print("No portfolio data available")
            return

        # Sort by symbol
        sorted_data = self.df.sort_values('Symbol')

        # Convert to display format
        display_data = self._format_display_data(sorted_data)

        # Add totals row if enabled
        if self.show_totals:
            totals_row = self._create_totals_row(self.df)
            display_data.append(totals_row)

        # Display the table using appropriate method
        if self.borders:
            # Use Rich table with borders
            self.rich_display.display_table(
                headers=self.headers,
                data=display_data,
                bordered=True,
                title="All Portfolios",
                width=self.terminal_width
            )
        else:
            # Use columnar table without borders
            self.rich_display.display_columnar_table(
                headers=self.headers,
                data=display_data,
                title="All Portfolios",
                width=self.terminal_width
            )

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

        # Create totals row matching display data format (9 columns, no Portfolio)
        return [
            '',  # Symbol
            '',  # Description
            '',  # Qty
            '',  # Ave$/Day$
            '',  # Gain%
            'TOTAL',
            totals['Cost'],  # Pass raw value for Rich coloring
            totals['Gain$'],
            totals['Value']
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
