// static/js/charts.js
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
                        'rgb(239, 68, 68)',
                        'rgb(251, 146, 60)',
                        'rgb(251, 191, 36)',
                        'rgb(34, 197, 94)'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });
    }

    updateScoreChart(scans) {
        this.scoreChart.data.labels = scans.map(scan => 
            new Date(scan.timestamp).toLocaleDateString()
        ).reverse();
        this.scoreChart.data.datasets[0].data = scans.map(scan => 
            scan.results.risk_score
        ).reverse();
        this.scoreChart.update();
    }

    updateIssuesChart(findings) {
        const severityCounts = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };

        findings.forEach(finding => {
            severityCounts[finding.severity.toLowerCase()]++;
        });

        this.issuesChart.data.datasets[0].data = [
            severityCounts.critical,
            severityCounts.high,
            severityCounts.medium,
            severityCounts.low
        ];
        this.issuesChart.update();
    }
}