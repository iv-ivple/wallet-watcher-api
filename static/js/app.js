// API Configuration
const API_BASE_URL = window.location.origin;
let currentWalletAddress = null;

// Get API Key from localStorage
function getApiKey() {
    return localStorage.getItem('wallet_watcher_api_key');
}

// Check authentication
function checkAuth() {
    const apiKey = getApiKey();
    if (!apiKey && window.location.pathname === '/dashboard') {
        window.location.href = '/';
        return false;
    }
    return true;
}

// API Request Helper
async function apiRequest(endpoint, options = {}) {
    const apiKey = getApiKey();
    
    const defaultOptions = {
        headers: {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        showNotification(error.message, 'error');
        throw error;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple alert for now - you can enhance this
    alert(message);
}

// Load Dashboard
async function loadDashboard() {
    if (!checkAuth()) return;
    
    showLoading(true);
    
    try {
        const data = await apiRequest('/api/v1/wallets');
        const wallets = data.wallets || [];
        
        // Update stats
        document.getElementById('totalWallets').textContent = wallets.length;
        
        // Calculate total alerts and transactions
        let totalAlerts = 0;
        let totalTransactions = 0;
        
        for (const wallet of wallets) {
            try {
                const alertsData = await apiRequest(`/api/v1/wallets/${wallet.address}/alerts`);
                totalAlerts += alertsData.count || 0;
                
                const txData = await apiRequest(`/api/v1/wallets/${wallet.address}/transactions`);
                totalTransactions += txData.count || 0;
            } catch (e) {
                console.error('Error loading wallet details:', e);
            }
        }
        
        document.getElementById('totalAlerts').textContent = totalAlerts;
        document.getElementById('totalTransactions').textContent = totalTransactions;
        
        // Display wallets
        displayWallets(wallets);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    } finally {
        showLoading(false);
    }
}

// Display wallets
function displayWallets(wallets) {
    const container = document.getElementById('walletsContainer');
    const noWallets = document.getElementById('noWallets');
    
    if (wallets.length === 0) {
        container.innerHTML = '';
        noWallets.style.display = 'block';
        return;
    }
    
    noWallets.style.display = 'none';
    
    container.innerHTML = wallets.map(wallet => `
        <div class="wallet-card" onclick="showWalletDetail('${wallet.address}')">
            <div class="wallet-header">
                <div>
                    <div class="wallet-label">${wallet.label || 'Unnamed Wallet'}</div>
                    <div class="wallet-address">${formatAddress(wallet.address)}</div>
                </div>
                <span class="badge">Active</span>
            </div>
            <div class="wallet-balance">${wallet.balance} ETH</div>
            <div class="wallet-footer">
                <span>Added: ${formatDate(wallet.created_at)}</span>
                <span>Last checked: ${wallet.last_monitored ? formatDate(wallet.last_monitored) : 'Never'}</span>
            </div>
        </div>
    `).join('');
}

// Format address (show first and last 6 chars)
function formatAddress(address) {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Show Add Wallet Modal
function showAddWalletModal() {
    document.getElementById('addWalletModal').classList.add('show');
}

// Close Modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

// Add Wallet Form Handler
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname === '/dashboard') {
        checkAuth();
        loadDashboard();
    }
    
    // Add Wallet Button
    const addWalletBtn = document.getElementById('addWalletBtn');
    if (addWalletBtn) {
        addWalletBtn.addEventListener('click', showAddWalletModal);
    }
    
    // Add Wallet Form
    const addWalletForm = document.getElementById('addWalletForm');
    if (addWalletForm) {
        addWalletForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const address = document.getElementById('walletAddress').value;
            const label = document.getElementById('walletLabel').value;
            
            showLoading(true);
            
            try {
                await apiRequest('/api/v1/wallets', {
                    method: 'POST',
                    body: JSON.stringify({ address, label })
                });
                
                closeModal('addWalletModal');
                showNotification('Wallet added successfully!');
                loadDashboard();
                
                // Reset form
                addWalletForm.reset();
            } catch (error) {
                console.error('Error adding wallet:', error);
            } finally {
                showLoading(false);
            }
        });
    }
    
    // Logout Button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            localStorage.removeItem('wallet_watcher_api_key');
            window.location.href = '/';
        });
    }
});

// Show Wallet Detail
async function showWalletDetail(address) {
    currentWalletAddress = address;
    document.getElementById('detailWalletAddress').textContent = formatAddress(address);
    document.getElementById('walletDetailModal').classList.add('show');
    
    // Load transactions by default
    switchTab('transactions');
}

// Switch Tab
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
    
    // Load data
    if (tabName === 'transactions') {
        loadTransactions(currentWalletAddress);
    } else if (tabName === 'alerts') {
        loadAlerts(currentWalletAddress);
    }
}

// Load Transactions
async function loadTransactions(address) {
    const container = document.getElementById('transactionsList');
    container.innerHTML = '<p style="color: var(--dove-grey);">Loading transactions...</p>';
    
    try {
        const data = await apiRequest(`/api/v1/wallets/${address}/transactions`);
        const transactions = data.transactions || [];
        
        if (transactions.length === 0) {
            container.innerHTML = '<p style="color: var(--dove-grey);">No transactions found.</p>';
            return;
        }
        
        container.innerHTML = transactions.map(tx => `
            <div class="transaction-item">
                <div class="transaction-hash">Hash: ${formatAddress(tx.tx_hash)}</div>
                <div>Amount: ${tx.value} ETH</div>
                <div style="font-size: 0.85em; color: var(--dove-grey);">${formatDate(tx.timestamp)}</div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: var(--dove-grey);">Error loading transactions.</p>';
        console.error('Error loading transactions:', error);
    }
}

// Load Alerts
async function loadAlerts(address) {
    const container = document.getElementById('alertsList');
    container.innerHTML = '<p style="color: var(--dove-grey);">Loading alerts...</p>';
    
    try {
        const data = await apiRequest(`/api/v1/wallets/${address}/alerts`);
        const alerts = data.alerts || [];
        
        if (alerts.length === 0) {
            container.innerHTML = '<p style="color: var(--dove-grey);">No alerts configured.</p>';
            return;
        }
        
        container.innerHTML = alerts.map(alert => `
            <div class="alert-item">
                <div class="alert-info">
                    <div class="alert-type">${alert.alert_type}</div>
                    <div class="alert-threshold">Threshold: ${alert.threshold || 'N/A'}</div>
                </div>
                <div class="alert-actions">
                    <button onclick="deleteAlert(${alert.id})">Delete</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        container.innerHTML = '<p style="color: var(--dove-grey);">Error loading alerts.</p>';
        console.error('Error loading alerts:', error);
    }
}

// Show Add Alert Form
function showAddAlertForm() {
    const form = document.getElementById('addAlertForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

// Create Alert Form Handler
const createAlertForm = document.getElementById('createAlertForm');
if (createAlertForm) {
    createAlertForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const alertType = document.getElementById('alertType').value;
        const threshold = document.getElementById('alertThreshold').value;
        
        showLoading(true);
        
        try {
            await apiRequest(`/api/v1/wallets/${currentWalletAddress}/alerts`, {
                method: 'POST',
                body: JSON.stringify({
                    alert_type: alertType,
                    threshold: threshold,
                    notification_method: 'email'
                })
            });
            
            showNotification('Alert created successfully!');
            loadAlerts(currentWalletAddress);
            
            // Reset form and hide
            createAlertForm.reset();
            document.getElementById('addAlertForm').style.display = 'none';
        } catch (error) {
            console.error('Error creating alert:', error);
        } finally {
            showLoading(false);
        }
    });
}

// Delete Alert
async function deleteAlert(alertId) {
    if (!confirm('Are you sure you want to delete this alert?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        await apiRequest(`/api/v1/alerts/${alertId}`, {
            method: 'DELETE'
        });
        
        showNotification('Alert deleted successfully!');
        loadAlerts(currentWalletAddress);
    } catch (error) {
        console.error('Error deleting alert:', error);
    } finally {
        showLoading(false);
    }
}

// Show/Hide Loading
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
    }
});
