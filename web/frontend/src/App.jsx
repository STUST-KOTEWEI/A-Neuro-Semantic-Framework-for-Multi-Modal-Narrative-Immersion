import { useState } from 'react';
import './App.css';

// 後端 API 的網址
const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [audioSrc, setAudioSrc] = useState('');
  const [ttsLoading, setTtsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('immersion');
  const [subsystemStatus, setSubsystemStatus] = useState(null);
  const [bookScanResult, setBookScanResult] = useState(null);

  const handleTTS = async () => {
    if (!text.trim()) {
      setError('請輸入要轉換為語音的文字');
      return;
    }
    setTtsLoading(true);
    setError('');
    setAudioSrc('');

    try {
        const response = await fetch(`${API_URL}/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, lang: 'zh-tw' })
        });

        if (!response.ok) {
            throw new Error(`TTS API 請求失敗，狀態碼: ${response.status}`);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setAudioSrc(url);
    } catch (err) {
        setError(err.message);
    } finally {
        setTtsLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    if (!text.trim()) {
      setError('請輸入敘事文字');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/generate_immersion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
      });

      if (!response.ok) {
        throw new Error(`API 請求失敗，狀態碼: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubsystemStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/subsystems/status`);
      if (!response.ok) {
        throw new Error(`無法獲取子系統狀態，狀態碼: ${response.status}`);
      }
      const data = await response.json();
      setSubsystemStatus(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');
    setBookScanResult(null);

    try {
      // Convert to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64String = reader.result.split(',')[1];
        
        const response = await fetch(`${API_URL}/scan_book`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            image_base64: base64String,
            language: 'zh-TW'
          }),
        });

        if (!response.ok) {
          throw new Error(`書籍掃描失敗，狀態碼: ${response.status}`);
        }

        const data = await response.json();
        setBookScanResult(data);
        setLoading(false);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Project-HOLO</h1>
        <p>多模態敘事沉浸體驗生成器 - 整合四大子系統</p>
        <button onClick={fetchSubsystemStatus} className="status-btn">
          檢查子系統狀態
        </button>
      </header>
      
      <div className="tabs">
        <button 
          className={activeTab === 'immersion' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('immersion')}
        >
          沉浸式體驗
        </button>
        <button 
          className={activeTab === 'scan' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('scan')}
        >
          📷 書籍掃描
        </button>
        <button 
          className={activeTab === 'status' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('status')}
        >
          🔧 系統狀態
        </button>
      </div>

      <main>
        {activeTab === 'immersion' && (
          <>
            <form onSubmit={handleSubmit} className="narrative-form">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="在這裡輸入您的故事或情境..."
                rows="5"
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? '生成中...' : '生成沉浸式體驗'}
              </button>
              <button type="button" onClick={handleTTS} disabled={ttsLoading}>
                {ttsLoading ? '語音生成中...' : '播放語音'}
              </button>
            </form>

            {error && <p className="error-message">{error}</p>}

            {audioSrc && (
              <div className="audio-player">
                <h3>語音輸出</h3>
                <audio controls autoPlay src={audioSrc}>
                  您的瀏覽器不支援音訊播放。
                </audio>
              </div>
            )}

            {result && (
              <div className="result-container">
                <h2>生成結果</h2>
                <div className="result-section">
                  <h3>🎵 聽覺輸出 (Multi-sensory Output)</h3>
                  <pre>{JSON.stringify(result.auditory_output, null, 2)}</pre>
                </div>
                <div className="result-section">
                  <h3>🎭 感官輸出 (Multi-sensory Output)</h3>
                  <pre>{JSON.stringify(result.sensory_output, null, 2)}</pre>
                </div>
                <div className="result-section">
                  <h3>📚 內容生成 (AI Content Generation)</h3>
                  <pre>{JSON.stringify(result.knowledge_graph, null, 2)}</pre>
                </div>
              </div>
            )}
          </>
        )}

        {activeTab === 'scan' && (
          <div className="scan-section">
            <h2>📷 書籍掃描 (Image Recognition Subsystem)</h2>
            <p>上傳書籍封面圖片進行OCR識別和分類</p>
            <div className="upload-area">
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleImageUpload}
                disabled={loading}
              />
            </div>

            {error && <p className="error-message">{error}</p>}

            {bookScanResult && (
              <div className="result-container">
                <h3>掃描結果</h3>
                <div className="result-section">
                  <h4>📖 OCR識別結果</h4>
                  <pre>{JSON.stringify(bookScanResult.ocr_result, null, 2)}</pre>
                </div>
                <div className="result-section">
                  <h4>🏷️ 圖像分類</h4>
                  <pre>{JSON.stringify(bookScanResult.classification, null, 2)}</pre>
                </div>
                <div className="result-section">
                  <h4>📚 書籍資訊 (Open Library)</h4>
                  <pre>{JSON.stringify(bookScanResult.enriched_data, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'status' && (
          <div className="status-section">
            <h2>🔧 子系統狀態</h2>
            {!subsystemStatus && (
              <p>點擊上方按鈕獲取子系統狀態</p>
            )}
            {subsystemStatus && (
              <div className="result-container">
                <div className="result-section">
                  <h3>1️⃣ Image Recognition (圖像識別子系統)</h3>
                  <pre>{JSON.stringify(subsystemStatus.image_recognition, null, 2)}</pre>
                </div>
                <div className="result-section">
                  <h3>2️⃣ AI Content Generation (內容生成子系統)</h3>
                  <pre>{JSON.stringify(subsystemStatus.content_generation, null, 2)}</pre>
                </div>
                <div className="result-section">
                  <h3>3️⃣ Multi-sensory Output (多感官輸出子系統)</h3>
                  <pre>{JSON.stringify(subsystemStatus.multi_sensory_output, null, 2)}</pre>
                </div>
                <div className="result-section">
                  <h3>4️⃣ UI & Control (使用者介面控制子系統)</h3>
                  <pre>{JSON.stringify(subsystemStatus.ui_control, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
