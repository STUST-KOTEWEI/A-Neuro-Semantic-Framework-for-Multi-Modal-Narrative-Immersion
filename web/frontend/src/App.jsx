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
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [imageAnalysis, setImageAnalysis] = useState(null);
  const [imageLoading, setImageLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [contentLoading, setContentLoading] = useState(false);

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

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageAnalysis = async () => {
    if (!imageFile) {
      setError('請先上傳圖片');
      return;
    }

    setImageLoading(true);
    setError('');
    setImageAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await fetch(`${API_URL}/analyze_image?use_ocr=true&use_vision=true`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`圖片分析失敗，狀態碼: ${response.status}`);
      }

      const data = await response.json();
      setImageAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setImageLoading(false);
    }
  };

  const handleGenerateContent = async (contentType) => {
    if (!text.trim()) {
      setError('請輸入文字內容');
      return;
    }

    setContentLoading(true);
    setError('');
    setGeneratedContent(null);

    try {
      const response = await fetch(`${API_URL}/generate_content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          content_type: contentType,
          style: 'narrative',
          duration_minutes: 5
        }),
      });

      if (!response.ok) {
        throw new Error(`內容生成失敗，狀態碼: ${response.status}`);
      }

      const data = await response.json();
      setGeneratedContent(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setContentLoading(false);
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
        <p>多模態敘事沉浸體驗生成器 - 整合影像識別與生成式 AI</p>
      </header>
      <main>
        <div className="feature-section">
          <h2>📷 影像識別與情緒分析</h2>
          <div className="image-upload-section">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              disabled={imageLoading}
            />
            <button onClick={handleImageAnalysis} disabled={imageLoading || !imageFile}>
              {imageLoading ? '分析中...' : '分析圖片'}
            </button>
          </div>
          
          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="預覽" style={{ maxWidth: '400px', maxHeight: '300px' }} />
            </div>
          )}

          {imageAnalysis && (
            <div className="result-container">
              <h3>圖片分析結果</h3>
              {imageAnalysis.vision_analysis && (
                <div className="result-section">
                  <h4>情緒檢測</h4>
                  <pre>{JSON.stringify(imageAnalysis.vision_analysis.emotions, null, 2)}</pre>
                  <h4>標籤識別</h4>
                  <pre>{JSON.stringify(imageAnalysis.vision_analysis.labels, null, 2)}</pre>
                </div>
              )}
              {imageAnalysis.ocr_result && (
                <div className="result-section">
                  <h4>文字提取 (OCR)</h4>
                  <p><strong>完整文字：</strong>{imageAnalysis.ocr_result.full_text}</p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="feature-section">
          <h2>🤖 生成式 AI 內容</h2>
          <form onSubmit={handleSubmit} className="narrative-form">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="在這裡輸入您的故事或情境..."
              rows="5"
              disabled={loading}
            />
            <div className="button-group">
              <button type="submit" disabled={loading}>
                {loading ? '生成中...' : '生成沉浸式體驗'}
              </button>
              <button type="button" onClick={handleTTS} disabled={ttsLoading}>
                {ttsLoading ? '語音生成中...' : '播放語音 (TTS)'}
              </button>
              <button type="button" onClick={() => handleGenerateContent('summary')} disabled={contentLoading}>
                生成摘要
              </button>
              <button type="button" onClick={() => handleGenerateContent('podcast')} disabled={contentLoading}>
                生成播客腳本
              </button>
              <button type="button" onClick={() => handleGenerateContent('analysis')} disabled={contentLoading}>
                文本分析
              </button>
            </div>
          </form>
        </div>

        {error && <p className="error-message">{error}</p>}

        {audioSrc && (
          <div className="audio-player">
            <h3>語音輸出</h3>
            <audio controls autoPlay src={audioSrc}>
              您的瀏覽器不支援音訊播放。
            </audio>
          </div>
        )}

        {generatedContent && (
          <div className="result-container">
            <h2>生成內容</h2>
            <div className="result-section">
              {generatedContent.content && <p>{generatedContent.content}</p>}
              {generatedContent.script && <pre>{generatedContent.script}</pre>}
              {generatedContent.emoticon && <p style={{ fontSize: '2em' }}>{generatedContent.emoticon}</p>}
            </div>
          </div>
        )}

        {result && (
          <div className="result-container">
            <h2>沉浸式體驗結果</h2>
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
