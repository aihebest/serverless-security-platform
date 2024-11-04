# src/monitoring/telemetry.py

import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import stats as stats_module
from opencensus.trace import config_integration
from typing import Dict, Any
import os

class TelemetryClient:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.logger = self._setup_logger()
        self.stats_recorder = stats_module.stats.new_stats_recorder()
        self._setup_metrics_exporter()
        config_integration.trace_integrations(['logging'])

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        handler = AzureLogHandler(connection_string=self.connection_string)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
        logger.addHandler(handler)
        return logger

    def _setup_metrics_exporter(self):
        self.metrics_exporter = metrics_exporter.new_metrics_exporter(
            connection_string=self.connection_string
        )

    def track_event(self, name: str, properties: Dict[str, Any] = None):
        """Track a custom event."""
        self.logger.info(f"Event: {name}", extra={
            "custom_dimensions": properties or {}
        })

    def track_metric(self, name: str, value: float, properties: Dict[str, Any] = None):
        """Track a custom metric."""
        mmap = self.stats_recorder.new_measurement_map()
        mmap.measure_float_put(name, value)
        
        if properties:
            self.logger.info(f"Metric: {name}={value}", extra={
                "custom_dimensions": properties
            })

    def track_exception(self, exception: Exception, properties: Dict[str, Any] = None):
        """Track an exception."""
        self.logger.exception(str(exception), extra={
            "custom_dimensions": properties or {}
        })