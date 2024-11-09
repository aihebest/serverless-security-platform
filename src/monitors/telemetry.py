# src/monitoring/telemetry.py

from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from opencensus.trace.span import SpanKind
import logging
from typing import Dict, Any
import json

class TelemetryClient:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.logger = self._setup_logger()
        self.metrics_exporter = self._setup_metrics()
        self.tracer = self._setup_tracer()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        handler = AzureLogHandler(connection_string=self.connection_string)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
        logger.addHandler(handler)
        return logger

    def _setup_metrics(self) -> metrics_exporter.MetricsExporter:
        return metrics_exporter.new_metrics_exporter(
            connection_string=self.connection_string
        )

    def _setup_tracer(self) -> Tracer:
        return Tracer(
            exporter=AzureExporter(
                connection_string=self.connection_string
            ),
            sampler=ProbabilitySampler(1.0)
        )

    def track_security_scan(self, scanner_name: str, findings: list) -> None:
        """Track security scan execution and findings."""
        with self.tracer.span(name=f"SecurityScan_{scanner_name}") as span:
            span.span_kind = SpanKind.SERVER
            
            # Log scan execution
            self.logger.info(f"Security scan completed: {scanner_name}", extra={
                'custom_dimensions': {
                    'scanner': scanner_name,
                    'findings_count': len(findings),
                    'severity_breakdown': self._get_severity_breakdown(findings)
                }
            })

            # Track metrics
            self._track_scan_metrics(scanner_name, findings)

    def track_compliance_check(self, framework: str, status: Dict[str, Any]) -> None:
        """Track compliance check results."""
        self.logger.info(f"Compliance check completed: {framework}", extra={
            'custom_dimensions': {
                'framework': framework,
                'status': status['status'],
                'score': status['score'],
                'findings_count': len(status['findings'])
            }
        })

    def track_security_alert(self, alert: Dict[str, Any]) -> None:
        """Track security alert generation."""
        self.logger.warning(f"Security alert generated", extra={
            'custom_dimensions': {
                'severity': alert['severity'],
                'category': alert['category'],
                'affected_resources': alert.get('affected_resources', [])
            }
        })

    def _get_severity_breakdown(self, findings: list) -> Dict[str, int]:
        """Calculate severity breakdown from findings."""
        breakdown = {}
        for finding in findings:
            severity = finding.severity
            breakdown[severity] = breakdown.get(severity, 0) + 1
        return breakdown

    def _track_scan_metrics(self, scanner_name: str, findings: list) -> None:
        """Track metrics for the security scan."""
        severity_breakdown = self._get_severity_breakdown(findings)
        
        # Track total findings
        self.metrics_exporter.add_metric(
            name=f"security_scan.findings.total",
            value=len(findings),
            description="Total number of security findings",
            unit="Count",
            tags={'scanner': scanner_name}
        )

        # Track findings by severity
        for severity, count in severity_breakdown.items():
            self.metrics_exporter.add_metric(
                name=f"security_scan.findings.by_severity",
                value=count,
                description="Number of findings by severity",
                unit="Count",
                tags={'scanner': scanner_name, 'severity': severity}
            )