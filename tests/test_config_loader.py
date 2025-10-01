"""
Tests for ConfigLoader class - focused on essential functionality.
"""
import pytest
import tempfile
import os
from pathlib import Path
import yaml

from libs.config_loader import ConfigLoader


class TestConfigLoader:
    """Test cases for ConfigLoader class."""

    def test_config_loader_init_default(self):
        """Test ConfigLoader initialization with default config path."""
        loader = ConfigLoader()
        assert loader.config_path == Path('conf/config.yaml')
        config = loader.load_config()
        assert config is not None

    def test_config_loader_init_custom_path(self, temp_dir):
        """Test ConfigLoader initialization with custom config path."""
        config_data = {'currency': {'decimal_places': 2}}
        config_file = os.path.join(temp_dir, 'test_config.yaml')
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigLoader(config_file)
        assert loader.config_path == Path(config_file)
        config = loader.load_config()
        assert config['currency']['decimal_places'] == 2

    def test_get_currency_config(self):
        """Test currency config retrieval."""
        loader = ConfigLoader()
        currency_config = loader.get_currency_config()
        assert 'decimal_places' in currency_config
        assert 'show_symbol' in currency_config

    def test_get_display_config(self):
        """Test display config retrieval."""
        loader = ConfigLoader()
        config = loader.load_config()
        display_config = config.get('display', {})
        assert 'terminal_width' in display_config
        assert 'borders' in display_config

    def test_config_loader_file_not_found(self, temp_dir):
        """Test config loading when file doesn't exist."""
        loader = ConfigLoader(os.path.join(temp_dir, 'nonexistent.yaml'))
        with pytest.raises(FileNotFoundError):
            loader.load_config()

    def test_config_loader_invalid_yaml(self, temp_dir):
        """Test config loading with invalid YAML."""
        config_file = os.path.join(temp_dir, 'invalid.yaml')
        with open(config_file, 'w') as f:
            f.write('invalid: yaml: content: [')
        
        loader = ConfigLoader(config_file)
        with pytest.raises(ValueError):
            loader.load_config()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir