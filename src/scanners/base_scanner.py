# src/scanners/base_scanner.py

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import asyncio
import json
import uuid

class SecurityFinding:
    def __init__(
        self,
        finding_id: str,
        timestamp: datetime,
        severity: str,
        category: str,
        description: str,
        resource: str,
        recommendation: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.finding_id = finding_id
        self.timestamp = timestamp
        self.severity = severity
        self.category = category
        self.description = description
        self.resource = resource
        self.recommendation = recommendation
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'finding_id': self.finding_id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity,
            'category': self.category,
            'description': self.description,
            'resource': self.resource,
            'recommendation': self.recommendation,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityFinding':
        return cls(
            finding_id=data['finding_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            severity=data['severity'],
            category=data['category'],
            description=data['description'],
            resource=data['resource'],
            recommendation=data['recommendation'],
            metadata=data.get('metadata', {})
        )

class BaseScanner(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def scan(self) -> List[SecurityFinding]:
        """Execute the security scan."""
        pass

    @abstractmethod
    async def validate_configuration(self) -> bool:
        """Validate scanner configuration."""
        pass

    async def pre_scan_hooks(self) -> None:
        """Execute actions before scanning."""
        self.logger.info(f"Starting scan with {self.__class__.__name__}")

    async def post_scan_hooks(self, findings: List[SecurityFinding]) -> None:
        """Execute actions after scanning."""
        self.logger.info(f"Completed scan with {len(findings)} findings")
        await self._process_findings(findings)

    async def _process_findings(self, findings: List[SecurityFinding]) -> None:
        """Process and store findings."""
        try:
            for finding in findings:
                await self._store_finding(finding)
                if self._is_critical(finding):
                    await self._send_alert(finding)
        except Exception as e:
            self.logger.error(f"Error processing findings: {str(e)}")

    async def _store_finding(self, finding: SecurityFinding) -> None:
        """Store the finding in the configured storage."""
        # Implementation will depend on your storage solution
        pass

    async def _send_alert(self, finding: SecurityFinding) -> None:
        """Send alert for critical findings."""
        # Implementation will depend on your alerting solution
        pass

    def _is_critical(self, finding: SecurityFinding) -> bool:
        """Determine if a finding is critical."""
        return finding.severity.upper() == 'CRITICAL'

    async def execute_scan(self) -> List[SecurityFinding]:
        """Main execution method with error handling."""
        try:
            # Validate configuration
            if not await self.validate_configuration():
                raise ValueError("Invalid scanner configuration")

            # Execute pre-scan hooks
            await self.pre_scan_hooks()

            # Execute scan
            findings = await self.scan()

            # Execute post-scan hooks
            await self.post_scan_hooks(findings)

            return findings

        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            raise

    def generate_finding_id(self) -> str:
        """Generate a unique finding ID."""
        return str(uuid.uuid4())