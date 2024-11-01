// dashboard.js
class SecurityDashboard {
    constructor() {
        this.connection = null;
        this.charts = new DashboardCharts();
        this.notifications = new NotificationManager();
        this.scans = [];
        this.isLoading = false;
        this.initialize();
    }

    async initialize() {
        try {
            await this.setupSignalR();
            this.setupEventListeners();
            await this.loadInitialData();
            this.startPeriodicRefresh();
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.notifications.show('Error', 'Failed to initialize dashboard. Retrying...', 'error');
            // Retry initialization after 5 seconds
            setTimeout(() => this.initialize(), 5000);
        }
    }

    async setupSignalR() {
        try {
            this.connection = new signalR.HubConnectionBuilder()
                .withUrl("/negotiate")
                .withAutomaticReconnect([0, 2000, 5000, 10000, null])
                .configureLogging(signalR.LogLevel.Information)
                .build();

            this.connection.on("newScanResult", (result) => {
                this.handleNewScanResult(result);
            });

            this.connection.onreconnecting(() => {
                this.updateConnectionStatus('reconnecting');
            });

            this.connection.onreconnected(() => {
                this.updateConnectionStatus('connected');
                this.loadInitialData();
            });

            this.connection.onclose(() => {
                this.updateConnectionStatus('disconnected');
            });

            await this.connection.start();
            this.updateConnectionStatus('connected');
        } catch (err) {
            console.error("SignalR Connection Error:", err);
            this.updateConnectionStatus('disconnected');
            throw err;
        }
    }

    async function triggerDependencyScan() {
        try {
            const response = await fetch('/scan/dependencies');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const results = await response.json();
            
            // Update dashboard with new scan results
            this.handleNewScanResult({
                timestamp: results.timestamp,
                scan_type: 'dependency',
                results: results
            });
            
            this.notifications.show(
                'Scan Complete', 
                `Found ${results.vulnerabilities_found} vulnerabilities`,
                results.vulnerabilities_found > 0 ? 'warning' : 'success'
            );
        } catch (error) {
            console.error('Scan failed:', error);
            this.notifications.show('Scan Error', error.message, 'error');
        }
    }
    
    // Add this to your setupEventListeners method
    document.getElementById('scanDepsBtn').addEventListener('click', () => {
        this.triggerDependencyScan();
    });

    async loadInitialData() {
        console.log('Loading initial data...');
        if (this.isLoading) return;
    
        this.isLoading = true;
        this.updateRefreshButton(true);
    
        try {
            console.log('Fetching dashboard data...');
            const response = await fetch('/dashboard-data');
            console.log('Response:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Received data:', data);
            this.updateDashboard(data);
            this.notifications.show('Success', 'Dashboard data updated', 'success');
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.notifications.show('Error', 'Failed to load dashboard data', 'error');
        } finally {
            this.isLoading = false;
            this.updateRefreshButton(false);
        }
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                if (!this.isLoading) {
                    this.loadInitialData();
                }
            });
        }

        // Setup other event listeners as needed
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.loadInitialData();
            }
        });
    }

    startPeriodicRefresh() {
        // Refresh data every 5 minutes
        setInterval(() => {
            if (!document.hidden && !this.isLoading) {
                this.loadInitialData();
            }
        }, 300000);
    }

    async loadInitialData() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.updateRefreshButton(true);

        try {
            const response = await fetch('/dashboard-data');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.updateDashboard(data);
            this.notifications.show('Success', 'Dashboard data updated', 'success');
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.notifications.show('Error', 'Failed to load dashboard data', 'error');
        } finally {
            this.isLoading = false;
            this.updateRefreshButton(false);
        }
    }

    updateRefreshButton(isLoading) {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.disabled = isLoading;
            refreshBtn.innerHTML = isLoading ? 
                '<svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">...</svg> Refreshing...' : 
                'Refresh';
        }
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        if (!statusElement) return;

        const statusColors = {
            connected: 'text-green-400',
            disconnected: 'text-red-400',
            reconnecting: 'text-yellow-400'
        };

        const statusMessages = {
            connected: 'Connected',
            disconnected: 'Disconnected',
            reconnecting: 'Reconnecting...'
        };

        statusElement.className = `${statusColors[status]} text-sm flex items-center`;
        statusElement.innerHTML = `
            <span class="w-2 h-2 rounded-full ${statusColors[status]} mr-2"></span>
            ${statusMessages[status]}
        `;
    }

    updateDashboard(data) {
        // Update Security Score
        this.updateSecurityScore(data.security_score);
        
        // Update Active Issues
        this.updateActiveIssues(data.active_issues);
        
        // Update Compliance Status
        this.updateComplianceStatus(data.compliance_status);
        
        // Update Charts
        this.charts.updateScoreChart(data.recent_scans);
        this.charts.updateIssuesChart(data.active_issues.by_severity);
        
        // Update Recent Scans Table
        this.updateRecentScans(data.recent_scans);
        
        // Store scans data
        this.scans = data.recent_scans;
    }

    updateSecurityScore(scoreData) {
        const scoreElement = document.getElementById('securityScore');
        const scoreChangeElement = document.getElementById('scoreChange');
        
        if (scoreElement) {
            scoreElement.textContent = scoreData.current.toFixed(1);
            scoreElement.className = `text-3xl font-bold ${
                scoreData.current >= 80 ? 'text-green-600' :
                scoreData.current >= 60 ? 'text-yellow-600' : 'text-red-600'
            }`;
        }
        
        if (scoreChangeElement) {
            const trend = scoreData.trend;
            scoreChangeElement.textContent = `${trend.direction} (${Math.abs(trend.change).toFixed(1)}%)`;
            scoreChangeElement.className = `text-sm ${
                trend.direction === 'improving' ? 'text-green-500' : 'text-red-500'
            }`;
        }
    }

    updateActiveIssues(issuesData) {
        const issuesElement = document.getElementById('activeIssues');
        if (issuesElement) {
            issuesElement.textContent = issuesData.total;
            issuesElement.className = `text-3xl font-bold ${
                issuesData.total === 0 ? 'text-green-600' :
                issuesData.total <= 5 ? 'text-yellow-600' : 'text-red-600'
            }`;
        }
    }

    updateComplianceStatus(complianceData) {
        const complianceElement = document.getElementById('complianceScore');
        const complianceStatusElement = document.getElementById('complianceStatus');
        
        if (complianceElement) {
            complianceElement.textContent = complianceData.score.toFixed(1);
            complianceElement.className = `text-3xl font-bold ${
                complianceData.score >= 80 ? 'text-green-600' : 'text-red-600'
            }`;
        }
        
        if (complianceStatusElement) {
            complianceStatusElement.textContent = complianceData.status;
            complianceStatusElement.className = `text-sm ${
                complianceData.score >= 80 ? 'text-green-500' : 'text-red-500'
            }`;
        }
    }

    updateRecentScans(scans) {
        const tbody = document.getElementById('recentScansBody');
        if (!tbody) return;

        tbody.innerHTML = scans.map(scan => `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${new Date(scan.timestamp).toLocaleString()}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                    ${scan.scan_type}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                        ${scan.results.scan_status === 'completed' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'}">
                        ${scan.results.scan_status}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${scan.results.total_issues}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${scan.results.risk_score.toFixed(1)}
                </td>
            </tr>
        `).join('');
    }

    handleNewScanResult(result) {
        // Add new scan to the beginning of the array
        this.scans.unshift(result);
        
        // Keep only the last 10 scans
        if (this.scans.length > 10) {
            this.scans.pop();
        }
        
        // Update UI
        this.updateRecentScans(this.scans);
        
        // Update charts
        this.charts.updateScoreChart(this.scans);
        this.charts.updateIssuesChart(result.results.findings);
        
        // Show notification
        this.notifications.show(
            'New Scan Complete',
            `${result.scan_type} scan completed with ${result.results.total_issues} issues`,
            result.results.total_issues > 0 ? 'warning' : 'success'
        );
    }
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SecurityDashboard();
});