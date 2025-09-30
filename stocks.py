#!/usr/bin/env python

import argparse
import os
import traceback
from conf.constants import *
from libs.utilities import *
from libs.portfolio_library import PortfolioLibrary


def main():
    # Main argument parser; command-line argument rules
    tool = os.path.basename(__file__)
    parser = argparse.ArgumentParser(
        add_help=False,  # This is so we can format help ourselves.
        prog=__file__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # argument_default=argparse.SUPPRESS,  # Suppress args creation (None) for optional parameters.
        description="""{} - Stock / Crypto Portfolio Tracking Tool.
by {}
{}
""".format(banner(tool), AUTHOR, GIT_REPO),
        epilog="""Example usage:

    $>{0} -p stash
    $>{0} -p stash -p webull -b
    $>{0} --stats

    """.format(tool)
    )

    # A bit of hacking to group optional/required parameters.
    required = parser.add_argument_group('Required arguments')
    optional = parser.add_argument_group('Optional arguments')

    # Required parameters will be dynamically be generated later in execution.

    # Because we used "add_help=False" in the constructor, we need to manually add it back in.
    # If we didn't add "add_help=False", we would have 3 sections in the help-text. Try it and see!
    optional.add_argument('-h', '--help', action='help',
                          help='Show this help message and exit.')
    optional.add_argument('--version', '-v', action='version', version=banner(tool))
    optional.add_argument('--debug', action='store_true',
                          default=False, help='Enable DEBUG mode.')
    optional.add_argument('-a', '--auth', action='store_true',
                          default=False, help='Authenticate via TD OAuth.')
    optional.add_argument('-f', '--force', action='store_true',
                          default=False, help='Force authentication even if tokens are still valid.')
    optional.add_argument('-d', '--day', action='store_true',
                          default=False, help='Show day gains.')
    optional.add_argument('-b', '--borders', action='store_true',
                          default=False, help='Display borders.')
    optional.add_argument('-n', '--no_totals', action='store_true',
                          default=False, help='Don\'t display \'Totals\' row.')
    optional.add_argument('-ic', '--crypto', action='store_true',
                          default=False, help='Include crypto in portfolio statistics.')
    optional.add_argument('-iu', '--unvested', action='store_true',
                          default=False, help='Include unvested stocks in portfolio statistics.')
    p_actions = optional.add_mutually_exclusive_group()
    p_actions.add_argument('-s', '--stats', action='store_true',
                           default=False, help='Display portfolio statistics.')
    p_actions.add_argument('-c', '--to_csv', dest='csv_file', help='Export portfolio to CSV.',
                           action='store', nargs=1)
    optional.add_argument("-t", "--terminal_width", type=int, default=120,
                          help="Terminal column width integer. Default is 120.")
    pl = PortfolioLibrary()
    portfolio_list = pl.get_portfolio_names()
    portfolio_list.append('ALL')

    # The lambda function makes the parameters portable so users can pass any text case.
    p_actions.add_argument('-p', dest='portfolio', help='Display portfolio',
                           action='append', nargs='+', choices=portfolio_list,
                           type=lambda s: s.upper())
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()
    else:
        args = parser.parse_args()
        pl.debug = args.debug
        pl.day = args.day
        pl.borders = args.borders
        pl.t_width = args.terminal_width
        pl.totals = not args.no_totals
        pl.no_crypto = not args.crypto
        pl.no_unvested = not args.unvested
        if not args.auth:
            pl.load_portfolios()
        if args.portfolio is not None:
            # Display individual portfolios (-p)
            for portfolio in args.portfolio:
                if portfolio[0] == 'ALL':
                    # For ALL, set default to 135
                    if args.terminal_width == 120:
                        pl.t_width = 140
                    pl.print_stats(print_stats=False, print_stocks=True)
                else:
                    pl.print_portfolio(portfolio[0])
        elif args.csv_file is not None:
            # Export to CSV (-c)
            pl.df.to_csv(args.csv_file[0], index=False, header=True, encoding='utf-8')
            print('Exported data to CSV file: {}'.format(args.csv_file[0]))
        elif args.stats:
            # Display statistics tables (-s)
            pl.print_stats()
        elif args.auth:
            # Perform OAuth web authentication (-a)
            pl.authenticate(force=args.force)


if __name__ == "__main__":
    main()
