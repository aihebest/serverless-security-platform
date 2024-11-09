// src/dashboard/realtime_manager.ts

import { HubConnection, HubConnectionBuilder, LogLevel } from '@microsoft/signalr';
import { Chart, ChartConfiguration } from 'chart.js';
import { format } from 'date-fns';

interface SecurityMetrics {
    riskScore: number;
    vulnerabilities: {
        critical: number;
        high: number;
        medium: number;
        low: number;
    };
    incidents: {
        open: number;
        investigating: number;
        resolved: number;
    };
    lastUpdated: string;
}

export class RealtimeDashboardManager {
    private connection: HubConnection;
    private charts: Map<string, Chart>;
    private metrics: SecurityMetrics;
    private updateInterval: NodeJS.Timeout | null = null;
    
    constructor() {
        this.charts = new Map();
        this.initializeConnection();
        this.setupCharts();
        this.startPeriodicUpdates();
    }

    private initializeConnection(): void {
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

    private setupCharts(): void {
        // Risk Score Gauge
        const riskGaugeConfig: ChartConfiguration = {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [0, 100],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(200, 200, 200, 0.2)'
                    ],
                    circumference: 180,
                    rotation: 270
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

        // Vulnerability Distribution
        const vulnDistConfig: ChartConfiguration = {
            type: 'bar',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    label: 'Vulnerabilities',
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(255, 159, 64, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        };

        // Initialize charts
        const riskCtx = document.getElementById('riskGauge')?.getContext('2d');
        const vulnCtx = document.getElementById('vulnDist')?.getContext('2d');

        if (riskCtx) {
            this.charts.set('riskGauge', new Chart(riskCtx, riskGaugeConfig));
        }
        if (vulnCtx) {
            this.charts.set('vulnDist', new Chart(vulnCtx, vulnDistConfig));
        }
    }

    private async startConnection(): Promise<void> {
        try {
            await this.connection.start();
            console.log('Connected to security hub');
            this.requestInitialData();
        } catch (err) {
            console.error('Error connecting to security hub:', err);
            setTimeout(() => this.startConnection(), 5000);
        }
    }

    private setupConnectionHandlers(): void {
        this.connection.on('SecurityMetricsUpdate', (metrics: SecurityMetrics) => {
            this.updateDashboard(metrics);
        });

        this.connection.on('SecurityAlert', (alert: any) => {
            this.handleSecurityAlert(alert);
        });
    }

    private updateDashboard(metrics: SecurityMetrics): void {
        this.metrics = metrics;

        // Update risk gauge
        const riskGauge = this.charts.get('riskGauge');
        if (riskGauge) {
            riskGauge.data.datasets[0].data = [metrics.riskScore, 100 - metrics.riskScore];
            riskGauge.update();
        }

        // Update vulnerability distribution
        const vulnDist = this.charts.get('vulnDist');
        if (vulnDist) {
            vulnDist.data.datasets[0].data = [
                metrics.vulnerabilities.critical,
                metrics.vulnerabilities.high,
                metrics.vulnerabilities.medium,
                metrics.vulnerabilities.low
            ];
            vulnDist.update();
        }

        // Update metrics display
        this.updateMetricsDisplay();
    }

    private updateMetricsDisplay(): void {
        const elements = {
            riskScore: document.getElementById('riskScoreValue'),
            criticalVulns: document.getElementById('criticalVulnsValue'),
            openIncidents: document.getElementById('openIncidentsValue'),
            lastUpdated: document.getElementById('lastUpdatedValue')
        };

        if (elements.riskScore) {
            elements.riskScore.textContent = `${this.metrics.riskScore.toFixed(1)}`;
        }
        if (elements.criticalVulns) {
            elements.criticalVulns.textContent = `${this.metrics.vulnerabilities.critical}`;
        }
        if (elements.openIncidents) {
            elements.openIncidents.textContent = `${this.metrics.incidents.open}`;
        }
        if (elements.lastUpdated) {
            elements.lastUpdated.textContent = format(
                new Date(this.metrics.lastUpdated),
                'yyyy-MM-dd HH:mm:ss'
            );
        }
    }

    private handleSecurityAlert(alert: any): void {
        // Create and show notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${alert.severity.toLowerCase()}`;
        notification.innerHTML = `
            <strong>${alert.title}</strong>
            <p>${alert.message}</p>
            <button class="close-btn">&times;</button>
        `;

        const alertsContainer = document.getElementById('alertsContainer');
        if (alertsContainer) {
            alertsContainer.appendChild(notification);
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }
    }

    private startPeriodicUpdates(): void {
        this.updateInterval = setInterval(() => {
            this.requestMetricsUpdate();
        }, 30000); // Update every 30 seconds
    }

    public destroy(): void {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this.connection.stop();
        this.charts.forEach(chart => chart.destroy());
    }

    private async requestMetricsUpdate(): Promise<void> {
        try {
            await this.connection.invoke('RequestMetricsUpdate');
        } catch (err) {
            console.error('Error requesting metrics update:', err);
        }
    }

    private async requestInitialData(): Promise<void> {
        try {
            await this.connection.invoke('RequestInitialData');
        } catch (err) {
            console.error('Error requesting initial data:', err);
        }
    }
}