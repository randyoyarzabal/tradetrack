#!/usr/bin/env python3

"""
TradeTrack - A personal CLI stock trading management and analysis tool.
Modern portfolio tracker with YAML configuration, Yahoo Finance API, and Rich display.
"""

from libs.config_loader import get_config_loader
from libs.portfolio_library import PortfolioLibrary
from conf.constants import *
import argparse
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


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
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"""{banner(tool)} - Stock / Crypto Portfolio Tracking Tool.
by {AUTHOR}
{GIT_REPO}

Modern portfolio tracker with YAML configuration, Yahoo Finance API, and Rich display.
""",
        epilog="""Example usage:

    $> {0} -p crypto
    $> {0} -p crypto -p stocks -b
    $> {0} --stats
    $> {0} --all -b

""".format(tool)
    )

    # Group arguments
    required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')

    # Add help
    optional.add_argument('-h', '--help', action='help',
                          help='Show this help message and exit.')
    optional.add_argument(
        '--version', '-v', action='version', version=banner(tool))
    optional.add_argument('--debug', action='store_true',
                          default=False, help='Enable DEBUG mode.')
    optional.add_argument('-d', '--day', action='store_true',
                          default=False, help='Show day gains instead of average cost.')
    optional.add_argument('-b', '--borders', action='store_true',
                          default=False, help='Display tables with borders (Rich mode).')
    optional.add_argument('-n', '--no_totals', action='store_true',
                          default=False, help='Don\'t display totals row.')
    optional.add_argument('-ic', '--crypto', action='store_true',
                          default=False, help='Include crypto in portfolio statistics.')
    optional.add_argument('-iu', '--unvested', action='store_true',
                          default=False, help='Include unvested stocks in portfolio statistics.')
    optional.add_argument('--live', action='store_true',
                          default=False, help='Force live data fetch (bypass cache).')

    # Action arguments
    p_actions = optional.add_mutually_exclusive_group()
    p_actions.add_argument('-s', '--stats', action='store_true',
                           default=False, help='Display portfolio statistics.')
    p_actions.add_argument('-c', '--to_csv', dest='csv_file', help='Export portfolio to CSV.',
                           action='store', nargs=1)
    p_actions.add_argument('--all', action='store_true',
                           default=False, help='Display all portfolios combined.')
    p_actions.add_argument('--list', action='store_true',
                           default=False, help='List available portfolios.')

    # Terminal width
    optional.add_argument("-t", "--terminal_width", type=int,
                          default=config_loader.get_terminal_width(),
                          help=f"Terminal column width integer. Default is {config_loader.get_terminal_width()}.")

    # Portfolio selection - will be populated dynamically
    p_actions.add_argument('-p', dest='portfolio', help='Display specific portfolio',
                           action='append', nargs='+', type=lambda s: s.upper())

    # Parse arguments
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()
    else:
        args = parser.parse_args()

        # Initialize portfolio library
        pl = PortfolioLibrary()

        # Configure portfolio library
        pl.debug = args.debug
        pl.day_mode = args.day
        pl.borders = args.borders
        pl.terminal_width = args.terminal_width
        pl.show_totals = not args.no_totals
        pl.include_crypto = args.crypto
        pl.include_unvested = args.unvested

        # Load portfolios
        try:
            pl.load_portfolios(live_data=args.live)
        except Exception as e:
            print(f"ERROR: Failed to load portfolios: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)

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
            available_portfolios.append('ALL')

            for portfolio in args.portfolio:
                if portfolio[0] not in available_portfolios:
                    print(f"ERROR: Portfolio '{portfolio[0]}' not found.")
                    print("Available portfolios:")
                    for name in sorted(available_portfolios):
                        if name != 'ALL':
                            print(f"  - {name}")
                    print("Use --list to see all available portfolios.")
                    sys.exit(1)

            # Display specific portfolios
            for portfolio in args.portfolio:
                if portfolio[0] == 'ALL':
                    # For ALL, adjust terminal width if using default
                    if args.terminal_width == config_loader.get_terminal_width():
                        pl.terminal_width = 140
                    pl.display_all_portfolios()
                else:
                    pl.display_portfolio(portfolio[0])

        elif args.all:
            # Display all portfolios
            pl.display_all_portfolios()

        elif args.csv_file is not None:
            # Export to CSV
            pl.export_to_csv(args.csv_file[0])

        elif args.stats:
            # Display statistics
            pl.display_statistics()

        else:
            # No action specified, show help
            parser.print_help()


if __name__ == "__main__":
    main()
