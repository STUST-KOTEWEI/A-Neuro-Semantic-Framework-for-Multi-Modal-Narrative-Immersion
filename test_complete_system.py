"""
全面測試多感官系統 - 包含智能表情偵測、主題推薦、圖片顯示
"""
import requests
import json
import time

API_BASE = "http://localhost:8010"

def test_emotion_detection():
    """測試表情偵測（智能動態偵測）"""
    print("\n" + "="*60)
    print("🎭 測試 1: 表情偵測（動態智能）")
    print("="*60)
    
    # 測試多次，驗證表情偵測是否會動態變化
    for i in range(3):
        print(f"\n第 {i+1} 次偵測:")
        response = requests.post(
            f"{API_BASE}/api/detect-emotion",
            json={"image_base64": f"test_image_{i}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ 主要情緒: {result['primary_emotion']}")
            print(f"  📊 強度: {result['intensity']:.2%}")
            print(f"  🎯 次要情緒: {result.get('secondary_emotions', [])}")
            print(f"  🤖 AI備註: {result.get('ai_note', 'N/A')}")
            print(f"  ⏰ 時間戳: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['timestamp']))}")
        else:
            print(f"  ❌ 失敗: {response.status_code} - {response.text}")
        
        time.sleep(1)  # 間隔1秒

def test_complete_generation():
    """測試完整生成流程（情緒 + RAG + AI推薦）"""
    print("\n" + "="*60)
    print("🚀 測試 2: 完整生成流程（情緒偵測 + RAG + AI推薦）")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE}/api/generate-complete",
        json={
            "camera_image_base64": "test_camera_image",
            "query": "未來科技與人工智慧",
            "total_count": 1
        }
    )
    
    if response.status_code == 410:
        print("ℹ️ 內容生成端點已停用，改用 RAG 代表圖搜尋 API。")
        s = requests.get(f"{API_BASE}/data/rag-images/search", params={"q": "未來科技與人工智慧", "top_k": 1})
        if s.status_code == 200:
            data = s.json()
            if data.get('count', 0) > 0:
                first = data['data'][0]
                print(f"✅ 取得代表圖: {first.get('image_url','N/A')}")
            else:
                print("⚠️ 沒有找到相關代表圖，請先建立 RAG 資料庫。")
        else:
            print(f"❌ RAG 搜尋失敗: {s.status_code} - {s.text}")
    elif response.status_code == 200:
        result = response.json()
        
        print("\n📊 情緒分析結果:")
        print(f"  主要情緒: {result['emotion']['primary_emotion']}")
        print(f"  強度: {result['emotion']['intensity']:.2%}")
        
        print("\n🖼️ 圖像生成統計:")
        stats = result['statistics']
        print(f"  總圖片數: {stats['total_images']}")
        print(f"  RAG 圖片: {stats['rag_images']}")
        print(f"  Gemini 圖片: {stats['gemini_images']}")
        
        print("\n🤖 AI 智能分析:")
        ai = result.get('ai_analysis', {})
        print(f"  偵測情緒: {ai.get('emotion_detected', 'N/A')}")
        print(f"  信心度: {ai.get('confidence', 0):.2%}")
        print(f"  AI備註: {ai.get('ai_note', 'N/A')}")
        
        theme_rec = ai.get('theme_recommendation', {})
        if theme_rec:
            print(f"\n🎨 主題推薦:")
            print(f"  建議主題: {', '.join(theme_rec.get('themes', []))}")
            print(f"  說明: {theme_rec.get('description', 'N/A')}")
            print(f"  色彩: {', '.join(theme_rec.get('colors', []))}")
            print(f"  音樂風格: {theme_rec.get('music_genre', 'N/A')}")
        
        print(f"\n下一步: {ai.get('next_action', 'N/A')}")
        
        print("\n📷 圖像範例 (前5張):")
        for i, img in enumerate(result['all_images'][:5], 1):
            print(f"  {i}. {img['caption']}")
            print(f"     來源: {img['source']}")
            print(f"     URL: {img['url'][:80]}...")
            if 'ai_matched' in img:
                print(f"     AI匹配: ✅")
            if 'theme' in img:
                print(f"     主題: {img.get('theme', 'N/A')} | 地區: {img.get('region', 'N/A')} | 語言: {img.get('language', 'N/A')}")
        
    else:
        print(f"❌ 失敗: {response.status_code} - {response.text}")

def test_tts():
    """測試 TTS（文字轉語音）"""
    print("\n" + "="*60)
    print("🔊 測試 3: 文字轉語音 (TTS)")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE}/api/tts",
        json={
            "text": "歡迎使用多感官沉浸式閱讀器，讓AI幫你探索未來世界！",
            "voice": "alloy",
            "emotion": "excited"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ TTS 生成成功")
        print(f"  引擎: {result.get('engine', 'N/A')}")
        print(f"  狀態: {result.get('status', 'N/A')}")
        if 'audio_url' in result:
            print(f"  音訊 URL: {result['audio_url']}")
        if 'audio_base64' in result:
            print(f"  Base64 長度: {len(result['audio_base64'])} 字元")
    else:
        print(f"  ❌ 失敗: {response.status_code} - {response.text}")

def test_device_broadcast():
    """測試設備廣播"""
    print("\n" + "="*60)
    print("📡 測試 4: 設備廣播")
    print("="*60)
    
    response = requests.post(
        f"{API_BASE}/api/broadcast-to-devices",
        json={
            "emotion": "happy",
            "intensity": 0.85,
            "devices": ["apple_watch", "rayban_meta", "bhaptics"],
            "content": {
                "text": "測試廣播內容",
                "images": ["https://example.com/img1.jpg"]
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('placeholder'):
            print("ℹ️ 多感官設備為合作預留區，未實際廣播。")
        else:
            print(f"  ✅ 廣播成功")
            print(f"  情緒: {result.get('emotion','N/A')}")
            print(f"  強度: {result.get('intensity','N/A')}")
    else:
        print(f"  ❌ 失敗: {response.status_code} - {response.text}")

def test_rag_images():
    """測試 RAG 圖像資料庫"""
    print("\n" + "="*60)
    print("🖼️ 測試 5: RAG 圖像資料庫（多主題、多語言、多地區）")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/data/rag-images")
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ 資料庫讀取成功")
        print(f"  總圖片數: {len(result['data'])}")
        
        print("\n  圖片主題分布:")
        themes = {}
        emotions = {}
        regions = {}
        
        for img in result['data']:
            theme = img.get('theme', 'unknown')
            emotion = img.get('emotion_tag', 'neutral')
            region = img.get('region', 'global')
            
            themes[theme] = themes.get(theme, 0) + 1
            emotions[emotion] = emotions.get(emotion, 0) + 1
            regions[region] = regions.get(region, 0) + 1
        
        print(f"    主題: {dict(themes)}")
        print(f"    情緒: {dict(emotions)}")
        print(f"    地區: {dict(regions)}")
    else:
        print(f"  ❌ 失敗: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("\n🌟 多感官沉浸式閱讀器 - 全面測試")
    print("=" * 60)
    
    try:
        test_emotion_detection()
        test_complete_generation()
        test_tts()
        test_device_broadcast()
        test_rag_images()
        
        print("\n" + "="*60)
        print("✅ 所有測試完成！")
        print("="*60)
        print("\n💡 下一步:")
        print("  1. 在瀏覽器打開: http://localhost:8010/web/multisensory_reader.html")
        print("  2. 依序操作: 啟動鏡頭 → 檢測情緒 → 連接設備 → 生成內容")
        print("  3. 觀察表情偵測數值是否動態變化")
        print("  4. 檢查圖片是否能正確顯示")
        print("  5. 測試主題推薦是否根據情緒調整")
        
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {e}")
