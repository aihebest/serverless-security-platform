# src/monitoring/alerts.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import asyncio
import aiohttp
import json

@dataclass
class Alert:
    severity: str
    message: str
    timestamp: datetime
    context: Dict
    alert_type: str

class AlertManager:
    def __init__(self, config: Dict):
        self.config = config
        self.webhook_urls = config.get('webhook_urls', [])
        self.email_config = config.get('email_config', {})
        self.alert_thresholds = config.get('alert_thresholds', {})

    async def process_findings(self, findings: List[Dict]) -> List[Alert]:
        alerts = []
        severity_counts = self._count_severities(findings)

        for severity, count in severity_counts.items():
            threshold = self.alert_thresholds.get(severity, float('inf'))
            if count >= threshold:
                alerts.append(Alert(
                    severity=severity,
                    message=f"Found {count} {severity} severity issues",
                    timestamp=datetime.utcnow(),
                    context={'count': count, 'threshold': threshold},
                    alert_type='THRESHOLD_EXCEEDED'
                ))

        return alerts

    async def send_alerts(self, alerts: List[Alert]):
        webhook_tasks = [self._send_webhook_alert(alert) for alert in alerts]
        email_tasks = [self._send_email_alert(alert) for alert in alerts]
        
        await asyncio.gather(*webhook_tasks, *email_tasks)

    async def _send_webhook_alert(self, alert: Alert):
        payload = {
            'severity': alert.severity,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat(),
            'context': alert.context,
            'type': alert.alert_type
        }

        async with aiohttp.ClientSession() as session:
            for webhook_url in self.webhook_urls:
                try:
                    async with session.post(webhook_url, json=payload) as response:
                        if response.status != 200:
                            print(f"Failed to send webhook alert: {response.status}")
                except Exception as e:
                    print(f"Error sending webhook alert: {str(e)}")

    async def _send_email_alert(self, alert: Alert):
        # Implement email sending logic here
        pass

    def _count_severities(self, findings: List[Dict]) -> Dict[str, int]:
        counts = {}
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN')
            counts[severity] = counts.get(severity, 0) + 1
        return counts