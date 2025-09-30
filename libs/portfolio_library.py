import re
import traceback
from termcolor import colored
import locale
import finnhub
import fnmatch
import pandas as pd
from dotenv import load_dotenv
from td.client import TDClient
from td.exceptions import TknExpError, ForbidError
from columnar import columnar
from .authentication import TDAuthenticationDriver
from .utilities import *

DJI = '$DJI'
COMPX = '$COMPX'
SPY = '$SPX.X'
locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'


class PortfolioLibrary:
    def __init__(self, debug=False):
        load_dotenv()
        self.debug = debug
        self.borders = False
        self.cache = False
        self.day = False
        self.totals = True
        self.df = None  # Pandas dataframe for all stocks
        self.t_width = 120
        self.stats = {}  # Various stock stats calculated
        self.cost_label = ''  # Ave$ or Day$
        self.headers = []
        self.print_data = []  # List of rows for console (colored) purposes
        self.calc_data = []  # List of rows for calculation (raw) purposes
        self.config = get_config()
        self.finnhub_client = None
        # ToDo: Check if API key is defined.
        self.api_key = self.config['FINNHUB']['API_KEY']
        self.finnhub_client = finnhub.Client(api_key=self.api_key)
        self.td_driver = TDAuthenticationDriver(self.debug)
        self.portfolios = {}
        self.td = None
        self.td_roth = None
        self.no_crypto = True
        self.no_unvested = True

        self.td_client = TDClient(
            client_id=self.td_driver.client_id,
            redirect_uri=self.td_driver.redirect_uri,
            credentials_path=os.getenv('CREDENTIAL_CACHE_FILE')
        )

        # Purposely make an API call and ignore errors.  Subsequent calls should work.
        try:
            with HiddenPrints(not debug):
                self.td_client.get_quotes(instruments=['AAPL'])  # A test API call to induce error/re-auth if needed.
        # except TknExpError:
        #     pass
        except ConnectionError as ce:
            print("Unable to make a connection TD Ameritrade API.  Exiting with errors:")
            print(ce)
            exit(1)

        self.read_portfolios()

    def authenticate(self, force=False):
        self.td_driver.debug = self.debug
        if not self.td_driver.verify_ssl_reqs():
            exit(1)
        self.td_driver.authenticate(force=force)

    def print_portfolio(self, pname, silent=False):
        portfolio = self.portfolios[pname]
        if 'ACCOUNT' in portfolio:
            self.get_positions(pname, account=portfolio['ACCOUNT'], silent=silent)
        else:
            self.get_positions(pname, portfolio=portfolio['HOLDINGS'], crypto=(pname == 'CRYPTO'), silent=silent)

    def print_stats(self, print_stats=True, print_stocks=False):
        if print_stats:
            self.print_ttable('Totals')
            self.print_ttable('Averages')
            self.print_mtable()

        if print_stocks:
            data = sorted(self.print_data, key=lambda x: x[0])
            if self.totals:
                # Generate totals here
                totals = ['', '', '', '', '', '', 'TOTAL',
                          self.num_fmt(self.stats['Totals']['Cost'], color=False),
                          self.num_fmt(self.stats['Totals']['Gain$']),
                          self.num_fmt(self.stats['Totals']['Value'],
                                       t_num=(self.stats['Totals']['Value'] - self.stats['Totals']['Cost']))]
                data.append(totals)

            print('All Portfolios (Ave. Gain%: {})'.format(self.num_fmt(self.stats['Averages']['Gain%'], percent=True)))
            print(columnar(data,
                           headers=self.headers,
                           no_borders=(not self.borders),
                           terminal_width=self.t_width
                           )
                  )

    def print_ttable(self, action):
        if action == 'Totals':
            t_header = ['', 'Cost', 'Gain$', 'Value']
        else:
            t_header = ['', 'Gain%', 'Cost', 'Gain$', 'Value']

        t_data = []
        row = [action]
        for c in t_header:
            if c == '':
                continue
            num_val = float(self.stats[action][c])
            if c == 'Gain%':
                if action == 'Totals':
                    continue
                num_val = self.num_fmt(num_val, percent=True)
            if c == 'Cost':
                num_val = self.num_fmt(num_val, color=False)
            if c == 'Gain$':
                num_val = self.num_fmt(num_val)
            if c == 'Value':
                num_val = self.num_fmt(num_val)
            row.append(num_val)
        t_data.append(row)

        print(columnar(t_data,
                       headers=t_header,
                       no_borders=(not self.borders),
                       terminal_width=self.t_width
                       )
              )

    def print_mtable(self):
        max_header = ['', 'Min', 'Symbol', 'Portfolio', '', 'Max', 'Symbol', 'Portfolio']
        m_cols = ['Qty', self.cost_label, 'Gain%', 'Cost', 'Gain$', 'Value']
        data = []
        for c in m_cols:
            row = ['', '', '', '', '', '', '', '']
            for action in ('Min', 'Max'):
                s_str = '{} {}'.format(action, c)
                num_val = float(self.stats[s_str][2])
                symbol = self.stats[s_str][1]
                portfolio = self.stats[s_str][0]
                if c == 'Qty':
                    if num_val.is_integer():
                        num_val = int(num_val)
                if c == self.cost_label:
                    num_val = self.num_fmt(num_val, color=False)
                if c == 'Gain%':
                    num_val = self.num_fmt(num_val, percent=True)
                if c == 'Cost':
                    num_val = self.num_fmt(num_val, color=False)
                if c == 'Gain$':
                    num_val = self.num_fmt(num_val)
                if c == 'Value':
                    # Make an a query on the pandas df looking for a particular row
                    row_val = self.df.query("Portfolio=='{}' and Symbol=='{}'".format(portfolio, symbol))
                    total_cost = row_val.at[row_val.index[0], 'Cost']
                    total_value = row_val.at[row_val.index[0], 'Value']
                    # Or
                    # total_cost = row_val.iloc[0]["Cost"]
                    # total_value = row_val.iloc[0]["Value"]
                    num_val = self.num_fmt(num_val, t_num=(total_value - total_cost))
                if action == "Min":
                    row[0] = c
                    row[1] = num_val
                    row[2] = symbol
                    row[3] = portfolio
                else:
                    row[4] = ''
                    row[5] = num_val
                    row[6] = symbol
                    row[7] = portfolio
            data.append(row)
        print(columnar(data,
                       headers=max_header,
                       no_borders=(not self.borders),
                       terminal_width=self.t_width
                       )
              )

    def get_xval(self, col_name, max=True):
        # Returns [0] = Portfolio, [1] = Symbol, [2] = Value
        col = self.df[col_name]
        if max:
            x_idx = col.idxmax()
        else:
            x_idx = col.idxmin()
        return self.df.loc[x_idx, 'Portfolio'], self.df.loc[x_idx, 'Symbol'], self.df.loc[x_idx, col_name]

    def get_portfolio_names(self):
        return sorted(self.portfolios.keys())

    def read_portfolios(self):
        directory = os.getenv('PORTFOLIOS_PATH')
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                portfolio = os.path.join(directory, filename)
                try:
                    with open(portfolio, "r") as portfolio_fh:
                        file_dict = json.load(portfolio_fh)
                        self.portfolios[file_dict['NAME']] = file_dict
                        if file_dict['NAME'] == 'TD':
                            self.td = file_dict['ACCOUNT']

                        if file_dict['NAME'] == 'TD_ROTH':
                            self.td_roth = file_dict['ACCOUNT']

                except Exception as e:
                    raise e
            else:
                continue

    def load_portfolios(self):
        for portfolio in self.get_portfolio_names():
            if self.no_crypto and portfolio == 'CRYPTO':
                continue
            if self.no_unvested and 'UNVESTED' in portfolio:
                continue        
            try:
                self.print_portfolio(portfolio, silent=True)
            except TypeError:
                print ('ERROR: Authentication expired? Try reauthenticating: "$> stocks.py --auth -f"')
                exit()
            except ForbidError:
                print ('WARNING: No access to account: "{}". Remove from portfolio list to suppress this message.'.format(portfolio))

        # Process data as pandas dataframe
        data = sorted(self.calc_data, key=lambda x: x[0])
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        self.df = pd.DataFrame(data, columns=self.headers)

        if self.day:
            self.cost_label = 'Day$'
        else:
            self.cost_label = 'Ave$'

        # Pre-calculate statistics
        self.stats = {
            "Totals": self.df.sum(),
            "Averages": self.df.mean(numeric_only=True),
            "Min Value": self.get_xval('Value', max=False),
            "Min Gain$": self.get_xval('Gain$', max=False),
            "Min Gain%": self.get_xval('Gain%', max=False),
            "Min Cost": self.get_xval('Cost', max=False),
            "Min Qty": self.get_xval('Qty', max=False),
            f"Min {self.cost_label}": self.get_xval(f'{self.cost_label}', max=False),

            "Max Gain%": self.get_xval('Gain%'),
            "Max Gain$": self.get_xval('Gain$'),
            "Max Value": self.get_xval('Value'),
            "Max Cost": self.get_xval('Cost'),
            "Max Qty": self.get_xval('Qty'),
            f"Max {self.cost_label}": self.get_xval(f'{self.cost_label}'),
        }

    def create_order(self, symbol, order_type, price_type='MARKET', quantity=0, price=0):
        order_type = order_type.upper()
        price_type = price_type.upper()
        if price_type == 'LIMIT' and price == 0:
            raise ValueError("Limit orders require price value.")
        limit_order = {
            "orderType": "LIMIT",
            "session": "NORMAL",
            "duration": "DAY",
            "price": price,
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": order_type,
                    "quantity": quantity,
                    "instrument": {
                        "symbol": symbol,
                        "assetType": "EQUITY"
                    }
                }
            ]
        }
        market_order = {
            "orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": order_type,
                    "quantity": quantity,
                    "instrument": {
                        "symbol": symbol,
                        "assetType": "EQUITY"
                    }
                }
            ]
        }
        if price_type == 'MARKET':
            order = market_order
        else:
            order = limit_order
        return order

    def get_vol(self, tvol):
        if tvol >= 1000000:
            tvol = int(tvol / 1000000)
            tvol_str = '{}M'.format(tvol)
        elif tvol >= 1000:
            tvol = int(tvol / 1000)
            tvol_str = '{}K'.format(tvol)
        else:
            tvol_str = '{}'.format(tvol)
        return tvol_str

    @staticmethod
    def get_desc(d_str):
        exclude_words = (
            'Class A',
            'Common Stock',
            'Ordinary Shares',
            'Common Shares',
            'Acquisition',
            'Consumer Discretionary',
            'Aberdeen Standard Physical',
            'Group',
            'Capital',
            'Entertainment',
            '-',
            'abrdn',
            'Status Alert: Deficient',
            'and Delinquent',
            'AMC Preferred Equity Units, each constituting a',
            'TR ETH Common units of fractional undivided beneficial intere',
            'and Future Mobility Index',
            'Basket Shares',
        )

        title_words = (
            'INVESCO',
            'GRAYSCALE',
            'ETHEREUM',
        )

        # Strip excluded words
        for word in exclude_words:
            if word in d_str:
                d_str = d_str.replace(word, '')

        # Replace Corporation with "Corp."
        word = 'Corporation'
        if word in d_str:
            d_str = d_str.replace(word, 'Corp.')

        # Titlecase words
        if any(substr in d_str for substr in title_words):
            d_str = d_str.title()

        # Remove all test starting with "American D*"
        d_str = re.sub(r'(.*)American [Dd].*', r'\1', d_str)
        d_str = ' '.join(d_str.split())  # Smash multi-spaces to one.
        d_str = d_str.replace('. ,', '.')
        d_str = d_str.replace(' ,', ',')
        d_str = d_str.strip()
        return d_str

    @staticmethod
    def get_change(change):
        return "{:.2f}".format(float(change) * 100)

    def get_movers(self, index=DJI, direction='up', change='percent'):
        data = []
        movers = self.td_client.get_movers(index, direction, change)
        for item in movers:
            # Clean fields
            desc = self.get_desc(item['description'])
            change = self.get_change(item['change'])
            vol = self.get_vol(item['totalVolume'])

            row = [item['symbol'], desc, item['last'], change, vol]
            data.append(row)
        table = columnar(data, headers=['Symbol', 'Description', 'Price', 'Change %', 'Vol'], no_borders=True, terminal_width=self.t_width)
        print(table)

    def __process_watch_list(self, wlist):
        print(wlist['name'])
        tickers = []
        data = []
        for x in wlist['watchlistItems']:
            ticker = x['instrument']['symbol']
            tickers.append(ticker)

        quotes = self.td_client.get_quotes(instruments=tickers)

        for ticker in quotes:
            stock = quotes[ticker]
            tvol_str = self.get_vol(stock['totalVolume'])
            row = [ticker, self.get_desc(stock['description']), stock['lastPrice'], stock['netChange'], tvol_str,
                   stock['exchangeName']]
            data.append(row)

        table = columnar(data, headers=['Symbol', 'Description', 'Price', 'Day Chg$', 'Vol', 'Exchange'],
                         no_borders=True, terminal_width=self.t_width)
        print(table)

    def get_watch_list(self, list_name=None):
        watch_lists = self.td_client.get_watchlist_accounts()
        for watch_list in watch_lists:
            if list_name:
                if list_name == watch_list['name']:
                    self.__process_watch_list(watch_list)
                    break
                # Ignore the rest of the watch lisself.td_client.
            else:
                self.__process_watch_list(watch_list)

    def jprint(self, j_obj):
        print(json.dumps(j_obj, indent=4))

    def get_gain(self, qty, cost, price, percent=False):
        gain = 0
        pl = price - cost  # gain/loss
        if percent:
            if cost != 0:  # For some reason, every now and then, some tickers have 0 cost.
                gd = pl / cost  # gain in decimal
                gain = '{0:.2f}'.format(100 * gd)
            else:
                if not self.day:
                    # If a stock didn't cost us anything, it's 100% gain. 
                    #  i.e. rewards, promotions.
                    gain = '{0:.2f}'.format(100)
        else:
            # In dollars
            gain = '{0:.2f}'.format(pl * qty)

        return float(gain)

    def num_fmt(self, num, t_num=None, color=True, symbol=True, percent=False, nround=True):
        # Determine test number
        if t_num:
            x = t_num
        else:
            x = num
        c_str = num
        text_color = 'none'

        if x < 0 and color:
            c_str = abs(c_str)
            text_color = 'red'
        elif x > 0:
            text_color = 'green'

        # Round or pad with zero decimals if necessary
        c_str = self.pad_float(c_str, nround)

        if symbol:
            if percent:
                c_str = '{}%'.format(c_str)
            else:
                c_str = '${}'.format(c_str)
        if text_color != 'none' and color:
            c_str = colored(c_str, text_color)
        return c_str

    def get_quotes(self, name, tickers, portfolio, crypto):
        # Artificially create dict of quotes as if it is a result of API call
        quotes = {}
        td_quotes = self.td_client.get_quotes(instruments=tickers.keys())
        for ticker in tickers:
            ticker_data = None
            if not portfolio:
                ticker_data = {
                    'description': td_quotes[ticker]['description'],
                    'longQuantity': tickers[ticker]['longQuantity'],
                    'averagePrice': tickers[ticker]['averagePrice'],
                    'openPrice': td_quotes[ticker]['openPrice'],
                    'lastPrice': td_quotes[ticker]['lastPrice'],
                }
            else:
                if crypto:
                    ticker_data = {
                        'description': tickers[ticker][0],
                        'longQuantity': float(tickers[ticker][1]),
                        'averagePrice': tickers[ticker][2],
                        # Use finnhub for Bitcoin quotes.
                        'openPrice': self.finnhub_client.quote(ticker)['o'],
                        'lastPrice': self.finnhub_client.quote(ticker)['c']
                    }
                else:
                    if ticker in td_quotes:
                        ticker_data = {
                            'description': td_quotes[ticker]['description'],
                            'longQuantity': float(tickers[ticker][0]),
                            'averagePrice': tickers[ticker][1],
                            'openPrice': td_quotes[ticker]['openPrice'],
                            'lastPrice': td_quotes[ticker]['lastPrice'],
                        }
                    else:
                        print('WARNING: Stock ticker "{}" not found in {}. Remove from portfolio to suppress this message.'.format(ticker, name))
            if ticker_data:
                quotes[ticker] = ticker_data     
        return quotes

    def pad_float(self, num, nround=False):
        # This is string hack to ensure that numbers always have at least 2 decimal places
        # when printed. Normally to check number of decimal places, one can simply:
        # x = 54.4
        # y = number - int(number)
        # y should give us the fractional part: .4, but for some reason it is giving '0.3999999999999986'
        # This complicates things, the below, ensures the behavior we want.
        if nround:
            c_str = '{:,.2f}'.format(num)
        else:
            c_str = str(num)
            if '.' in c_str:
                dec = c_str.split('.')[1]
                if len(dec) < 2:  # Are there 2 decimal places?
                    c_str = '{:,.2f}'.format(float(c_str))
                else:
                    c_str = '{:,}'.format(float(c_str))
            else:
                c_str = '{:,.2f}'.format(float(c_str))
        return c_str

    def get_positions(self, name, account=None, portfolio=None, crypto=False, silent=False):
        tickers = {}
        data = []
        if not portfolio:
            data_dict = self.td_client.get_accounts(account=account, fields=['positions'])
            if 'positions' in data_dict['securitiesAccount']:  # Possibly empty account
                positions = data_dict['securitiesAccount']['positions']
                for x in positions:
                    ticker = x['instrument']['symbol']
                    tickers[ticker] = x  # Convert list to dict of dicts w/ ticker as the key
        else:
            for x in portfolio:
                tickers[x] = portfolio[x]  # Convert list to dict of dicts w/ ticker as the key

        quotes = self.get_quotes(name, tickers, portfolio, crypto)

        total_gain_p = 0
        total_cost = 0
        total_gain_d = 0
        ave_gain_p = 0
        total_value = 0

        count = 0
        label = ''
        for ticker in sorted(quotes):
            if ticker == 'MMDA1':
                continue
            count += 1
            stock = quotes[ticker]
            qty = stock['longQuantity']

            if self.day:
                label = 'Day$'
                cost = stock['openPrice']
            else:
                label = 'Ave$'
                cost = stock['averagePrice']

            price = stock['lastPrice']

            # Sometimes, there isn't a price for a crypto, if this is the case
            #  use a user-defined price, 4th field in the portfolio (if defined)
            if crypto:
                # Check if the quote is 0
                if price == 0:
                    # Is there a user-defined quote, use it.
                    if len(portfolio[ticker]) == 4:
                        print("WARNING: Price $0 found for {}, using user-defined price: {}.".format(ticker, portfolio[ticker][3]))
                        price = portfolio[ticker][3]
                        cost = price # Since the price is 0, assume cost is the same.
                    else:
                        print("WARNING: Price $0 found for {} and no default price found. Define a 4th field in the portfolio file to supress this message.".format(ticker))

            desc = self.get_desc(stock['description'])

            gain_d = self.get_gain(qty, cost, price)
            gain_p = self.get_gain(qty, cost, price, percent=True)
            t_cost = (qty * cost)
            m_value = (qty * price)

            # Some portfolios support fractional shares, don't cast
            if qty.is_integer():
                qty = int(qty)

            print_row = [
                name,
                ticker,
                desc,
                qty,
                self.num_fmt(cost, color=False, nround=False),
                self.num_fmt(price, color=False, nround=False),
                self.num_fmt(gain_p, percent=True),
                self.num_fmt(t_cost, color=False),
                self.num_fmt(gain_d),
                self.num_fmt(m_value, gain_p),
            ]

            calc_row = [
                name,
                ticker,
                desc,
                qty,
                cost,
                price,
                gain_p,
                t_cost,
                gain_d,
                m_value,
            ]

            data.append(print_row[1:])  # Remove "Portfolio" column
            self.print_data.append(print_row)
            self.calc_data.append(calc_row)

            # Track totals
            total_gain_d = total_gain_d + float(gain_d)
            total_cost = total_cost + t_cost
            total_gain_p = total_gain_p + float(gain_p)
            ave_gain_p = self.num_fmt((total_gain_p / count), percent=True)
            total_value = total_value + m_value

        if self.totals:
            # Generate totals here
            totals = ['', '', '', '', '', 'TOTAL',
                      self.num_fmt(total_cost, color=False), self.num_fmt(total_gain_d),
                      self.num_fmt(total_value, t_num=(total_value - total_cost))]
            data.append(totals)
        self.headers = ['Portfolio', 'Symbol', 'Description', 'Qty', label, 'Price', 'Gain%', 'Cost', 'Gain$', 'Value']

        table = columnar(data,
                         headers=self.headers[1:],  # Remove "Portfolio" column
                         no_borders=(not self.borders), terminal_width=self.t_width)

        if not silent:
            print('Portfolio: {} (Ave. Gain%: {})'.format(colored(name, color='blue'), ave_gain_p))
            print(table)
            print("")

    def get_date(self, rec):
        non_trades = ['ELECTRONIC_FUND', 'RECEIVE_AND_DELIVER', 'JOURNAL']
        trade = 'TRADE'
        tmp_date = ''
        try:
            if rec['type'] in non_trades:
                tmp_date = rec['transactionDate']
            elif rec['type'] == trade:
                tmp_date = rec['orderDate']
            else:
                print(rec['type'])
                exit()
        except:
            traceback.print_exc()
            self.jprint(rec)
            exit()
        return tmp_date.split('T')[0]

    def get_history(self, account):
        data_dict = self.td_client.get_transactions(account=account, transaction_type='ALL', start_date='2021-01-01')
        other = []
        trades = []
        xfers = []
        symbols = {}
        for rec in data_dict:
            rec_type = rec['type']
            rec_date = self.get_date(rec)
            if rec_type == 'TRADE':
                if 'CORRECTION' in rec['description']:
                    continue
                # ToDo: Calculate fees
                # ToDo: Display dividends
                amount = rec['netAmount']
                t_type = rec['transactionItem']['instruction']
                qty = rec['transactionItem']['amount']
                price = rec['transactionItem']['price']
                symbol = rec['transactionItem']['instrument']['symbol']
                row = [rec_date, t_type, symbol, qty, price, amount]
                trades.append(row)
            if rec_type == 'RECEIVE_AND_DELIVER':
                qty = rec['transactionItem']['amount']
                symbol = rec['transactionItem']['instrument']['symbol']
                symbols[symbol] = int(qty)

        print('TRADES')
        table = columnar(trades, headers=['Date', 'Type', 'Symbol', 'Qty', 'Cost', 'Amount'], no_borders=True, terminal_width=self.t_width)
        print(table)

        if account != self.td_roth:
            print('TRANSFERS')
            for key in sorted(symbols):
                xfers.append([key, symbols[key]])
            table = columnar(xfers, headers=['Symbol', 'Qty'], no_borders=True, terminal_width=self.t_width)
            print(table)
