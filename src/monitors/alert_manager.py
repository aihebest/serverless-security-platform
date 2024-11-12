# src/monitors/alert_manager.py

from typing import Dict, Any, List
import logging
from datetime import datetime
import asyncio
from ..api.signalr_client import SignalRClient

logger = logging.getLogger(__name__)

class SecurityAlert:
    def __init__(
        self,
        alert_id: str,
        severity: str,
        title: str,
        description: str,
        source: str,
        timestamp: str = None
    ):
        self.alert_id = alert_id
        self.severity = severity
        self.title = title
        self.description = description
        self.source = source
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'timestamp': self.timestamp
        }

class AlertManager:
    def __init__(self):
        self.signalr_client = SignalRClient()
        self.alert_thresholds = {
            'risk_score': 70.0,  # Alert if risk score drops below this
            'critical_issues': 1, # Alert on any critical issues
            'high_issues': 3      # Alert if high severity issues exceed this
        }

    async def process_scan_results(self, scan_results: Dict[str, Any]):
        """Process scan results and generate alerts if needed"""
        try:
            alerts = []
            severity_counts = scan_results.get('summary', {}).get('severity_counts', {})

            # Check for critical issues
            if severity_counts.get('CRITICAL', 0) >= self.alert_thresholds['critical_issues']:
                alerts.append(SecurityAlert(
                    alert_id=f"CRIT_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    severity="CRITICAL",
                    title="Critical Security Issues Detected",
                    description=f"Found {severity_counts['CRITICAL']} critical security issues",
                    source="security_scan"
                ))

            # Check for high severity issues
            if severity_counts.get('HIGH', 0) >= self.alert_thresholds['high_issues']:
                alerts.append(SecurityAlert(
                    alert_id=f"HIGH_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    severity="HIGH",
                    title="High Risk Issues Detected",
                    description=f"Found {severity_counts['HIGH']} high severity issues",
                    source="security_scan"
                ))

            # Process and send alerts
            for alert in alerts:
                await self.send_alert(alert)

        except Exception as e:
            logger.error(f"Error processing scan results for alerts: {str(e)}")

    async def send_alert(self, alert: SecurityAlert):
        """Send alert through SignalR"""
        try:
            await self.signalr_client.send_message(
                "securityAlert",
                alert.to_dict()
            )
            logger.info(f"Sent security alert: {alert.title}")
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")

    async def check_metrics(self, metrics: Dict[str, Any]):
        """Check metrics and generate alerts if thresholds are exceeded"""
        try:
            if metrics.get('risk_score', 100) < self.alert_thresholds['risk_score']:
                alert = SecurityAlert(
                    alert_id=f"RISK_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    severity="HIGH",
                    title="Security Risk Score Alert",
                    description=f"Security risk score has dropped below threshold: {metrics['risk_score']}",
                    source="security_metrics"
                )
                await self.send_alert(alert)

        except Exception as e:
            logger.error(f"Error checking metrics for alerts: {str(e)}")