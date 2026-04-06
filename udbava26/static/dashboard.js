/**
 * Cold Storage Monitoring System
 * Dashboard JavaScript
 */

// Global chart instance
let temperatureChart = null;

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    updateAlertBadge();
    
    // Set up auto-refresh
    setInterval(refreshData, 60000); // Refresh every minute
});

// ==================== CHART FUNCTIONS ====================

function initTemperatureChart() {
    const ctx = document.getElementById('temperatureChart');
    if (!ctx) return;
    
    temperatureChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperature (°C)',
                data: [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6
            }, {
                label: 'Humidity (%)',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'transparent',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 5,
                yAxisID: 'humidity'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14 },
                    bodyFont: { size: 13 }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 12
                    }
                },
                y: {
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                humidity: {
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Humidity (%)'
                    },
                    grid: {
                        display: false
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
    
    // Load initial data
    updateChart();
}

async function updateChart() {
    const unitSelect = document.getElementById('chartUnitSelect');
    const timeSelect = document.getElementById('chartTimeRange');
    
    if (!unitSelect || !timeSelect || !temperatureChart) return;
    
    const unitId = unitSelect.value;
    const hours = timeSelect.value;
    
    try {
        const response = await fetch(`/api/temperature/${unitId}/history?hours=${hours}`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            const labels = data.data.map(r => formatTime(r.recorded_at));
            const temps = data.data.map(r => r.temperature);
            const humidity = data.data.map(r => r.humidity || null);
            
            temperatureChart.data.labels = labels;
            temperatureChart.data.datasets[0].data = temps;
            temperatureChart.data.datasets[1].data = humidity;
            temperatureChart.update();
        }
    } catch (error) {
        console.error('Failed to update chart:', error);
    }
}

// ==================== DATA FUNCTIONS ====================

async function refreshData() {
    try {
        // Refresh summary
        const summaryResponse = await fetch('/api/dashboard/summary');
        const summaryData = await summaryResponse.json();
        
        if (summaryData.success) {
            updateSummaryCards(summaryData.data);
        }
        
        // Refresh chart
        updateChart();
        
        // Update alert badge
        updateAlertBadge();
        
    } catch (error) {
        console.error('Failed to refresh data:', error);
    }
}

function updateSummaryCards(data) {
    // Update card values if they exist
    const cards = document.querySelectorAll('.summary-card');
    if (cards.length >= 4) {
        cards[0].querySelector('h3').textContent = data.total_units;
        cards[1].querySelector('h3').textContent = data.today_readings;
        cards[2].querySelector('h3').textContent = data.active_alerts;
        cards[3].querySelector('h3').textContent = data.units_with_issues;
    }
}

async function updateAlertBadge() {
    try {
        const response = await fetch('/api/alerts?active=true');
        const data = await response.json();
        
        if (data.success) {
            const badge = document.getElementById('alertBadge');
            if (badge) {
                badge.textContent = data.data.length;
                badge.style.display = data.data.length > 0 ? 'block' : 'none';
            }
        }
    } catch (error) {
        console.error('Failed to update alert badge:', error);
    }
}

// ==================== MODAL FUNCTIONS ====================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function openAddReading(unitId) {
    const unitInput = document.getElementById('readingUnitId');
    if (unitInput) {
        unitInput.value = unitId;
    }
    openModal('addReadingModal');
}

// ==================== FORM SUBMISSIONS ====================

async function submitReading(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {
        unit_id: parseInt(formData.get('unit_id')),
        temperature: parseFloat(formData.get('temperature')),
        humidity: formData.get('humidity') ? parseFloat(formData.get('humidity')) : null,
        recorded_by: formData.get('recorded_by') || 'Manual Entry',
        is_manual: true
    };
    
    try {
        showLoading();
        
        const response = await fetch('/api/temperature', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showToast('Temperature reading saved!', 'success');
            closeModal('addReadingModal');
            form.reset();
            
            // Check for alerts
            if (result.evaluation.alerts && result.evaluation.alerts.length > 0) {
                result.evaluation.alerts.forEach(alert => {
                    showToast(alert.message, alert.severity === 'critical' ? 'error' : 'warning');
                });
            }
            
            // Refresh data
            refreshData();
        } else {
            showToast(result.error || 'Failed to save reading', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('An error occurred', 'error');
        console.error('Submit reading error:', error);
    }
}

// ==================== ALERT FUNCTIONS ====================

async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`/api/alerts/${alertId}/acknowledge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ acknowledged_by: 'Admin' })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Alert acknowledged', 'success');
            // Remove alert from list or refresh
            const alertItem = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (alertItem) {
                alertItem.remove();
            } else {
                location.reload();
            }
            updateAlertBadge();
        }
    } catch (error) {
        showToast('Failed to acknowledge alert', 'error');
    }
}

// ==================== UNIT DETAILS ====================

async function showUnitDetails(unitId) {
    try {
        showLoading();
        
        // Fetch unit data and history
        const [unitResponse, historyResponse] = await Promise.all([
            fetch(`/api/units/${unitId}`),
            fetch(`/api/temperature/${unitId}/history?hours=24`)
        ]);
        
        const unitData = await unitResponse.json();
        const historyData = await historyResponse.json();
        
        hideLoading();
        
        if (unitData.success) {
            const unit = unitData.data;
            const history = historyData.data || [];
            
            const modalTitle = document.getElementById('unitDetailsTitle');
            const modalContent = document.getElementById('unitDetailsContent');
            
            modalTitle.textContent = unit.name;
            
            modalContent.innerHTML = `
                <div class="unit-details-grid">
                    <div class="detail-item">
                        <label>Storage Type</label>
                        <span>${unit.storage_type}</span>
                    </div>
                    <div class="detail-item">
                        <label>Location</label>
                        <span>${unit.location || 'Not specified'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Capacity</label>
                        <span>${unit.capacity_tons} tons</span>
                    </div>
                    <div class="detail-item">
                        <label>Safe Range</label>
                        <span>${unit.min_temp}°C to ${unit.max_temp}°C</span>
                    </div>
                </div>
                
                <h4 style="margin-top: 1.5rem; margin-bottom: 1rem;">Recent Readings</h4>
                <div class="mini-chart-container" style="height: 200px;">
                    <canvas id="miniChart"></canvas>
                </div>
                
                <h4 style="margin-top: 1.5rem; margin-bottom: 0.5rem;">Last 10 Readings</h4>
                <div class="readings-table-wrapper" style="max-height: 200px; overflow-y: auto;">
                    <table class="data-table" style="font-size: 0.8125rem;">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Temperature</th>
                                <th>Humidity</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${history.slice(-10).reverse().map(r => `
                                <tr>
                                    <td>${formatTime(r.recorded_at)}</td>
                                    <td>${r.temperature.toFixed(1)}°C</td>
                                    <td>${r.humidity ? r.humidity + '%' : '--'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            openModal('unitDetailsModal');
            
            // Initialize mini chart
            setTimeout(() => {
                const ctx = document.getElementById('miniChart');
                if (ctx && history.length > 0) {
                    new Chart(ctx.getContext('2d'), {
                        type: 'line',
                        data: {
                            labels: history.map(r => formatTime(r.recorded_at)),
                            datasets: [{
                                label: 'Temperature',
                                data: history.map(r => r.temperature),
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                fill: true,
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { display: false } },
                            scales: {
                                x: { display: false },
                                y: { title: { display: true, text: '°C' } }
                            }
                        }
                    });
                }
            }, 100);
        }
    } catch (error) {
        hideLoading();
        showToast('Failed to load unit details', 'error');
    }
}

// ==================== UI HELPERS ====================

function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="toast-icon ${icons[type] || icons.info}"></i>
        <span class="toast-message">${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'toastSlide 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
        document.body.style.overflow = '';
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.active');
        modals.forEach(modal => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
});
