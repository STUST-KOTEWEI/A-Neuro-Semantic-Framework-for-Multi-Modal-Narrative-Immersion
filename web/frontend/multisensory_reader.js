// 多感官沉浸式閱讀器 - JavaScript
const API_BASE = 'http://localhost:8010';

// 全局狀態
const state = {
    videoStream: null,
    mediaRecorder: null,
    audioChunks: [],
    currentEmotion: null,
    emotionIntensity: 0.5,
    connectedDevices: new Set(),
    generatedImages: [],
    currentImageIndex: 0,
    autoPlayInterval: null,
    isAutoPlaying: false
};

// DOM 元素
const elements = {
    videoElement: document.getElementById('videoElement'),
    capturedCanvas: document.getElementById('capturedCanvas'),
    startCameraBtn: document.getElementById('startCameraBtn'),
    detectEmotionBtn: document.getElementById('detectEmotionBtn'),
    currentEmotion: document.getElementById('currentEmotion'),
    emotionIntensity: document.getElementById('emotionIntensity'),
    
    startRecordBtn: document.getElementById('startRecordBtn'),
    stopRecordBtn: document.getElementById('stopRecordBtn'),
    recordingIndicator: document.getElementById('recordingIndicator'),
    ttsInput: document.getElementById('ttsInput'),
    speakBtn: document.getElementById('speakBtn'),
    audioPlayer: document.getElementById('audioPlayer'),
    audioElement: document.getElementById('audioElement'),
    
    broadcastBtn: document.getElementById('broadcastBtn'),
    autoPlayBtn: document.getElementById('autoPlayBtn'),
    
    carouselImages: document.getElementById('carouselImages'),
    carouselTitle: document.getElementById('carouselTitle'),
    carouselCaption: document.getElementById('carouselCaption'),
    carouselControls: document.getElementById('carouselControls'),
    
    dataContent: document.getElementById('dataContent'),
    
    statImages: document.getElementById('statImages'),
    statEmotion: document.getElementById('statEmotion'),
    statDevices: document.getElementById('statDevices'),
    statAutoplay: document.getElementById('statAutoplay')
};

// 1. 鏡頭與情緒檢測
elements.startCameraBtn.addEventListener('click', async () => {
    try {
        state.videoStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 },
            audio: false
        });
        elements.videoElement.srcObject = state.videoStream;
        elements.startCameraBtn.textContent = '✓ 鏡頭已啟動';
        elements.startCameraBtn.disabled = true;
        elements.detectEmotionBtn.disabled = false;
        logData('✅ 鏡頭已啟動', 'success');
    } catch (error) {
        logData('❌ 無法啟動鏡頭: ' + error.message, 'error');
    }
});

elements.detectEmotionBtn.addEventListener('click', async () => {
    const canvas = elements.capturedCanvas;
    canvas.width = elements.videoElement.videoWidth;
    canvas.height = elements.videoElement.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(elements.videoElement, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    const base64 = imageData.split(',')[1];

    elements.detectEmotionBtn.disabled = true;
    elements.detectEmotionBtn.textContent = '🔍 分析中...';

    try {
        const response = await fetch(`${API_BASE}/api/detect-emotion`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: base64 })
        });

        const result = await response.json();
        state.currentEmotion = result.primary_emotion;
        state.emotionIntensity = result.intensity;

        elements.currentEmotion.textContent = `${result.primary_emotion}`;
        elements.emotionIntensity.textContent = `強度: ${(result.intensity * 100).toFixed(0)}%`;
        elements.statEmotion.textContent = result.primary_emotion;

        elements.detectEmotionBtn.textContent = '✓ 已檢測';
        elements.broadcastBtn.disabled = false;

        logData(`😊 檢測到情緒: ${result.primary_emotion} (強度 ${(result.intensity * 100).toFixed(0)}%)`, 'info');

        // 如果有設備連接，自動廣播
        if (state.connectedDevices.size > 0) {
            await broadcastToDevices();
        }

    } catch (error) {
        logData('❌ 情緒檢測失敗: ' + error.message, 'error');
        elements.detectEmotionBtn.disabled = false;
        elements.detectEmotionBtn.textContent = '檢測情緒';
    }
});

// 2. 語音控制 - STT (語音轉文字)
elements.startRecordBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        state.mediaRecorder = new MediaRecorder(stream);
        state.audioChunks = [];

        state.mediaRecorder.ondataavailable = (event) => {
            state.audioChunks.push(event.data);
        };

        state.mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(state.audioChunks, { type: 'audio/webm' });
            await processAudioToText(audioBlob);
        };

        state.mediaRecorder.start();
        elements.startRecordBtn.disabled = true;
        elements.stopRecordBtn.disabled = false;
        elements.recordingIndicator.classList.add('active');
        logData('🎙️ 開始錄音...', 'info');

    } catch (error) {
        logData('❌ 無法啟動麥克風: ' + error.message, 'error');
    }
});

elements.stopRecordBtn.addEventListener('click', () => {
    if (state.mediaRecorder && state.mediaRecorder.state !== 'inactive') {
        state.mediaRecorder.stop();
        elements.startRecordBtn.disabled = false;
        elements.stopRecordBtn.disabled = true;
        elements.recordingIndicator.classList.remove('active');
        logData('⏹️ 錄音已停止，處理中...', 'info');
    }
});

async function processAudioToText(audioBlob) {
    try {
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = async () => {
            const base64Audio = reader.result.split(',')[1];
            
            const response = await fetch(`${API_BASE}/api/stt`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ audio_base64: base64Audio })
            });

            const result = await response.json();
            elements.ttsInput.value = result.text;
            logData(`🔊 識別文字: "${result.text}" (置信度: ${(result.confidence * 100).toFixed(0)}%)`, 'success');
        };
    } catch (error) {
        logData('❌ STT 失敗: ' + error.message, 'error');
    }
}

// 3. TTS (文字轉語音)
elements.speakBtn.addEventListener('click', async () => {
    const text = elements.ttsInput.value.trim();
    if (!text) {
        logData('⚠️ 請輸入要朗讀的文字', 'warning');
        return;
    }

    elements.speakBtn.disabled = true;
    elements.speakBtn.textContent = '🔄 生成中...';

    try {
        const response = await fetch(`${API_BASE}/api/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                emotion: state.currentEmotion || 'neutral',
                voice: 'alloy'
            })
        });

        const result = await response.json();
        
        // 播放音訊
        if (result.audio_url) {
            elements.audioElement.src = `${API_BASE}${result.audio_url}`;
            elements.audioPlayer.classList.add('active');
            elements.audioElement.play();
            logData(`🔊 開始朗讀: "${text.substring(0, 30)}..."`, 'success');
        } else if (result.audio_base64) {
            elements.audioElement.src = `data:audio/mp3;base64,${result.audio_base64}`;
            elements.audioPlayer.classList.add('active');
            elements.audioElement.play();
            logData(`🔊 開始朗讀 (Base64)`, 'success');
        }

        elements.speakBtn.textContent = '🔊 朗讀文字 (TTS)';
        elements.speakBtn.disabled = false;

    } catch (error) {
        logData('❌ TTS 失敗: ' + error.message, 'error');
        elements.speakBtn.textContent = '🔊 朗讀文字 (TTS)';
        elements.speakBtn.disabled = false;
    }
});

// 4. 設備連接
document.querySelectorAll('.device-card').forEach(card => {
    card.addEventListener('click', () => {
        const device = card.dataset.device;
        
        if (state.connectedDevices.has(device)) {
            state.connectedDevices.delete(device);
            card.classList.remove('connected');
            logData(`❌ 已斷開: ${card.querySelector('.device-name').textContent}`, 'info');
        } else {
            state.connectedDevices.add(device);
            card.classList.add('connected');
            logData(`✅ 已連接: ${card.querySelector('.device-name').textContent}`, 'success');
        }
        
        elements.statDevices.textContent = state.connectedDevices.size;
        elements.broadcastBtn.disabled = state.connectedDevices.size === 0;
    });
});

// 5. 廣播到所有設備
elements.broadcastBtn.addEventListener('click', broadcastToDevices);

async function broadcastToDevices() {
    if (!state.currentEmotion) {
        logData('⚠️ 請先檢測情緒', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/broadcast-to-devices`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                emotion: state.currentEmotion,
                intensity: state.emotionIntensity,
                devices: Array.from(state.connectedDevices),
                content: {
                    text: elements.ttsInput.value,
                    images: state.generatedImages.slice(0, 3).map(img => img.url)
                }
            })
        });

        const result = await response.json();
        logData(`📡 已廣播到 ${Object.keys(result.devices).length} 個設備`, 'success');
        
        Object.entries(result.devices).forEach(([device, status]) => {
            logData(`  • ${device}: ${status.status}`, 'info');
        });

    } catch (error) {
        logData('❌ 廣播失敗: ' + error.message, 'error');
    }
}

// 6. 功能按鈕
document.querySelectorAll('.feature-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const feature = btn.dataset.feature;
        
        // 移除所有 active
        document.querySelectorAll('.feature-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        if (feature === 'generate') {
            await generateContent();
        } else {
            await loadFeatureData(feature);
        }
    });
});

async function loadFeatureData(feature) {
    try {
        const endpoints = {
            'isbn': '/data/book-covers',
            'podcast': '/data/podcasts',
            'nlp': '/data/nlp',
            'rag': '/data/rag-images'
        };
        
        const response = await fetch(`${API_BASE}${endpoints[feature]}`);
        const result = await response.json();
        
        state.generatedImages = result.data.map(item => ({
            url: item.image_url || item.cover_url || `https://source.unsplash.com/800x600/?${feature}`,
            caption: item.title || item.caption || item.query || 'No caption',
            source: feature
        }));
        
        displayImages();
        logData(`✅ 載入 ${feature.toUpperCase()} 數據: ${result.data.length} 筆`, 'success');
        
    } catch (error) {
        logData(`❌ 載入 ${feature} 失敗: ` + error.message, 'error');
    }
}

async function generateContent() {
    if (!state.currentEmotion) {
        logData('⚠️ 請先檢測情緒再生成內容', 'warning');
        return;
    }

    try {
        const canvas = elements.capturedCanvas;
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        const base64 = imageData.split(',')[1];

        const userQuery = elements.ttsInput.value || '未來科技';
        logData('� 尋找代表圖中...', 'info');

        // 嘗試舊端點（預期 410），以便向使用者提示
        let usedFallback = false;
        try {
            const resp = await fetch(`${API_BASE}/api/generate-complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ camera_image_base64: base64, query: userQuery, total_count: 1 })
            });
            if (resp.status === 410) {
                usedFallback = true;
                logData('ℹ️ 內容生成已停用，改用 RAG 代表圖。', 'warning');
            } else if (resp.ok) {
                const data = await resp.json();
                state.generatedImages = data.all_images?.slice(0,1) || [];
            }
        } catch (_) {
            usedFallback = true;
        }

        if (usedFallback || state.generatedImages.length === 0) {
            const searchResp = await fetch(`${API_BASE}/data/rag-images/search?q=${encodeURIComponent(userQuery)}&top_k=1`);
            if (!searchResp.ok) throw new Error('RAG 搜尋失敗');
            const searchData = await searchResp.json();
            const first = searchData.data?.[0];
            if (first) {
                state.generatedImages = [{
                    url: first.image_url,
                    caption: first.description || first.query || '代表圖',
                    source: 'RAG'
                }];
            } else {
                // 無結果時給予佔位圖
                state.generatedImages = [{
                    url: `https://via.placeholder.com/800x600/1f2937/9ca3af?text=${encodeURIComponent(userQuery)}`,
                    caption: '沒有找到相關圖片，顯示佔位圖',
                    source: 'placeholder'
                }];
            }
        }

        displayImages();
        logData(`✅ 已選定 1 張代表圖`, 'success');

    } catch (error) {
        logData('❌ 生成失敗: ' + error.message, 'error');
    }
}

// 7. 圖像輪播（加入圖片載入失敗處理）
function displayImages() {
    if (state.generatedImages.length === 0) return;

    elements.carouselImages.innerHTML = '';
    elements.carouselControls.innerHTML = '';

    state.generatedImages.forEach((img, index) => {
        const imgElement = document.createElement('img');
        imgElement.src = img.url;
        imgElement.alt = img.caption;
        imgElement.className = 'carousel-image';
        if (index === 0) imgElement.classList.add('active');
        
        // 圖片載入失敗處理
        imgElement.onerror = function() {
            console.warn(`圖片載入失敗: ${img.url}`);
            // 使用佔位圖或錯誤提示
            this.src = `https://via.placeholder.com/800x600/cccccc/666666?text=${encodeURIComponent(img.caption || 'Image Not Found')}`;
            logData(`⚠️ 圖片載入失敗，已顯示佔位圖: ${img.caption}`, 'warning');
        };
        
        // 圖片載入成功
        imgElement.onload = function() {
            console.log(`✅ 圖片載入成功: ${img.caption}`);
        };
        
        elements.carouselImages.appendChild(imgElement);

        const dot = document.createElement('div');
        dot.className = 'carousel-dot';
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => showImage(index));
        elements.carouselControls.appendChild(dot);
    });

    showImage(0);
    elements.statImages.textContent = state.generatedImages.length;
}

function showImage(index) {
    state.currentImageIndex = index;
    const images = document.querySelectorAll('.carousel-image');
    const dots = document.querySelectorAll('.carousel-dot');

    images.forEach((img, i) => {
        img.classList.toggle('active', i === index);
    });

    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
    });

    const currentImg = state.generatedImages[index];
    elements.carouselTitle.textContent = currentImg.caption;
    elements.carouselCaption.textContent = `來源: ${currentImg.source?.toUpperCase() || 'Unknown'} | ${index + 1} / ${state.generatedImages.length}`;
}

// 8. 自動播放
elements.autoPlayBtn.addEventListener('click', () => {
    if (state.isAutoPlaying) {
        clearInterval(state.autoPlayInterval);
        state.isAutoPlaying = false;
        elements.autoPlayBtn.textContent = '▶️ 自動播放';
        elements.statAutoplay.textContent = '關閉';
        logData('⏸️ 自動播放已停止', 'info');
    } else {
        state.isAutoPlaying = true;
        elements.autoPlayBtn.textContent = '⏸️ 暫停';
        elements.statAutoplay.textContent = '開啟';
        logData('▶️ 自動播放已啟動 (每3秒切換)', 'success');

        state.autoPlayInterval = setInterval(() => {
            const nextIndex = (state.currentImageIndex + 1) % state.generatedImages.length;
            showImage(nextIndex);
        }, 3000);
    }
});

// 9. 日誌系統
function logData(message, type = 'info') {
    const item = document.createElement('div');
    item.className = 'data-item';
    
    const time = new Date().toLocaleTimeString('zh-TW');
    const emoji = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }[type] || 'ℹ️';
    
    item.innerHTML = `
        <h4>${emoji} ${time}</h4>
        <p>${message}</p>
    `;
    
    elements.dataContent.insertBefore(item, elements.dataContent.firstChild);
    
    // 只保留最新 20 條
    while (elements.dataContent.children.length > 20) {
        elements.dataContent.removeChild(elements.dataContent.lastChild);
    }
}

// 初始化
logData('🚀 多感官沉浸式閱讀器已啟動', 'success');
logData('📋 請依序操作: 1️⃣ 啟動鏡頭 → 2️⃣ 檢測情緒 → 3️⃣ 連接設備 → 4️⃣ 生成內容', 'info');

// 聊天掛件：簡易示範（需先登入並將 token 放到 localStorage.token）
(() => {
    const chatToggle = document.getElementById('chatToggle');
    const chatWidget = document.getElementById('chatWidget');
    const closeChat = document.getElementById('closeChat');
    const chatBody = document.getElementById('chatBody');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    let sessionId = null;

    function appendMsg(role, text) {
        const el = document.createElement('div');
        el.className = 'chat-msg ' + (role === 'user' ? 'user' : 'assistant');
        el.textContent = (role === 'user' ? '你：' : 'AI：') + text;
        chatBody.appendChild(el);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    async function ensureSession() {
        if (sessionId) return sessionId;
        const token = localStorage.getItem('token');
        if (!token) {
            appendMsg('assistant', '請先登入才能使用聊天');
            return null;
        }
        const res = await fetch(`${API_BASE}/chat/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ topic: 'general' })
        });
        const data = await res.json();
        sessionId = data.session_id;
        return sessionId;
    }

    chatToggle.addEventListener('click', async () => {
        chatWidget.style.display = 'flex';
        await ensureSession();
    });
    closeChat.addEventListener('click', () => chatWidget.style.display = 'none');

    chatSend.addEventListener('click', async () => {
        const text = chatInput.value.trim();
        if (!text) return;
        const token = localStorage.getItem('token');
        if (!token) { appendMsg('assistant', '請先登入'); return; }
        const sid = await ensureSession();
        if (!sid) return;
        appendMsg('user', text);
        chatInput.value = '';
        const res = await fetch(`${API_BASE}/chat/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({
                session_id: sid,
                text,
                emotion: state.currentEmotion,
                intensity: state.emotionIntensity
            })
        });
        const data = await res.json();
        appendMsg('assistant', data.reply || '（無回覆）');
    });
})();
