// src/dashboard/static/js/components/ReportPanel.ts

interface Report {
    report_id: string;
    type: string;
    generated_at: string;
    period: string;
    summary: any;
}

class ReportPanel {
    private container: HTMLElement;
    private reports: Report[] = [];
    private updateInterval: number = 60000; // 1 minute
    private intervalId: number | null = null;

    constructor(containerId: string) {
        this.container = document.getElementById(containerId)!;
        this.initialize();
    }

    private async initialize(): Promise<void> {
        await this.loadReports();
        this.setupEventListeners();
        this.startPeriodicUpdates();
    }

    private async loadReports(): Promise<void> {
        try {
            const response = await fetch('/api/v1/reports?limit=5');
            if (!response.ok) throw new Error('Failed to fetch reports');
            
            this.reports = await response.json();
            this.renderReports();
        } catch (error) {
            console.error('Failed to load reports:', error);
            this.showError('Failed to load reports');
        }
    }

    private renderReports(): void {
        if (!this.container) return;

        const content = `
            <div class="reports-panel">
                <div class="panel-header">
                    <h2>Security Reports</h2>
                    <button class="btn-primary" onclick="reportPanel.generateReport()">
                        Generate Report
                    </button>
                </div>
                <div class="reports-list">
                    ${this.reports.map(report => this.renderReportItem(report)).join('')}
                </div>
            </div>
        `;

        this.container.innerHTML = content;
    }

    private renderReportItem(report: Report): string {
        return `
            <div class="report-item">
                <div class="report-info">
                    <h3>${report.type} Report</h3>
                    <p>Generated: ${new Date(report.generated_at).toLocaleString()}</p>
                    <p>Period: ${report.period}</p>
                </div>
                <div class="report-actions">
                    <button onclick="reportPanel.viewReport('${report.report_id}')">
                        View
                    </button>
                    <button onclick="reportPanel.downloadReport('${report.report_id}')">
                        Download
                    </button>
                </div>
            </div>
        `;
    }

    public async generateReport(): Promise<void> {
        try {
            const response = await fetch('/api/v1/reports', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    report_type: 'full',
                    time_period: 'last_7_days',
                    include_charts: true
                })
            });

            if (!response.ok) throw new Error('Failed to generate report');
            
            const result = await response.json();
            this.showSuccess('Report generated successfully');
            await this.loadReports();
        } catch (error) {
            console.error('Failed to generate report:', error);
            this.showError('Failed to generate report');
        }
    }

    public async viewReport(reportId: string): Promise<void> {
        window.open(`/api/v1/reports/${reportId}`, '_blank');
    }

    public async downloadReport(reportId: string): Promise<void> {
        try {
            const response = await fetch(`/api/v1/reports/${reportId}/download`);
            if (!response.ok) throw new Error('Failed to download report');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `security-report-${reportId}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Failed to download report:', error);
            this.showError('Failed to download report');
        }
    }

    private setupEventListeners(): void {
        // Add any event listeners here
    }

    private startPeriodicUpdates(): void {
        this.intervalId = window.setInterval(() => {
            this.loadReports();
        }, this.updateInterval);
    }

    private showError(message: string): void {
        // Show error notification
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        this.container.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    private showSuccess(message: string): void {
        // Show success notification
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.textContent = message;
        this.container.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    public destroy(): void {
        if (this.intervalId !== null) {
            window.clearInterval(this.intervalId);
        }
    }
}

// Initialize the report panel
const reportPanel = new ReportPanel('reportPanel');