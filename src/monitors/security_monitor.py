# src/monitors/security_monitor.py

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from enum import Enum
from src.monitoring.app_insights import app_insights

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class SecurityMonitor:
    async def analyze_scan_results(self, scan_results: Dict[str, Any]) -> SecurityMetrics:
        """Analyze security scan results and update metrics."""
        try:
            findings = scan_results.get('findings', [])
            
            # Track findings metrics
            metrics = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            
            # Analyze findings
            for finding in findings:
                severity = finding.get('severity', 'MEDIUM').lower()
                metrics[severity] += 1
                
                # Track each finding in App Insights
                app_insights.track_event("SecurityFinding", {
                    'severity': severity,
                    'type': finding.get('type'),
                    'component': finding.get('component')
                })
            
            # Track overall metrics
            for severity, count in metrics.items():
                app_insights.track_metric(f"Vulnerabilities_{severity}", count)
            
            total_findings = len(findings)
            app_insights.track_metric("TotalVulnerabilities", total_findings)
            
            # Calculate and track risk score
            risk_score = self._calculate_risk_score(metrics)
            app_insights.track_metric("SecurityRiskScore", risk_score)
            
            return metrics
            
        except Exception as e:
            app_insights.track_exception(e)
            raise