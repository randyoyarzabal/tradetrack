"""
Configuration loader for the Stock Portfolio Tracker.
Supports both YAML and JSON configuration files.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Handles loading and validation of configuration files."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.

        Args:
            config_path: Path to configuration file. If None, uses environment variable.
        """
        if config_path is None:
            config_path = os.getenv('CONFIG_FILE', 'conf/config.yaml')

        self.config_path = Path(config_path)
        self._config: Optional[Dict[str, Any]] = None

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Dictionary containing configuration settings.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            ValueError: If configuration file format is invalid.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.yaml' or self.config_path.suffix.lower() == '.yml':
                    self._config = yaml.safe_load(f)
                elif self.config_path.suffix.lower() == '.json':
                    self._config = json.load(f)
                else:
                    # Try YAML first, then JSON
                    try:
                        f.seek(0)
                        self._config = yaml.safe_load(f)
                    except yaml.YAMLError:
                        f.seek(0)
                        self._config = json.load(f)

            if not isinstance(self._config, dict):
                raise ValueError(
                    "Configuration file must contain a dictionary/object")

            return self._config

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

    def get_config(self) -> Dict[str, Any]:
        """
        Get configuration, loading if necessary.

        Returns:
            Dictionary containing configuration settings.
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., 'display.terminal_width')
            default: Default value if key not found

        Returns:
            Configuration value or default.
        """
        config = self.get_config()
        keys = key.split('.')
        value = config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_portfolio_path(self) -> str:
        """Get the portfolios directory path."""
        return self.get('paths.portfolios_dir', 'conf/portfolios')

    def get_terminal_width(self) -> int:
        """Get the default terminal width."""
        return self.get('display.terminal_width', 120)

    def get_max_description_length(self) -> int:
        """Get the maximum description length."""
        return self.get('display.max_description_length', 28)

    def should_stretch_to_terminal(self) -> bool:
        """Check if tables should stretch to full terminal width."""
        return self.get('display.stretch_to_terminal', True)

    def get_currency_config(self) -> Dict[str, Any]:
        """Get currency formatting configuration."""
        return self.get('currency', {
            'decimal_places': 2,
            'show_symbol': True,
            'colored_mode': True,
            'negative_format': 'parentheses'
        })

    def get_table_config(self) -> Dict[str, Any]:
        """Get table display configuration."""
        return self.get('tables', {
            'bordered_style': 'heavy',
            'columnar_style': 'clean',
            'header_style': 'bold',
            'number_alignment': 'right'
        })

    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self.get('api', {
            'yahoo': {
                'timeout': 30,
                'retries': 3,
                'cache_duration': 300
            }
        })

    def is_td_enabled(self) -> bool:
        """Check if TD Ameritrade API is enabled."""
        return self.get('api.td_ameritrade.enabled', False)

    def get_crypto_symbols(self) -> list:
        """Get list of known crypto symbols."""
        return self.get('portfolio.crypto_symbols', [])

    def is_crypto_symbol(self, symbol: str) -> bool:
        """Check if a symbol is a crypto symbol."""
        crypto_symbols = self.get_crypto_symbols()
        return symbol.upper() in [s.upper() for s in crypto_symbols]

    def get_debug_config(self) -> Dict[str, Any]:
        """Get debug configuration."""
        return self.get('debug', {
            'enabled': False,
            'show_cache_status': False,
            'show_spinner_debug': False
        })

    def is_debug_enabled(self) -> bool:
        """Check if debug output is enabled."""
        return self.get_debug_config().get('enabled', False)

    def should_show_cache_status(self) -> bool:
        """Check if cache status messages should be shown."""
        return self.get_debug_config().get('show_cache_status', False)

    def should_show_spinner_debug(self) -> bool:
        """Check if spinner debug messages should be shown."""
        return self.get_debug_config().get('show_spinner_debug', False)

    def get_sorting_config(self) -> Dict[str, Any]:
        """Get sorting configuration."""
        return self.get('display', {}).get('sorting', {
            'default_sort_column': 'symbol',
            'default_sort_descending': False,
            'available_sort_columns': [
                'portfolio', 'symbol', 'description', 'qty', 'ave',
                'price', 'gain_pct', 'cost', 'gain_dollars', 'value'
            ]
        })

    def get_default_sort_column(self) -> str:
        """Get the default sort column."""
        return self.get('display.default_sort_column', 'symbol')

    def get_default_sort_descending(self) -> bool:
        """Get the default sort order."""
        return self.get('display.default_sort_descending', False)

    def get_available_sort_columns(self) -> list:
        """Get list of available sort columns."""
        return self.get('display.available_sort_columns', [
            'portfolio', 'symbol', 'description', 'qty', 'ave',
            'price', 'gain_pct', 'cost', 'gain_dollars', 'value'
        ])


# Global configuration instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def get_config() -> Dict[str, Any]:
    """Get configuration using the global loader."""
    return get_config_loader().get_config()


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value using the global loader."""
    return get_config_loader().get(key, default)
