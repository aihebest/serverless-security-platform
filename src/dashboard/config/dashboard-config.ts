// src/dashboard/config/dashboard-config.ts

export const DashboardConfig = {
    api: {
        baseUrl: process.env.REACT_APP_API_BASE_URL || 'https://fa-security-automation.azurewebsites.net',
        endpoints: {
            scan: '/api/scan',
            metrics: '/api/metrics',
            incidents: '/api/incidents'
        }
    },
    signalR: {
        hubUrl: process.env.REACT_APP_SIGNALR_HUB_URL || 'https://securityauto.service.signalr.net/api',
        hubName: 'securityHub'
    },
    refresh: {
        interval: 30000, // 30 seconds
        retryAttempts: 3
    },
    charts: {
        colors: {
            critical: '#dc3545',
            high: '#fd7e14',
            medium: '#ffc107',
            low: '#20c997'
        }
    }
};

export const SecurityThresholds = {
    critical: 9.0,
    high: 7.0,
    medium: 4.0,
    low: 0.0
};