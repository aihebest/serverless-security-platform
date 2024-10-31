# src/scanners/base_scanner.py
from datetime import datetime, UTC
from typing import Dict, Any, List

class BaseScanner:
    """Base class for all scanners"""
    
    async def scan(self, target: Any) -> Dict:
        return {
            'timestamp': datetime.now(UTC).isoformat(),
            'status': 'completed',
            'scanned': True
        }

    async def check_security(self) -> Dict:
        return {
            'secure': True,
            'timestamp': datetime.now(UTC).isoformat()
        }