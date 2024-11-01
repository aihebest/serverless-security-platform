from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import Dict, Any, List
import hashlib
import json

class BaseScanner(ABC):
    """Enhanced base class for all security scanners"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.scan_history = []
    
    @abstractmethod
    async def scan(self, target: Any) -> Dict:
        """Execute security scan on target"""
        pass
    
    def generate_report(self, findings: List[Dict]) -> Dict:
        """Generate standardized report format with enhanced metadata"""
        report = {
            'timestamp': datetime.now(UTC).isoformat(),
            'findings': findings,
            'total_issues': len(findings),
            'scan_status': 'completed',
            'risk_score': self._calculate_risk_score(findings),
            'scan_id': self._generate_scan_id(findings)
        }
        
        # Store in history for trending
        self.scan_history.append({
            'timestamp': report['timestamp'],
            'risk_score': report['risk_score'],
            'total_issues': report['total_issues']
        })
        
        if len(self.scan_history) > 10:
            self.scan_history.pop(0)
        
        report['trend'] = self._calculate_trend()
        
        return report
    
    def _calculate_risk_score(self, findings: List[Dict]) -> float:
        """Calculate risk score based on findings severity"""
        if not findings:
            return 0.0
        
        severity_weights = {
            'critical': 1.0,
            'high': 0.7,
            'medium': 0.4,
            'low': 0.1
        }
        
        total_weight = sum(
            severity_weights.get(finding.get('severity', 'low'), 0.1)
            for finding in findings
        )
        
        return round(min(total_weight / len(findings), 1.0) * 100, 2)
    
    def _generate_scan_id(self, findings: List[Dict]) -> str:
        """Generate unique scan ID based on content"""
        content = json.dumps(findings, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def _calculate_trend(self) -> Dict:
        """Calculate trend data from scan history"""
        if len(self.scan_history) < 2:
            return {'direction': 'stable', 'change': 0}
        
        current = self.scan_history[-1]['risk_score']
        previous = self.scan_history[-2]['risk_score']
        change = current - previous
        
        return {
            'direction': 'improving' if change < 0 else 'degrading' if change > 0 else 'stable',
            'change': round(change, 2)
        }