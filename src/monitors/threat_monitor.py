# src/monitors/threat_monitor.py
from datetime import datetime, UTC
from typing import Dict
import re

class ThreatMonitor:
    def __init__(self):
        self.patterns = [
            r'(?i)DROP\s+TABLE',
            r'(?i)DELETE\s+FROM',
            r'(?i)<script>'
        ]

    async def detect_suspicious_activity(self, activity: Dict) -> bool:
        content = str(activity.get('content', ''))
        return any(re.search(pattern, content) for pattern in self.patterns)

    async def analyze_activity(self, activity: Dict) -> Dict:
        is_suspicious = await self.detect_suspicious_activity(activity)
        return {
            'timestamp': datetime.now(UTC).isoformat(),
            'suspicious': is_suspicious,
            'details': activity
        }