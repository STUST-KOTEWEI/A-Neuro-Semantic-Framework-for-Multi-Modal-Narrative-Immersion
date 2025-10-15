# 伺服器啟動指南

## 快速啟動

### 選項 1: HTTPS 伺服器（推薦用於前端測試）

```bash
python https_server.py
```

- **HTTPS URL**: `https://localhost:8443`
- **優點**: 支援相機、麥克風等需要 HTTPS 的瀏覽器 API
- **注意**: 瀏覽器會顯示自簽憑證警告，點「進階」→「繼續前往」即可

### 選項 2: HTTP 伺服器（開發除錯用）

```bash
python integrated_server.py
```

或

```bash
uvicorn integrated_server:app --host 0.0.0.0 --port 8010 --reload
```

- **HTTP URL**: `http://localhost:8010`
- **優點**: 無憑證警告，支援 hot reload
- **限制**: 瀏覽器會阻擋相機/麥克風存取（需 HTTPS）

## 常用端點

### 健康檢查

```bash
curl https://localhost:8443/health -k
# 或
curl http://localhost:8010/health
```

### RAG 代表圖搜尋

```bash
curl "https://localhost:8443/data/rag-images/search?q=科技&top_k=1" -k
# 或
curl "http://localhost:8010/data/rag-images/search?q=科技&top_k=1"
```

### 前端頁面

- **多感官閱讀器**: `https://localhost:8443/web/multisensory_reader.html`
- **情緒生成器**: `https://localhost:8443/web/emotion_matter_generator.html`
- **登入頁面**: `https://localhost:8443/web/auth.html`

## 測試流程

### 執行整合測試

```bash
# 先啟動伺服器（另一個終端）
python https_server.py

# 執行測試
python test_complete_system.py
```

### 初始化資料庫

```bash
# 建立資料庫結構
python init_modernreader_db.py

# 擴充 RAG 圖像資料
python expand_rag_database.py
```

## 常見問題

### Q: 瀏覽器顯示「不安全」警告？

**A**: 這是自簽憑證的正常行為：
1. 點擊「進階」或 "Advanced"
2. 點擊「繼續前往 localhost (不安全)」或 "Proceed to localhost (unsafe)"
3. 這在本地開發環境是安全的

### Q: 相機無法啟動？

**A**: 相機需要 HTTPS：
- 使用 `python https_server.py` 啟動
- 或使用 ngrok 等工具建立 HTTPS tunnel

### Q: 找不到 uvicorn？

**A**: 安裝依賴：

```bash
pip install -r requirements.txt
# 或
pip install fastapi uvicorn sqlalchemy bcrypt pyjwt pydantic[email]
```

## 進階設定

### 自訂埠號

編輯 `https_server.py` 或使用環境變數：

```bash
PORT=9000 python https_server.py
```

### 重新產生憑證

```bash
rm certificates/*.pem
python https_server.py  # 會自動重建
```

### 正式環境部署

使用 Gunicorn + Nginx + Let's Encrypt：

```bash
gunicorn integrated_server:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --keyfile=/path/to/privkey.pem \
  --certfile=/path/to/fullchain.pem
```
