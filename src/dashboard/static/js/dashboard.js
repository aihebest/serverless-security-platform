// src/dashboard/static/js/dashboard.js - Update the API URLs

class SecurityDashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:7071';  // Base URL for Azure Functions
        this.initialize();
        this.fetchData();
    }

    async fetchData() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/dashboard-data`);
            const data = await response.json();
            this.updateDashboard(data);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        }
    }

    initialize() {
        this.apiUrl = 'http://localhost:7071/api';
        this.setupCharts();
        this.startDataRefresh();
    }

    setupCharts() {
        // Trend Chart
        const trendCtx = document.getElementById('trendChart');
        this.trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Security Score',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
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

        // Severity Distribution Chart
        const severityCtx = document.getElementById('severityDistribution');
        this.severityChart = new Chart(severityCtx, {
            type: 'doughnut',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    data: [0, 0, 0],
                    backgroundColor: ['#dc3545', '#ffc107', '#28a745']
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    async fetchData() {
        try {
            const response = await fetch(`${this.apiUrl}/dashboard-data`);
            if (!response.ok) throw new Error('Failed to fetch data');
            const data = await response.json();
            this.updateDashboard(data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    updateDashboard(data) {
        // Update severity counts
        document.querySelector('#highSeverity .metric-value').textContent = 
            data.active_issues.by_severity.high;
        document.querySelector('#mediumSeverity .metric-value').textContent = 
            data.active_issues.by_severity.medium;
        document.querySelector('#lowSeverity .metric-value').textContent = 
            data.active_issues.by_severity.low;

        // Update charts
        this.updateCharts(data);
    }

    updateCharts(data) {
        // Update trend chart
        const timestamps = data.recent_scans.map(scan => new Date(scan.timestamp).toLocaleTimeString());
        const scores = data.recent_scans.map(() => data.security_score.current);

        this.trendChart.data.labels = timestamps;
        this.trendChart.data.datasets[0].data = scores;
        this.trendChart.update();

        // Update severity distribution
        const severityCounts = [
            data.active_issues.by_severity.high,
            data.active_issues.by_severity.medium,
            data.active_issues.by_severity.low
        ];
        this.severityChart.data.datasets[0].data = severityCounts;
        this.severityChart.update();
    }

    startDataRefresh() {
        setInterval(() => this.fetchData(), 30000); // Refresh every 30 seconds
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SecurityDashboard();
});