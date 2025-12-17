"""Configuration management for the Book Price Drop Watcher."""

import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager that loads from YAML and environment variables."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize configuration from YAML file and environment variables."""
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            # Use defaults if config file doesn't exist
            self._config = self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'csv_file_path': 'data/packt_books.csv',
            'csv_check_interval_minutes': 15,
            'threshold_percentage': 10,
            'threshold_absolute': 5.00,
            'price_check_interval_hours': 24,
            'notification_cooldown_hours': 24,
            'db_path': 'data/books.db',
            'third_party_sources': ['google_books', 'open_library']
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value, checking environment variables first."""
        # Check environment variable first (uppercase with underscores)
        env_key = key.upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Try to convert to appropriate type
            if isinstance(default, bool):
                return env_value.lower() in ('true', '1', 'yes')
            elif isinstance(default, int):
                try:
                    return int(env_value)
                except ValueError:
                    return default
            elif isinstance(default, float):
                try:
                    return float(env_value)
                except ValueError:
                    return default
            elif isinstance(default, list):
                return [item.strip() for item in env_value.split(',')]
            return env_value
        
        # Fall back to YAML config
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default
    
    @property
    def csv_file_path(self) -> str:
        """Get CSV file path."""
        return self.get('csv_file_path', 'data/packt_books.csv')
    
    @property
    def csv_check_interval_minutes(self) -> int:
        """Get CSV check interval in minutes."""
        return self.get('csv_check_interval_minutes', 15)
    
    @property
    def threshold_percentage(self) -> float:
        """Get percentage threshold."""
        return self.get('threshold_percentage', 10.0)
    
    @property
    def threshold_absolute(self) -> float:
        """Get absolute threshold."""
        return self.get('threshold_absolute', 5.00)
    
    @property
    def price_check_interval_hours(self) -> int:
        """Get price check interval in hours."""
        return self.get('price_check_interval_hours', 24)
    
    @property
    def notification_cooldown_hours(self) -> int:
        """Get notification cooldown in hours."""
        return self.get('notification_cooldown_hours', 24)
    
    @property
    def db_path(self) -> str:
        """Get database path."""
        return self.get('db_path', 'data/books.db')
    
    @property
    def third_party_sources(self) -> list:
        """Get list of third-party sources."""
        return self.get('third_party_sources', ['google_books', 'open_library'])


# Global config instance
config = Config()

