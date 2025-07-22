// Server Selection Interface JavaScript
class ServerSelectionDashboard {
    constructor() {
        this.currentServerId = '1';
        this.initializeEventListeners();
        this.loadServerData();
        this.startDataRefresh();
    }

    initializeEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Server selection
        document.querySelectorAll('.server-circle').forEach(circle => {
            circle.addEventListener('click', (e) => {
                const serverId = e.currentTarget.dataset.serverId;
                if (serverId) {
                    this.switchServer(serverId);
                } else if (e.currentTarget.classList.contains('add-server')) {
                    this.showAddServerModal();
                }
            });
        });

        // Volume slider
        const volumeSlider = document.getElementById('volume-slider');
        const volumeValue = document.getElementById('volume-value');
        if (volumeSlider && volumeValue) {
            volumeSlider.addEventListener('input', (e) => {
                volumeValue.textContent = e.target.value + '%';
                this.updateVolume(e.target.value);
            });
        }

        // Default volume slider
        const defaultVolumeSlider = document.getElementById('default-volume');
        const defaultVolumeValue = document.getElementById('default-volume-value');
        if (defaultVolumeSlider && defaultVolumeValue) {
            defaultVolumeSlider.addEventListener('input', (e) => {
                defaultVolumeValue.textContent = e.target.value + '%';
            });
        }

        // Avatar upload
        const avatarUpload = document.getElementById('avatar-upload');
        if (avatarUpload) {
            avatarUpload.addEventListener('change', (e) => this.handleAvatarUpload(e));
        }

        // Auto-moderation toggles
        document.querySelectorAll('.automod-settings input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => this.updateAutoModSettings());
        });
    }

    switchTab(tabId) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');

        // Load tab-specific data
        this.loadTabData(tabId);
    }

    switchServer(serverId) {
        this.currentServerId = serverId;

        // Update server selection UI
        document.querySelectorAll('.server-circle').forEach(circle => circle.classList.remove('active'));
        document.querySelector(`[data-server-id="${serverId}"]`).classList.add('active');

        // Load server-specific data
        this.loadServerData();
        this.showMessage('Server switched successfully', 'success');
    }

    async loadServerData() {
        try {
            // Load basic server info
            const serverResponse = await fetch(`/api/servers/${this.currentServerId}`);
            if (serverResponse.ok) {
                const serverData = await serverResponse.json();
                this.updateServerHeader(serverData);
            }

            // Load stats
            const statsResponse = await fetch(`/api/servers/${this.currentServerId}/stats`);
            if (statsResponse.ok) {
                const statsData = await statsResponse.json();
                this.updateStats(statsData);
            }
        } catch (error) {
            console.error('Error loading server data:', error);
            this.showMessage('Error loading server data', 'error');
        }
    }

    async loadTabData(tabId) {
        switch (tabId) {
            case 'music':
                await this.loadMusicData();
                break;
            case 'moderation':
                await this.loadModerationData();
                break;
            case 'minecraft':
                await this.loadMinecraftData();
                break;
            case 'settings':
                await this.loadSettingsData();
                break;
        }
    }

    async loadMusicData() {
        try {
            // Load music status
            const statusResponse = await fetch('/api/music/status');
            if (statusResponse.ok) {
                const statusData = await statusResponse.json();
                this.updateMusicStatus(statusData);
            }

            // Load queue
            const queueResponse = await fetch('/api/music/queue');
            if (queueResponse.ok) {
                const queueData = await queueResponse.json();
                this.updateMusicQueue(queueData);
            }
        } catch (error) {
            console.error('Error loading music data:', error);
        }
    }

    async loadModerationData() {
        try {
            const response = await fetch('/api/moderation/stats');
            if (response.ok) {
                const data = await response.json();
                this.updateModerationStats(data);
            }

            const settingsResponse = await fetch('/api/moderation/settings');
            if (settingsResponse.ok) {
                const settingsData = await settingsResponse.json();
                this.updateModerationSettings(settingsData);
            }
        } catch (error) {
            console.error('Error loading moderation data:', error);
        }
    }

    async loadMinecraftData() {
        try {
            const response = await fetch('/api/servers/minecraft');
            if (response.ok) {
                const servers = await response.json();
                this.updateMinecraftServers(servers);
            }
        } catch (error) {
            console.error('Error loading minecraft data:', error);
        }
    }

    async loadSettingsData() {
        try {
            const response = await fetch('/api/settings/bot');
            if (response.ok) {
                const settings = await response.json();
                this.updateBotSettings(settings);
            }
        } catch (error) {
            console.error('Error loading settings data:', error);
        }
    }

    updateServerHeader(serverData) {
        const serverInfo = document.querySelector('.server-details h1');
        const serverStatus = document.querySelector('.status-online');
        
        if (serverInfo) serverInfo.textContent = serverData.name || 'My Discord Server';
        if (serverStatus) {
            serverStatus.textContent = serverData.bot_online ? 'Online' : 'Offline';
            serverStatus.className = serverData.bot_online ? 'status-online' : 'status-offline';
        }
    }

    updateStats(statsData) {
        const statValues = document.querySelectorAll('.stat-value');
        if (statValues.length >= 4) {
            statValues[0].textContent = statsData.total_members?.toLocaleString() || '1,234';
            statValues[1].textContent = statsData.messages_today?.toLocaleString() || '567';
            statValues[2].textContent = statsData.music_played?.toLocaleString() || '89';
            statValues[3].textContent = statsData.mod_actions?.toLocaleString() || '12';
        }
    }

    updateMusicStatus(statusData) {
        const playPauseBtn = document.querySelector('.play-pause');
        if (playPauseBtn) {
            playPauseBtn.textContent = statusData.is_playing ? '⏸' : '▶';
        }

        const volumeSlider = document.getElementById('volume-slider');
        const volumeValue = document.getElementById('volume-value');
        if (volumeSlider && volumeValue) {
            volumeSlider.value = statusData.volume || 50;
            volumeValue.textContent = (statusData.volume || 50) + '%';
        }
    }

    updateMusicQueue(queueData) {
        const queueList = document.querySelector('.queue-list');
        if (queueList && queueData.queue) {
            // Update queue display with real data
            // For now, keeping the static example data
        }
    }

    updateModerationStats(statsData) {
        // Update moderation statistics in the UI
        console.log('Moderation stats:', statsData);
    }

    updateModerationSettings(settingsData) {
        const antiSpamToggle = document.getElementById('anti-spam');
        const badWordFilterToggle = document.getElementById('bad-word-filter');
        const antiRaidToggle = document.getElementById('anti-raid');
        const antiLinkToggle = document.getElementById('anti-link');

        if (antiSpamToggle) antiSpamToggle.checked = settingsData.anti_spam || false;
        if (badWordFilterToggle) badWordFilterToggle.checked = settingsData.bad_word_filter || false;
        if (antiRaidToggle) antiRaidToggle.checked = settingsData.anti_raid || false;
        if (antiLinkToggle) antiLinkToggle.checked = settingsData.anti_link || false;
    }

    updateMinecraftServers(servers) {
        // Update minecraft server list with real data
        console.log('Minecraft servers:', servers);
    }

    updateBotSettings(settings) {
        const botPrefix = document.getElementById('bot-prefix');
        const defaultVolume = document.getElementById('default-volume');
        const welcomeEnabled = document.getElementById('welcome-enabled');

        if (botPrefix) botPrefix.value = settings.prefix || '!';
        if (defaultVolume) defaultVolume.value = settings.default_volume || 50;
        if (welcomeEnabled) welcomeEnabled.checked = settings.welcome_enabled || false;
    }

    startDataRefresh() {
        // Refresh data every 30 seconds
        setInterval(() => {
            this.loadServerData();
            const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
            this.loadTabData(activeTab);
        }, 30000);
    }

    showAddServerModal() {
        const modal = document.getElementById('add-server-modal');
        if (modal) {
            modal.style.display = 'block';
        }
    }

    showMessage(message, type = 'info') {
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;

        // Insert at top of main content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertBefore(messageDiv, mainContent.firstChild);

            // Remove after 3 seconds
            setTimeout(() => {
                messageDiv.remove();
            }, 3000);
        }
    }

    async handleAvatarUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            this.showMessage('Please select an image file', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('avatar', file);
        formData.append('server_id', this.currentServerId);

        try {
            const response = await fetch('/api/bot/avatar', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                this.showMessage('Bot avatar updated successfully', 'success');
                
                // Update avatar preview
                const botAvatar = document.getElementById('bot-avatar');
                if (botAvatar) {
                    botAvatar.src = data.avatar_url;
                }
            } else {
                this.showMessage('Error updating avatar', 'error');
            }
        } catch (error) {
            console.error('Error uploading avatar:', error);
            this.showMessage('Error uploading avatar', 'error');
        }
    }

    async updateVolume(volume) {
        try {
            const response = await fetch('/api/music/volume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ volume: parseInt(volume) })
            });

            if (!response.ok) {
                console.error('Error updating volume');
            }
        } catch (error) {
            console.error('Error updating volume:', error);
        }
    }

    async updateAutoModSettings() {
        const settings = {
            anti_spam: document.getElementById('anti-spam')?.checked || false,
            bad_word_filter: document.getElementById('bad-word-filter')?.checked || false,
            anti_raid: document.getElementById('anti-raid')?.checked || false,
            anti_link: document.getElementById('anti-link')?.checked || false
        };

        try {
            const response = await fetch('/api/moderation/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            if (response.ok) {
                this.showMessage('Auto-moderation settings updated', 'success');
            } else {
                this.showMessage('Error updating settings', 'error');
            }
        } catch (error) {
            console.error('Error updating auto-mod settings:', error);
            this.showMessage('Error updating settings', 'error');
        }
    }
}

// Global functions for button actions
async function musicControl(action) {
    try {
        const response = await fetch(`/api/music/control/${action}`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            dashboard.showMessage(data.message, 'success');
            dashboard.loadMusicData();
        } else {
            dashboard.showMessage('Error controlling music', 'error');
        }
    } catch (error) {
        console.error('Error controlling music:', error);
        dashboard.showMessage('Error controlling music', 'error');
    }
}

async function addToQueue() {
    const musicUrl = document.getElementById('music-url');
    const url = musicUrl?.value.trim();

    if (!url) {
        dashboard.showMessage('Please enter a YouTube URL or search term', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/music/play', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        if (response.ok) {
            const data = await response.json();
            dashboard.showMessage(data.message, 'success');
            musicUrl.value = '';
            dashboard.loadMusicData();
        } else {
            dashboard.showMessage('Error adding to queue', 'error');
        }
    } catch (error) {
        console.error('Error adding to queue:', error);
        dashboard.showMessage('Error adding to queue', 'error');
    }
}

async function removeFromQueue(index) {
    try {
        const response = await fetch(`/api/music/queue/${index}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            dashboard.showMessage('Removed from queue', 'success');
            dashboard.loadMusicData();
        } else {
            dashboard.showMessage('Error removing from queue', 'error');
        }
    } catch (error) {
        console.error('Error removing from queue:', error);
        dashboard.showMessage('Error removing from queue', 'error');
    }
}

async function loadPlaylist(playlistId) {
    try {
        const response = await fetch(`/api/music/playlist/${playlistId}`, {
            method: 'POST'
        });

        if (response.ok) {
            dashboard.showMessage('Playlist loaded', 'success');
            dashboard.loadMusicData();
        } else {
            dashboard.showMessage('Error loading playlist', 'error');
        }
    } catch (error) {
        console.error('Error loading playlist:', error);
        dashboard.showMessage('Error loading playlist', 'error');
    }
}

async function moderateUser(action) {
    const userId = document.getElementById('target-user')?.value.trim();
    const reason = document.getElementById('mod-reason')?.value.trim();

    if (!userId) {
        dashboard.showMessage('Please enter a user ID or mention', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/moderation/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                action: action,
                reason: reason || 'No reason provided'
            })
        });

        if (response.ok) {
            const data = await response.json();
            dashboard.showMessage(data.message, 'success');
            
            // Clear inputs
            document.getElementById('target-user').value = '';
            document.getElementById('mod-reason').value = '';
            
            dashboard.loadModerationData();
        } else {
            dashboard.showMessage('Error performing moderation action', 'error');
        }
    } catch (error) {
        console.error('Error performing moderation action:', error);
        dashboard.showMessage('Error performing moderation action', 'error');
    }
}

async function saveAutomodSettings() {
    await dashboard.updateAutoModSettings();
}

async function forceUpdateServer(serverId) {
    try {
        const response = await fetch(`/api/minecraft/force-update/${serverId}`, {
            method: 'POST'
        });

        if (response.ok) {
            dashboard.showMessage('Server updated successfully', 'success');
            dashboard.loadMinecraftData();
        } else {
            dashboard.showMessage('Error updating server', 'error');
        }
    } catch (error) {
        console.error('Error updating server:', error);
        dashboard.showMessage('Error updating server', 'error');
    }
}

async function resetServerCounter(serverId) {
    try {
        const response = await fetch(`/api/minecraft/reset-counter/${serverId}`, {
            method: 'POST'
        });

        if (response.ok) {
            dashboard.showMessage('Counter reset successfully', 'success');
            dashboard.loadMinecraftData();
        } else {
            dashboard.showMessage('Error resetting counter', 'error');
        }
    } catch (error) {
        console.error('Error resetting counter:', error);
        dashboard.showMessage('Error resetting counter', 'error');
    }
}

async function removeServer(serverId) {
    if (!confirm('Are you sure you want to remove this server monitoring?')) {
        return;
    }

    try {
        const response = await fetch(`/api/servers/minecraft/${serverId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            dashboard.showMessage('Server monitoring removed', 'success');
            dashboard.loadMinecraftData();
        } else {
            dashboard.showMessage('Error removing server', 'error');
        }
    } catch (error) {
        console.error('Error removing server:', error);
        dashboard.showMessage('Error removing server', 'error');
    }
}

async function addMinecraftServer() {
    const serverIp = document.getElementById('server-ip')?.value.trim();
    const serverPort = document.getElementById('server-port')?.value.trim();

    if (!serverIp) {
        dashboard.showMessage('Please enter a server IP', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/servers/minecraft', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                server_ip: serverIp,
                server_port: parseInt(serverPort) || 25565
            })
        });

        if (response.ok) {
            const data = await response.json();
            dashboard.showMessage(data.message, 'success');
            
            // Clear inputs
            document.getElementById('server-ip').value = '';
            document.getElementById('server-port').value = '25565';
            
            dashboard.loadMinecraftData();
        } else {
            dashboard.showMessage('Error adding server', 'error');
        }
    } catch (error) {
        console.error('Error adding server:', error);
        dashboard.showMessage('Error adding server', 'error');
    }
}

async function changeBotAvatar() {
    document.getElementById('avatar-upload')?.click();
}

async function resetBotAvatar() {
    try {
        const response = await fetch('/api/bot/avatar/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ server_id: dashboard.currentServerId })
        });

        if (response.ok) {
            dashboard.showMessage('Bot avatar reset to default', 'success');
            
            // Update avatar preview
            const botAvatar = document.getElementById('bot-avatar');
            if (botAvatar) {
                botAvatar.src = 'https://cdn.discordapp.com/avatars/bot/avatar.png';
            }
        } else {
            dashboard.showMessage('Error resetting avatar', 'error');
        }
    } catch (error) {
        console.error('Error resetting avatar:', error);
        dashboard.showMessage('Error resetting avatar', 'error');
    }
}

async function saveTokens() {
    const youtubeToken = document.getElementById('youtube-token')?.value.trim();
    const spotifyToken = document.getElementById('spotify-token')?.value.trim();

    try {
        const response = await fetch('/api/settings/tokens', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                youtube_api_key: youtubeToken,
                spotify_api_key: spotifyToken
            })
        });

        if (response.ok) {
            dashboard.showMessage('API tokens saved securely', 'success');
            
            // Clear password fields
            document.getElementById('youtube-token').value = '';
            document.getElementById('spotify-token').value = '';
        } else {
            dashboard.showMessage('Error saving tokens', 'error');
        }
    } catch (error) {
        console.error('Error saving tokens:', error);
        dashboard.showMessage('Error saving tokens', 'error');
    }
}

async function exportLogs() {
    try {
        const response = await fetch('/api/logs/export', {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            dashboard.showMessage(data.message, 'success');
        } else {
            dashboard.showMessage('Error exporting logs', 'error');
        }
    } catch (error) {
        console.error('Error exporting logs:', error);
        dashboard.showMessage('Error exporting logs', 'error');
    }
}

async function restartBot() {
    if (!confirm('Are you sure you want to restart the bot? This may cause temporary downtime.')) {
        return;
    }

    try {
        const response = await fetch('/api/bot/restart', {
            method: 'POST'
        });

        if (response.ok) {
            dashboard.showMessage('Bot restart initiated', 'warning');
        } else {
            dashboard.showMessage('Error restarting bot', 'error');
        }
    } catch (error) {
        console.error('Error restarting bot:', error);
        dashboard.showMessage('Error restarting bot', 'error');
    }
}

async function removeBotFromServer() {
    if (!confirm('Are you sure you want to remove the bot from this server? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/bot/remove/${dashboard.currentServerId}`, {
            method: 'POST'
        });

        if (response.ok) {
            dashboard.showMessage('Bot removal initiated', 'warning');
        } else {
            dashboard.showMessage('Error removing bot', 'error');
        }
    } catch (error) {
        console.error('Error removing bot:', error);
        dashboard.showMessage('Error removing bot', 'error');
    }
}

function closeAddServerModal() {
    const modal = document.getElementById('add-server-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new ServerSelectionDashboard();
});

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('add-server-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});