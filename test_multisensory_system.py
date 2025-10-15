"""
完整多感官系統測試
測試所有功能：情緒檢測、語音、設備廣播、圖像生成
"""

import requests
import json
import base64

API_BASE = "http://localhost:8010"


def create_test_image():
    """創建測試圖像"""
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="


def test_emotion_detection():
    """測試情緒檢測"""
    print("\n" + "="*60)
    print("🧪 測試 1: 情緒檢測 API")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_BASE}/api/detect-emotion",
            json={"image_base64": create_test_image()},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 情緒檢測成功")
            print(f"   主要情緒: {result['primary_emotion']}")
            print(f"   強度: {result['intensity']}")
            print(f"   狀態: {result['status']}")
            return result
        else:
            print(f"❌ 失敗: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return None


def test_tts():
    """測試 TTS (文字轉語音)"""
    print("\n" + "="*60)
    print("🧪 測試 2: TTS (文字轉語音)")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_BASE}/api/tts",
            json={
                "text": "你好！這是多感官閱讀器的語音測試。",
                "voice": "alloy",
                "emotion": "happy",
                "speed": 1.0
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ TTS 成功")
            print(f"   語音: {result.get('voice')}")
            print(f"   時長: {result.get('duration'):.2f} 秒")
            print(f"   格式: {result.get('format')}")
            print(f"   提供商: {result.get('provider')}")
            if result.get('note'):
                print(f"   ⚠️  {result['note']}")
            return result
        else:
            print(f"❌ 失敗: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return None


def test_stt():
    """測試 STT (語音轉文字)"""
    print("\n" + "="*60)
    print("🧪 測試 3: STT (語音轉文字)")
    print("="*60)
    
    try:
        # 使用模擬音訊數據
        mock_audio = base64.b64encode(b"mock_audio_data").decode('utf-8')
        
        response = requests.post(
            f"{API_BASE}/api/stt",
            json={
                "audio_base64": mock_audio,
                "language": "zh-TW"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ STT 成功")
            print(f"   識別文字: {result.get('text')}")
            print(f"   置信度: {result.get('confidence'):.2%}")
            print(f"   語言: {result.get('language')}")
            print(f"   提供商: {result.get('provider')}")
            if result.get('note'):
                print(f"   ⚠️  {result['note']}")
            return result
        else:
            print(f"❌ 失敗: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return None


def test_device_broadcast():
    """測試多設備廣播"""
    print("\n" + "="*60)
    print("🧪 測試 4: 多設備廣播")
    print("="*60)
    
    try:
        devices = [
            "apple_watch",
            "rayban_meta",
            "tesla_suit",
            "bhaptics",
            "aromajoin",
            "foodini"
        ]
        
        response = requests.post(
            f"{API_BASE}/api/broadcast-to-devices",
            json={
                "emotion": "happy",
                "intensity": 0.8,
                "devices": devices,
                "content": {
                    "text": "這是一個快樂的時刻！",
                    "images": ["img1.jpg", "img2.jpg", "img3.jpg"]
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 廣播成功")
            print(f"   情緒: {result['emotion']}")
            print(f"   強度: {result['intensity']}")
            print(f"   設備狀態:")
            
            for device, status in result['devices'].items():
                print(f"     • {device}: {status['status']}")
            
            return result
        else:
            print(f"❌ 失敗: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return None


def test_complete_generation():
    """測試完整生成流程"""
    print("\n" + "="*60)
    print("🧪 測試 5: 完整內容生成 (RAG + Gemini)")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_BASE}/api/generate-complete",
            json={
                "camera_image_base64": create_test_image(),
                "query": "未來科技與AI",
                "total_count": 60
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 生成成功")
            
            stats = result['statistics']
            print(f"\n   📊 統計資訊:")
            print(f"     • 總圖像: {stats['total_images']}")
            print(f"     • RAG 生成: {stats['rag_images']}")
            print(f"     • Gemini 補充: {stats['gemini_images']}")
            print(f"     • 情緒: {stats['emotion']} (強度 {stats['intensity']:.0%})")
            
            print(f"\n   🖼️  RAG 圖像範例:")
            for i, img in enumerate(result['rag_images'][:3], 1):
                print(f"     {i}. {img['caption'][:50]}...")
            
            print(f"\n   🤖 Gemini 圖像範例:")
            for i, img in enumerate(result['gemini_images'][:3], 1):
                print(f"     {i}. {img['caption'][:50]}...")
                matter = img.get('programmable_matter', {})
                if matter:
                    print(f"        物質: {matter.get('motion_pattern')} (密度 {matter.get('density'):.2f})")
            
            return result
        else:
            print(f"❌ 失敗: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return None


def test_feature_endpoints():
    """測試功能端點"""
    print("\n" + "="*60)
    print("🧪 測試 6: 功能端點 (ISBN, Podcast, NLP, RAG)")
    print("="*60)
    
    endpoints = {
        "ISBN 書籍": "/data/book-covers",
        "播客內容": "/data/podcasts",
        "NLP 分析": "/data/nlp",
        "RAG 圖像": "/data/rag-images"
    }
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()['data']
                print(f"✅ {name}: {len(data)} 筆記錄")
            else:
                print(f"❌ {name}: 失敗")
        except Exception as e:
            print(f"❌ {name}: {e}")


def main():
    print("\n" + "🚀"*30)
    print("     多感官沉浸式閱讀器 - 完整測試套件")
    print("🚀"*30)
    print(f"\n📡 API 端點: {API_BASE}")
    
    # 執行所有測試
    emotion_result = test_emotion_detection()
    tts_result = test_tts()
    stt_result = test_stt()
    broadcast_result = test_device_broadcast()
    generation_result = test_complete_generation()
    test_feature_endpoints()
    
    # 總結
    print("\n" + "="*60)
    print("📊 測試總結")
    print("="*60)
    
    results = {
        "情緒檢測": emotion_result is not None,
        "TTS": tts_result is not None,
        "STT": stt_result is not None,
        "設備廣播": broadcast_result is not None,
        "內容生成": generation_result is not None
    }
    
    passed = sum(results.values())
    total = len(results)
    
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n{'='*60}")
    print(f"總計: {passed}/{total} 測試通過")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 所有測試通過！")
        print("\n📝 下一步：")
        print("1. 在瀏覽器打開: http://localhost:8010/web/multisensory_reader.html")
        print("2. 依序操作:")
        print("   • 啟動鏡頭 → 檢測情緒")
        print("   • 連接設備 (點擊設備卡片)")
        print("   • 輸入文字 → 測試 TTS")
        print("   • 錄音 → 測試 STT")
        print("   • 生成內容 → 查看圖像輪播")
        print("   • 廣播到設備 → 體驗多感官輸出")
        
        print("\n💡 提示：")
        print("   • 設定 OPENAI_API_KEY 以啟用真實 TTS/STT")
        print("   • 設定 GEMINI_API_KEY 以啟用真實情緒檢測")
        print("   • 設定 ELEVENLABS_API_KEY 以啟用情緒語音")
    else:
        print("\n⚠️  部分測試失敗，請檢查服務器日誌")
    
    print()


if __name__ == "__main__":
    main()
