document.addEventListener('DOMContentLoaded', () => {
    // --- Navigation ---
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.page');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('data-target');
            
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            pages.forEach(page => {
                page.classList.remove('active');
                if (page.id === targetId) {
                    page.classList.add('active');
                }
            });
            
            if (targetId === 'config') loadConfig();
            if (targetId === 'sentiment') fetchSentiment();
            if (targetId === 'positions') fetchPositions();
        });
    });

    // --- Config Tabs & Action Buttons ---
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.config-tab-pane');
    const btnSaveConfig = document.getElementById('btn-save-config');
    const btnSaveEnv = document.getElementById('btn-save-env');
    
    function updateConfigActionButtons(targetTab) {
        if (targetTab === 'tab-env') {
            if (btnSaveEnv) btnSaveEnv.style.display = 'inline-block';
            if (btnSaveConfig) btnSaveConfig.style.display = 'none';
        } else {
            if (btnSaveEnv) btnSaveEnv.style.display = 'none';
            if (btnSaveConfig) btnSaveConfig.style.display = 'inline-block';
        }
    }

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-tab');
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            const targetEl = document.getElementById(target);
            if (targetEl) targetEl.classList.add('active');
            updateConfigActionButtons(target);
        });
    });

    // --- Bot Engine Control ---
    const btnStart = document.getElementById('btn-start');
    const btnStop = document.getElementById('btn-stop');
    const controlMsg = document.getElementById('control-msg');
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const uptimeText = document.getElementById('uptime-text');

    async function checkBotStatus() {
        try {
            const res = await fetch('/api/bot/status');
            const data = await res.json();
            if (data.running) {
                btnStart.disabled = true;
                btnStop.disabled = false;
                statusIndicator.className = 'status-online';
                statusText.textContent = 'SYSTEM ONLINE';
                uptimeText.textContent = 'Engine is processing trades...';
            } else {
                btnStart.disabled = false;
                btnStop.disabled = true;
                statusIndicator.className = 'status-offline';
                statusText.textContent = 'SYSTEM OFFLINE';
                
                if (data.last_error) {
                    uptimeText.textContent = `Crash Error: ${data.last_error}`;
                    uptimeText.style.color = 'var(--danger)';
                    controlMsg.textContent = `❌ Terjadi Error: ${data.last_error}`;
                    controlMsg.style.color = 'var(--danger)';
                } else {
                    uptimeText.textContent = 'Waiting for ignition...';
                    uptimeText.style.color = 'var(--text-muted)';
                }
            }
        } catch (e) {
            console.error('Status check failed', e);
        }
    }

    btnStart.addEventListener('click', async () => {
        try {
            controlMsg.textContent = "Memulai trading engine...";
            controlMsg.style.color = 'var(--neon-blue)';
            const res = await fetch('/api/bot/start', { method: 'POST' });
            const data = await res.json();
            controlMsg.textContent = data.message;
            if (data.status === 'success') {
                controlMsg.style.color = 'var(--success)';
            } else {
                controlMsg.style.color = 'var(--danger)';
            }
            setTimeout(checkBotStatus, 1000);
        } catch (e) { 
            controlMsg.textContent = "Error starting engine."; 
            controlMsg.style.color = 'var(--danger)';
        }
    });

    btnStop.addEventListener('click', async () => {
        try {
            controlMsg.textContent = "Mengirim sinyal stop...";
            controlMsg.style.color = 'var(--neon-blue)';
            const res = await fetch('/api/bot/stop', { method: 'POST' });
            const data = await res.json();
            controlMsg.textContent = data.message;
            setTimeout(checkBotStatus, 1500);
        } catch (e) { 
            controlMsg.textContent = "Error stopping engine."; 
            controlMsg.style.color = 'var(--danger)';
        }
    });

    // --- Configuration Logic (.env & JSON) ---
    let currentConfig = {};
    let currentEnv = {};
    const jsonEditor = document.getElementById('json-editor');
    const formInputs = document.querySelectorAll('[id^="cfg-"]');
    const envInputs = document.querySelectorAll('[id^="env-"]');

    async function checkEnvStatus() {
        try {
            const res = await fetch('/api/config/env/status');
            const data = await res.json();
            if (data.status === 'success') {
                const s = data.data;
                updateBadge('badge-binance', s.has_binance_live || s.has_binance_testnet, s.has_binance_live ? 'Live Set' : (s.has_binance_testnet ? 'Testnet Set' : 'Missing'));
                updateBadge('badge-ai', s.has_ai, s.has_ai ? 'Key Active' : 'Missing Key');
                updateBadge('badge-mongo', s.has_mongo, s.has_mongo ? 'URI Set' : 'Missing URI');
            }
        } catch (e) {
            console.error("Failed to check env status", e);
        }
    }

    function updateBadge(badgeId, isReady, label) {
        const el = document.getElementById(badgeId);
        if (!el) return;
        el.className = 'env-badge ' + (isReady ? 'status-ready' : 'status-missing');
        const small = el.querySelector('small');
        if (small) small.textContent = label;
    }

    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            const data = await res.json();
            currentConfig = data.json || {};
            currentEnv = data.env || {};
            
            // Populate Raw JSON Editor
            if (jsonEditor) {
                jsonEditor.value = JSON.stringify(currentConfig, null, 2);
            }
            
            // Populate Dynamic JSON Forms
            formInputs.forEach(input => {
                const key = input.id.replace('cfg-', '');
                if (currentConfig[key] !== undefined) {
                    if (input.type === 'checkbox') {
                        input.checked = currentConfig[key];
                    } else {
                        input.value = currentConfig[key];
                    }
                }
            });

            // Populate .env Forms
            envInputs.forEach(input => {
                const key = input.id.replace('env-', '');
                if (currentEnv[key] !== undefined) {
                    input.value = currentEnv[key];
                }
            });
            
            renderCoinsList();
            renderArrayManager('RSS_FEED_URLS', 'rss-list-container');
            renderArrayManager('MACRO_KEYWORDS', 'macro-list-container');
            checkEnvStatus();
        } catch (e) {
            console.error("Config load error", e);
        }
    }

    // Toggle Password Visibility
    document.querySelectorAll('.btn-toggle-pwd').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (!input) return;
            if (input.type === 'password') {
                input.type = 'text';
                btn.textContent = '🙈';
            } else {
                input.type = 'password';
                btn.textContent = '👁️';
            }
        });
    });

    // Save Environment (.env) Handler
    async function saveEnvConfig() {
        const saveMsg = document.getElementById('config-save-msg');
        try {
            const envPayload = {};
            envInputs.forEach(input => {
                const key = input.id.replace('env-', '');
                envPayload[key] = input.value.trim();
            });

            const res = await fetch('/api/config/env', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ env: envPayload })
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                currentEnv = envPayload;
                checkEnvStatus();
                if (saveMsg) {
                    saveMsg.textContent = "✅ " + data.message;
                    saveMsg.style.color = 'var(--success)';
                    setTimeout(() => saveMsg.textContent = '', 3000);
                }
            } else {
                throw new Error(data.detail || "Gagal menyimpan .env");
            }
        } catch (e) {
            if (saveMsg) {
                saveMsg.textContent = "❌ " + (e.message || "Gagal menyimpan .env");
                saveMsg.style.color = 'var(--danger)';
            }
        }
    }

    if (btnSaveEnv) btnSaveEnv.addEventListener('click', saveEnvConfig);
    const btnSaveEnvInner = document.getElementById('btn-save-env-inner');
    if (btnSaveEnvInner) btnSaveEnvInner.addEventListener('click', saveEnvConfig);

    // --- Array Managers (RSS & Macro) ---
    function renderArrayManager(configKey, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';
        
        const arr = currentConfig[configKey] || [];
        arr.forEach((item, idx) => {
            const div = document.createElement('div');
            div.className = 'list-item';
            div.innerHTML = `
                <span>${item}</span>
                <button class="btn-del-item" onclick="deleteArrayItem('${configKey}', ${idx})">🗑️</button>
            `;
            container.appendChild(div);
        });
    }

    window.deleteArrayItem = (configKey, idx) => {
        if(confirm(`Remove item from ${configKey}?`)) {
            currentConfig[configKey].splice(idx, 1);
            renderArrayManager(configKey, configKey === 'RSS_FEED_URLS' ? 'rss-list-container' : 'macro-list-container');
            updateRawJSON();
        }
    };

    const btnAddRss = document.getElementById('btn-add-rss');
    if (btnAddRss) {
        btnAddRss.addEventListener('click', () => {
            const input = document.getElementById('new-rss-url');
            if(input && input.value.trim()) {
                if(!currentConfig.RSS_FEED_URLS) currentConfig.RSS_FEED_URLS = [];
                currentConfig.RSS_FEED_URLS.push(input.value.trim());
                input.value = '';
                renderArrayManager('RSS_FEED_URLS', 'rss-list-container');
                updateRawJSON();
            }
        });
    }

    const btnAddMacro = document.getElementById('btn-add-macro');
    if (btnAddMacro) {
        btnAddMacro.addEventListener('click', () => {
            const input = document.getElementById('new-macro-kw');
            if(input && input.value.trim()) {
                if(!currentConfig.MACRO_KEYWORDS) currentConfig.MACRO_KEYWORDS = [];
                currentConfig.MACRO_KEYWORDS.push(input.value.trim());
                input.value = '';
                renderArrayManager('MACRO_KEYWORDS', 'macro-list-container');
                updateRawJSON();
            }
        });
    }

    // --- Coins Manager ---
    function renderCoinsList() {
        const container = document.getElementById('coins-list-container');
        if (!container) return;
        container.innerHTML = '';
        
        if (!currentConfig.DAFTAR_KOIN) return;
        
        currentConfig.DAFTAR_KOIN.forEach((coin, idx) => {
            const div = document.createElement('div');
            div.className = 'coin-card';
            div.innerHTML = `
                <div class="coin-info">
                    <h4>${coin.symbol}</h4>
                    <small>${coin.category} | ${coin.leverage}x | $${coin.amount}</small>
                </div>
                <div class="coin-actions">
                    <button onclick="editCoin(${idx})">✏️</button>
                    <button onclick="deleteCoin(${idx})">🗑️</button>
                </div>
            `;
            container.appendChild(div);
        });
    }

    const modal = document.getElementById('coin-modal');
    const closeBtn = document.querySelector('.close-modal');
    const btnSaveCoin = document.getElementById('btn-save-coin');
    let editingCoinIdx = -1;

    window.editCoin = (idx) => {
        editingCoinIdx = idx;
        const coin = currentConfig.DAFTAR_KOIN[idx];
        document.getElementById('modal-coin-symbol').value = coin.symbol;
        document.getElementById('modal-coin-category').value = coin.category;
        document.getElementById('modal-coin-leverage').value = coin.leverage;
        document.getElementById('modal-coin-amount').value = coin.amount;
        document.getElementById('modal-coin-btc-corr').checked = coin.btc_corr || false;
        document.getElementById('modal-coin-keywords').value = (coin.keywords || []).join(', ');
        
        document.getElementById('modal-coin-title').textContent = "Edit Coin";
        if (modal) modal.style.display = 'block';
    };

    window.deleteCoin = (idx) => {
        if(confirm("Are you sure you want to remove this coin?")) {
            currentConfig.DAFTAR_KOIN.splice(idx, 1);
            renderCoinsList();
            updateRawJSON();
        }
    };

    const btnAddCoin = document.getElementById('btn-add-coin');
    if (btnAddCoin) {
        btnAddCoin.addEventListener('click', () => {
            editingCoinIdx = -1;
            document.getElementById('modal-coin-symbol').value = 'NEW/USDT';
            document.getElementById('modal-coin-category').value = 'ALTS';
            document.getElementById('modal-coin-leverage').value = 10;
            document.getElementById('modal-coin-amount').value = 10;
            document.getElementById('modal-coin-btc-corr').checked = true;
            document.getElementById('modal-coin-keywords').value = '';
            
            document.getElementById('modal-coin-title').textContent = "Add Coin";
            if (modal) modal.style.display = 'block';
        });
    }

    if (closeBtn && modal) {
        closeBtn.onclick = () => modal.style.display = 'none';
    }

    if (btnSaveCoin) {
        btnSaveCoin.addEventListener('click', () => {
            const kwRaw = document.getElementById('modal-coin-keywords').value;
            const keywords = kwRaw.split(',').map(s => s.trim()).filter(s => s.length > 0);
            
            const newCoin = {
                symbol: document.getElementById('modal-coin-symbol').value,
                category: document.getElementById('modal-coin-category').value,
                leverage: parseInt(document.getElementById('modal-coin-leverage').value) || 10,
                amount: parseFloat(document.getElementById('modal-coin-amount').value) || 10,
                margin_type: 'isolated',
                btc_corr: document.getElementById('modal-coin-btc-corr').checked,
            };
            
            if (keywords.length > 0) newCoin.keywords = keywords;

            if (editingCoinIdx > -1) {
                currentConfig.DAFTAR_KOIN[editingCoinIdx] = { ...currentConfig.DAFTAR_KOIN[editingCoinIdx], ...newCoin };
            } else {
                if (!currentConfig.DAFTAR_KOIN) currentConfig.DAFTAR_KOIN = [];
                currentConfig.DAFTAR_KOIN.push(newCoin);
            }
            
            if (modal) modal.style.display = 'none';
            renderCoinsList();
            updateRawJSON();
        });
    }

    function updateRawJSON() {
        formInputs.forEach(input => {
            const key = input.id.replace('cfg-', '');
            const isFloat = input.step && input.step.includes('.');
            
            if (input.type === 'checkbox') {
                currentConfig[key] = input.checked;
            } else if (input.type === 'number') {
                currentConfig[key] = isFloat || input.value.includes('.') ? parseFloat(input.value) : parseInt(input.value);
                if(isNaN(currentConfig[key])) currentConfig[key] = 0;
            } else {
                currentConfig[key] = input.value;
            }
        });
        if (jsonEditor) jsonEditor.value = JSON.stringify(currentConfig, null, 2);
    }

    if (btnSaveConfig) {
        btnSaveConfig.addEventListener('click', async () => {
            const saveMsg = document.getElementById('config-save-msg');
            try {
                updateRawJSON();
                const finalConfig = JSON.parse(jsonEditor.value);
                
                const res = await fetch('/api/config/json', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ config: finalConfig })
                });
                const data = await res.json();
                if (saveMsg) {
                    saveMsg.textContent = "✅ " + data.message;
                    saveMsg.style.color = 'var(--success)';
                    setTimeout(() => saveMsg.textContent = '', 3000);
                }
                
                currentConfig = finalConfig;
            } catch (e) {
                if (saveMsg) {
                    saveMsg.textContent = "❌ Format JSON Tidak Valid / Gagal Simpan";
                    saveMsg.style.color = 'var(--danger)';
                }
            }
        });
    }

    // --- Market Sentiment Data ---
    let sentimentChart = null;

    async function fetchSentiment() {
        try {
            const res = await fetch('/api/data/sentiment');
            const data = await res.json();
            
            if (data.data) {
                const latest = data.data;
                const scoreEl = document.getElementById('sentiment-score');
                if (scoreEl) scoreEl.textContent = latest.sentiment_score || '--';
                
                let moodColor = 'var(--text-main)';
                let moodIcon = '😐';
                if (latest.sentiment_score > 60) { moodColor = 'var(--success)'; moodIcon = '🚀'; }
                if (latest.sentiment_score < 40) { moodColor = 'var(--danger)'; moodIcon = '🐻'; }
                
                const moodEl = document.getElementById('sentiment-mood');
                if (moodEl) {
                    moodEl.textContent = `${moodIcon} ${latest.overall_sentiment || 'NEUTRAL'}`;
                    moodEl.style.color = moodColor;
                }
                if (scoreEl) scoreEl.style.color = moodColor;
                
                const phaseEl = document.getElementById('market-phase');
                if (phaseEl) phaseEl.textContent = latest.market_phase || '--';
                
                const summaryEl = document.getElementById('sentiment-summary');
                if (summaryEl) summaryEl.textContent = latest.summary || 'No summary provided.';
                
                const riskEl = document.getElementById('sentiment-risk');
                if (riskEl) riskEl.textContent = latest.risk_assessment || '--';
                
                const driversList = document.getElementById('sentiment-drivers');
                if (driversList) {
                    driversList.innerHTML = '';
                    if (latest.key_drivers && latest.key_drivers.length > 0) {
                        latest.key_drivers.forEach(d => {
                            const li = document.createElement('li');
                            li.textContent = `• ${d}`;
                            driversList.appendChild(li);
                        });
                    } else {
                        driversList.innerHTML = '<li>No specific drivers identified.</li>';
                    }
                }

                if (data.history && data.history.length > 0) {
                    renderSentimentChart(data.history);
                }
            }
        } catch (e) {
            console.error("Failed to load sentiment", e);
        }
    }

    function renderSentimentChart(historyData) {
        const chartCanvas = document.getElementById('sentimentChart');
        if (!chartCanvas) return;
        const ctx = chartCanvas.getContext('2d');
        
        const labels = historyData.map(h => {
            if(!h.last_updated) return '';
            const d = new Date(h.last_updated * 1000);
            return `${d.getHours()}:${d.getMinutes().toString().padStart(2, '0')}`;
        });
        const scores = historyData.map(h => h.sentiment_score);
        
        if (sentimentChart) {
            sentimentChart.data.labels = labels;
            sentimentChart.data.datasets[0].data = scores;
            sentimentChart.update();
        } else {
            sentimentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'AI Sentiment Score',
                        data: scores,
                        borderColor: '#0ea5e9',
                        backgroundColor: 'rgba(14, 165, 233, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: '#0ea5e9'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    }

    // --- Trade Positions ---
    async function fetchPositions() {
        try {
            const res = await fetch('/api/data/positions');
            const result = await res.json();
            
            const tbody = document.getElementById('positions-tbody');
            if (!tbody) return;
            tbody.innerHTML = '';
            
            if (!result.data || Object.keys(result.data).length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No active positions.</td></tr>';
                return;
            }
            
            Object.values(result.data).forEach(pos => {
                const tr = document.createElement('tr');
                
                const pnl = parseFloat(pos.unrealized_pnl) || 0;
                const pnlClass = pnl >= 0 ? 'text-success' : 'text-danger';
                const pnlSign = pnl > 0 ? '+' : '';
                
                const side = (pos.side || 'BUY').toUpperCase();
                const sideClass = side === 'LONG' || side === 'BUY' ? 'text-success' : 'text-danger';
                
                tr.innerHTML = `
                    <td><strong>${pos.symbol}</strong></td>
                    <td class="${sideClass}">${side}</td>
                    <td>${pos.size || '--'}</td>
                    <td>$${pos.entry_price ? parseFloat(pos.entry_price).toFixed(4) : '--'}</td>
                    <td class="${pnlClass}">${pnlSign}$${pnl.toFixed(2)}</td>
                    <td><span style="padding: 4px 8px; border-radius: 4px; background: rgba(59, 130, 246, 0.2); font-size: 11px;">ACTIVE</span></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (e) {
            console.error("Failed to load positions", e);
        }
    }

    // --- Live System Stats Polling ---
    const cpuStatEl = document.getElementById('cpu-stat');
    const memStatEl = document.getElementById('mem-stat');

    async function fetchSystemStats() {
        try {
            const res = await fetch('/api/data/system_stats');
            const data = await res.json();
            if (data.status === 'success') {
                if (cpuStatEl) cpuStatEl.textContent = `${data.cpu_usage}%`;
                if (memStatEl) memStatEl.textContent = `${data.mem_usage_mb} MB`;
            }
        } catch (e) {
            // Abaikan jika server belum responsif
        }
    }

    // --- SSE Logging ---
    const dashboardTerminal = document.getElementById('dashboard-terminal');
    const fullTerminal = document.getElementById('full-terminal');

    function appendLog(msg) {
        let className = 'log-line';
        if (msg.includes('INFO')) className += ' log-info';
        if (msg.includes('WARN')) className += ' log-warn';
        if (msg.includes('ERROR') || msg.includes('FAIL') || msg.includes('Crash')) className += ' log-err';

        const lineHtml = `<div class="${className}">${msg}</div>`;
        if (dashboardTerminal) {
            dashboardTerminal.insertAdjacentHTML('beforeend', lineHtml);
            dashboardTerminal.scrollTop = dashboardTerminal.scrollHeight;
            if (dashboardTerminal.childElementCount > 100) dashboardTerminal.removeChild(dashboardTerminal.firstChild);
        }
        if (fullTerminal) {
            fullTerminal.insertAdjacentHTML('beforeend', lineHtml);
            fullTerminal.scrollTop = fullTerminal.scrollHeight;
            if (fullTerminal.childElementCount > 1000) fullTerminal.removeChild(fullTerminal.firstChild);
        }
    }

    let eventSource = null;
    function connectLogStream() {
        try {
            if (eventSource) eventSource.close();
            eventSource = new EventSource('/api/bot/logs/stream');
            eventSource.onmessage = (e) => appendLog(e.data);
            eventSource.onerror = () => {
                // Auto retry quietly
                setTimeout(connectLogStream, 3000);
            };
        } catch (e) {
            console.error("SSE stream error", e);
        }
    }

    connectLogStream();

    // --- Initialization & Polling ---
    checkBotStatus();
    fetchSystemStats();
    setInterval(checkBotStatus, 4000);
    setInterval(fetchSystemStats, 3000);
    
    setInterval(() => {
        const sentimentPage = document.getElementById('sentiment');
        const positionsPage = document.getElementById('positions');
        if (sentimentPage && sentimentPage.classList.contains('active')) fetchSentiment();
        if (positionsPage && positionsPage.classList.contains('active')) fetchPositions();
    }, 8000);

    // Initial load config on start
    loadConfig();
});
