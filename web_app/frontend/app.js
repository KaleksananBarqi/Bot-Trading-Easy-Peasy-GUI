document.addEventListener('DOMContentLoaded', () => {
    // --- Security Utilities ---
    function escapeHtml(str) {
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // --- Central Time Formatter (WIB / UTC+7) ---
    function formatWIB(timestamp, formatType = 'table') {
        if (!timestamp) return '--';
        let date;
        if (typeof timestamp === 'number') {
            date = new Date(timestamp < 10000000000 ? timestamp * 1000 : timestamp);
        } else if (typeof timestamp === 'string') {
            let s = timestamp.trim();
            // Jika format string adalah ISO naive tanpa timezone offset, tambahkan 'Z' agar di-parse sebagai UTC
            if (/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}/.test(s) && !s.includes('+') && !s.endsWith('Z')) {
                s = s.replace(' ', 'T') + 'Z';
            }
            date = new Date(s);
        } else if (timestamp instanceof Date) {
            date = timestamp;
        } else {
            return String(timestamp);
        }

        if (isNaN(date.getTime())) return String(timestamp);

        const tz = 'Asia/Jakarta';

        if (formatType === 'time') {
            return date.toLocaleTimeString('id-ID', { timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) + ' WIB';
        } else if (formatType === 'time-short') {
            return date.toLocaleTimeString('id-ID', { timeZone: tz, hour: '2-digit', minute: '2-digit', hour12: false }) + ' WIB';
        } else if (formatType === 'chart') {
            const dStr = date.toLocaleDateString('id-ID', { timeZone: tz, day: '2-digit', month: '2-digit' });
            const tStr = date.toLocaleTimeString('id-ID', { timeZone: tz, hour: '2-digit', minute: '2-digit', hour12: false });
            return `${dStr} ${tStr}`;
        } else if (formatType === 'table') {
            const dStr = date.toLocaleDateString('id-ID', { timeZone: tz, day: '2-digit', month: '2-digit', year: 'numeric' });
            const tStr = date.toLocaleTimeString('id-ID', { timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            return `${dStr} ${tStr} WIB`;
        } else if (formatType === 'full') {
            const dStr = date.toLocaleDateString('id-ID', { timeZone: tz, weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
            const tStr = date.toLocaleTimeString('id-ID', { timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            return `${dStr}, ${tStr} WIB`;
        } else {
            const dStr = date.toLocaleDateString('id-ID', { timeZone: tz, day: '2-digit', month: '2-digit', year: 'numeric' });
            const tStr = date.toLocaleTimeString('id-ID', { timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            return `${dStr} ${tStr} WIB`;
        }
    }

    // --- Real-time Live WIB Clock ---
    function updateLiveClock() {
        const clockEl = document.getElementById('live-wib-clock');
        const dateEl = document.getElementById('live-wib-date');
        if (!clockEl && !dateEl) return;
        
        const now = new Date();
        const tz = 'Asia/Jakarta';
        if (clockEl) {
            clockEl.textContent = now.toLocaleTimeString('id-ID', { timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) + ' WIB';
        }
        if (dateEl) {
            dateEl.textContent = now.toLocaleDateString('id-ID', { timeZone: tz, weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
        }
    }
    updateLiveClock();
    setInterval(updateLiveClock, 1000);

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
            if (targetId === 'ai-recap') loadAIEvaluations();
            if (targetId === 'positions') fetchPositions();
            if (targetId === 'history') loadTradeHistoryAndAnalytics();
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

    // Set initial button state for active tab
    updateConfigActionButtons('tab-env');

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
    const formInputs = document.querySelectorAll('input[id^="cfg-"], select[id^="cfg-"], textarea[id^="cfg-"]');
    const envInputs = document.querySelectorAll('input[id^="env-"], select[id^="env-"], textarea[id^="env-"]');

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
            const dynamicFormInputs = document.querySelectorAll('input[id^="cfg-"], select[id^="cfg-"], textarea[id^="cfg-"]');
            dynamicFormInputs.forEach(input => {
                if (!input || !input.id) return;
                const key = input.id.replace('cfg-', '');
                if (currentConfig[key] !== undefined) {
                    if (input.type === 'checkbox') {
                        input.checked = Boolean(currentConfig[key]);
                    } else {
                        input.value = currentConfig[key];
                    }
                }
            });

            // Populate .env Forms
            const dynamicEnvInputs = document.querySelectorAll('input[id^="env-"], select[id^="env-"], textarea[id^="env-"]');
            dynamicEnvInputs.forEach(input => {
                if (!input || !input.id) return;
                const key = input.id.replace('env-', '');
                if (currentEnv[key] !== undefined) {
                    input.value = currentEnv[key];
                }
            });

            // Populate Strategy Switches
            const enabledStrats = currentConfig.ENABLED_STRATEGIES || ['LIQUIDITY_REVERSAL_MASTER', 'PULLBACK_CONTINUATION', 'BREAKDOWN_FOLLOW'];
            ['LIQUIDITY_REVERSAL_MASTER', 'PULLBACK_CONTINUATION', 'BREAKDOWN_FOLLOW'].forEach(strat => {
                const el = document.getElementById(`strat-${strat}`);
                if (el) el.checked = enabledStrats.includes(strat);
            });
            
            renderCoinsList();
            renderArrayManager('RSS_FEED_URLS', 'rss-list-container');
            renderArrayManager('MACRO_KEYWORDS', 'macro-list-container');
            loadPresets();
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
            const activeEnvInputs = document.querySelectorAll('input[id^="env-"], select[id^="env-"], textarea[id^="env-"]');
            activeEnvInputs.forEach(input => {
                if (!input || !input.id) return;
                const key = input.id.replace('env-', '');
                const rawVal = input.value !== undefined && input.value !== null ? input.value : '';
                envPayload[key] = String(rawVal).trim();
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
                    setTimeout(() => {
                        if (saveMsg.textContent.includes(data.message)) saveMsg.textContent = '';
                    }, 3000);
                }
            } else {
                throw new Error(data.detail || data.message || "Gagal menyimpan .env");
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
                <span>${escapeHtml(item)}</span>
                <button class="btn-del-item" onclick="deleteArrayItem('${escapeHtml(configKey)}', ${idx})">🗑️</button>
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
                    <h4>${escapeHtml(coin.symbol)}</h4>
                    <small>${escapeHtml(coin.category)} | ${escapeHtml(coin.leverage)}x | $${escapeHtml(coin.amount)}</small>
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
        document.getElementById('modal-coin-symbol').value = coin.symbol || '';
        document.getElementById('modal-coin-category').value = coin.category || 'ALTS';
        document.getElementById('modal-coin-leverage').value = coin.leverage || 10;
        document.getElementById('modal-coin-amount').value = coin.amount || 10;
        document.getElementById('modal-coin-margin-type').value = (coin.margin_type || 'isolated').toLowerCase();
        document.getElementById('modal-coin-btc-corr').checked = coin.btc_corr !== undefined ? coin.btc_corr : true;
        document.getElementById('modal-coin-keywords').value = (coin.keywords || []).join(', ');
        
        document.getElementById('modal-coin-title').textContent = "Edit Coin: " + (coin.symbol || '');
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
            document.getElementById('modal-coin-margin-type').value = 'isolated';
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
                symbol: document.getElementById('modal-coin-symbol').value.trim().toUpperCase(),
                category: document.getElementById('modal-coin-category').value,
                leverage: parseInt(document.getElementById('modal-coin-leverage').value) || 10,
                amount: parseFloat(document.getElementById('modal-coin-amount').value) || 10,
                margin_type: document.getElementById('modal-coin-margin-type').value || 'isolated',
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
        const activeFormInputs = document.querySelectorAll('input[id^="cfg-"], select[id^="cfg-"], textarea[id^="cfg-"]');
        activeFormInputs.forEach(input => {
            if (!input || !input.id) return;
            let key = input.id.replace('cfg-', '');
            // Handle duplicate binding (e.g. cfg-MAX_TOTAL_OPEN_POSITIONS_2)
            if (input.getAttribute('data-bind')) {
                key = input.getAttribute('data-bind');
            }
            
            const isFloat = input.step && input.step.includes('.');
            
            if (input.type === 'checkbox') {
                currentConfig[key] = input.checked;
            } else if (input.type === 'number') {
                const val = input.value !== undefined && input.value !== null ? input.value : '';
                currentConfig[key] = isFloat || (typeof val === 'string' && val.includes('.')) ? parseFloat(val) : parseInt(val);
                if(isNaN(currentConfig[key])) currentConfig[key] = 0;
            } else {
                currentConfig[key] = input.value !== undefined ? input.value : '';
            }
        });

        // Collect Enabled Strategies
        const activeStrategies = [];
        ['LIQUIDITY_REVERSAL_MASTER', 'PULLBACK_CONTINUATION', 'BREAKDOWN_FOLLOW'].forEach(strat => {
            const el = document.getElementById(`strat-${strat}`);
            if (el && el.checked) activeStrategies.push(strat);
        });
        currentConfig.ENABLED_STRATEGIES = activeStrategies;

        if (jsonEditor) jsonEditor.value = JSON.stringify(currentConfig, null, 2);
    }

    // --- Preset Profiles Manager ---
    async function loadPresets() {
        const container = document.getElementById('presets-container');
        if (!container) return;
        
        try {
            const res = await fetch('/api/config/presets');
            const data = await res.json();
            if (data.status === 'success') {
                const presets = data.data || {};
                container.innerHTML = '';
                
                Object.keys(presets).forEach(presetId => {
                    const p = presets[presetId];
                    const card = document.createElement('div');
                    card.className = 'preset-card';
                    card.innerHTML = `
                        <div class="preset-header">
                            <div class="preset-title">${escapeHtml(p.name || presetId)}</div>
                            <span class="preset-badge">${p.is_custom ? 'CUSTOM' : 'BUILT-IN'}</span>
                        </div>
                        <p class="preset-desc">${escapeHtml(p.description || 'No description available.')}</p>
                        <div class="preset-actions">
                            <button class="btn btn-primary btn-sm btn-apply-preset" data-id="${escapeHtml(presetId)}">🚀 Terapkan Preset</button>
                        </div>
                    `;
                    container.appendChild(card);
                });

                document.querySelectorAll('.btn-apply-preset').forEach(btn => {
                    btn.addEventListener('click', async () => {
                        const pid = btn.getAttribute('data-id');
                        await applyPreset(pid);
                    });
                });
            }
        } catch (e) {
            console.error("Gagal memuat preset", e);
        }
    }

    async function applyPreset(presetId) {
        const saveMsg = document.getElementById('config-save-msg');
        try {
            const res = await fetch('/api/config/presets/apply', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ preset_id: presetId })
            });
            const data = await res.json();
            if (data.status === 'success') {
                if (saveMsg) {
                    saveMsg.textContent = "✅ " + data.message;
                    saveMsg.style.color = 'var(--success)';
                    setTimeout(() => saveMsg.textContent = '', 3500);
                }
                await loadConfig();
            } else {
                throw new Error(data.detail || "Gagal menerapkan preset");
            }
        } catch (e) {
            if (saveMsg) {
                saveMsg.textContent = "❌ " + e.message;
                saveMsg.style.color = 'var(--danger)';
            }
        }
    }

    const btnSaveCustomPreset = document.getElementById('btn-save-custom-preset');
    if (btnSaveCustomPreset) {
        btnSaveCustomPreset.addEventListener('click', async () => {
            const pid = document.getElementById('custom-preset-id').value.trim();
            const pname = document.getElementById('custom-preset-name').value.trim();
            const pdesc = document.getElementById('custom-preset-desc').value.trim();
            const saveMsg = document.getElementById('config-save-msg');
            
            if (!pid || !pname) {
                alert("Mohon masukkan Preset ID dan Nama Preset!");
                return;
            }
            
            try {
                updateRawJSON();
                const res = await fetch('/api/config/presets/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        preset_id: pid,
                        name: pname,
                        description: pdesc,
                        config: currentConfig
                    })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    if (saveMsg) {
                        saveMsg.textContent = "✅ " + data.message;
                        saveMsg.style.color = 'var(--success)';
                        setTimeout(() => saveMsg.textContent = '', 3500);
                    }
                    document.getElementById('custom-preset-id').value = '';
                    document.getElementById('custom-preset-name').value = '';
                    document.getElementById('custom-preset-desc').value = '';
                    loadPresets();
                } else {
                    throw new Error(data.detail || "Gagal menyimpan preset");
                }
            } catch (e) {
                if (saveMsg) {
                    saveMsg.textContent = "❌ " + e.message;
                    saveMsg.style.color = 'var(--danger)';
                }
            }
        });
    }

    // --- AI Prompts Reset Handler ---
    const btnResetPrompts = document.getElementById('btn-reset-prompts');
    if (btnResetPrompts) {
        btnResetPrompts.addEventListener('click', async () => {
            if (!confirm("Kembalikan seluruh template prompt AI ke pengaturan bawaan (default)?")) return;
            try {
                const res = await fetch('/api/config/prompts/defaults');
                const data = await res.json();
                if (data.status === 'success' && data.data) {
                    const defaults = data.data;
                    if (defaults.AI_SYSTEM_ROLE) document.getElementById('cfg-AI_SYSTEM_ROLE').value = defaults.AI_SYSTEM_ROLE;
                    if (defaults.PROMPT_STRATEGY_SELECTION) document.getElementById('cfg-PROMPT_STRATEGY_SELECTION').value = defaults.PROMPT_STRATEGY_SELECTION;
                    if (defaults.PROMPT_SENTIMENT_ANALYSIS) document.getElementById('cfg-PROMPT_SENTIMENT_ANALYSIS').value = defaults.PROMPT_SENTIMENT_ANALYSIS;
                    if (defaults.PROMPT_PATTERN_RECOGNITION) document.getElementById('cfg-PROMPT_PATTERN_RECOGNITION').value = defaults.PROMPT_PATTERN_RECOGNITION;
                    updateRawJSON();
                    alert("Template prompt AI berhasil di-reset ke default! Klik 'SAVE JSON SETTINGS' untuk menyimpan permanen.");
                }
            } catch (e) {
                alert("Gagal mengambil template prompt default.");
            }
        });
    }

    // Helper: Set MongoDB Collection format to current month (trades_MM_YYYY)
    const btnSetCurrentMonth = document.getElementById('btn-set-current-month-col');
    if (btnSetCurrentMonth) {
        btnSetCurrentMonth.addEventListener('click', () => {
            const now = new Date();
            const mm = String(now.getMonth() + 1).padStart(2, '0');
            const yyyy = now.getFullYear();
            const autoCol = `trades_${mm}_${yyyy}`;
            const inputCol = document.getElementById('cfg-MONGO_COLLECTION_NAME');
            if (inputCol) {
                inputCol.value = autoCol;
                updateRawJSON();
            }
        });
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
                // Refresh trade collections selector jika halaman history aktif
                if (typeof loadTradeCollections === 'function') {
                    loadTradeCollections(true);
                }
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

                const updateTimeEl = document.getElementById('sentiment-last-update-time');
                if (updateTimeEl && latest.last_updated) {
                    updateTimeEl.textContent = formatWIB(latest.last_updated, 'full');
                }
                
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
            return formatWIB(h.last_updated, 'time-short');
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
                    <td><strong>${escapeHtml(pos.symbol)}</strong></td>
                    <td class="${sideClass}">${escapeHtml(side)}</td>
                    <td>${escapeHtml(String(pos.size || '--'))}</td>
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
    let hasReceivedLog = false;

    function appendLog(msg) {
        if (!hasReceivedLog) {
            hasReceivedLog = true;
            if (dashboardTerminal) dashboardTerminal.innerHTML = '';
            if (fullTerminal) fullTerminal.innerHTML = '';
        }

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

    // --- TRADE HISTORY & QUANT PERFORMANCE ANALYTICS ---
    let equityChartInstance = null;
    let drawdownChartInstance = null;
    let symbolPnlChartInstance = null;
    let outcomeChartInstance = null;

    let currentHistPage = 1;
    let cachedTradesList = [];
    let filterOptionsLoaded = false;
    let tradeCollectionsLoaded = false;

    async function loadTradeCollections(force = false) {
        if (tradeCollectionsLoaded && !force) return;
        const colSelect = document.getElementById('hist-filter-collection');
        if (!colSelect) return;
        try {
            const res = await fetch('/api/data/trades/collections');
            const data = await res.json();
            if (data.status === 'success') {
                const currentSelected = colSelect.value || data.active_collection || (currentConfig.MONGO_COLLECTION_NAME || 'trades_08_2026');
                colSelect.innerHTML = '';
                const collections = data.collections || [data.active_collection];
                collections.forEach(col => {
                    const opt = document.createElement('option');
                    opt.value = col;
                    opt.textContent = col;
                    if (col === currentSelected) opt.selected = true;
                    colSelect.appendChild(opt);
                });
                tradeCollectionsLoaded = true;
            }
        } catch (e) {
            console.error("Failed to load trade collections", e);
        }
    }

    async function loadTradeFilterOptions() {
        if (filterOptionsLoaded) return;
        try {
            const col = document.getElementById('hist-filter-collection')?.value || '';
            let url = '/api/data/trades/filters';
            if (col) url += `?collection=${encodeURIComponent(col)}`;
            const res = await fetch(url);
            const data = await res.json();
            if (data.status === 'success') {
                const symSelect = document.getElementById('hist-filter-symbol');
                const stratSelect = document.getElementById('hist-filter-strategy');
                
                if (symSelect && data.symbols) {
                    const currentVal = symSelect.value;
                    symSelect.innerHTML = '<option value="ALL">All Symbols</option>';
                    data.symbols.forEach(sym => {
                        const opt = document.createElement('option');
                        opt.value = sym;
                        opt.textContent = sym;
                        symSelect.appendChild(opt);
                    });
                    symSelect.value = currentVal || 'ALL';
                }

                if (stratSelect && data.strategies) {
                    const currentStrat = stratSelect.value;
                    stratSelect.innerHTML = '<option value="ALL">All Strategies</option>';
                    data.strategies.forEach(strat => {
                        const opt = document.createElement('option');
                        opt.value = strat;
                        opt.textContent = strat;
                        stratSelect.appendChild(opt);
                    });
                    stratSelect.value = currentStrat || 'ALL';
                }
                filterOptionsLoaded = true;
            }
        } catch (e) {
            console.error("Failed to load trade filter options", e);
        }
    }

    function getHistoryFilterParams() {
        const days = document.getElementById('hist-filter-days')?.value || '30';
        const symbol = document.getElementById('hist-filter-symbol')?.value || 'ALL';
        const strategy = document.getElementById('hist-filter-strategy')?.value || 'ALL';
        const result = document.getElementById('hist-filter-result')?.value || 'ALL';
        const collection = document.getElementById('hist-filter-collection')?.value || '';
        return { days, symbol, strategy, result, collection };
    }

    async function fetchTradeAnalytics() {
        try {
            const { days, symbol, strategy, collection } = getHistoryFilterParams();
            let url = `/api/data/trades/analytics?days=${days}&symbol=${symbol}&strategy=${strategy}`;
            if (collection) url += `&collection=${encodeURIComponent(collection)}`;
            const res = await fetch(url);
            const result = await res.json();
            
            if (result.status !== 'success') return;
            const s = result.summary || {};

            // 1. Update 8 KPI Cards
            const netPnlEl = document.getElementById('kpi-net-pnl');
            if (netPnlEl) {
                const net = s.net_pnl_usdt || 0;
                netPnlEl.textContent = (net >= 0 ? '+$' : '-$') + Math.abs(net).toFixed(2);
                netPnlEl.className = 'quant-val ' + (net >= 0 ? 'text-success' : 'text-danger');
            }

            const feesEl = document.getElementById('kpi-fees');
            if (feesEl) feesEl.textContent = '$' + (s.total_fees_usdt || 0).toFixed(2);

            const wrEl = document.getElementById('kpi-win-rate');
            if (wrEl) {
                const wr = s.win_rate_percent || 0;
                wrEl.textContent = wr.toFixed(1) + '%';
                wrEl.className = 'quant-val ' + (wr >= 50 ? 'text-success' : (wr > 0 ? 'text-warning' : 'text-main'));
            }

            const winLossEl = document.getElementById('kpi-win-loss-count');
            if (winLossEl) winLossEl.textContent = `${s.win_count || 0}W / ${s.loss_count || 0}L (${s.cancelled_count || 0} Canc)`;

            const payoffEl = document.getElementById('kpi-payoff');
            if (payoffEl) payoffEl.textContent = (s.payoff_ratio || 0).toFixed(2);

            const evEl = document.getElementById('kpi-ev');
            if (evEl) {
                const ev = s.expected_value_usdt || 0;
                evEl.textContent = (ev >= 0 ? '+$' : '-$') + Math.abs(ev).toFixed(2);
                evEl.className = 'quant-val ' + (ev >= 0 ? 'text-success' : 'text-danger');
            }

            const evRoiEl = document.getElementById('kpi-ev-roi');
            if (evRoiEl) evRoiEl.textContent = (s.expected_value_roi_percent || 0).toFixed(2) + '%';

            const pfEl = document.getElementById('kpi-pf');
            if (pfEl) {
                const pf = s.profit_factor || 0;
                pfEl.textContent = pf.toFixed(2);
                pfEl.className = 'quant-val ' + (pf >= 1.5 ? 'text-success' : (pf >= 1.0 ? 'text-warning' : 'text-danger'));
            }

            const grossProfitEl = document.getElementById('kpi-gross-profit');
            if (grossProfitEl) grossProfitEl.textContent = '$' + (s.gross_profit_usdt || 0).toFixed(0);

            const grossLossEl = document.getElementById('kpi-gross-loss');
            if (grossLossEl) grossLossEl.textContent = '$' + (s.gross_loss_usdt || 0).toFixed(0);

            const calmarEl = document.getElementById('kpi-calmar');
            if (calmarEl) {
                const calmar = s.calmar_ratio || 0;
                calmarEl.textContent = calmar.toFixed(2);
                calmarEl.className = 'quant-val ' + (calmar >= 2.0 ? 'text-success' : (calmar >= 1.0 ? 'text-warning' : 'text-main'));
            }

            const mddEl = document.getElementById('kpi-mdd');
            if (mddEl) mddEl.textContent = '-$' + (s.max_drawdown_usdt || 0).toFixed(2);

            const mddPctEl = document.getElementById('kpi-mdd-pct');
            if (mddPctEl) mddPctEl.textContent = (s.max_drawdown_percent || 0).toFixed(1) + '%';

            const ssEl = document.getElementById('kpi-sharpe-sortino');
            if (ssEl) ssEl.textContent = `${(s.sharpe_ratio || 0).toFixed(2)} / ${(s.sortino_ratio || 0).toFixed(2)}`;

            const sqnEl = document.getElementById('kpi-sqn');
            if (sqnEl) sqnEl.textContent = (s.sqn || 0).toFixed(2);

            const sqnGradeEl = document.getElementById('kpi-sqn-grade');
            if (sqnGradeEl) sqnGradeEl.textContent = s.sqn_grade || '--';

            const kellyEl = document.getElementById('kpi-kelly');
            if (kellyEl) kellyEl.textContent = (s.half_kelly_percent || 0).toFixed(1) + '%';

            // 2. Render Charts
            renderEquityChart(result.charts?.equity_curve || []);
            renderDrawdownChart(result.charts?.drawdown_curve || []);
            renderSymbolPnlChart(result.breakdown?.by_symbol || []);
            renderOutcomeChart(result.charts?.distribution || {});

        } catch (e) {
            console.error("Failed to fetch trade analytics", e);
        }
    }

    function renderEquityChart(curveData) {
        const canvas = document.getElementById('equityChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        
        const labels = curveData.map(d => d.label || formatWIB(d.timestamp, 'chart'));
        const cumPnls = curveData.map(d => d.cumulative_pnl);

        if (equityChartInstance) {
            equityChartInstance.data.labels = labels;
            equityChartInstance.data.datasets[0].data = cumPnls;
            equityChartInstance.update();
            return;
        }

        const gradient = ctx.createLinearGradient(0, 0, 0, 240);
        gradient.addColorStop(0, 'rgba(16, 185, 129, 0.35)');
        gradient.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

        equityChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Cumulative PnL ($)',
                    data: cumPnls,
                    borderColor: '#10b981',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: curveData.length > 50 ? 0 : 3,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#34d399'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: (ctx) => ` Cumulative: $${parseFloat(ctx.raw).toFixed(2)}`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', maxTicksLimit: 8, font: { size: 10 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            callback: (v) => '$' + v
                        }
                    }
                }
            }
        });
    }

    function renderDrawdownChart(ddData) {
        const canvas = document.getElementById('drawdownChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const labels = ddData.map(d => d.label || formatWIB(d.timestamp, 'chart'));
        const ddPct = ddData.map(d => -Math.abs(d.drawdown_pct));

        if (drawdownChartInstance) {
            drawdownChartInstance.data.labels = labels;
            drawdownChartInstance.data.datasets[0].data = ddPct;
            drawdownChartInstance.update();
            return;
        }

        const gradient = ctx.createLinearGradient(0, 0, 0, 240);
        gradient.addColorStop(0, 'rgba(239, 68, 68, 0.0)');
        gradient.addColorStop(1, 'rgba(239, 68, 68, 0.35)');

        drawdownChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Underwater Drawdown (%)',
                    data: ddPct,
                    borderColor: '#ef4444',
                    backgroundColor: gradient,
                    borderWidth: 1.8,
                    fill: true,
                    tension: 0.2,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` Drawdown: ${parseFloat(ctx.raw).toFixed(2)}%`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', maxTicksLimit: 8, font: { size: 10 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            callback: (v) => v + '%'
                        },
                        max: 0
                    }
                }
            }
        });
    }

    function renderSymbolPnlChart(bySymbol) {
        const canvas = document.getElementById('symbolPnlChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const symbols = bySymbol.slice(0, 8).map(s => s.category);
        const pnls = bySymbol.slice(0, 8).map(s => s.net_pnl_usdt);
        const bgColors = pnls.map(p => p >= 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)');

        if (symbolPnlChartInstance) {
            symbolPnlChartInstance.data.labels = symbols;
            symbolPnlChartInstance.data.datasets[0].data = pnls;
            symbolPnlChartInstance.data.datasets[0].backgroundColor = bgColors;
            symbolPnlChartInstance.update();
            return;
        }

        symbolPnlChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: symbols,
                datasets: [{
                    label: 'Net PnL ($)',
                    data: pnls,
                    backgroundColor: bgColors,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` Net PnL: $${parseFloat(ctx.raw).toFixed(2)}`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#e2e8f0', font: { size: 11 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            callback: (v) => '$' + v
                        }
                    }
                }
            }
        });
    }

    function renderOutcomeChart(distribution) {
        const canvas = document.getElementById('outcomeChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const dataVals = [
            distribution.win || 0,
            distribution.loss || 0,
            distribution.breakeven || 0,
            distribution.cancelled || 0
        ];

        if (outcomeChartInstance) {
            outcomeChartInstance.data.datasets[0].data = dataVals;
            outcomeChartInstance.update();
            return;
        }

        outcomeChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['WIN', 'LOSS', 'BREAKEVEN', 'CANCELLED'],
                datasets: [{
                    data: dataVals,
                    backgroundColor: [
                        '#10b981',
                        '#ef4444',
                        '#94a3b8',
                        '#475569'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#e2e8f0', boxWidth: 12, font: { size: 11 } }
                    }
                }
            }
        });
    }

    async function fetchTradeHistory(page = 1) {
        try {
            currentHistPage = page;
            const { days, symbol, strategy, result, collection } = getHistoryFilterParams();
            let url = `/api/data/trades/history?page=${page}&limit=20&days=${days}&symbol=${symbol}&strategy=${strategy}&result=${result}`;
            if (collection) url += `&collection=${encodeURIComponent(collection)}`;
            const res = await fetch(url);
            const data = await res.json();

            const tbody = document.getElementById('history-tbody');
            if (!tbody) return;
            tbody.innerHTML = '';

            if (data.status !== 'success' || !data.data || data.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="11" class="text-center">No trade history found matching filters.</td></tr>';
                document.getElementById('hist-total-count').textContent = '0';
                document.getElementById('current-page-num').textContent = '1';
                document.getElementById('total-page-num').textContent = '1';
                document.getElementById('btn-prev-page').disabled = true;
                document.getElementById('btn-next-page').disabled = true;
                return;
            }

            cachedTradesList = data.data;
            const pagination = data.pagination || { page: 1, total_pages: 1, total_items: data.data.length };

            document.getElementById('hist-total-count').textContent = pagination.total_items;
            document.getElementById('current-page-num').textContent = pagination.page;
            document.getElementById('total-page-num').textContent = pagination.total_pages;
            
            document.getElementById('btn-prev-page').disabled = pagination.page <= 1;
            document.getElementById('btn-next-page').disabled = pagination.page >= pagination.total_pages;

            data.data.forEach((trade, idx) => {
                const tr = document.createElement('tr');
                
                // Format timestamp ke WIB
                const timeStr = formatWIB(trade.timestamp, 'table');

                const side = (trade.side || 'BUY').toUpperCase();
                const sideBadge = `<span class="badge-pill ${side === 'BUY' || side === 'LONG' ? 'badge-long' : 'badge-short'}">${side}</span>`;
                
                const pnl = parseFloat(trade.pnl_usdt) || 0;
                const roi = parseFloat(trade.roi_percent) || 0;
                const pnlClass = pnl > 0 ? 'text-success' : (pnl < 0 ? 'text-danger' : 'text-muted');
                const pnlSign = pnl > 0 ? '+' : '';
                const pnlFormatted = `<span class="${pnlClass}"><strong>${pnlSign}$${pnl.toFixed(2)}</strong> <small>(${pnlSign}${roi.toFixed(1)}%)</small></span>`;

                let resBadge = '';
                const resText = (trade.result || 'UNKNOWN').toUpperCase();
                if (resText === 'WIN') resBadge = '<span class="badge-pill badge-win">WIN</span>';
                else if (resText === 'LOSS') resBadge = '<span class="badge-pill badge-loss">LOSS</span>';
                else if (resText === 'BREAKEVEN') resBadge = '<span class="badge-pill badge-be">BE</span>';
                else resBadge = `<span class="badge-pill badge-cancelled">${escapeHtml(resText)}</span>`;

                tr.innerHTML = `
                    <td style="font-size: 11px; color: #94a3b8; font-family: monospace;">${escapeHtml(timeStr)}</td>
                    <td><strong>${escapeHtml(trade.symbol || '--')}</strong></td>
                    <td>${sideBadge}</td>
                    <td>$${parseFloat(trade.size_usdt || 0).toFixed(0)}</td>
                    <td>$${parseFloat(trade.entry_price || 0).toFixed(4)}</td>
                    <td>$${parseFloat(trade.exit_price || 0).toFixed(4)}</td>
                    <td>${pnlFormatted}</td>
                    <td>${resBadge}</td>
                    <td><small style="color: #cbd5e1;">${escapeHtml(trade.exit_type || '-')}</small></td>
                    <td><span style="font-size: 10px; padding: 2px 6px; border-radius: 3px; background: rgba(255,255,255,0.06);">${escapeHtml(trade.strategy_tag || 'MANUAL')}</span></td>
                    <td><button class="btn-detail" data-index="${idx}">👁️ Detail</button></td>
                `;

                tbody.appendChild(tr);
            });

            // Add click listeners to detail buttons
            document.querySelectorAll('.btn-detail').forEach(btn => {
                btn.addEventListener('click', () => {
                    const idx = parseInt(btn.getAttribute('data-index'));
                    if (cachedTradesList[idx]) openTradeModal(cachedTradesList[idx]);
                });
            });

        } catch (e) {
            console.error("Failed to fetch trade history", e);
        }
    }

    function openTradeModal(trade) {
        const modal = document.getElementById('trade-modal');
        if (!modal) return;

        const timeFinished = formatWIB(trade.timestamp, 'full');
        const timeSetup = trade.setup_at ? formatWIB(trade.setup_at, 'full') : '-';
        const timeFilled = trade.filled_at ? formatWIB(trade.filled_at, 'full') : '-';

        document.getElementById('modal-trade-title').textContent = `📊 Trade Detail: ${trade.symbol} (${trade.result})`;
        document.getElementById('modal-trade-symbol-side').textContent = `${trade.symbol} | ${trade.side} | Size: $${trade.size_usdt}`;
        
        const modalTimeEl = document.getElementById('modal-trade-time');
        if (modalTimeEl) modalTimeEl.textContent = timeFinished;

        const modalTimelineEl = document.getElementById('modal-trade-timeline');
        if (modalTimelineEl) {
            modalTimelineEl.textContent = `Setup: ${timeSetup} ➜ Filled: ${timeFilled} ➜ Close: ${timeFinished}`;
        }
        
        const pnl = parseFloat(trade.pnl_usdt) || 0;
        const roi = parseFloat(trade.roi_percent) || 0;
        const pnlSign = pnl > 0 ? '+' : '';
        document.getElementById('modal-trade-pnl').innerHTML = `<span class="${pnl >= 0 ? 'text-success' : 'text-danger'}">${pnlSign}$${pnl.toFixed(2)} (${pnlSign}${roi.toFixed(2)}%) | Fee: $${trade.fee || 0}</span>`;
        
        document.getElementById('modal-trade-prices').textContent = `Entry: $${trade.entry_price} ➜ Exit: $${trade.exit_price}`;
        document.getElementById('modal-trade-exit-strat').textContent = `Exit: ${trade.exit_type || '-'} | Strategy: ${trade.strategy_tag || '-'}`;

        // AI Reasoning
        let reasonText = trade.reason || '-';
        if (trade.prompt && trade.prompt !== '-') {
            reasonText = `AI REASONING:\n${reasonText}\n\nPROMPT CONTEXT:\n${trade.prompt}`;
        }
        document.getElementById('modal-trade-reason').textContent = reasonText;

        // Technical Data Snapshot
        let techObj = trade.technical_data;
        if (typeof techObj === 'string') {
            try { techObj = JSON.parse(techObj); } catch(e) {}
        }
        document.getElementById('modal-trade-tech').textContent = typeof techObj === 'object' ? JSON.stringify(techObj, null, 2) : String(techObj || '{}');

        modal.classList.add('active');
    }

    function exportTradeHistoryCSV() {
        if (!cachedTradesList || cachedTradesList.length === 0) {
            alert("No trade data to export.");
            return;
        }
        
        const headers = ["Timestamp (WIB)", "Symbol", "Side", "Size_USDT", "Entry_Price", "Exit_Price", "PnL_USDT", "ROI_Percent", "Fee", "Result", "Exit_Type", "Strategy", "Reason"];
        const rows = cachedTradesList.map(t => [
            `"${formatWIB(t.timestamp, 'table')}"`,
            `"${t.symbol || ''}"`,
            `"${t.side || ''}"`,
            t.size_usdt || 0,
            t.entry_price || 0,
            t.exit_price || 0,
            t.pnl_usdt || 0,
            t.roi_percent || 0,
            t.fee || 0,
            `"${t.result || ''}"`,
            `"${t.exit_type || ''}"`,
            `"${t.strategy_tag || ''}"`,
            `"${(t.reason || '').replace(/"/g, '""')}"`
        ]);

        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', `trade_history_wib_${new Date().toISOString().slice(0,10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    async function loadTradeHistoryAndAnalytics(resetPage = true) {
        if (resetPage) currentHistPage = 1;
        await loadTradeCollections();
        await loadTradeFilterOptions();
        await Promise.all([
            fetchTradeAnalytics(),
            fetchTradeHistory(currentHistPage)
        ]);
    }

    // History Event Listeners
    document.getElementById('btn-refresh-history')?.addEventListener('click', () => loadTradeHistoryAndAnalytics(true));
    document.getElementById('hist-filter-collection')?.addEventListener('change', () => {
        filterOptionsLoaded = false;
        loadTradeHistoryAndAnalytics(true);
    });
    document.getElementById('hist-filter-days')?.addEventListener('change', () => loadTradeHistoryAndAnalytics(true));
    document.getElementById('hist-filter-symbol')?.addEventListener('change', () => loadTradeHistoryAndAnalytics(true));
    document.getElementById('hist-filter-strategy')?.addEventListener('change', () => loadTradeHistoryAndAnalytics(true));
    document.getElementById('hist-filter-result')?.addEventListener('change', () => loadTradeHistoryAndAnalytics(true));
    document.getElementById('btn-export-csv')?.addEventListener('click', exportTradeHistoryCSV);

    document.getElementById('btn-prev-page')?.addEventListener('click', () => {
        if (currentHistPage > 1) fetchTradeHistory(currentHistPage - 1);
    });
    document.getElementById('btn-next-page')?.addEventListener('click', () => {
        fetchTradeHistory(currentHistPage + 1);
    });

    // Modal Close
    document.getElementById('close-trade-modal')?.addEventListener('click', () => {
        document.getElementById('trade-modal')?.classList.remove('active');
    });
    document.getElementById('btn-close-trade-modal')?.addEventListener('click', () => {
        document.getElementById('trade-modal')?.classList.remove('active');
    });

    // Quick Search filter
    document.getElementById('hist-search')?.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        const rows = document.querySelectorAll('#history-tbody tr');
        rows.forEach(r => {
            const text = r.textContent.toLowerCase();
            r.style.display = text.includes(query) ? '' : 'none';
        });
    });

    // =========================================================================
    // AI INTELLIGENCE HUB & RECAP MANAGER
    // =========================================================================
    let currentAIEvalPage = 1;
    let cachedAIEvalsList = [];

    async function loadAIEvaluations(resetPage = true) {
        if (resetPage) currentAIEvalPage = 1;
        await Promise.all([
            fetchAIStats(),
            fetchAIEvaluations(currentAIEvalPage)
        ]);
        populateAISymbolFilter();
    }

    async function fetchAIStats() {
        try {
            const res = await fetch('/api/data/ai/stats');
            const json = await res.json();
            if (json.status === 'success' && json.data) {
                const s = json.data;
                const elTotal = document.getElementById('ai-stat-total');
                const elBuy = document.getElementById('ai-stat-buy');
                const elSell = document.getElementById('ai-stat-sell');
                const elWait = document.getElementById('ai-stat-wait');
                const elAvg = document.getElementById('ai-stat-avg-conf');

                if (elTotal) elTotal.textContent = s.total_evaluations || 0;
                if (elBuy) elBuy.textContent = s.buy_count || 0;
                if (elSell) elSell.textContent = s.sell_count || 0;
                if (elWait) elWait.textContent = s.wait_count || 0;
                if (elAvg) elAvg.textContent = (s.avg_confidence || 0) + '%';
            }
        } catch (e) {
            console.error("Failed to fetch AI stats:", e);
        }
    }

    async function fetchAIEvaluations(page = 1) {
        const tbody = document.getElementById('ai-evals-tbody');
        if (!tbody) return;

        currentAIEvalPage = page;
        const symbol = document.getElementById('ai-filter-symbol')?.value || 'ALL';
        const decision = document.getElementById('ai-filter-decision')?.value || 'ALL';

        try {
            const res = await fetch(`/api/data/ai/evaluations?page=${page}&limit=25&symbol=${encodeURIComponent(symbol)}&decision=${encodeURIComponent(decision)}`);
            const json = await res.json();

            if (json.status === 'success') {
                cachedAIEvalsList = json.data || [];
                const pagination = json.pagination || { page: 1, total_pages: 1, total_items: 0 };

                // Update pagination controls
                const pageNumEl = document.getElementById('ai-page-number');
                const pageInfoEl = document.getElementById('ai-eval-page-info');
                const btnPrev = document.getElementById('ai-btn-prev-page');
                const btnNext = document.getElementById('ai-btn-next-page');

                if (pageNumEl) pageNumEl.textContent = `Page ${pagination.page} of ${pagination.total_pages}`;
                if (pageInfoEl) pageInfoEl.textContent = `Total: ${pagination.total_items} AI Decisions`;
                if (btnPrev) btnPrev.disabled = pagination.page <= 1;
                if (btnNext) btnNext.disabled = pagination.page >= pagination.total_pages;

                if (cachedAIEvalsList.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="8" class="text-center" style="padding: 28px; color: var(--text-muted);">
                                Belum ada riwayat evaluasi AI yang tercatat. Nyalakan bot engine untuk memulai scanning pasar.
                            </td>
                        </tr>
                    `;
                    return;
                }

                tbody.innerHTML = '';
                cachedAIEvalsList.forEach((ev, idx) => {
                    const tr = document.createElement('tr');
                    
                    // Decision Badge styling
                    let badgeBg = 'rgba(148, 163, 184, 0.2)';
                    let badgeColor = '#94a3b8';
                    const dec = (ev.decision || 'WAIT').toUpperCase();
                    if (dec === 'BUY' || dec === 'LONG') {
                        badgeBg = 'rgba(16, 185, 129, 0.2)';
                        badgeColor = 'var(--neon-green)';
                    } else if (dec === 'SELL' || dec === 'SHORT') {
                        badgeBg = 'rgba(244, 63, 94, 0.2)';
                        badgeColor = 'var(--neon-pink)';
                    } else {
                        badgeBg = 'rgba(245, 158, 11, 0.2)';
                        badgeColor = '#f59e0b';
                    }

                    const timeDisplay = formatWIB(ev.timestamp || ev.time_wib, 'table');
                    const conf = Math.round(ev.confidence || 0);

                    // Truncate reason
                    const reasonSnippet = ev.reason ? (ev.reason.length > 75 ? ev.reason.substring(0, 75) + '...' : ev.reason) : '-';

                    tr.innerHTML = `
                        <td style="font-size: 0.82rem; color: var(--text-muted); font-family: monospace;">${escapeHtml(timeDisplay)}</td>
                        <td><strong>${escapeHtml(ev.symbol || '--')}</strong></td>
                        <td>
                            <span class="badge" style="background: ${badgeBg}; color: ${badgeColor}; font-weight: 600; padding: 4px 8px; border-radius: 4px;">
                                ${escapeHtml(dec)}
                            </span>
                        </td>
                        <td>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 50px; background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;">
                                    <div style="width: ${conf}%; background: ${conf >= 65 ? 'var(--neon-green)' : '#f59e0b'}; height: 100%;"></div>
                                </div>
                                <span style="font-size: 0.82rem;">${conf}%</span>
                            </div>
                        </td>
                        <td style="font-size: 0.82rem;"><span class="badge" style="background: rgba(255,255,255,0.06); color: var(--neon-cyan);">${escapeHtml(ev.strategy_mode || 'STANDARD')}</span></td>
                        <td style="font-size: 0.82rem;">${escapeHtml(ev.sentiment_status || 'NEUTRAL')} (${ev.sentiment_score || 50})</td>
                        <td style="font-size: 0.82rem; color: #cbd5e1; max-width: 250px;">${escapeHtml(reasonSnippet)}</td>
                        <td style="text-align: center;">
                            <button class="btn btn-outline btn-xs" onclick="openAIEvalDetail(${idx})" style="padding: 3px 8px; font-size: 0.75rem;">🔍 Detail</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        } catch (e) {
            console.error("Failed to fetch AI evaluations:", e);
            tbody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Gagal memuat evaluasi AI: ${e.message}</td></tr>`;
        }
    }

    function populateAISymbolFilter() {
        const select = document.getElementById('ai-filter-symbol');
        if (!select) return;
        
        const currentVal = select.value;
        const symbols = new Set();
        (currentConfig.DAFTAR_KOIN || []).forEach(c => {
            if (c.symbol) symbols.add(c.symbol.toUpperCase());
        });
        cachedAIEvalsList.forEach(e => {
            if (e.symbol) symbols.add(e.symbol.toUpperCase());
        });

        // Keep 'ALL' as first option
        select.innerHTML = '<option value="ALL">All Symbols</option>';
        Array.from(symbols).sort().forEach(sym => {
            const opt = document.createElement('option');
            opt.value = sym;
            opt.textContent = sym;
            if (sym === currentVal) opt.selected = true;
            select.appendChild(opt);
        });
    }

    window.openAIEvalDetail = (idx) => {
        const ev = cachedAIEvalsList[idx];
        if (!ev) return;

        const modal = document.getElementById('ai-eval-modal');
        if (!modal) return;

        const formattedTime = formatWIB(ev.timestamp || ev.time_wib, 'full');
        document.getElementById('modal-ai-symbol-time').textContent = `${ev.symbol || '--'} @ ${formattedTime}`;
        document.getElementById('modal-ai-decision-conf').textContent = `${ev.decision || 'WAIT'} (${ev.confidence || 0}% Confidence)`;
        document.getElementById('modal-ai-strategy').textContent = `${ev.strategy_mode || 'STANDARD'} (${ev.execution_mode || 'MARKET'})`;
        document.getElementById('modal-ai-sentiment').textContent = `${ev.sentiment_status || 'NEUTRAL'} (Score: ${ev.sentiment_score || 50}/100)`;

        document.getElementById('modal-ai-reason').textContent = ev.reason || 'No detailed reason provided.';
        document.getElementById('modal-ai-vision').textContent = ev.vision_summary || 'Vision AI analysis not recorded or disabled.';
        document.getElementById('modal-ai-tech').textContent = JSON.stringify(ev.technical_snapshot || {}, null, 2);
        document.getElementById('modal-ai-prompt').textContent = ev.prompt_snippet || 'Prompt snippet not available.';

        modal.classList.add('active');
        modal.style.display = 'block';
    };

    // AI Eval Modal Closes
    document.getElementById('close-ai-modal')?.addEventListener('click', () => {
        const m = document.getElementById('ai-eval-modal');
        if (m) { m.classList.remove('active'); m.style.display = 'none'; }
    });
    document.getElementById('btn-close-ai-modal')?.addEventListener('click', () => {
        const m = document.getElementById('ai-eval-modal');
        if (m) { m.classList.remove('active'); m.style.display = 'none'; }
    });

    // AI Recap Event Listeners
    document.getElementById('btn-refresh-ai-recap')?.addEventListener('click', () => loadAIEvaluations(true));
    document.getElementById('ai-filter-symbol')?.addEventListener('change', () => fetchAIEvaluations(1));
    document.getElementById('ai-filter-decision')?.addEventListener('change', () => fetchAIEvaluations(1));
    document.getElementById('ai-btn-prev-page')?.addEventListener('click', () => {
        if (currentAIEvalPage > 1) fetchAIEvaluations(currentAIEvalPage - 1);
    });
    document.getElementById('ai-btn-next-page')?.addEventListener('click', () => {
        fetchAIEvaluations(currentAIEvalPage + 1);
    });

    // --- Initialization & Polling ---
    checkBotStatus();
    fetchSystemStats();
    connectLogStream();
    setInterval(checkBotStatus, 4000);
    setInterval(fetchSystemStats, 3000);
    
    setInterval(() => {
        const sentimentPage = document.getElementById('sentiment');
        const aiRecapPage = document.getElementById('ai-recap');
        const positionsPage = document.getElementById('positions');
        const historyPage = document.getElementById('history');
        if (sentimentPage && sentimentPage.classList.contains('active')) fetchSentiment();
        if (aiRecapPage && aiRecapPage.classList.contains('active')) loadAIEvaluations(false);
        if (positionsPage && positionsPage.classList.contains('active')) fetchPositions();
        if (historyPage && historyPage.classList.contains('active')) loadTradeHistoryAndAnalytics(false);
    }, 8000);

    // Initial load config on start
    loadConfig();
});

