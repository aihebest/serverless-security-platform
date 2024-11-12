// src/dashboard/static/js/components/SecurityDashboard.ts

interface SecurityMetrics {
    timestamp: string;
    risk_score: number;
    total_issues: number;
    issues_by_severity: {
        critical: number;
        high: number;
        medium: number;
        low: number;
    };
    trend: Array<{
        timestamp: string;
        risk_score: number;
    }>;
}

interface ScanResult {
    scan_id: string;
    scan_type: string;
    findings: Array<any>;
    summary: any;
    timestamp: string;
}

class SecurityDashboard {
    private metricsChart: Chart;
    private trendChart: Chart;
    private severityChart: Chart;
    private signalRConnection: signalR.HubConnection;
    private updateInterval: number = 30000; // 30 seconds
    private intervalId: number | null = null;

    constructor() {
        this.initializeCharts();
        this.setupSignalR();
        this.startPeriodicUpdates();
    }

    private async initializeCharts() {
        // Risk score gauge
        const riskCtx = document.getElementById('riskScore')?.getContext('2d');
        if (riskCtx) {
            this.metricsChart = new Chart(riskCtx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [0, 100],
                        backgroundColor: ['#4CAF50', '#f3f3f3'],
                        circumference: 180,
                        rotation: 270
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        title: {
                            display: true,
                            text: 'Security Score'
                        }
                    }
                }
            });
        }

        // Trend chart
        const trendCtx = document.getElementById('securityTrend')?.getContext('2d');
        if (trendCtx) {
            this.trendChart = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Security Score',
                        data: [],
                        borderColor: '#4CAF50',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }

        // Severity distribution
        const severityCtx = document.getElementById('severityDistribution')?.getContext('2d');
        if (severityCtx) {
            this.severityChart = new Chart(severityCtx, {
                type: 'bar',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        label: 'Issues',
                        data: [0, 0, 0, 0],
                        backgroundColor: [
                            '#dc3545',
                            '#fd7e14',
                            '#ffc107',
                            '#28a745'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Load initial data
        await this.updateDashboard();
    }

    private setupSignalR() {
        this.signalRConnection = new signalR.HubConnectionBuilder()
            .withUrl('/api/security-hub')
            .withAutomaticReconnect()
            .build();

        this.signalRConnection.on('scanCompleted', (result: any) => {
            this.updateDashboard();
        });

        this.signalRConnection.start().catch(console.error);
    }

    private startPeriodicUpdates() {
        this.intervalId = window.setInterval(() => {
            this.updateDashboard();
        }, this.updateInterval);
    }

    private async updateDashboard() {
        try {
            const [metrics, recentScans] = await Promise.all([
                this.fetchMetrics(),
                this.fetchRecentScans()
            ]);

            this.updateMetricsDisplay(metrics);
            this.updateScanHistory(recentScans);
        } catch (error) {
            console.error('Failed to update dashboard:', error);
        }
    }

    private async fetchMetrics(): Promise<SecurityMetrics> {
        const response = await fetch('/api/metrics');
        if (!response.ok) {
            throw new Error('Failed to fetch metrics');
        }
        return await response.json();
    }

    private async fetchRecentScans(): Promise<ScanResult[]> {
        const response = await fetch('/api/scans/recent');
        if (!response.ok) {
            throw new Error('Failed to fetch recent scans');
        }
        return await response.json();
    }

    private updateMetricsDisplay(metrics: SecurityMetrics) {
        // Update risk score gauge
        this.metricsChart.data.datasets[0].data = [
            metrics.risk_score,
            100 - metrics.risk_score
        ];
        this.metricsChart.update();

        // Update trend chart
        this.trendChart.data.labels = metrics.trend.map(
            t => new Date(t.timestamp).toLocaleTimeString()
        );
        this.trendChart.data.datasets[0].data = metrics.trend.map(
            t => t.risk_score
        );
        this.trendChart.update();

        // Update severity chart
        this.severityChart.data.datasets[0].data = [
            metrics.issues_by_severity.critical,
            metrics.issues_by_severity.high,
            metrics.issues_by_severity.medium,
            metrics.issues_by_severity.low
        ];
        this.severityChart.update();

        // Update summary numbers
        document.getElementById('totalIssues')!.textContent = 
            metrics.total_issues.toString();
        document.getElementById('riskScoreValue')!.textContent = 
            metrics.risk_score.toFixed(1);
    }

    private updateScanHistory(scans: ScanResult[]) {
        const container = document.getElementById('scanHistory');
        if (!container) return;

        container.innerHTML = scans.map(scan => `
            <div class="scan-entry">
                <div class="scan-header">
                    <span class="scan-type">${scan.scan_type}</span>
                    <span class="scan-time">
                        ${new Date(scan.timestamp).toLocaleString()}
                    </span>
                </div>
                <div class="scan-summary">
                    <span class="finding-count">
                        ${scan.findings.length} findings
                    </span>
                    <a href="/api/scan/${scan.scan_id}" class="view-details">
                        View Details
                    </a>
                </div>
            </div>
        `).join('');
    }

    public destroy() {
        if (this.intervalId !== null) {
            window.clearInterval(this.intervalId);
        }
        if (this.signalRConnection) {
            this.signalRConnection.stop();
        }
    }
}