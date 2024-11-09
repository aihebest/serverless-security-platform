// src/dashboard/static/js/components/SecurityDashboard.ts

import { Chart, ChartConfiguration } from 'chart.js';
import { HubConnection, HubConnectionBuilder, LogLevel } from '@microsoft/signalr';

interface SecurityMetrics {
    findings: number;
    incidents: number;
    riskScore: number;
    complianceScore: number;
    lastUpdated: string;
}

interface ChartData {
    labels: string[];
    datasets: Array<{
        label: string;
        data: number[];
        backgroundColor?: string[];
        borderColor?: string[];
        fill?: boolean;
    }>;
}

interface SecurityFinding {
    id: string;
    timestamp: string;
    severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
    description: string;
    source: string;
    status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED';
}

export class SecurityDashboard {
    private connection: HubConnection;
    private charts: Map<string, Chart>;
    private updateHandlers: Map<string, (data: any) => void>;
    private lastUpdateTime: Date;
    private metrics: SecurityMetrics;
    private offlineCache: Map<string, any[]>;
    
    constructor() {
        this.charts = new Map();
        this.updateHandlers = new Map();
        this.lastUpdateTime = new Date();
        this.offlineCache = new Map();
        this.initializeSignalR();
        this.setupUpdateHandlers();
        this.initializeCharts();
        this.setupEventListeners();
        this.initializeMetrics();
    }

    private initializeMetrics(): void {
        this.metrics = {
            findings: 0,
            incidents: 0,
            riskScore: 0,
            complianceScore: 0,
            lastUpdated: new Date().toISOString()
        };
    }

    private initializeSignalR(): void {
        this.connection = new HubConnectionBuilder()
            .withUrl('/api/security-hub')
            .withAutomaticReconnect({
                nextRetryDelayInMilliseconds: retryContext => {
                    if (retryContext.elapsedMilliseconds < 60000) {
                        return Math.random() * 10000;
                    }
                    return null;
                }
            })
            .configureLogging(LogLevel.Information)
            .build();

        this.setupConnectionHandlers();
        this.startConnection();
    }

    private setupConnectionHandlers(): void {
        this.connection.onreconnecting(error => {
            console.log('Reconnecting to security hub...', error);
            this.showConnectionStatus('reconnecting');
            this.enableOfflineMode();
        });

        this.connection.onreconnected(connectionId => {
            console.log('Reconnected to security hub');
            this.showConnectionStatus('connected');
            this.syncOfflineData();
            this.requestDataRefresh();
        });

        this.connection.onclose(error => {
            console.log('Connection closed', error);
            this.showConnectionStatus('disconnected');
            this.enableOfflineMode();
        });
    }

    private initializeCharts(): void {
        // Risk Score Gauge
        const riskCtx = document.getElementById('risk-gauge')?.getContext('2d');
        if (riskCtx) {
            this.charts.set('riskGauge', new Chart(riskCtx, this.getRiskGaugeConfig()));
        }

        // Findings Trend
        const trendCtx = document.getElementById('findings-trend')?.getContext('2d');
        if (trendCtx) {
            this.charts.set('findingsTrend', new Chart(trendCtx, this.getFindingsTrendConfig()));
        }

        // Severity Distribution
        const severityCtx = document.getElementById('severity-distribution')?.getContext('2d');
        if (severityCtx) {
            this.charts.set('severityDist', new Chart(severityCtx, this.getSeverityDistConfig()));
        }
    }

    private getRiskGaugeConfig(): ChartConfiguration {
        return {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#ff6b6b', '#e9ecef'],
                    circumference: 180,
                    rotation: 270,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: { enabled: false },
                    legend: { display: false }
                }
            }
        };
    }

    private updateCharts(type: string, data: any): void {
        const chart = this.charts.get(type);
        if (!chart) return;

        switch (type) {
            case 'riskGauge':
                this.updateRiskGauge(chart, data);
                break;
            case 'findingsTrend':
                this.updateFindingsTrend(chart, data);
                break;
            case 'severityDist':
                this.updateSeverityDist(chart, data);
                break;
        }
    }

    private handleSecurityFinding(finding: SecurityFinding): void {
        // Cache finding if offline
        if (!this.connection.state) {
            this.cacheOfflineData('findings', finding);
            return;
        }

        // Update metrics
        this.metrics.findings++;
        this.metrics.lastUpdated = new Date().toISOString();

        // Update UI
        this.updateFindingsList(finding);
        this.updateCharts('findingsTrend', finding);
        this.updateRiskScore();

        // Show notification for critical findings
        if (finding.severity === 'CRITICAL') {
            this.showNotification('Critical Security Finding', finding.description);
        }
    }

    private showNotification(title: string, message: string): void {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, { body: message });
        }
    }

    private cacheOfflineData(type: string, data: any): void {
        const cache = this.offlineCache.get(type) || [];
        cache.push({ data, timestamp: new Date().toISOString() });
        this.offlineCache.set(type, cache);
    }

    private async syncOfflineData(): Promise<void> {
        for (const [type, data] of this.offlineCache.entries()) {
            try {
                await this.connection.invoke('SyncOfflineData', type, data);
                this.offlineCache.delete(type);
            } catch (error) {
                console.error(`Failed to sync offline ${type} data:`, error);
            }
        }
    }

    private enableOfflineMode(): void {
        const offlineIndicator = document.getElementById('offline-indicator');
        if (offlineIndicator) {
            offlineIndicator.style.display = 'block';
        }
    }

    public destroy(): void {
        this.charts.forEach(chart => chart.destroy());
        this.connection.stop();
    }
}

export default SecurityDashboard;