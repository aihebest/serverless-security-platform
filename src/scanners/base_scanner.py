# src/scanners/base_scanner.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class SecurityFinding:
    def __init__(
        self,
        finding_id: str,
        severity: str,
        title: str,
        description: str,
        resource_id: str,
        finding_type: str,
        recommendation: str = None,
        details: Dict[str, Any] = None
    ):
        self.finding_id = finding_id
        self.severity = severity
        self.title = title
        self.description = description
        self.resource_id = resource_id
        self.finding_type = finding_type
        self.recommendation = recommendation
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'finding_id': self.finding_id,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'resource_id': self.resource_id,
            'finding_type': self.finding_type,
            'recommendation': self.recommendation,
            'details': self.details,
            'timestamp': self.timestamp
        }

class BaseScanner(ABC):
    def __init__(self, scan_type: str):
        self.scan_type = scan_type
        self.findings: List[SecurityFinding] = []
        self.scan_id = str(uuid.uuid4())
        self.start_time = None
        self.end_time = None

    @abstractmethod
    async def scan(self, target: Any) -> Dict[str, Any]:
        """Implement the scanning logic"""
        pass

    def add_finding(self, finding: SecurityFinding):
        """Add a security finding"""
        self.findings.append(finding)
        logger.info(f"Added finding: {finding.title} ({finding.severity})")

    def get_findings(self) -> List[Dict[str, Any]]:
        """Get all findings as dictionaries"""
        return [finding.to_dict() for finding in self.findings]

    async def run_scan(self, target: Any) -> Dict[str, Any]:
        """Run the scanner and return results"""
        try:
            self.start_time = datetime.utcnow().isoformat()
            logger.info(f"Starting {self.scan_type} scan {self.scan_id}")
            
            # Run the actual scan
            await self.scan(target)
            
            self.end_time = datetime.utcnow().isoformat()
            
            return {
                'scan_id': self.scan_id,
                'scan_type': self.scan_type,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'findings': self.get_findings(),
                'summary': self._generate_summary()
            }
            
        except Exception as e:
            logger.error(f"Scan failed: {str(e)}")
            raise

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate scan summary"""
        severity_counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for finding in self.findings:
            if finding.severity in severity_counts:
                severity_counts[finding.severity] += 1
                
        return {
            'total_findings': len(self.findings),
            'severity_counts': severity_counts,
            'scan_duration': (
                datetime.fromisoformat(self.end_time) - 
                datetime.fromisoformat(self.start_time)
            ).total_seconds() if self.end_time and self.start_time else None
        }