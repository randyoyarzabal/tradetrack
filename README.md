# Stock and Crypto Portfolio Management

## Prequisites
- A TD Ameritrade account is required.
- A Finnhub.io account is required only if processing Crypto quotes.

## Quick Start
1. Install package requirements from `requirements.txt`
2. Create a config file (sample provided) config.json, fill in the "API_KEY" vars.
3. Create portfolio JSON files (samples provided) named <portfolio>.json.  For example `webull.json`.
   Entries in this file is: Portfolio, Symbol, Number of Shares, Cost.
4. Create a copy of the .env_sample to .env and edit to suit.
5. Run the authentication for the first time: `./stocks.py -a`

## Portfolio JSON Format

There are 2 types of portfolio files:

1. TD Account Portfolio

Example:
```json
{
    "NAME": "TD_ACOUNT",
    "ACCOUNT": "576825539"
}
```

2. Non-TD Portfolio or Crypto

*Note that crypto needs to be in a separate `crypto.json` file.*

Example:
```json
{
   "__COMMENTS__": "Ticker, # of Shares, $ Cost., Optional $ Price",
   "NAME": "ROBINHOOD",
   "HOLDINGS": {
      "SEV": [
         50,
         10.25
      ],
      "GSAT": [
         200,
         1.56,
         1.99 # This is an optional element to define a price (if quote not available.)
      ],
  }
}
```

## Basic Use Commands
- Help: `./stocks.py -h`
- Stats: `./stocks.py -s`
- Portfolio View: `./stocks.py -p <portfolio>`
- All Portfolios: `./stocks.py -a all`
- All Portfolios (show Crypto and Unvested): `./stocks.py -a all -ic -iu`

## Other Notes
- You can track "unvested" stocks, i.e. restricted stock units.  Name the porfolio *UNVESTED, and it will automaticlly be excluded from view unless the `-iu, --unvested` options are used.
- Crypto must be tracked in a separate `crypto.json` file and is automatically excluded from view unless the `-ic, --crypto` options are used.

