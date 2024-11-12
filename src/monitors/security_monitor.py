import asyncio
from datetime import datetime
from typing import Dict, Any
import logging
from azure.cosmos import CosmosClient
from azure.monitor.opentelemetry import configure_azure_monitor
import os

logger = logging.getLogger(__name__)

class SecurityMetrics:
    def __init__(self):
        self.risk_score = 0.0
        self.active_issues = 0
        self.critical_issues = 0
        self.high_issues = 0
        self.medium_issues = 0
        self.low_issues = 0
        self.recent_incidents = []
        self.last_updated = None

class SecurityMonitor:
    def __init__(self):
        self.cosmos_client = CosmosClient.from_connection_string(
            os.getenv('COSMOS_DB_CONNECTION_STRING')
        )
        self.database = self.cosmos_client.get_database_client(
            os.getenv('COSMOS_DB_DATABASE_NAME')
        )
        self.container = self.database.get_container_client('SecurityMetrics')
        
        # Configure App Insights
        configure_azure_monitor(
            connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
        )

    async def monitor_security(self):
        """Main security monitoring loop"""
        while True:
            try:
                metrics = await self.get_current_metrics()
                await self.analyze_security_status(metrics)
                await self.store_metrics(metrics)
                await self.check_thresholds(metrics)
                
                logger.info(f"Security Status: Risk Score {metrics['risk_score']}")
                logger.info(f"Active Issues: {metrics['active_issues']}")
                logger.info(f"Recent Incidents: {len(metrics['incidents'])}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Security monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retry

    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current security metrics"""
        try:
            # Get recent scan results
            query = """
                SELECT TOP 1 *
                FROM c
                WHERE c.type = 'security_metrics'
                ORDER BY c._ts DESC
            """
            
            results = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if results:
                return results[0]
                
            return {
                'risk_score': 100.0,
                'active_issues': 0,
                'incidents': [],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            raise

    async def analyze_security_status(self, metrics: Dict[str, Any]):
        """Analyze security status and trigger alerts if needed"""
        try:
            # Check risk score
            if metrics['risk_score'] < 70:
                await self.trigger_alert(
                    severity='HIGH',
                    title='Low Security Score',
                    description=f"Security score dropped to {metrics['risk_score']}"
                )
                
            # Check critical issues
            if metrics.get('critical_issues', 0) > 0:
                await self.trigger_alert(
                    severity='CRITICAL',
                    title='Critical Security Issues',
                    description=f"Found {metrics['critical_issues']} critical issues"
                )
                
        except Exception as e:
            logger.error(f"Security analysis failed: {str(e)}")

    async def store_metrics(self, metrics: Dict[str, Any]):
        """Store security metrics"""
        try:
            metrics['timestamp'] = datetime.utcnow().isoformat()
            metrics['type'] = 'security_metrics'
            
            await self.container.create_item(body=metrics)
            logger.info("Security metrics stored successfully")
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {str(e)}")

    async def check_thresholds(self, metrics: Dict[str, Any]):
        """Check security thresholds"""
        thresholds = {
            'risk_score_min': 70.0,
            'max_critical_issues': 0,
            'max_high_issues': 3,
            'max_medium_issues': 5
        }
        
        violations = []
        
        if metrics['risk_score'] < thresholds['risk_score_min']:
            violations.append('Risk Score below threshold')
            
        if metrics.get('critical_issues', 0) > thresholds['max_critical_issues']:
            violations.append('Too many critical issues')
            
        if violations:
            await self.trigger_alert(
                severity='HIGH',
                title='Security Threshold Violations',
                description=f"Violations: {', '.join(violations)}"
            )

    async def trigger_alert(self, severity: str, title: str, description: str):
        """Trigger security alert"""
        try:
            alert = {
                'severity': severity,
                'title': title,
                'description': description,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store alert
            await self.container.create_item(
                body={
                    'type': 'security_alert',
                    **alert
                }
            )
            
            logger.warning(f"Security Alert: {title}")
            
            # Could integrate with other notification systems here
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {str(e)}")