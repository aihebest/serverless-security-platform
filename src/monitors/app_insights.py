# src/monitoring/app_insights.py

import json
import os
from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from applicationinsights import TelemetryClient
import logging

class ApplicationInsights:
    def __init__(self):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'application-insights.json')
        with open(config_path) as f:
            self.config = json.load(f)
            
        # Initialize telemetry client
        self.telemetry_client = TelemetryClient(self.config['instrumentationKey'])
        
        # Setup tracer
        self.tracer = Tracer(
            exporter=AzureExporter(
                connection_string=self.config['connectionString']
            ),
            sampler=ProbabilitySampler(1.0)
        )
        
        # Setup logging
        self._setup_logging()
        
        # Setup metrics
        self.metrics_exporter = metrics_exporter.new_metrics_exporter(
            connection_string=self.config['connectionString']
        )

    def _setup_logging(self):
        """Configure logging with Application Insights"""
        handler = AzureLogHandler(
            connection_string=self.config['connectionString']
        )
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-5s %(message)s'))
        
        logger = logging.getLogger('security_platform')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def track_event(self, name: str, properties: dict = None):
        """Track custom event"""
        self.telemetry_client.track_event(name, properties)

    def track_metric(self, name: str, value: float, properties: dict = None):
        """Track custom metric"""
        self.telemetry_client.track_metric(name, value, properties=properties)

    def track_exception(self, exception: Exception, properties: dict = None):
        """Track exception"""
        self.telemetry_client.track_exception(exception, properties=properties)

    def flush(self):
        """Flush all telemetry"""
        self.telemetry_client.flush()

# Usage example
app_insights = ApplicationInsights()

# Track security events
def track_security_scan(scan_result: dict):
    app_insights.track_event(
        name="SecurityScan",
        properties={
            "scan_id": scan_result.get("id"),
            "vulnerabilities_found": len(scan_result.get("findings", [])),
            "risk_score": scan_result.get("risk_score")
        }
    )
    
    # Track metrics
    app_insights.track_metric(
        name="SecurityRiskScore",
        value=scan_result.get("risk_score", 0)
    )