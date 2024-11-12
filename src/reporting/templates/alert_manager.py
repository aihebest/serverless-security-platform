# src/reporting/alert_manager.py
import logging
import json
import aiohttp
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_username': os.getenv('SMTP_USERNAME'),
            'smtp_password': os.getenv('SMTP_PASSWORD'),
            'from_email': os.getenv('FROM_EMAIL')
        }
        self.alert_thresholds = {
            'CRITICAL': 0,  # Any critical finding
            'HIGH': 3,      # More than 3 high findings
            'MEDIUM': 5     # More than 5 medium findings
        }

    async def process_scan_results(self, scan_results: Dict[str, Any]) -> None:
        """Process scan results and send alerts if needed"""
        try:
            severity_counts = self._count_severities(scan_results)
            alerts = self._generate_alerts(severity_counts, scan_results)
            
            if alerts:
                await self._send_alerts(alerts)
                
        except Exception as e:
            logger.error(f"Failed to process alerts: