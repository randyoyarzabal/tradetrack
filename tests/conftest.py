"""
Pytest configuration and fixtures for TradeTrack tests.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import pandas as pd

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from libs.config_loader import ConfigLoader
from libs.portfolio_library import PortfolioLibrary
from libs.currency_formatter import CurrencyFormatter
from libs.rich_display import RichDisplay


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'paths': {
            'portfolios_dir': '/tmp/test_portfolios',
            'log_file': '/tmp/test.log'
        },
        'display': {
            'terminal_width': 120,
            'borders': False,
            'show_totals': True,
            'include_crypto': False,
            'max_description_length': 28,
            'stretch_to_terminal': False,
            'default_sort_column': 'symbol',
            'default_sort_descending': False
        },
        'currency': {
            'decimal_places': 2,
            'show_symbol': True,
            'colored_mode': True,
            'negative_format': 'parentheses'
        },
        'tables': {
            'bordered_style': 'heavy',
            'columnar_style': 'clean',
            'header_style': 'bold',
            'number_alignment': 'right'
        },
        'api': {
            'yahoo': {
                'timeout': 30,
                'retries': 3,
                'cache_duration': 3600
            }
        },
        'debug': {
            'enabled': False,
            'show_cache_status': False,
            'show_spinner_debug': False
        },
        'portfolio': {
            'default_currency': 'USD',
            'lot_date_format': '%Y-%m-%d',
            'auto_detect_crypto': True,
            'crypto_symbols': ['BTC-USD', 'ETH-USD']
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file_logging': False,
            'console_logging': True
        }
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return pd.DataFrame({
        'Portfolio': ['TEST', 'TEST', 'TEST'],
        'Symbol': ['AAPL', 'GOOGL', 'MSFT'],
        'Description': ['Apple Inc.', 'Alphabet Inc.', 'Microsoft Corp.'],
        'Qty': [10, 5, 8],
        'Ave$': [150.0, 2800.0, 300.0],
        'Price': [175.0, 2900.0, 320.0],
        'Gain%': [16.67, 3.57, 6.67],
        'Cost': [1500.0, 14000.0, 2400.0],
        'Gain$': [250.0, 500.0, 160.0],
        'Value': [1750.0, 14500.0, 2560.0]
    })


@pytest.fixture
def mock_yahoo_quotes():
    """Mock Yahoo Finance quotes for testing."""
    return {
        'AAPL': {
            'regularMarketPrice': 175.0,
            'regularMarketChange': 2.5,
            'regularMarketChangePercent': 1.45
        },
        'GOOGL': {
            'regularMarketPrice': 2900.0,
            'regularMarketChange': 50.0,
            'regularMarketChangePercent': 1.75
        },
        'MSFT': {
            'regularMarketPrice': 320.0,
            'regularMarketChange': 5.0,
            'regularMarketChangePercent': 1.59
        }
    }


@pytest.fixture
def config_loader(sample_config, temp_dir):
    """ConfigLoader instance with test configuration."""
    config_file = os.path.join(temp_dir, 'test_config.yaml')
    import yaml
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    
    return ConfigLoader(config_file)


@pytest.fixture
def currency_formatter():
    """CurrencyFormatter instance for testing."""
    return CurrencyFormatter()


@pytest.fixture
def rich_display():
    """RichDisplay instance for testing."""
    return RichDisplay()


@pytest.fixture
def portfolio_library():
    """PortfolioLibrary instance for testing."""
    return PortfolioLibrary()
