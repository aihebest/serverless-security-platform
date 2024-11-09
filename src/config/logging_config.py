# src/config/logging_config.py

import logging.config
import json
from typing import Dict, Any

def setup_logging(config: Dict[str, Any]) -> None:
    """Configure logging for the application."""
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'json': {
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'security_platform.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'json',
                'level': 'INFO'
            },
            'application_insights': {
                'class': 'opencensus.ext.azure.log_exporter.AzureLogHandler',
                'connection_string': config['application_insights']['connection_string'],
                'formatter': 'json',
                'level': 'INFO'
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file', 'application_insights'],
                'level': 'INFO',
                'propagate': True
            },
            'security_scanner': {
                'handlers': ['console', 'file', 'application_insights'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)