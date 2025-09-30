#!/usr/bin/env python3

"""
TradeTrack - A personal CLI stock trading management and analysis tool.
Modern portfolio tracker with YAML configuration, Yahoo Finance API, and Rich display.
Includes comprehensive CRUD operations for portfolio management and tax analysis.
"""

from libs.config_loader import get_config_loader
from libs.portfolio_library import PortfolioLibrary
from libs.tax_analysis import TaxAnalyzer
from libs.lot_analysis import LotAnalyzer
from conf.constants import *
import argparse
import os
import sys
from pathlib import Path
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from termcolor import colored

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter that adds colors to group headings."""

    def __init__(self, prog):
        super().__init__(prog, max_help_position=50, width=120)
        # Override the _Section class to add colors to headings
        self._Section = self._ColoredSection

    class _ColoredSection(argparse.HelpFormatter._Section):
        """Custom section class that adds colors to headings."""

        def format_help(self):
            # format the indented section
            if self.parent is not None:
                self.formatter._indent()
            join = self.formatter._join_parts
            item_help = join([func(*args) for func, args in self.items])
            if self.parent is not None:
                self.formatter._dedent()

            # return nothing if the section was empty
            if not item_help:
                return ''

            # add the heading if the section was non-empty
            if self.heading is not argparse.SUPPRESS and self.heading is not None:
                current_indent = self.formatter._current_indent

                # Colorize the heading based on the group name
                heading = self.heading
                if 'General' in heading:
                    color = 'cyan'
                elif 'Screen Display' in heading:
                    color = 'magenta'
                elif 'Portfolio Display' in heading:
                    color = 'green'
                elif 'Lot Management' in heading:
                    color = 'yellow'
                elif 'Symbol Management' in heading:
                    color = 'blue'
                elif 'Portfolio Management' in heading:
                    color = 'red'
                elif 'Analysis' in heading:
                    color = 'white'
                elif 'Data' in heading:
                    color = 'grey'
                else:
                    color = 'yellow'

                colored_heading = colored(f"{heading}:", color, attrs=[
                                          'bold'], force_color=True)
                heading_text = colored_heading
                heading = '%*s%s\n' % (current_indent, '', heading_text)
            else:
                heading = ''

            # join the section-initial newline, the heading and the help
            return join(['\n', heading, item_help, '\n'])

    def _format_action_invocation(self, action):
        """Format action invocation with colors."""
        if not action.option_strings:
            # Positional arguments
            return super()._format_action_invocation(action)

        # Colorize option strings
        parts = []
        for option_string in action.option_strings:
            if option_string.startswith('--'):
                # Long options in cyan
                parts.append(colored(option_string, 'cyan', force_color=True))
            else:
                # Short options in green
                parts.append(colored(option_string, 'green', force_color=True))

        return ', '.join(parts)

    def _format_usage(self, usage, actions, groups, prefix):
        """Format usage with colors."""
        # Colorize the usage prefix
        colored_prefix = colored(prefix, 'white', attrs=[
                                 'bold'], force_color=True)
        return super()._format_usage(usage, actions, groups, colored_prefix)

    def _format_text(self, text):
        """Format text with proper line breaks and colors."""
        if text is None:
            return ""

        # Colorize the description text
        lines = text.split('\n')
        colored_lines = []

        for line in lines:
            if line.strip().startswith('TradeTrack ver.'):
                # Colorize the main title
                colored_lines.append(
                    colored(line, 'cyan', attrs=['bold'], force_color=True))
            elif line.strip().startswith('by '):
                # Colorize the author line
                colored_lines.append(colored(line, 'blue', force_color=True))
            elif line.strip().startswith('https://'):
                # Colorize the URL
                colored_lines.append(
                    colored(line, 'blue', attrs=['underline'], force_color=True))
            elif line.strip().startswith('Modern portfolio tracker'):
                # Colorize the description
                colored_lines.append(colored(line, 'green', force_color=True))
            elif line.strip().startswith('Example usage:'):
                # Colorize section headers
                colored_lines.append(
                    colored(line, 'yellow', attrs=['bold'], force_color=True))
            elif line.strip().startswith('$> '):
                # Colorize command examples
                colored_lines.append(colored(line, 'white', force_color=True))
            else:
                colored_lines.append(line)

        return '\n'.join(colored_lines)

    def _format_action(self, action):
        """Format individual actions with consistent indentation."""
        # Get the default formatting
        result = super()._format_action(action)

        # Ensure consistent indentation for help text
        if action.help and action.help != argparse.SUPPRESS:
            # Split into lines to handle multi-line help text
            lines = result.split('\n')
            if len(lines) > 1:
                # Find the indentation level of the first line
                first_line = lines[0]
                indent_level = len(first_line) - len(first_line.lstrip())

                # Apply consistent indentation to continuation lines
                for i in range(1, len(lines)):
                    if lines[i].strip():  # Only indent non-empty lines
                        lines[i] = ' ' * indent_level + lines[i].lstrip()

                result = '\n'.join(lines)

        return result

    def _strip_color_codes(self, text):
        """Remove ANSI color codes from text to get actual width."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)


class PortfolioCRUD:
    """
    Comprehensive CRUD operations for portfolio management.
    Handles adding, removing, updating lots and portfolio data.
    Ensures portfolios are kept in alphabetical order and lots sorted by date (newest first).
    """

    def __init__(self):
        """Initialize the CRUD operations with configuration."""
        self.config_loader = get_config_loader()
        self.config = self.config_loader.get_config()
        self.portfolios_dir = Path(self.config['paths']['portfolios_dir'])
        self.tax_analyzer = TaxAnalyzer()
        self.lot_analyzer = LotAnalyzer()

    def add_lot(self, portfolio_name: str, symbol: str, shares: float, cost_basis: float,
                date: Optional[str] = None, manual_price: Optional[float] = None,
                description: Optional[str] = None, notes: str = "") -> bool:
        """
        Add a new lot to a portfolio.

        Args:
            portfolio_name: Name of the portfolio
            symbol: Stock symbol
            shares: Number of shares
            cost_basis: Cost per share
            date: Purchase date (YYYY-MM-DD format, defaults to current date)
            manual_price: Optional manual price override
            description: Optional stock description
            notes: Optional notes

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use current date if not provided
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')

            # Load portfolio
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return False

            with open(portfolio_file, 'r') as f:
                portfolio_data = yaml.safe_load(f)

            # Initialize stocks section if it doesn't exist
            if 'stocks' not in portfolio_data:
                portfolio_data['stocks'] = {}

            # Initialize symbol if it doesn't exist
            if symbol not in portfolio_data['stocks']:
                portfolio_data['stocks'][symbol] = {
                    'description': description or symbol,
                    'notes': notes,
                    'lots': []
                }

            # Create new lot
            new_lot = {
                'date': date,
                'shares': float(shares),
                'cost_basis': float(cost_basis),
                'manual_price': manual_price
            }

            # Add lot to symbol
            portfolio_data['stocks'][symbol]['lots'].append(new_lot)

            # Sort lots by date (newest first)
            portfolio_data['stocks'][symbol]['lots'].sort(
                key=lambda x: x['date'], reverse=True)

            # Sort stocks alphabetically
            portfolio_data['stocks'] = dict(
                sorted(portfolio_data['stocks'].items()))

            # Save portfolio
            with open(portfolio_file, 'w') as f:
                yaml.dump(portfolio_data, f,
                          default_flow_style=False, sort_keys=False)

            print(
                f"Added lot: {shares} shares of {symbol} at ${cost_basis:.4f} on {date}")
            return True

        except Exception as e:
            print(f"Error adding lot: {e}")
            return False

    def remove_lot(self, portfolio_name: str, symbol: str, lot_index: int) -> bool:
        """
        Remove a lot from a portfolio.

        Args:
            portfolio_name: Name of the portfolio
            symbol: Stock symbol
            lot_index: Index of the lot to remove (0-based)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load portfolio
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return False

            with open(portfolio_file, 'r') as f:
                portfolio_data = yaml.safe_load(f)

            if symbol not in portfolio_data.get('stocks', {}):
                print(f"Symbol '{symbol}' not found in portfolio")
                return False

            lots = portfolio_data['stocks'][symbol]['lots']
            if lot_index < 0 or lot_index >= len(lots):
                print(f"Invalid lot index: {lot_index}")
                return False

            # Remove the lot
            removed_lot = lots.pop(lot_index)

            # Sort stocks alphabetically
            portfolio_data['stocks'] = dict(
                sorted(portfolio_data['stocks'].items()))

            # Save portfolio
            with open(portfolio_file, 'w') as f:
                yaml.dump(portfolio_data, f,
                          default_flow_style=False, sort_keys=False)

            print(
                f"Removed lot: {removed_lot['shares']} shares of {symbol} from {removed_lot['date']}")
            return True

        except Exception as e:
            print(f"Error removing lot: {e}")
            return False

    def update_lot(self, portfolio_name: str, symbol: str, lot_index: int,
                   date: Optional[str] = None, shares: Optional[float] = None,
                   cost_basis: Optional[float] = None, manual_price: Optional[float] = None) -> bool:
        """
        Update an existing lot in a portfolio.

        Args:
            portfolio_name: Name of the portfolio
            symbol: Stock symbol
            lot_index: Index of the lot to update (0-based)
            date: New purchase date (optional)
            shares: New number of shares (optional)
            cost_basis: New cost per share (optional)
            manual_price: New manual price (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load portfolio
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return False

            with open(portfolio_file, 'r') as f:
                portfolio_data = yaml.safe_load(f)

            if symbol not in portfolio_data.get('stocks', {}):
                print(f"Symbol '{symbol}' not found in portfolio")
                return False

            lots = portfolio_data['stocks'][symbol]['lots']
            if lot_index < 0 or lot_index >= len(lots):
                print(f"Invalid lot index: {lot_index}")
                return False

            # Update the lot
            lot = lots[lot_index]
            if date is not None:
                lot['date'] = date
            if shares is not None:
                lot['shares'] = float(shares)
            if cost_basis is not None:
                lot['cost_basis'] = float(cost_basis)
            if manual_price is not None:
                lot['manual_price'] = manual_price

            # Sort lots by date after update (newest first)
            lots.sort(key=lambda x: x['date'], reverse=True)

            # Sort stocks alphabetically
            portfolio_data['stocks'] = dict(
                sorted(portfolio_data['stocks'].items()))

            # Save portfolio
            with open(portfolio_file, 'w') as f:
                yaml.dump(portfolio_data, f,
                          default_flow_style=False, sort_keys=False)

            print(f"Updated lot {lot_index} for {symbol}")
            return True

        except Exception as e:
            print(f"Error updating lot: {e}")
            return False

    def add_symbol(self, portfolio_name: str, symbol: str, description: str = "",
                   notes: str = "") -> bool:
        """
        Add a new symbol to a portfolio.

        Args:
            portfolio_name: Name of the portfolio
            symbol: Stock symbol
            description: Stock description
            notes: Optional notes

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load portfolio
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return False

            with open(portfolio_file, 'r') as f:
                portfolio_data = yaml.safe_load(f)

            # Initialize stocks section if it doesn't exist
            if 'stocks' not in portfolio_data:
                portfolio_data['stocks'] = {}

            if symbol in portfolio_data['stocks']:
                print(f"Symbol '{symbol}' already exists in portfolio")
                return False

            # Add new symbol
            portfolio_data['stocks'][symbol] = {
                'description': description or symbol,
                'notes': notes,
                'lots': []
            }

            # Save portfolio
            with open(portfolio_file, 'w') as f:
                yaml.dump(portfolio_data, f,
                          default_flow_style=False, sort_keys=False)

            print(f"Added symbol '{symbol}' to portfolio '{portfolio_name}'")
            return True

        except Exception as e:
            print(f"Error adding symbol: {e}")
            return False

    def remove_symbol(self, portfolio_name: str, symbol: str) -> bool:
        """
        Remove a symbol and all its lots from a portfolio.

        Args:
            portfolio_name: Name of the portfolio
            symbol: Stock symbol

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load portfolio
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return False

            with open(portfolio_file, 'r') as f:
                portfolio_data = yaml.safe_load(f)

            if symbol not in portfolio_data.get('stocks', {}):
                print(f"Symbol '{symbol}' not found in portfolio")
                return False

            # Count lots before removal
            lot_count = len(portfolio_data['stocks'][symbol]['lots'])

            # Remove symbol
            del portfolio_data['stocks'][symbol]

            # Save portfolio
            with open(portfolio_file, 'w') as f:
                yaml.dump(portfolio_data, f,
                          default_flow_style=False, sort_keys=False)

            print(
                f"Removed symbol '{symbol}' and {lot_count} lots from portfolio '{portfolio_name}'")
            return True

        except Exception as e:
            print(f"Error removing symbol: {e}")
            return False

    def create_portfolio(self, portfolio_name: str, description: str = "") -> bool:
        """
        Create a new portfolio.

        Args:
            portfolio_name: Name of the portfolio
            description: Portfolio description

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' already exists")
                return False

            # Create new portfolio structure
            portfolio_data = {
                'name': portfolio_name.upper(),
                'description': description or f"My {portfolio_name} portfolio",
                'stocks': {}
            }

            # Save portfolio
            with open(portfolio_file, 'w') as f:
                yaml.dump(portfolio_data, f,
                          default_flow_style=False, sort_keys=False)

            print(f"Created portfolio '{portfolio_name}'")
            return True

        except Exception as e:
            print(f"Error creating portfolio: {e}")
            return False

    def delete_portfolio(self, portfolio_name: str) -> bool:
        """
        Delete a portfolio file.

        Args:
            portfolio_name: Name of the portfolio

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return False

            # Count symbols before deletion
            with open(portfolio_file, 'r') as f:
                portfolio_data = yaml.safe_load(f)
            symbol_count = len(portfolio_data.get('stocks', {}))

            # Delete file
            portfolio_file.unlink()

            print(
                f"Deleted portfolio '{portfolio_name}' with {symbol_count} symbols")
            return True

        except Exception as e:
            print(f"Error deleting portfolio: {e}")
            return False

    def backup_portfolio(self, portfolio_name: str, backup_dir: Optional[str] = None) -> bool:
        """
        Create a backup of a portfolio.

        Args:
            portfolio_name: Name of the portfolio
            backup_dir: Optional backup directory (defaults to portfolios_dir/backups)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return False

            # Set backup directory
            if backup_dir is None:
                backup_dir = self.portfolios_dir / "backups"
            else:
                backup_dir = Path(backup_dir)

            backup_dir.mkdir(exist_ok=True)

            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / \
                f"{portfolio_name.lower()}_{timestamp}.yaml"

            # Copy file
            import shutil
            shutil.copy2(portfolio_file, backup_file)

            print(f"Backed up portfolio '{portfolio_name}' to {backup_file}")
            return True

        except Exception as e:
            print(f"Error backing up portfolio: {e}")
            return False

    def restore_portfolio(self, backup_file: str, portfolio_name: Optional[str] = None) -> bool:
        """
        Restore a portfolio from backup.

        Args:
            backup_file: Path to backup file
            portfolio_name: Optional new portfolio name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                print(f"Backup file '{backup_file}' not found")
                return False

            # Load backup to get original name
            with open(backup_path, 'r') as f:
                backup_data = yaml.safe_load(f)

            original_name = backup_data.get('name', 'UNKNOWN')
            target_name = portfolio_name or original_name

            # Restore to portfolios directory
            target_file = self.portfolios_dir / f"{target_name.lower()}.yaml"

            # Update name in data if different
            if target_name != original_name:
                backup_data['name'] = target_name.upper()

            # Save restored portfolio
            with open(target_file, 'w') as f:
                yaml.dump(backup_data, f, default_flow_style=False,
                          sort_keys=False)

            print(f"Restored portfolio '{original_name}' as '{target_name}'")
            return True

        except Exception as e:
            print(f"Error restoring portfolio: {e}")
            return False

    def list_lots(self, portfolio_name: str, symbol: Optional[str] = None) -> None:
        """
        List all lots in a portfolio or for a specific symbol.

        Args:
            portfolio_name: Name of the portfolio
            symbol: Optional specific symbol to list
        """
        try:
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return

            with open(portfolio_file, 'r') as f:
                portfolio_data = yaml.safe_load(f)

            stocks = portfolio_data.get('stocks', {})
            if not stocks:
                print(f"No stocks found in portfolio '{portfolio_name}'")
                return

            if symbol:
                if symbol not in stocks:
                    print(f"Symbol '{symbol}' not found in portfolio")
                    return
                stocks = {symbol: stocks[symbol]}

            print(f"\nLots in portfolio '{portfolio_name}':")
            print("-" * 80)

            for sym, stock_data in stocks.items():
                lots = stock_data.get('lots', [])
                if not lots:
                    print(f"{sym}: No lots")
                    continue

                print(f"\n{sym} ({stock_data.get('description', '')}):")
                total_shares = 0
                total_cost = 0

                for i, lot in enumerate(lots):
                    shares = lot['shares']
                    cost = lot['cost_basis']
                    date = lot['date']
                    manual_price = lot.get('manual_price')

                    total_shares += shares
                    total_cost += shares * cost

                    manual_str = f" (manual: ${manual_price:.4f})" if manual_price else ""
                    print(
                        f"  [{i}] {date}: {shares:>10.4f} shares @ ${cost:>8.4f}{manual_str}")

                avg_cost = total_cost / total_shares if total_shares > 0 else 0
                print(
                    f"  Total: {total_shares:>10.4f} shares, avg cost: ${avg_cost:.4f}")

        except Exception as e:
            print(f"Error listing lots: {e}")

    def get_tax_analysis(self, portfolio_name: str, symbol: Optional[str] = None) -> None:
        """
        Get tax analysis for lots in a portfolio.

        Args:
            portfolio_name: Name of the portfolio
            symbol: Optional specific symbol to analyze
        """
        try:
            portfolio_file = self.portfolios_dir / \
                f"{portfolio_name.lower()}.yaml"
            if not portfolio_file.exists():
                print(f"Portfolio '{portfolio_name}' not found")
                return

            with open(portfolio_file, 'r') as f:
                portfolio_data = yaml.safe_load(f)

            stocks = portfolio_data.get('stocks', {})
            if not stocks:
                print(f"No stocks found in portfolio '{portfolio_name}'")
                return

            if symbol:
                if symbol not in stocks:
                    print(f"Symbol '{symbol}' not found in portfolio")
                    return
                stocks = {symbol: stocks[symbol]}

            print(f"\nTax Analysis for portfolio '{portfolio_name}':")
            print("=" * 80)

            for sym, stock_data in stocks.items():
                lots = stock_data.get('lots', [])
                if not lots:
                    continue

                print(f"\n{sym} ({stock_data.get('description', '')}):")
                print("-" * 60)

                # Analyze each lot
                for i, lot in enumerate(lots):
                    purchase_date = datetime.strptime(lot['date'], '%Y-%m-%d')
                    days_held = (datetime.now() - purchase_date).days
                    years_held = days_held / 365.25

                    is_long_term = years_held >= 1.0
                    term_type = "LONG-TERM" if is_long_term else "SHORT-TERM"

                    shares = lot['shares']
                    cost_basis = lot['cost_basis']
                    total_cost = shares * cost_basis

                    print(
                        f"  Lot [{i}] {lot['date']}: {shares:>8.4f} shares @ ${cost_basis:>8.4f}")
                    print(
                        f"    Days held: {days_held:>4d} ({years_held:.2f} years) - {term_type}")
                    print(f"    Total cost: ${total_cost:>10.2f}")

                    if lot.get('manual_price'):
                        current_price = lot['manual_price']
                        current_value = shares * current_price
                        gain_loss = current_value - total_cost
                        gain_pct = (gain_loss / total_cost *
                                    100) if total_cost > 0 else 0

                        print(
                            f"    Current value: ${current_value:>10.2f} (manual price: ${current_price:.4f})")
                        print(
                            f"    Gain/Loss: ${gain_loss:>10.2f} ({gain_pct:>6.2f}%)")
                        print(
                            f"    Tax treatment: {'No capital gains' if is_long_term else 'Short-term capital gains'}")

                    print()

        except Exception as e:
            print(f"Error in tax analysis: {e}")


def _display_all_portfolios(pl, args, config_loader):
    """Helper function to display all portfolios with consistent settings."""
    # Only override terminal width if explicitly provided via command line
    # Otherwise, respect the config setting
    if args.terminal_width != config_loader.get_terminal_width():
        pl.terminal_width = args.terminal_width
    pl.display_all_portfolios()


def main():
    """Main entry point for the TradeTrack application."""
    # Get configuration
    config_loader = get_config_loader()
    app_config = config_loader.get_config()

    # Main argument parser
    tool = os.path.basename(__file__)
    parser = argparse.ArgumentParser(
        add_help=False,
        prog=__file__,
        formatter_class=ColoredHelpFormatter,
        description=f"""{banner(tool)} - Stock / Crypto Portfolio Tracking Tool.
by {AUTHOR}
{GIT_REPO}

Modern portfolio tracker with YAML configuration, Yahoo Finance API, and Rich display.
""",
        epilog="""Example usage:

    # Display portfolios
    $> {0} -p crypto
    $> {0} -p crypto -p stocks -b
    $> {0} -p crypto -t 0
    $> {0} --stats
    $> {0} --all -b
    $> {0} --all -ic
    $> {0} --list

    # Sorting options
    $> {0} -p crypto --sort value --desc
    $> {0} --all --sort gain_pct
    $> {0} -p robinhood --sort-multi portfolio symbol
    $> {0} --all --sort-multi portfolio value --desc

    # CRUD Operations
    $> {0} --add-lot crypto BTC-USD today 0.5 45000.0
    $> {0} --add-lot robinhood AAPL 2024-01-15 10 150.0 155.0
    $> {0} --remove-lot crypto BTC-USD 0
    $> {0} --add-symbol crypto ETH-USD "Ethereum"
    $> {0} --remove-symbol crypto BTC-USD
    $> {0} --create-portfolio new_portfolio "My new portfolio"
    $> {0} --delete-portfolio old_portfolio
    $> {0} --backup-portfolio crypto
    $> {0} --restore-portfolio backups/crypto_20241201_120000.yaml restored_crypto
    $> {0} --list-lots crypto BTC-USD
    $> {0} --tax-analysis crypto all

""".format(tool)
    )

    # Create argument groups
    general = parser.add_argument_group('General Options')
    screen = parser.add_argument_group('Screen Display Options')
    portfolio = parser.add_argument_group('Portfolio Display Options')
    lots = parser.add_argument_group('Lot Management Options')
    symbols = parser.add_argument_group('Symbol Management Options')
    portfolios = parser.add_argument_group('Portfolio Management Options')
    analysis = parser.add_argument_group('Analysis Options')
    data = parser.add_argument_group('Data Options')

    # General options
    general.add_argument('-h', '--help', action='help',
                         help='Show this help message and exit.')
    general.add_argument(
        '--version', '-v', action='version', version=banner(tool))
    general.add_argument('--debug', action='store_true',
                         default=False, help='Enable DEBUG mode.')

    # Screen display options
    screen.add_argument('-b', '--borders', action='store_true',
                        default=False, help='Display tables with borders (Rich mode).')
    screen.add_argument("-t", "--terminal_width", type=int,
                        default=config_loader.get_terminal_width(),
                        help=f"Terminal column width integer. 0 means use entire/stretch terminal width. Default is {config_loader.get_terminal_width()}.")
    screen.add_argument('-n', '--no_totals', action='store_true',
                        default=False, help='Don\'t display totals row.')

    # Portfolio display options
    portfolio.add_argument('-p', dest='portfolio', help='Display specific portfolio',
                           action='append', nargs='+', type=lambda s: s.upper())
    portfolio.add_argument('--all', action='store_true',
                           default=False, help='Display all portfolios combined.')
    portfolio.add_argument('--list', action='store_true',
                           default=False, help='List available portfolios.')
    portfolio.add_argument('-s', '--stats', action='store_true',
                           default=False, help='Display portfolio statistics.')
    portfolio.add_argument('-c', '--to_csv', dest='csv_file', help='Export portfolio to CSV.',
                           action='store', nargs=1)
    portfolio.add_argument('-ic', '--crypto', action='store_true',
                           default=False, help='Include crypto in portfolio statistics (--all only).')
    portfolio.add_argument('-d', '--day', action='store_true',
                           default=False, help='Show day gains instead of average cost.')

    # Sorting options
    portfolio.add_argument('--sort', '--sort-by', dest='sort_column',
                           help='Sort table by specified column. Available: portfolio, symbol, description, qty, ave, price, gain_pct, cost, gain_dollars, value')
    portfolio.add_argument('--sort-desc', '--desc', action='store_true',
                           default=False, help='Sort in descending order (default: ascending)')
    portfolio.add_argument('--sort-multi', nargs='+', metavar='COLUMN',
                           help='Sort by multiple columns (e.g., --sort-multi portfolio symbol)')

    # Lot management options
    lots.add_argument('--add-lot', nargs='+', metavar='ARG',
                      help='Add a new lot to a portfolio. Use "today" for current date. Manual price is optional. Args: PORTFOLIO SYMBOL DATE SHARES COST_BASIS [MANUAL_PRICE]')
    lots.add_argument('--remove-lot', nargs=3, metavar=('PORTFOLIO', 'SYMBOL', 'LOT_INDEX'),
                      help='Remove a lot from a portfolio by index.')
    lots.add_argument('--update-lot', nargs=4, metavar=('PORTFOLIO', 'SYMBOL', 'LOT_INDEX', 'FIELD'),
                      help='Update a lot field (date, shares, cost_basis, manual_price).')
    lots.add_argument('--list-lots', nargs=2, metavar=('PORTFOLIO', 'SYMBOL'),
                      help='List all lots for a symbol in a portfolio.')

    # Symbol management options
    symbols.add_argument('--add-symbol', nargs=3, metavar=('PORTFOLIO', 'SYMBOL', 'DESCRIPTION'),
                         help='Add a new symbol to a portfolio.')
    symbols.add_argument('--remove-symbol', nargs=2, metavar=('PORTFOLIO', 'SYMBOL'),
                         help='Remove a symbol and all its lots from a portfolio.')

    # Portfolio management options
    portfolios.add_argument('--create-portfolio', nargs=2, metavar=('PORTFOLIO', 'DESCRIPTION'),
                            help='Create a new portfolio.')
    portfolios.add_argument('--delete-portfolio', nargs=1, metavar=('PORTFOLIO',),
                            help='Delete a portfolio.')
    portfolios.add_argument('--backup-portfolio', nargs=1, metavar=('PORTFOLIO',),
                            help='Create a backup of a portfolio.')
    portfolios.add_argument('--restore-portfolio', nargs=2, metavar=('BACKUP_FILE', 'PORTFOLIO'),
                            help='Restore a portfolio from backup.')

    # Analysis options
    analysis.add_argument('--tax-analysis', nargs=2, metavar=('PORTFOLIO', 'SYMBOL'),
                          help='Show tax analysis for a portfolio or specific symbol.')

    # Data options
    data.add_argument('--live', action='store_true',
                      default=False, help='Force live data fetch (bypass cache).')

    # Parse arguments
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()
    else:
        args = parser.parse_args()

        # Determine if we need to load portfolios for display operations
        needs_portfolio_loading = (
            args.portfolio is not None or
            args.all or
            args.csv_file is not None or
            args.stats or
            args.list
        )

        # Only initialize and load portfolios if needed for display operations
        if needs_portfolio_loading:
            # Initialize portfolio library
            pl = PortfolioLibrary()

            # Configure portfolio library
            pl.debug = args.debug
            pl.day_mode = args.day
            pl.borders = args.borders
            pl.terminal_width = args.terminal_width
            pl.show_totals = not args.no_totals
            pl.include_crypto = args.crypto

            # Configure sorting
            pl.set_sorting(
                column=args.sort_column,
                descending=args.sort_desc,
                multi_columns=args.sort_multi
            )

            # Auto-include crypto for specific portfolio display if portfolio contains crypto
            if args.portfolio and not args.all:
                pl.load_portfolio_names_only()
                # Flatten the portfolio list (args.portfolio is a list of lists)
                portfolio_names = [
                    name for sublist in args.portfolio for name in sublist]
                for portfolio_name in portfolio_names:
                    if pl._portfolio_contains_crypto(portfolio_name):
                        pl.include_crypto = True
                        break

            # Load portfolios
            try:
                pl.load_portfolios(live_data=args.live)
            except Exception as e:
                print(f"ERROR: Failed to load portfolios: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
                sys.exit(1)

        # Handle display operations (only if portfolios were loaded)
        if needs_portfolio_loading:
            # Handle list portfolios
            if args.list:
                portfolio_names = pl.get_portfolio_names()
                print("Available portfolios:")
                for name in sorted(portfolio_names):
                    print(f"  - {name}")
                print(f"\nTotal: {len(portfolio_names)} portfolios")
                return

            # Handle different actions
            if args.portfolio is not None:
                # Validate portfolio names
                available_portfolios = pl.get_portfolio_names()

                for portfolio in args.portfolio:
                    if portfolio[0] not in available_portfolios:
                        print(f"ERROR: Portfolio '{portfolio[0]}' not found.")
                        print("Available portfolios:")
                        for name in sorted(available_portfolios):
                            print(f"  - {name}")
                        print("Use --list to see all available portfolios.")
                        print("Use --all to display all portfolios combined.")
                        sys.exit(1)

                # Display specific portfolios
                for portfolio in args.portfolio:
                    pl.display_portfolio(portfolio[0])

            elif args.all:
                # Display all portfolios
                _display_all_portfolios(pl, args, config_loader)

            elif args.csv_file is not None:
                # Export to CSV
                pl.export_to_csv(args.csv_file[0])

            elif args.stats:
                # Display statistics
                pl.display_statistics()

        # Handle CRUD operations
        if args.add_lot is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            # Validate minimum required arguments
            if len(args.add_lot) < 5:
                print(
                    "Error: --add-lot requires at least 5 arguments: PORTFOLIO SYMBOL DATE SHARES COST_BASIS [MANUAL_PRICE]")
                sys.exit(1)

            portfolio, symbol, date, shares, cost_basis = args.add_lot[:5]
            manual_price = args.add_lot[5] if len(args.add_lot) > 5 else None

            # Handle special values
            if date.lower() == 'today':
                date = None  # Will use current date

            # Handle manual price
            if manual_price is not None:
                try:
                    manual_price = float(manual_price)
                except ValueError:
                    print("Error: Manual price must be a number")
                    sys.exit(1)

            try:
                shares = float(shares)
                cost_basis = float(cost_basis)
            except ValueError:
                print("Error: Shares and cost basis must be numbers")
                sys.exit(1)

            success = crud.add_lot(
                portfolio, symbol, shares, cost_basis, date, manual_price)
            sys.exit(0 if success else 1)

        if args.remove_lot is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            portfolio, symbol, lot_index = args.remove_lot

            try:
                lot_index = int(lot_index)
            except ValueError:
                print("Error: Lot index must be a number")
                sys.exit(1)

            success = crud.remove_lot(portfolio, symbol, lot_index)
            sys.exit(0 if success else 1)

        if args.add_symbol is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            portfolio, symbol, description = args.add_symbol
            success = crud.add_symbol(portfolio, symbol, description)
            sys.exit(0 if success else 1)

        if args.remove_symbol is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            portfolio, symbol = args.remove_symbol
            success = crud.remove_symbol(portfolio, symbol)
            sys.exit(0 if success else 1)

        if args.create_portfolio is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            portfolio, description = args.create_portfolio
            success = crud.create_portfolio(portfolio, description)
            sys.exit(0 if success else 1)

        if args.delete_portfolio is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            portfolio = args.delete_portfolio[0]
            success = crud.delete_portfolio(portfolio)
            sys.exit(0 if success else 1)

        if args.backup_portfolio is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            portfolio = args.backup_portfolio[0]
            success = crud.backup_portfolio(portfolio)
            sys.exit(0 if success else 1)

        if args.restore_portfolio is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            backup_file, portfolio = args.restore_portfolio
            success = crud.restore_portfolio(backup_file, portfolio)
            sys.exit(0 if success else 1)

        if args.list_lots is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            portfolio, symbol = args.list_lots
            crud.list_lots(portfolio, symbol)
            sys.exit(0)

        if args.tax_analysis is not None:
            # Initialize CRUD operations
            crud = PortfolioCRUD()

            portfolio, symbol = args.tax_analysis
            if symbol.lower() == 'all':
                symbol = None
            crud.get_tax_analysis(portfolio, symbol)
            sys.exit(0)

        # Check if any action was specified
        action_specified = (
            needs_portfolio_loading or
            args.add_lot is not None or
            args.remove_lot is not None or
            args.add_symbol is not None or
            args.remove_symbol is not None or
            args.create_portfolio is not None or
            args.delete_portfolio is not None or
            args.backup_portfolio is not None or
            args.restore_portfolio is not None or
            args.list_lots is not None or
            args.tax_analysis is not None
        )

        if not action_specified:
            # No action specified, show help
            parser.print_help()


if __name__ == "__main__":
    main()
