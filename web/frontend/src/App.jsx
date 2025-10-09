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

  return (
    <div className="App">
      <header className="App-header">
        <h1>Project-HOLO</h1>
        <p>多模態敘事沉浸體驗生成器</p>
      </header>
      <main>
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
              <h3>聽覺輸出</h3>
              <pre>{JSON.stringify(result.auditory_output, null, 2)}</pre>
            </div>
            <div className="result-section">
              <h3>感官輸出</h3>
              <pre>{JSON.stringify(result.sensory_output, null, 2)}</pre>
            </div>
            <div className="result-section">
              <h3>知識圖譜</h3>
              <pre>{JSON.stringify(result.knowledge_graph, null, 2)}</pre>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
