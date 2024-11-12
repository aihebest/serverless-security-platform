from datetime import datetime, UTC
from typing import Dict

class ActivityMonitor:
    def __init__(self):
        self.logs = []

    async def audit_logging(self, activity: Dict) -> Dict:
        log_entry = {
            'timestamp': datetime.now(UTC).isoformat(),
            'activity': activity,
            'logged': True
        }
        self.logs.append(log_entry)
        return log_entry

    def log_activity(self, activity: Dict) -> Dict:
        """Helper method for logging activities"""
        return {
            'timestamp': datetime.now(UTC).isoformat(),
            'details': activity,
            'logged': True
        }