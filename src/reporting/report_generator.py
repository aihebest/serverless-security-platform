# src/reporting/report_generator.py
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
from azure.cosmos import CosmosClient

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.template_env = Environment(
            loader=FileSystemLoader('src/reporting/templates')
        )
        self._init_cosmos_client()

    def _init_cosmos_client(self):
        """Initialize Cosmos DB client"""
        try:
            connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING')
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            self.database = self.cosmos_client.get_database_client(
                os.getenv('COSMOS_DB_DATABASE_NAME')
            )
            self.container = self.database.get_container_client(
                os.getenv('COSMOS_DB_CONTAINER_NAME')
            )
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB client: {str(e)}")
            self.cosmos_client = None

    async def generate_detailed_report(self, scan_results: Dict[str, Any]) -> str:
        """Generate detailed HTML report from scan results"""
        template = self.template_env.get_template('detailed_report.html')
        
        report_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'scan_results': scan_results,
            'summary': self._generate_summary(scan_results),
            'severity_counts': self._count_severities(scan_results),
            'recommendations': self._generate_recommendations(scan_results)
        }
        
        return template.render(**report_data)

    async def generate_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Generate trend analysis of security scans"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = f"""
            SELECT * FROM c 
            WHERE c.timestamp >= '{start_date.isoformat()}' 
            ORDER BY c.timestamp DESC
            """
            
            scans = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            return {
                'total_scans': len(scans),
                'trend_data': self._analyze_trends(scans),
                'severity_trends': self._analyze_severity_trends(scans),
                'most_common_issues': self._find_common_issues(scans)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate trend analysis: {str(e)}")
            return {}

    def _generate_summary(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of scan results"""
        return {
            'total_findings': len(scan_results.get('findings', [])),
            'scan_status': scan_results.get('status'),
            'scan_duration': scan_results.get('duration'),
            'critical_findings': sum(1 for f in scan_results.get('findings', []) 
                                   if f.get('severity') == 'CRITICAL'),
            'high_findings': sum(1 for f in scan_results.get('findings', []) 
                               if f.get('severity') == 'HIGH'),
            'medium_findings': sum(1 for f in scan_results.get('findings', []) 
                                 if f.get('severity') == 'MEDIUM'),
            'low_findings': sum(1 for f in scan_results.get('findings', []) 
                              if f.get('severity') == 'LOW')
        }

    def _count_severities(self, scan_results: Dict[str, Any]) -> Dict[str, int]:
        """Count findings by severity"""
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in scan_results.get('findings', []):
            severity = finding.get('severity', 'LOW')
            severity_counts[severity] += 1
        return severity_counts

    def _generate_recommendations(self, scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on findings"""
        recommendations = []
        for finding in scan_results.get('findings', []):
            if finding.get('severity') in ['CRITICAL', 'HIGH']:
                recommendations.append({
                    'title': f"Fix {finding.get('type')} issue",
                    'description': finding.get('description'),
                    'severity': finding.get('severity'),
                    'remediation': finding.get('remediation', 'No specific remediation provided')
                })
        return recommendations

    def _analyze_trends(self, scans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in scan results"""
        daily_counts = {}
        severity_trends = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        
        for scan in scans:
            date = scan.get('timestamp', '').split('T')[0]
            if date not in daily_counts:
                daily_counts[date] = {'total': 0, 'severities': {}}
            
            findings = scan.get('findings', [])
            daily_counts[date]['total'] += len(findings)
            
            for finding in findings:
                severity = finding.get('severity', 'LOW')
                if severity not in daily_counts[date]['severities']:
                    daily_counts[date]['severities'][severity] = 0
                daily_counts[date]['severities'][severity] += 1
        
        return {
            'daily_counts': daily_counts,
            'severity_trends': severity_trends
        }

    def _analyze_severity_trends(self, scans: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """Analyze trends in severity levels"""
        severity_trends = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        dates = sorted(set(scan.get('timestamp', '').split('T')[0] for scan in scans))
        
        for date in dates:
            day_scans = [s for s in scans if s.get('timestamp', '').startswith(date)]
            for severity in severity_trends.keys():
                count = sum(
                    sum(1 for f in scan.get('findings', []) if f.get('severity') == severity)
                    for scan in day_scans
                )
                severity_trends[severity].append(count)
                
        return severity_trends

    def _find_common_issues(self, scans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find most common security issues"""
        issue_counts = {}
        
        for scan in scans:
            for finding in scan.get('findings', []):
                issue_type = finding.get('type')
                if issue_type not in issue_counts:
                    issue_counts[issue_type] = {
                        'count': 0,
                        'severity': finding.get('severity'),
                        'description': finding.get('description')
                    }
                issue_counts[issue_type]['count'] += 1
        
        return sorted(
            [{'type': k, **v} for k, v in issue_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]  # Top 10 issues