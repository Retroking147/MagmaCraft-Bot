// Discord Bot Dashboard JavaScript
class Dashboard {
    constructor() {
        this.charts = {};
        this.gauges = {};
        this.updateInterval = 30000; // Update every 30 seconds
        this.init();
    }

    async init() {
        this.setupGauges();
        this.setupMonitoringUrl();
        await this.loadData();
        this.startAutoUpdate();
    }

    setupGauges() {
        // Create gauge charts using Chart.js
        const gaugeOptions = {
            type: 'doughnut',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                rotation: -90,
                circumference: 180,
                cutout: '75%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                },
                elements: {
                    arc: {
                        borderWidth: 0
                    }
                }
            }
        };

        // Minecraft Counter Gauge
        this.gauges.minecraft = new Chart(
            document.getElementById('minecraftCounterGauge'),
            {
                ...gaugeOptions,
                data: {
                    datasets: [{
                        data: [0, 100],
                        backgroundColor: ['#5865f2', 'rgba(255,255,255,0.1)'],
                        borderWidth: 0
                    }]
                }
            }
        );

        // Bot Usage Gauge
        this.gauges.botUsage = new Chart(
            document.getElementById('botUsageGauge'),
            {
                ...gaugeOptions,
                data: {
                    datasets: [{
                        data: [0, 100],
                        backgroundColor: ['#ff8c42', 'rgba(255,255,255,0.1)'],
                        borderWidth: 0
                    }]
                }
            }
        );

        // Uptime Gauge
        this.gauges.uptime = new Chart(
            document.getElementById('uptimeGauge'),
            {
                ...gaugeOptions,
                data: {
                    datasets: [{
                        data: [0, 100],
                        backgroundColor: ['#57f287', 'rgba(255,255,255,0.1)'],
                        borderWidth: 0
                    }]
                }
            }
        );
    }

    setupMonitoringUrl() {
        const currentUrl = window.location.origin;
        const monitoringUrl = `${currentUrl}/api/health`;
        document.getElementById('monitoringUrl').value = monitoringUrl;
    }

    async loadData() {
        try {
            const response = await fetch('/api/stats');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.updateUI(result.data);
            } else {
                console.error('Failed to load data:', result.message);
                this.showError('Failed to load dashboard data');
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Network error loading dashboard data');
        }
    }

    updateUI(data) {
        // Update bot status indicator
        const statusIndicator = document.getElementById('botStatus');
        const isOnline = data.uptime.current_session_seconds > 0;
        statusIndicator.classList.toggle('online', isOnline);

        // Update main statistics
        document.getElementById('minecraftCounterValue').textContent = this.formatNumber(data.minecraft_counter_updates);
        document.getElementById('botUsageValue').textContent = this.formatNumber(data.total_commands_used);
        document.getElementById('uptimeValue').textContent = `${data.uptime.uptime_percentage}%`;

        // Update server stats
        document.getElementById('serversMonitored').textContent = data.minecraft_stats.servers_monitored;
        document.getElementById('successRate').textContent = `${data.minecraft_stats.success_rate.toFixed(1)}%`;
        document.getElementById('avgResponse').textContent = `${data.minecraft_stats.avg_response_time}ms`;
        document.getElementById('maxPlayers').textContent = data.minecraft_stats.max_players_seen;

        // Update system info
        document.getElementById('botRestarts').textContent = this.formatNumber(data.bot_restarts);
        document.getElementById('guildsJoined').textContent = this.formatNumber(data.guilds_joined);
        document.getElementById('currentSession').textContent = data.uptime.formatted_current;
        document.getElementById('totalUptime').textContent = data.uptime.formatted_total;

        // Update gauges
        this.updateGauge('minecraft', data.minecraft_counter_updates, 10000); // Max expected updates
        this.updateGauge('botUsage', data.total_commands_used, 1000); // Max expected commands
        this.updateGauge('uptime', data.uptime.uptime_percentage, 100);

        // Update charts
        this.updateCommandChart(data.command_breakdown);
        this.updateMinecraftHistory();

        // Update last updated timestamp
        const lastUpdated = new Date(data.last_updated);
        document.getElementById('lastUpdated').textContent = 
            `Last updated: ${lastUpdated.toLocaleString()}`;
    }

    updateGauge(gaugeName, value, max) {
        const percentage = Math.min((value / max) * 100, 100);
        const remaining = 100 - percentage;
        
        this.gauges[gaugeName].data.datasets[0].data = [percentage, remaining];
        this.gauges[gaugeName].update('none');
    }

    updateCommandChart(commandData) {
        const ctx = document.getElementById('commandUsageChart').getContext('2d');
        
        if (this.charts.commands) {
            this.charts.commands.destroy();
        }

        const labels = Object.keys(commandData);
        const data = Object.values(commandData);
        const colors = [
            '#5865f2', '#57f287', '#fee75c', '#ed4245', '#ff8c42',
            '#9146ff', '#00d4aa', '#ff6b6b', '#4ecdc4', '#45b7d1'
        ];

        this.charts.commands = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: '#36393f'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#b9bbbe',
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                }
            }
        });
    }

    async updateMinecraftHistory() {
        try {
            const response = await fetch('/api/minecraft-history');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.renderMinecraftChart(result.data);
            }
        } catch (error) {
            console.error('Error loading Minecraft history:', error);
        }
    }

    renderMinecraftChart(serverData) {
        const ctx = document.getElementById('minecraftHistoryChart').getContext('2d');
        
        if (this.charts.minecraft) {
            this.charts.minecraft.destroy();
        }

        const datasets = [];
        const colors = ['#5865f2', '#57f287', '#fee75c', '#ed4245', '#ff8c42'];
        let colorIndex = 0;

        // Create datasets for each server
        Object.keys(serverData).forEach(serverKey => {
            const server = serverData[serverKey];
            const color = colors[colorIndex % colors.length];
            
            datasets.push({
                label: `${serverKey} Players`,
                data: server.timestamps.map((timestamp, index) => ({
                    x: timestamp,
                    y: server.player_counts[index]
                })),
                borderColor: color,
                backgroundColor: color + '20',
                fill: false,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 6,
                borderWidth: 2
            });

            colorIndex++;
        });

        this.charts.minecraft = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#b9bbbe',
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            displayFormats: {
                                hour: 'HH:mm',
                                minute: 'HH:mm'
                            }
                        },
                        ticks: {
                            color: '#72767d',
                            maxTicksLimit: 12
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#72767d',
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        title: {
                            display: true,
                            text: 'Player Count',
                            color: '#b9bbbe'
                        }
                    }
                }
            }
        });
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    showError(message) {
        console.error(message);
        // You could implement a toast notification here
    }

    startAutoUpdate() {
        setInterval(() => {
            this.loadData();
        }, this.updateInterval);
    }
}

// Copy to clipboard functionality
function copyToClipboard() {
    const urlInput = document.getElementById('monitoringUrl');
    urlInput.select();
    urlInput.setSelectionRange(0, 99999); // For mobile devices

    try {
        document.execCommand('copy');
        
        const copyBtn = document.querySelector('.copy-btn');
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        copyBtn.style.background = '#57f287';
        
        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.background = '';
        }, 2000);
    } catch (err) {
        console.error('Failed to copy text: ', err);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});

// Add Chart.js time adapter for time series charts
if (typeof Chart !== 'undefined') {
    // Import moment.js adapter for Chart.js time handling
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js';
    document.head.appendChild(script);
    
    script.onload = () => {
        const timeScript = document.createElement('script');
        timeScript.src = 'https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@1.0.1/dist/chartjs-adapter-moment.min.js';
        document.head.appendChild(timeScript);
    };
}