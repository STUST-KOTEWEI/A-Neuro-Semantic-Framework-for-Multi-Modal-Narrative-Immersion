#!/bin/bash
# 快速啟動 HTTPS 伺服器腳本

echo "🚀 啟動 AI Reader HTTPS 伺服器..."
echo ""
echo "📋 啟動資訊:"
echo "   • HTTPS: https://localhost:8443"
echo "   • 前端: https://localhost:8443/web/multisensory_reader.html"
echo "   • 健康: https://localhost:8443/health"
echo ""
echo "⚠️  瀏覽器會顯示憑證警告，點擊「進階」→「繼續前往」即可"
echo ""

# 檢查 Python 與依賴
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 python3，請先安裝 Python"
    exit 1
fi

# 檢查憑證
if [ ! -f "certificates/cert.pem" ] || [ ! -f "certificates/key.pem" ]; then
    echo "⚠️  SSL 憑證不存在，將自動建立..."
fi

# 啟動伺服器
python3 https_server.py
