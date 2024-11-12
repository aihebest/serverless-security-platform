# src/monitoring/logger.py
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from datetime import datetime, UTC
from typing import Dict, Any

class SecurityLogger:
    def __init__(self, connection_string: str):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add Azure Application Insights handler
        self.logger.addHandler(
            AzureLogHandler(
                connection_string=connection_string
            )
        )
        
        # Add console handler for local debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log security-related events with standardized format"""
        event_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        self.logger.info(f"Security Event: {event_type}", extra={
            "custom_dimensions": event_data
        })
    
    def log_alert(self, severity: str, message: str, context: Dict[str, Any]) -> None:
        """Log security alerts with severity levels"""
        alert_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": severity,
            "message": message,
            "context": context
        }
        
        if severity.lower() == "critical":
            self.logger.critical(f"Security Alert: {message}", extra={
                "custom_dimensions": alert_data
            })
        elif severity.lower() == "high":
            self.logger.error(f"Security Alert: {message}", extra={
                "custom_dimensions": alert_data
            })
        else:
            self.logger.warning(f"Security Alert: {message}", extra={
                "custom_dimensions": alert_data
            })