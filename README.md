# A Neuro-Semantic Framework for Multi-Modal Narrative Immersion

## 專案願景

故事的核心在於體驗，而非僅是文字。數百年來，我們透過視覺解碼符號來理解故事，但文字本身僅是通往故事世界的媒介。

Project H.O.L.O. 的使命，就是打破這個媒介的限制，提出一個大膽的問題：如果我們不僅能"閱讀"故事，而是能真正地"感受"它呢？

## 專案目標

- 重新定義"閱讀"的體驗，讓讀者不僅僅是解讀文字，而是全方位感受故事中的情感與情境，成為故事的一部分。

## 核心技術

1. **深度語意分析**：
   - 使用自然語言處理 (NLP) 技術，將文本解構為語意單元。
   - 分析情感、語調、角色關係與故事背景。

2. **生成式 AI**：
   - 基於語意單元創建動態的聽覺體驗（例如角色對話、環境音效）。
   - 使用文本到聲音 (Text-to-Sound) 與文本到氣味 (Text-to-Scent) 的生成技術，
     模擬多感官回饋。

3. **多模態感知系統**：
   - 整合聽覺、觸覺與嗅覺回饋，打造沉浸式的敘事體驗。
   - 開發 API 供硬體設備（如觸覺反饋裝置）使用。

## 預期成果

- 一個沉浸式敘事框架，能夠將任何文本轉化為多感官體驗。
- 支援多語言，應用於教育、娛樂與療癒場景。

## 版權與貢獻

歡迎對此專案感興趣的開發者提供意見並提交 PR.

---

## Backend 功能總覽

整合伺服器 `integrated_server.py` (FastAPI) 已提供以下模組：

| 類別 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| 健康檢查 | `GET /health` | 基本狀態 | 無需 |
| 同步 Manifest | `GET /sync/manifest` | 回傳白名單檔案摘要<br>(sha256, mtime, size, etag) | 需 API Key |
| 檔案內容 | `GET /sync/file?path=...` | 取得單一白名單檔案內容 | 需 API Key |
| 功能旗標 | `GET /sync/feature-flags` | 目前啟用的功能旗標 | 需 API Key |
| 模型選擇 | `GET /ai/model-select` | 根據裝置/記憶體/省電/品質偏好自動選擇模型 | 需 API Key |
| RAG 查詢 | `GET /rag/query?q=...` | 向本地嵌入式檔案庫檢索 | 需 API Key |
| RAG 列出 | `GET /rag/list` | 清單與數量 | 需 API Key |
| RAG Upsert | `POST /rag/upsert` | 新增或更新文件 | 需 API Key |
| RAG 刪除 | `DELETE /rag/delete?doc_id=...` | 刪除指定文件 | 需 API Key |
| WebSocket Sync | `WS /ws/sync` | 變更推播 (etag 改變) | 無（可再加 API Key） |

### API Key 驗證

環境變數 `MODERN_READER_API_KEYS` (逗號分隔) 預設: `dev-key-123,example-key-abc`。
請於請求 header 加入：

```http
X-API-Key: dev-key-123
```

### 同步流程 (Manifest + ETag)

1. 客戶端啟動：`GET /sync/manifest` 取得 `files[]` + `etag`
2. 比對本地快取，決定需要下載的檔案清單。
3. 對每個需要的檔案呼叫：`GET /sync/file?path=<whitelisted>`
4. 監聽 WebSocket：`/ws/sync`，收到 `{"type":"update","etag":...}` 後重拉 manifest。

### WebSocket 訊息格式

```json
{ "type": "welcome", "etag": "<hash>", "file_count": N }
{ "type": "update", "etag": "<new-hash>", "changed": true, "ts": 1710000000 }
{ "type": "pong" }
```

### 模型選擇範例

```http
GET /ai/model-select?device=mobile&memory_mb=1024
-> { "chosen": "ModernReaderLite", "fallback": "ModernReader",
     "reasons": ["device-class"], ... }

GET /ai/model-select?device=desktop&memory_mb=8192&prefer_quality=true
-> { "chosen": "ModernReader", "reasons": ["quality-override"] }
```

### RAG CRUD 使用

查詢：

```http
GET /rag/query?q=關鍵字&top_k=3
```

新增/更新：

```http
POST /rag/upsert { "text": "一段內容", "doc_id": "可選", "meta": {"source":"note"} }
```

列表：

```http
GET /rag/list
```

刪除：

```http
DELETE /rag/delete?doc_id=xxxx
```

### 測試

單元 / 端點測試位於 `tests/`：

- `test_rag.py` RAG 查詢 / Upsert / 刪除 / Auth
- `test_model_select.py` 模型選擇自動降級/品質覆寫/認證
- `test_sync_auth.py` 同步與檔案讀取的 API Key 保護

執行 (需安裝 dev 依賴)：

```bash
pytest -q
```

### React Native / Flutter / 其他客戶端

`frontends/react-native-app/` 提供最小示例（Manifest + WebSocket）。
可參考 `clients/sync_client.py` 的 Python CLI 同步實作 (ETag + API Key)。

---

## 後續 Roadmap (建議)

- 嵌入向量改為真正 embedding model (目前為簡單 token 重疊) 並增加向量索引
- 加入 OpenAI / Azure OpenAI / 本地 LLM 選擇層
- RAG 查詢結果 rerank
- WebSocket 加入簽章或 API Key 驗證
- 使用者帳號 + OAuth / JWT (整合 `user_auth_sql.py` 或 dual auth)
- File diff / chunk 智慧同步 (目前為整檔)
