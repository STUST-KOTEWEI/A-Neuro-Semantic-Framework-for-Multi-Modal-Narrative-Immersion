# Modern Reader React Native App

## 功能

- 透過 `/sync/manifest` + ETag 差異同步
- WebSocket `/ws/sync` 推播變更
- 點擊檔案載入內容 (`/sync/file`)
- 使用 API Key 保護端點

## 目錄結構 (最小骨架)

```text
frontends/react-native-app/
  App.js
  package.json
  .env.example
```

(實際完整 RN 專案若要建置原生模組，需要執行 `npx react-native init`；這裡提供的是輕量示例，可用 Expo 或整合到既有專案。)

## 安裝與啟動

1. 複製環境變數：

  ```bash
  cp .env.example .env   # 若使用 react-native-config 套件可自動載入
  ```

2. 安裝套件：

  ```bash
  npm install
  ```

3. 啟動 Metro：

  ```bash
  npm start
  ```

4. 另外在原生專案或 Expo 專案中引入 `App.js` 內容。

## 直接整合到既有 React Native 專案

將 `App.js` 複製到你專案根目錄（或 `src/`）並調整：

```js
const BASE_URL = 'http://<你的伺服器>:8010';
const API_KEY = '<你的 API Key>';
```

## 測試同步

啟動後端：

```bash
python integrated_server.py
```

修改白名單檔案（例如 `models/ModernReaderLite.modelfile`）→ App 偵測到 WebSocket update → 重新拉取 manifest。

## 常見問題

1. Exit Code 1 執行失敗：未初始化完整 RN 專案或沒有 ios/android 目錄。
2. iOS 模擬器無法連線 `localhost`：改用 `http://127.0.0.1:8010` 或 Mac 局域網 IP。
3. Android 模擬器需用 `http://10.0.2.2:8010`。
4. WebSocket 斷線：會自動 5 秒後重連。

## 下一步可擴充

- 加入登入流程與 token 換發
- 內嵌離線快取 (AsyncStorage)
- 加入 RAG 查詢介面 (`/rag/query`)
- 模型選擇 UI (`/ai/model-select`)
