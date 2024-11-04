// src/dashboard/static/js/dashboard.js

class SecurityDashboard {
    constructor() {
        this.charts = new ChartManager();
        this.notifications = new NotificationManager();
        this.timeRange = '24h';
        this.updateInterval = 30000; // 30 seconds
        this.initialize();
    }

    async initialize() {
        this.setupEventListeners();
        await this.loadInitialData();
        this.startPeriodicUpdates();
    }

    setupEventListeners() {
        document.getElementById('timeRange').addEventListener('change', (e) => {
            this.timeRange = e.target.value;
            this.loadInitialData();
        });
    }

    async loadInitialData() {
        try {
            const data = await this.fetchSecurityMetrics(this.timeRange);
            this.updateDashboard(data);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.notifications.showError('Failed to load dashboard data');
        }
    }

    startPeriodicUpdates() {
        setInterval(async () => {
            try {
                const data = await this.fetchSecurityMetrics(this.timeRange);
                this.updateDashboard(data);
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }, this.updateInterval);
    }

    async fetchSecurityMetrics(timeRange) {
        const response = await fetch(`/api/metrics?timeRange=${timeRange}`);
        if (!response.ok) {
            throw new Error('Failed to fetch metrics');
        }
        return await response.json();
    }

    updateDashboard(data) {
        this.updateMetricCards(data.severity_counts);
        this.charts.updateCharts(data);
        this.updateAlertsList(data.alerts);
    }

    updateMetricCards(severityCounts) {
        for (const [severity, count] of Object.entries(severityCounts)) {
            const element = document.getElementById(`${severity.toLowerCase()}Severity`);
            if (element) {
                element.querySelector('.metric-value').textContent = count;
            }
        }
    }

    updateAlertsList(alerts) {
        const alertsList = document.getElementById('alertsList');
        alertsList.innerHTML = alerts
            .map(alert => this.createAlertElement(alert))
            .join('');
    }

    createAlertElement(alert) {
        return `
            <div class="alert-item ${alert.severity.toLowerCase()}">
                <div class="alert-header">
                    <span class="alert-severity">${alert.severity}</span>
                    <span class="alert-time">${new Date(alert.timestamp).toLocaleString()}</span>
                </div>
                <div class="alert-message">${alert.message}</div>
            </div>
        `;
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SecurityDashboard();
});