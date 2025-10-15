"""測試所有 ModernReader 功能 API 端點"""
import requests
import json

BASE_URL = "http://localhost:8010"

def test_api(endpoint, name):
    print(f"\n{'='*60}")
    print(f"測試: {name}")
    print(f"端點: {endpoint}")
    print(f"{'='*60}")
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}")
        if resp.status_code == 200:
            data = resp.json()
            count = len(data.get("data", []))
            print(f"✅ 成功！返回 {count} 筆數據")
            if count > 0:
                print(f"範例數據:")
                print(json.dumps(data["data"][0], indent=2, ensure_ascii=False))
        else:
            print(f"❌ 失敗！狀態碼: {resp.status_code}")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

if __name__ == "__main__":
    print("🚀 開始測試 ModernReader 所有功能 API...")
    
    test_api("/data/users", "📊 用戶數據")
    test_api("/data/book-covers", "📚 書籍封面 (ISBN)")
    test_api("/data/podcasts", "🔊 播客內容 (TTS)")
    test_api("/data/emotions", "🎙️ 情感偵測 (STT)")
    test_api("/data/nlp", "📝 NLP 分析")
    test_api("/data/rag-images", "🔍 RAG 搜圖")
    
    print(f"\n{'='*60}")
    print("✅ 所有測試完成！")
    print(f"{'='*60}")
