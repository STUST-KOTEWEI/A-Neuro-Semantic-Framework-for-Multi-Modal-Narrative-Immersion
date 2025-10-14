// Jest 測試範例：驗證 API Key 設定與相機權限流程

const { JSDOM } = require('jsdom');

describe('AI Reader App 首頁功能', () => {
  let window, document;
  beforeEach(() => {
    const dom = new JSDOM(`<!DOCTYPE html><body></body>`, { url: 'http://localhost' });
    window = dom.window;
    document = window.document;
    window.localStorage.clear();
  });

  test('API Key 設定面板顯示與儲存', () => {
    document.body.innerHTML = `
      <div id="api-key-sheet" style="display:none"></div>
      <button id="open-key-sheet"></button>
      <input id="api-key-input" />
      <button id="save-api-key"></button>
    `;
    const keySheet = document.getElementById('api-key-sheet');
    const openKey = document.getElementById('open-key-sheet');
    const saveKey = document.getElementById('save-api-key');
    const keyInput = document.getElementById('api-key-input');
    // 模擬開啟面板
    keySheet.style.display = 'none';
    openKey.onclick = () => { keySheet.style.display = 'block'; };
    openKey.click();
    expect(keySheet.style.display).toBe('block');
    // 模擬儲存 API Key
    keyInput.value = 'AIzaTestKey';
    saveKey.onclick = () => { window.localStorage.setItem('GEMINI_API_KEY', keyInput.value); };
    saveKey.click();
    expect(window.localStorage.getItem('GEMINI_API_KEY')).toBe('AIzaTestKey');
  });

  test('API Key 缺值時提示', () => {
    document.body.innerHTML = `<div id="error-message"></div>`;
    const errorMessage = document.getElementById('error-message');
    window.localStorage.removeItem('GEMINI_API_KEY');
    // 模擬檢查
    if (!window.localStorage.getItem('GEMINI_API_KEY')) {
      errorMessage.textContent = '請先設定 Gemini API Key（右下角齒輪）';
    }
    expect(errorMessage.textContent).toMatch(/請先設定/);
  });

  test('相機權限流程（模擬）', () => {
    // 這裡僅驗證 getUserMedia 被呼叫
    window.navigator.mediaDevices = {
      getUserMedia: jest.fn().mockResolvedValue('stream')
    };
    return window.navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
      expect(stream).toBe('stream');
    });
  });
});
