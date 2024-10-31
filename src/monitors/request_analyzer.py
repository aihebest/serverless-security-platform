from datetime import datetime, UTC
from typing import Dict
import re

class RequestAnalyzer:
    def __init__(self):
        self.malicious_patterns = [
            r'(?i)DROP\s+TABLE',
            r'(?i)DELETE\s+FROM',
            r'(?i)<script>'
        ]

    async def analyze_request(self, request_data: Dict) -> Dict:
        is_malicious = self._check_malicious_patterns(request_data)
        return {
            'timestamp': datetime.now(UTC).isoformat(),
            'threats_detected': is_malicious,
            'blocked': is_malicious
        }

    def _check_malicious_patterns(self, request_data: Dict) -> bool:
        content = str(request_data.get('body', ''))
        return any(re.search(pattern, content) for pattern in self.malicious_patterns)