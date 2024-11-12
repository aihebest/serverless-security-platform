# src/reporting/report_generator.py

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import asyncio
import json
import os
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt
import io
import base64

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )

    async def generate_security_report(
        self,
        scan_results: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        incidents: List[Dict[str, Any]],
        report_type: str = "full",
        time_period: str = "last_7_days"
    ) -> Dict[str, Any]:
        """Generate a comprehensive security report"""
        try:
            # Process data
            report_data = await self._prepare_report_data(
                scan_results,
                metrics,
                incidents,
                time_period
            )
            
            # Generate charts
            charts = self._generate_charts(report_data)
            
            # Generate report content
            if report_type == "full":
                content = await self._generate_full_report(report_data, charts)
            elif report_type == "executive":
                content = await self._generate_executive_summary(report_data, charts)
            else:
                content = await self._generate_basic_report(report_data, charts)
            
            return {
                'report_id': f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'type': report_type,
                'content': content,
                'generated_at': datetime.utcnow().isoformat(),
                'period': time_period,
                'summary': report_data['summary']
            }
            
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            raise

    async def _prepare_report_data(
        self,
        scan_results: List[Dict[str, Any]],
        metrics: Dict[str, Any],
        incidents: List[Dict[str, Any]],
        time_period: str
    ) -> Dict[str, Any]:
        """Prepare and analyze data for reporting"""
        # Calculate summary statistics
        severity_counts = {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for result in scan_results:
            for finding in result.get('findings', []):
                severity = finding.get('severity', 'LOW')
                if severity in severity_counts:
                    severity_counts[severity] += 1

        # Calculate trends
        risk_score_trend = self._calculate_trend(metrics.get('trend', []))
        
        # Prepare incidents summary
        incident_summary = {
            'total': len(incidents),
            'open': len([i for i in incidents if i['status'] == 'OPEN']),
            'resolved': len([i for i in incidents if i['status'] == 'RESOLVED']),
            'by_priority': {
                'P1': len([i for i in incidents if i['priority'] == 'P1']),
                'P2': len([i for i in incidents if i['priority'] == 'P2']),
                'P3': len([i for i in incidents if i['priority'] == 'P3']),
                'P4': len([i for i in incidents if i['priority'] == 'P4'])
            }
        }

        return {
            'summary': {
                'total_scans': len(scan_results),
                'current_risk_score': metrics.get('risk_score', 0),
                'risk_score_trend': risk_score_trend,
                'total_findings': sum(severity_counts.values()),
                'severity_distribution': severity_counts,
                'incidents': incident_summary
            },
            'details': {
                'scan_results': scan_results,
                'incidents': incidents,
                'metrics': metrics
            },
            'period': time_period
        }

    def _generate_charts(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate charts for the report"""
        charts = {}
        
        # Risk Score Trend
        plt.figure(figsize=(10, 5))
        trend_data = report_data['details']['metrics'].get('trend', [])
        plt.plot(
            [d['timestamp'] for d in trend_data],
            [d['risk_score'] for d in trend_data],
            marker='o'
        )
        plt.title('Risk Score Trend')
        plt.xlabel('Time')
        plt.ylabel('Risk Score')
        plt.grid(True)
        charts['risk_trend'] = self._fig_to_base64(plt)
        plt.close()

        # Severity Distribution
        plt.figure(figsize=(8, 8))
        severity_data = report_data['summary']['severity_distribution']
        plt.pie(
            severity_data.values(),
            labels=severity_data.keys(),
            autopct='%1.1f%%',
            colors=['#dc3545', '#fd7e14', '#ffc107', '#28a745']
        )
        plt.title('Finding Severity Distribution')
        charts['severity_dist'] = self._fig_to_base64(plt)
        plt.close()

        return charts

    async def _generate_full_report(
        self,
        report_data: Dict[str, Any],
        charts: Dict[str, str]
    ) -> str:
        """Generate full detailed report"""
        template = self.env.get_template('full_report.html')
        return template.render(
            data=report_data,
            charts=charts,
            generated_at=datetime.utcnow().isoformat()
        )

    async def _generate_executive_summary(
        self,
        report_data: Dict[str, Any],
        charts: Dict[str, str]
    ) -> str:
        """Generate executive summary report"""
        template = self.env.get_template('executive_summary.html')
        return template.render(
            data=report_data,
            charts=charts,
            generated_at=datetime.utcnow().isoformat()
        )

    async def _generate_basic_report(
        self,
        report_data: Dict[str, Any],
        charts: Dict[str, str]
    ) -> str:
        """Generate basic report"""
        template = self.env.get_template('basic_report.html')
        return template.render(
            data=report_data,
            charts=charts,
            generated_at=datetime.utcnow().isoformat()
        )

    @staticmethod
    def _calculate_trend(trend_data: List[Dict[str, Any]]) -> str:
        """Calculate trend direction and magnitude"""
        if not trend_data or len(trend_data) < 2:
            return "stable"
            
        first = trend_data[-1]['risk_score']
        last = trend_data[0]['risk_score']
        diff = last - first
        
        if abs(diff) < 1:
            return "stable"
        return "improving" if diff > 0 else "degrading"

    @staticmethod
    def _fig_to_base64(fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')