"""
YAML portfolio loader for the Stock Portfolio Tracker.
Handles loading and parsing of YAML portfolio files.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from .config_loader import get_config_loader


class PortfolioLoader:
    """Handles loading and parsing of YAML portfolio files."""

    def __init__(self):
        """Initialize the portfolio loader."""
        self.config_loader = get_config_loader()
        self.portfolios_dir = Path(self.config_loader.get_portfolio_path())
        self.portfolios: Dict[str, Dict[str, Any]] = {}

    def load_portfolios(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all portfolio files from the portfolios directory.

        Returns:
            Dictionary mapping portfolio names to portfolio data
        """
        if not self.portfolios_dir.exists():
            raise FileNotFoundError(
                f"Portfolios directory not found: {self.portfolios_dir}")

        self.portfolios.clear()

        for yaml_file in self.portfolios_dir.glob("*.yaml"):
            try:
                portfolio_data = self._load_portfolio_file(yaml_file)
                if portfolio_data:
                    portfolio_name = portfolio_data.get('name', yaml_file.stem)
                    self.portfolios[portfolio_name] = portfolio_data
            except Exception as e:
                print(f"WARNING: Failed to load portfolio {yaml_file}: {e}")
                continue

        return self.portfolios

    def _load_portfolio_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a single portfolio file.

        Args:
            file_path: Path to the YAML file

        Returns:
            Portfolio data dictionary or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                portfolio_data = yaml.safe_load(f)

            if not isinstance(portfolio_data, dict):
                print(f"WARNING: Invalid portfolio file format: {file_path}")
                return None

            # Validate required fields
            if 'name' not in portfolio_data:
                portfolio_data['name'] = file_path.stem

            if 'stocks' not in portfolio_data:
                print(f"WARNING: No stocks found in portfolio: {file_path}")
                return None

            # Validate and normalize stock data
            portfolio_data['stocks'] = self._validate_stocks(
                portfolio_data['stocks'])

            return portfolio_data

        except yaml.YAMLError as e:
            print(f"ERROR: Invalid YAML in {file_path}: {e}")
            return None
        except Exception as e:
            print(f"ERROR: Failed to load {file_path}: {e}")
            return None

    def _validate_stocks(self, stocks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize stock data.

        Args:
            stocks: Raw stocks data from YAML

        Returns:
            Validated and normalized stocks data
        """
        validated_stocks = {}

        for symbol, stock_data in stocks.items():
            if not isinstance(stock_data, dict):
                print(f"WARNING: Invalid stock data for {symbol}, skipping")
                continue

            # Validate required fields
            if 'lots' not in stock_data:
                print(f"WARNING: No lots found for {symbol}, skipping")
                continue

            # Normalize stock data
            normalized_stock = {
                'description': stock_data.get('description', symbol),
                'notes': stock_data.get('notes', ''),
                'lots': self._validate_lots(stock_data['lots'])
            }

            if normalized_stock['lots']:  # Only include if there are valid lots
                validated_stocks[symbol] = normalized_stock

        return validated_stocks

    def _validate_lots(self, lots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and normalize lot data.

        Args:
            lots: List of lot dictionaries

        Returns:
            Validated and normalized lots
        """
        validated_lots = []

        for lot in lots:
            if not isinstance(lot, dict):
                print(f"WARNING: Invalid lot data, skipping")
                continue

            # Validate required fields
            required_fields = ['date', 'shares', 'cost_basis']
            if not all(field in lot for field in required_fields):
                print(f"WARNING: Missing required fields in lot, skipping")
                continue

            # Normalize lot data
            normalized_lot = {
                'date': str(lot['date']),
                'shares': float(lot['shares']),
                'cost_basis': float(lot['cost_basis']),
                'manual_price': lot.get('manual_price')
            }

            # Convert manual_price to float if present
            if normalized_lot['manual_price'] is not None:
                try:
                    normalized_lot['manual_price'] = float(
                        normalized_lot['manual_price'])
                except (ValueError, TypeError):
                    print(f"WARNING: Invalid manual_price in lot, setting to None")
                    normalized_lot['manual_price'] = None

            validated_lots.append(normalized_lot)

        return validated_lots

    def get_portfolio(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific portfolio by name.

        Args:
            name: Portfolio name

        Returns:
            Portfolio data or None if not found
        """
        if not self.portfolios:
            self.load_portfolios()

        return self.portfolios.get(name)

    def get_portfolio_names(self) -> List[str]:
        """
        Get list of all portfolio names.

        Returns:
            List of portfolio names
        """
        if not self.portfolios:
            self.load_portfolios()

        return sorted(self.portfolios.keys())

    def get_all_stocks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all stocks from all portfolios.

        Returns:
            Dictionary mapping symbol to stock data
        """
        if not self.portfolios:
            self.load_portfolios()

        all_stocks = {}
        for portfolio_name, portfolio_data in self.portfolios.items():
            for symbol, stock_data in portfolio_data.get('stocks', {}).items():
                # Create a unique key for each portfolio-symbol combination
                portfolio_symbol_key = f"{portfolio_name}_{symbol}"

                all_stocks[portfolio_symbol_key] = {
                    'symbol': symbol,
                    'description': stock_data.get('description', symbol),
                    'notes': stock_data.get('notes', ''),
                    'portfolio': portfolio_name,
                    'lots': []
                }

                # Add lots with portfolio context
                for lot in stock_data.get('lots', []):
                    lot_with_portfolio = lot.copy()
                    lot_with_portfolio['portfolio'] = portfolio_name
                    all_stocks[portfolio_symbol_key]['lots'].append(
                        lot_with_portfolio)

        return all_stocks


# Global portfolio loader instance
_portfolio_loader: Optional[PortfolioLoader] = None


def get_portfolio_loader() -> PortfolioLoader:
    """Get the global portfolio loader instance."""
    global _portfolio_loader
    if _portfolio_loader is None:
        _portfolio_loader = PortfolioLoader()
    return _portfolio_loader


def load_portfolios() -> Dict[str, Dict[str, Any]]:
    """Load all portfolios using the global loader."""
    return get_portfolio_loader().load_portfolios()


def get_portfolio(name: str) -> Optional[Dict[str, Any]]:
    """Get a specific portfolio using the global loader."""
    return get_portfolio_loader().get_portfolio(name)


def get_portfolio_names() -> List[str]:
    """Get portfolio names using the global loader."""
    return get_portfolio_loader().get_portfolio_names()
