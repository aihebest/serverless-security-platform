class DashboardCharts {
    constructor() {
        this.scoreChart = this.initializeScoreChart();
        this.issuesChart = this.initializeIssuesChart();
    }

    initializeScoreChart() {
        const ctx = document.getElementById('scoreChart').getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Security Score',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
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
    }

    initializeIssuesChart() {
        const ctx = document.getElementById('issuesChart').getContext('2d');
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgb(239, 68, 68)',  // Critical - Red
                        'rgb(251, 146, 60)', // High - Orange
                        'rgb(251, 191, 36)', // Medium - Yellow
                        'rgb(34, 197, 94)'   // Low - Green
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
    }

    updateScoreChart(scans) {
        const data = scans.map(scan => ({
            x: new Date(scan.timestamp),
            y: scan.results.risk_score
        })).reverse();

        this.scoreChart.data.datasets[0].data = data;
        this.scoreChart.data.labels = data.map(d => 
            d.x.toLocaleDateString()
        );
        this.scoreChart.update();
    }

    updateIssuesChart(severityData) {
        this.issuesChart.data.datasets[0].data = [
            severityData.critical || 0,
            severityData.high || 0,
            severityData.medium || 0,
            severityData.low || 0
        ];
        this.issuesChart.update();
    }
}