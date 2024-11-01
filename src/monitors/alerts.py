# src/monitoring/alerts.py
from typing import Dict, Any
import aiohttp
import json
from datetime import datetime, UTC

class AlertManager:
    def __init__(self, webhook_url: str, logger):
        self.webhook_url = webhook_url
        self.logger = logger
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> None:
        """Send alert to configured webhook (e.g., Teams, Slack)"""
        try:
            payload = {
                "timestamp": datetime.now(UTC).isoformat(),
                "title": alert_data["title"],
                "severity": alert_data["severity"],
                "description": alert_data["description"],
                "actionUrl": alert_data.get("actionUrl", "")
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload
                ) as response:
                    if response.status != 200:
                        self.logger.log_alert(
                            "high",
                            f"Failed to send alert: {response.status}",
                            {"alert": alert_data}
                        )
        except Exception as e:
            self.logger.log_alert(
                "high",
                f"Alert sending failed: {str(e)}",
                {"alert": alert_data}
            )