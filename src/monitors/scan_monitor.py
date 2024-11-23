from datetime import datetime
import logging
from typing import Dict, Any
from .activity_monitor import ActivityMonitor
from .threat_monitor import ThreatMonitor

class ScanMonitor:
    def __init__(self):
        self.activity_monitor = ActivityMonitor()
        self.threat_monitor = ThreatMonitor()
        self.logger = logging.getLogger(__name__)

    async def track_scan_execution(self, scan_type: str, details: Dict[str, Any]):
        """Track scan execution and monitor for threats"""
        try:
            # Log activity
            activity = {
                'type': 'security_scan',
                'scan_type': scan_type,
                'timestamp': datetime.utcnow().isoformat(),
                'details': details
            }
            await self.activity_monitor.audit_logging(activity)

            # Monitor for suspicious activity
            if await self.threat_monitor.detect_suspicious_activity(activity):
                self.logger.warning(f"Suspicious activity detected in {scan_type} scan")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking scan execution: {str(e)}")
            raise

    async def track_scan_metrics(self, metrics: Dict[str, Any]):
        """Track scan metrics"""
        try:
            await self.activity_monitor.log_metrics(metrics)
        except Exception as e:
            self.logger.error(f"Error tracking metrics: {str(e)}")
            raise