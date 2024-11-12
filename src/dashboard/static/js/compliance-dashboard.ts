// src/dashboard/static/js/compliance-dashboard.ts

interface ComplianceStatus {
    framework: string;
    status: 'COMPLIANT' | 'PARTIAL' | 'NON_COMPLIANT';
    score: number;
    findings: ComplianceFinding[];
    lastUpdated: string;
}

interface ComplianceFinding {
    category: string;
    status: 'PASS' | 'FAIL';
    details: string;
    severity: string;
}

class ComplianceDashboard {
    private complianceChart: Chart;
    private trendsChart: Chart;
    private frameworkDetails: Map<string, ComplianceStatus>;

    constructor() {
        this.frameworkDetails = new Map();
        this.initializeCharts();
        this.setupEventHandlers();
    }

    private initializeCharts(): void {
        // Initialize compliance score chart
        const ctxScore = document.getElementById('complianceScoreChart') as HTMLCanvasElement;
        this.complianceChart = new Chart(ctxScore, {
            type: 'doughnut',
            data: {
                labels: ['OWASP Top 10', 'PCI DSS', 'ISO 27001'],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(153, 102, 255, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Initialize trends chart
        const ctxTrends = document.getElementById('complianceTrendsChart') as HTMLCanvasElement;
        this.trendsChart = new Chart(ctxTrends, {
            type: 'line',
            data: {
                labels: [],
                datasets: []
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

    public updateComplianceStatus(status: ComplianceStatus): void {
        this.frameworkDetails.set(status.framework, status);
        this.updateCharts();
        this.updateComplianceTable();
    }

    private updateCharts(): void {
        // Update compliance score chart
        const scores = Array.from(this.frameworkDetails.values()).map(detail => detail.score);
        this.complianceChart.data.datasets[0].data = scores;
        this.complianceChart.update();

        // Update trends
        this.updateTrendsChart();
    }

    private updateComplianceTable(): void {
        const tableBody = document.getElementById('complianceTable')?.querySelector('tbody');
        if (!tableBody) return;

        tableBody.innerHTML = '';
        this.frameworkDetails.forEach((status, framework) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${framework}</td>
                <td><span class="badge ${this.getStatusClass(status.status)}">${status.status}</span></td>
                <td>${status.score}%</td>
                <td>${status.findings.filter(f => f.status === 'FAIL').length}</td>
                <td>${new Date(status.lastUpdated).toLocaleDateString()}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    private getStatusClass(status: string): string {
        const classMap = {
            'COMPLIANT': 'bg-success',
            'PARTIAL': 'bg-warning',
            'NON_COMPLIANT': 'bg-danger'
        };
        return classMap[status] || 'bg-secondary';
    }
}