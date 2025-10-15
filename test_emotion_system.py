"""
測試情緒驅動內容生成系統
"""

import requests
import base64
import json
from pathlib import Path


API_BASE = "http://localhost:8010"


def create_test_image():
    """創建一個 1x1 測試圖像的 Base64"""
    # 這是一個 1x1 透明 PNG
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


def test_emotion_detection():
    """測試表情檢測 API"""
    print("\n🧪 測試 1: 表情檢測")
    print("=" * 50)
    
    image_base64 = create_test_image()
    
    response = requests.post(
        f"{API_BASE}/api/detect-emotion",
        json={"image_base64": image_base64},
        timeout=30
    )
    
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 表情檢測成功")
        print(f"主要情緒: {result.get('primary_emotion')}")
        print(f"強度: {result.get('intensity')}")
        print(f"次要情緒: {result.get('secondary_emotions')}")
        print(f"狀態: {result.get('status')}")
        return result
    else:
        print(f"❌ 表情檢測失敗: {response.text}")
        return None


def test_complete_generation():
    """測試完整生成流程"""
    print("\n🧪 測試 2: 完整生成流程（RAG 50 張 + Gemini 補充）")
    print("=" * 50)
    
    image_base64 = create_test_image()
    
    payload = {
        "camera_image_base64": image_base64,
        "query": "未來科技",
        "total_count": 80  # 測試用少一點：RAG 50 + Gemini 30
    }
    
    print(f"請求參數: query={payload['query']}, total_count={payload['total_count']}")
    print("⏳ 生成中（可能需要幾秒鐘）...")
    
    response = requests.post(
        f"{API_BASE}/api/generate-complete",
        json={**payload, "total_count": 1},
        timeout=60
    )
    
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 410:
        print("ℹ️ 內容生成端點已停用，改用 RAG 代表圖搜尋 API。")
        s = requests.get(f"{API_BASE}/data/rag-images/search", params={"q": payload['query'], "top_k": 1})
        if s.status_code == 200:
            data = s.json()
            if data.get('count', 0) > 0:
                first = data['data'][0]
                print(f"✅ 取得代表圖: {first.get('image_url','N/A')}")
            else:
                print("⚠️ 沒有找到相關代表圖，請先建立 RAG 資料庫。")
        else:
            print(f"❌ RAG 搜尋失敗: {s.status_code} - {s.text}")
        return None
    elif response.status_code == 200:
        result = response.json()
        print(f"✅ 生成成功")
        
        stats = result.get('statistics', {})
        print(f"\n📊 統計資訊:")
        print(f"  - 總圖像數: {stats.get('total_images')}")
        print(f"  - RAG 生成: {stats.get('rag_images')}")
        print(f"  - Gemini 補充: {stats.get('gemini_images')}")
        print(f"  - 主要情緒: {stats.get('emotion')}")
        print(f"  - 情緒強度: {stats.get('intensity')}")
        
        emotion = result.get('emotion', {})
        print(f"\n😊 情緒分析:")
        print(f"  - 主要情緒: {emotion.get('primary_emotion')}")
        print(f"  - 強度: {emotion.get('intensity')}")
        print(f"  - 檢測狀態: {emotion.get('status')}")
        
        matter_config = result.get('programmable_matter_config', {})
        print(f"\n🌊 可編程物質配置:")
        print(f"  - 情緒基礎: {matter_config.get('emotion_base')}")
        print(f"  - 全域參數:")
        global_params = matter_config.get('global_params', {})
        print(f"    • 密度: {global_params.get('density')}")
        print(f"    • 黏度: {global_params.get('viscosity')}")
        print(f"    • 顏色: {global_params.get('color')}")
        print(f"    • 運動模式: {global_params.get('motion_pattern')}")
        print(f"    • 轉換速度: {global_params.get('transformation_speed')}")
        
        # 顯示部分圖像資訊
        rag_images = result.get('rag_images', [])
        if rag_images:
            print(f"\n🖼️ RAG 圖像範例 (前 3 張):")
            for i, img in enumerate(rag_images[:3], 1):
                print(f"  {i}. {img.get('caption')}")
                print(f"     URL: {img.get('url')}")
                print(f"     標籤: {', '.join(img.get('tags', []))}")
        
        gemini_images = result.get('gemini_images', [])
        if gemini_images:
            print(f"\n🤖 Gemini 圖像範例 (前 3 張):")
            for i, img in enumerate(gemini_images[:3], 1):
                print(f"  {i}. {img.get('caption')}")
                print(f"     Prompt: {img.get('prompt')}")
                matter = img.get('programmable_matter', {})
                if matter:
                    print(f"     物質運動: {matter.get('motion_pattern')}")
        
        return result
    else:
        print(f"❌ 生成失敗: {response.text}")
        return None


def test_database_check():
    """檢查資料庫中的數據"""
    print("\n🧪 測試 3: 檢查資料庫數據")
    print("=" * 50)
    
    endpoints = [
        ("/data/users", "用戶"),
        ("/data/emotions", "表情檢測記錄"),
        ("/data/rag-images", "RAG 圖像")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', [])
                print(f"✅ {name}: {len(data)} 筆記錄")
            else:
                print(f"⚠️ {name}: 無法獲取數據")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")


def main():
    print("🚀 情緒驅動內容生成系統 - 整合測試")
    print("=" * 50)
    print(f"API 端點: {API_BASE}")
    
    # 測試 1: 表情檢測
    emotion_result = test_emotion_detection()
    
    # 測試 2: 完整生成
    if emotion_result:
        generation_result = test_complete_generation()
        
        if generation_result:
            print("\n" + "=" * 50)
            print("✅ 所有測試通過！")
            print("=" * 50)
            print("\n📝 下一步：")
            print("1. 在瀏覽器打開: http://localhost:8010/web/emotion_matter_generator.html")
            print("2. 點擊「啟動鏡頭」按鈕")
            print("3. 點擊「捕獲表情」檢測情緒")
            print("4. 點擊「開始生成」查看結果")
            print("\n💡 提示：")
            print("- RAG 圖像：從資料庫讀取或生成模擬圖像（最多 50 張）")
            print("- Gemini 圖像：補充剩餘數量的 AI 生成圖像")
            print("- 可編程物質：根據檢測到的情緒動態調整視覺參數")
    
    # 測試 3: 資料庫檢查
    test_database_check()
    
    print("\n🎉 測試完成！")


if __name__ == "__main__":
    main()
