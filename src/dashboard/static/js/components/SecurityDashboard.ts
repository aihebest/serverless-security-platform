// src/dashboard/static/js/components/SecurityDashboard.ts

interface SecurityUpdate {
    timestamp: string;
    type: string;
    data: any;
}

class SecurityDashboard {
    private connection: signalR.HubConnection;
    private charts: Map<string, Chart>;
    private updateHandlers: Map<string, (data: any) => void>;
    private lastUpdateTime: Date;

    constructor() {
        this.charts = new Map();
        this.updateHandlers = new Map();
        this.lastUpdateTime = new Date();
        this.initializeSignalR();
        this.setupUpdateHandlers();
        this.initializeCharts();
        this.setupEventListeners();
    }

    private initializeSignalR(): void {
        this.connection = new signalR.HubConnectionBuilder()
            .withUrl('/api/security-hub')
            .withAutomaticReconnect({
                nextRetryDelayInMilliseconds: retryContext => {
                    if (retryContext.elapsedMilliseconds < 60000) {
                        return Math.random() * 10000;
                    } else {
                        return null;
                    }
                }
            })
            .configureLogging(signalR.LogLevel.Information)
            .build();

        // Set up connection handlers
        this.connection.onreconnecting(error => {
            console.log('Reconnecting to security hub...', error);
            this.showConnectionStatus('reconnecting');
        });

        this.connection.onreconnected(connectionId => {
            console.log('Reconnected to security hub');
            this.showConnectionStatus('connected');
            this.requestDataRefresh();
        });

        this.connection.onclose(error => {
            console.log('Connection closed', error);
            this.showConnectionStatus('disconnected');
        });

        // Start the connection
        this.startConnection();
    }

    private setupUpdateHandlers(): void {
        // Register handlers for different update types
        this.updateHandlers.set('securityFinding', (data) => this.handleSecurityFinding(data));
        this.updateHandlers.set('incident', (data) => this.handleIncident(data));
        this.updateHandlers.set('compliance', (data) => this.handleComplianceUpdate(data));
        this.updateHandlers.set('metrics', (data) => this.handleMetricsUpdate(data));
        this.updateHandlers.set('heartbeat', (data) => this.handleHeartbeat(data));

        // Register handlers with SignalR connection
        this.updateHandlers.forEach((handler, type) => {
            this.connection.on(type, handler);
        });
    }

    private async startConnection(): Promise<void> {
        try {
            await this.connection.start();
            console.log('Connected to security hub');
            this.showConnectionStatus('connected');
            this.requestDataRefresh();
        } catch (err) {
            console.error('Error connecting to security hub:', err);
            this.showConnectionStatus('error');
            setTimeout(() => this.startConnection(), 5000);
        }
    }

    private handleSecurityFinding(data: any): void {
        // Update findings chart
        const chart = this.charts.get('findingsChart');
        if (chart) {
            this.updateFindingsChart(chart, data);
        }

        // Update findings list
        this.updateFindingsList(data);

        // Update metrics
        this.updateSecurityMetrics(data);

        // Show notification if critical
        if (data.severity === 'CRITICAL') {
            this.showNotification('Critical Security Finding', data.description);
        }
    }

    private handleIncident(data: any): void {
        // Update incidents view
        this.updateIncidentsView(data);

        // Show notification
        this.showNotification('Security Incident', data.title);

        // Update metrics
        this.updateIncidentMetrics(data);
    }

    private showConnectionStatus(status: 'connected' | 'disconnected' | 'reconnecting' | 'error'): void {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            statusElement.textContent = `Status: ${status}`;
        }
    }

    // Additional methods...
}