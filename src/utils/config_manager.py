"""Configuration manager for application settings"""
import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_file='config.json'):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_dir = Path(__file__).parent.parent.parent
        self.config_file = self.config_dir / config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            'sms': {
                'enabled': False,
                'api_key': '',
                'api_url': '',
                'sender_number': ''
            },
            'notifications': {
                'enabled': True,
                'reminder_days_ahead': 7
            },
            'ui': {
                'theme': 'light',
                'font_size': 10,
                'language': 'fa'
            },
            'reports': {
                'default_format': 'excel',
                'include_charts': True
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_sms_config(self):
        """Get SMS configuration"""
        return self.config.get('sms', {})
    
    def set_sms_config(self, api_key, api_url, sender_number=''):
        """Set SMS configuration"""
        self.config['sms'] = {
            'enabled': bool(api_key and api_url),
            'api_key': api_key,
            'api_url': api_url,
            'sender_number': sender_number
        }
        return self.save_config()
    
    def get_ui_config(self):
        """Get UI configuration"""
        return self.config.get('ui', {})
    
    def set_ui_config(self, theme=None, font_size=None, language=None):
        """Set UI configuration"""
        ui_config = self.config.get('ui', {})
        
        if theme is not None:
            ui_config['theme'] = theme
        if font_size is not None:
            ui_config['font_size'] = font_size
        if language is not None:
            ui_config['language'] = language
        
        self.config['ui'] = ui_config
        return self.save_config()


# Global config instance
_config_instance = None


def get_config():
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
