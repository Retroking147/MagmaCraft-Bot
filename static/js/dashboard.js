// Discord Bot Dashboard JavaScript
class Dashboard {
    constructor() {
        this.charts = {};
        this.gauges = {};
        this.updateInterval = 30000; // Update every 30 seconds
        this.currentTab = 'dashboard';
        this.musicQueue = [];
        this.currentTrack = null;
        this.isPlaying = false;
        this.init();
    }

    async init() {
        this.setupGauges();
        this.setupMonitoringUrl();
        this.setupVolumeSlider();
        await this.loadData();
        this.startAutoUpdate();
        this.loadModerationStats();
        this.loadMinecraftServers();
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

    setupVolumeSlider() {
        const volumeSlider = document.getElementById('defaultVolume');
        const volumeDisplay = document.getElementById('volumeDisplay');
        
        if (volumeSlider && volumeDisplay) {
            volumeSlider.addEventListener('input', (e) => {
                volumeDisplay.textContent = `${e.target.value}%`;
            });
        }
    }

    loadModerationStats() {
        // Simulate moderation stats
        document.getElementById('warningsToday').textContent = Math.floor(Math.random() * 15);
        document.getElementById('bansWeek').textContent = Math.floor(Math.random() * 5);
        document.getElementById('activeTimeouts').textContent = Math.floor(Math.random() * 8);
        document.getElementById('deletedMessages').textContent = Math.floor(Math.random() * 50);
    }

    loadMinecraftServers() {
        const serverList = document.getElementById('minecraftServerList');
        if (!serverList) return;

        // Simulate server list
        const servers = [
            { name: 'play.hypixel.net:25565', status: 'Online', players: '47,234/200,000' },
            { name: 'mc.mineplex.com:25565', status: 'Online', players: '8,492/20,000' },
            { name: 'play.cubecraft.net:25565', status: 'Offline', players: '0/0' }
        ];

        serverList.innerHTML = servers.map(server => `
            <div class="server-item">
                <div class="server-info">
                    <div class="server-name">${server.name}</div>
                    <div class="server-status">${server.status} • ${server.players} players</div>
                </div>
                <div class="server-actions-inline">
                    <button onclick="updateServer('${server.name}')">Update</button>
                    <button onclick="removeServer('${server.name}')">Remove</button>
                </div>
            </div>
        `).join('');
    }

    showError(message) {
        console.error(message);
        // You could implement a toast notification here
    }

    startAutoUpdate() {
        setInterval(() => {
            if (this.currentTab === 'dashboard') {
                this.loadData();
            }
        }, this.updateInterval);
    }
}

// Tab Navigation
function switchTab(tabName) {
    // Remove active class from all tabs and nav items
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to selected tab and nav item
    document.getElementById(`${tabName}-tab`).classList.add('active');
    document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
    
    // Update current tab
    if (window.dashboardInstance) {
        window.dashboardInstance.currentTab = tabName;
    }
    
    // Load tab-specific content
    if (tabName === 'minecraft') {
        refreshServerList();
    } else if (tabName === 'moderation') {
        loadModerationLog();
    }
}

// Music Controls
function togglePlayPause() {
    const btn = document.getElementById('playPauseBtn');
    const dashboard = window.dashboardInstance;
    
    if (dashboard.isPlaying) {
        btn.textContent = '▶️';
        dashboard.isPlaying = false;
        document.getElementById('musicStatus').textContent = 'Paused';
    } else {
        btn.textContent = '⏸️';
        dashboard.isPlaying = true;
        document.getElementById('musicStatus').textContent = 'Playing';
    }
}

function previousTrack() {
    showNotification('Previous track');
}

function nextTrack() {
    showNotification('Next track');
}

function toggleShuffle() {
    showNotification('Shuffle toggled');
}

function toggleRepeat() {
    showNotification('Repeat toggled');
}

function addMusic() {
    const url = document.getElementById('musicUrl').value;
    if (url) {
        showNotification(`Added to queue: ${url}`);
        document.getElementById('musicUrl').value = '';
        updateQueue();
    }
}

function joinVoice() {
    showNotification('Joining voice channel...');
}

function leaveVoice() {
    showNotification('Left voice channel');
}

function clearQueue() {
    document.getElementById('queueList').innerHTML = '<div class="empty-queue">No songs in queue</div>';
    document.getElementById('queueCount').textContent = '0 songs';
    showNotification('Queue cleared');
}

function shuffleQueue() {
    showNotification('Queue shuffled');
}

function updateQueue() {
    // Simulate queue update
    const queueCount = Math.floor(Math.random() * 10) + 1;
    document.getElementById('queueCount').textContent = `${queueCount} songs`;
    
    const queueList = document.getElementById('queueList');
    queueList.innerHTML = Array.from({ length: queueCount }, (_, i) => `
        <div class="queue-item">
            <div>
                <div class="song-title">Song Title ${i + 1}</div>
                <div class="song-artist">Artist ${i + 1}</div>
            </div>
            <button onclick="removeFromQueue(${i})">Remove</button>
        </div>
    `).join('');
}

function removeFromQueue(index) {
    showNotification(`Removed song from queue`);
    updateQueue();
}

// Moderation Functions
function performModAction() {
    const userId = document.getElementById('userId').value;
    const action = document.getElementById('actionType').value;
    const reason = document.getElementById('reason').value;
    
    if (userId) {
        showNotification(`${action} action performed on ${userId}${reason ? `: ${reason}` : ''}`);
        document.getElementById('userId').value = '';
        document.getElementById('reason').value = '';
        loadModerationLog();
    }
}

function saveAutoModSettings() {
    showNotification('Auto-moderation settings saved');
}

function loadModerationLog() {
    const actionLog = document.getElementById('actionLog');
    if (!actionLog) return;
    
    const actions = [
        { time: '2 minutes ago', action: 'Warned', user: 'User#1234', reason: 'Spam' },
        { time: '15 minutes ago', action: 'Timeout', user: 'User#5678', reason: 'Inappropriate language' },
        { time: '1 hour ago', action: 'Banned', user: 'User#9101', reason: 'Raid attempt' }
    ];
    
    actionLog.innerHTML = actions.map(entry => `
        <div class="log-entry">
            <span class="log-time">${entry.time}</span>
            <span class="log-action">${entry.action}</span>
            <span class="log-user">${entry.user}</span>
            <span class="log-reason">${entry.reason}</span>
        </div>
    `).join('');
}

// Minecraft Management
function addMinecraftServer() {
    const ip = document.getElementById('serverIp').value;
    const port = document.getElementById('serverPort').value;
    const statusName = document.getElementById('statusChannelName').value;
    const countName = document.getElementById('countChannelName').value;
    
    if (ip) {
        showNotification(`Added server monitoring for ${ip}:${port}`);
        document.getElementById('serverIp').value = '';
        document.getElementById('serverPort').value = '25565';
        document.getElementById('statusChannelName').value = '';
        document.getElementById('countChannelName').value = '';
        refreshServerList();
    }
}

function forceUpdateCounters() {
    showNotification('Force updating all counters...');
}

function resetCounters() {
    showNotification('Resetting all counters...');
}

function testConnections() {
    showNotification('Testing server connections...');
}

function exportServerList() {
    showNotification('Exporting server list...');
}

function refreshServerList() {
    if (window.dashboardInstance) {
        window.dashboardInstance.loadMinecraftServers();
    }
}

function updateServer(serverName) {
    showNotification(`Updating ${serverName}...`);
}

function removeServer(serverName) {
    if (confirm(`Remove monitoring for ${serverName}?`)) {
        showNotification(`Removed ${serverName}`);
        refreshServerList();
    }
}

// Settings Functions
function saveGuildSettings() {
    showNotification('Guild settings saved');
}

function saveWelcomeSettings() {
    showNotification('Welcome settings saved');
}

function saveTokens() {
    showNotification('API tokens saved securely');
}

function testToken(service) {
    showNotification(`Testing ${service} token...`);
    setTimeout(() => {
        showNotification(`${service} token is valid`);
    }, 2000);
}

function restartBot() {
    if (confirm('Are you sure you want to restart the bot? This will temporarily disconnect it.')) {
        showNotification('Restarting bot...');
    }
}

function exportLogs() {
    showNotification('Exporting logs...');
}

function clearCache() {
    showNotification('Cache cleared');
}

// Utility Functions
function showNotification(message) {
    // Simple notification system
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #5865f2;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        notification.style.transition = 'all 0.3s ease';
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Copy to clipboard functionality
function copyToClipboard() {
    const urlInput = document.getElementById('monitoringUrl');
    urlInput.select();
    urlInput.setSelectionRange(0, 99999);

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
    window.dashboardInstance = new Dashboard();
});

// Add Chart.js time adapter for time series charts
if (typeof Chart !== 'undefined') {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js';
    document.head.appendChild(script);
    
    script.onload = () => {
        const timeScript = document.createElement('script');
        timeScript.src = 'https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@1.0.1/dist/chartjs-adapter-moment.min.js';
        document.head.appendChild(timeScript);
    };
}