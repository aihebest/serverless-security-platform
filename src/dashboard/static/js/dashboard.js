// static/js/dashboard.js
class SecurityDashboard {
    constructor() {
        this.connection = null;
        this.charts = new DashboardCharts();
        this.notifications = new NotificationManager();
        this.scans = [];
        this.initialize();
    }

    async initialize() {
        await this.setupSignalR();
        this.setupEventListeners();
        this.loadInitialData();
    }

    async setupSignalR() {
        try {
            // Create SignalR connection
            this.connection = new signalR.HubConnectionBuilder()
                .withUrl("/api/negotiate")
                .withAutomaticReconnect()
                .build();

            // Handle real-time updates
            this.connection.on("newScanResult", (result) => {
                this.handleNewScanResult(result);
            });

            // Start connection
            await this.connection.start();
            this.updateConnectionStatus(true);
        } catch (err) {
            console.error("SignalR Connection Error:", err);
            this.updateConnectionStatus(false);
            this.notifications.show("Connection Error", "Failed to connect to real-time updates", "error");
        }
    }

    setupEventListeners() {
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadInitialData();
        });
    }

    async loadInitialData() {
        try {
            const response = await fetch('/api/dashboard-data');
            const data = await response.json();
            this.updateDashboard(data);
        } catch (err) {
            console.error("Failed to load dashboard data:", err);
            this.notifications.show("Data Load Error", "Failed to load dashboard data", "error");
        }
    }

    handleNewScanResult(result) {
        // Update scans array
        this.scans.unshift(result);
        if (this.scans.length > 10) this.scans.pop();

        // Update UI
        this.updateSecurityScore(result.results.risk_score, result.results.trend);
        this.updateActiveIssues(result.results.total_issues);
        this.updateRecentScans();
        
        // Update charts
        this.charts.updateScoreChart(this.scans);
        this.charts.updateIssuesChart(result.results.findings);

        // Show notification
        this.notifications.show(
            "New Scan Complete",
            `${result.scan_type} scan completed with ${result.results.total_issues} issues`,
            result.results.total_issues > 0 ? "warning" : "success"
        );
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        statusElement.className = connected ? 'text-green-400' : 'text-red-400';
        statusElement.textContent = '●';
    }

    updateSecurityScore(score, trend) {
        document.getElementById('securityScore').textContent = score;
        const scoreChange = document.getElementById('scoreChange');
        scoreChange.textContent = `${trend.direction} (${trend.change}%)`;
        scoreChange.className = `text-sm ${trend.direction === 'improving' ? 'text-green-500' : 'text-red-500'}`;
    }

    updateActiveIssues(count) {
        document.getElementById('activeIssues').textContent = count;
    }

    updateRecentScans() {
        const tbody = document.getElementById('recentScansBody');
        tbody.innerHTML = this.scans.map(scan => `
            <tr>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${new Date(scan.timestamp).toLocaleString()}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${scan.scan_type}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${scan.results.scan_status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${scan.results.scan_status}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${scan.results.total_issues}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${scan.results.risk_score}
                </td>
            </tr>
        `).join('');
    }
}