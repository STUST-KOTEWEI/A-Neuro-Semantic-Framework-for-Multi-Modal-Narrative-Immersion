"""
擴充 RAG 圖像資料庫
增加更多主題和多語言、多地區支援
"""
import sqlite3
import json

def expand_rag_database():
    conn = sqlite3.connect("modernreader.db")
    cur = conn.cursor()
    
    # 擴充 RAG 圖像資料表結構（加入主題、地區、語言欄位）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rag_images_v2 (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_url TEXT NOT NULL,
            caption TEXT,
            tags TEXT,
            prompt TEXT,
            theme TEXT,
            region TEXT,
            language TEXT,
            emotion_tag TEXT,
            relevance_score REAL DEFAULT 0.9,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 多主題、多情緒、多地區的圖像數據
    expanded_images = [
        # Happy 情緒 - 多地區
        ("https://images.unsplash.com/photo-1469474968028-56623f02e42e", 
         "Beautiful nature landscape", '["happy", "nature", "landscape"]', 
         "happy nature scene", "nature", "global", "en", "happy"),
        ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
         "Mountain sunrise", '["happy", "mountain", "sunrise"]',
         "mountain sunrise view", "nature", "global", "en", "happy"),
        ("https://images.unsplash.com/photo-1501594907352-04cda38ebc29",
         "Ocean waves", '["calm", "ocean", "water"]',
         "peaceful ocean scene", "nature", "global", "en", "calm"),
        
        # Sad 情緒
        ("https://images.unsplash.com/photo-1515694346937-94d85e41e6f0",
         "Rainy day", '["sad", "rain", "weather"]',
         "rainy atmospheric scene", "weather", "global", "en", "sad"),
        ("https://images.unsplash.com/photo-1519331379826-f10be5486c6f",
         "Misty forest", '["sad", "forest", "fog"]',
         "misty forest atmosphere", "nature", "global", "en", "sad"),
        
        # Excited 情緒
        ("https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9",
         "Colorful fireworks", '["excited", "celebration", "fireworks"]',
         "exciting fireworks display", "celebration", "global", "en", "excited"),
        ("https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3",
         "Concert lights", '["excited", "music", "concert"]',
         "energetic concert scene", "entertainment", "global", "en", "excited"),
        
        # Calm 情緒
        ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
         "Zen garden", '["calm", "zen", "meditation"]',
         "peaceful zen garden", "wellness", "asia", "en", "calm"),
        ("https://images.unsplash.com/photo-1545289414-1c3d0b777ff0",
         "Meditation space", '["calm", "meditation", "mindfulness"]',
         "serene meditation space", "wellness", "global", "en", "calm"),
        
        # Tech 主題 - 多語言
        ("https://images.unsplash.com/photo-1518770660439-4636190af475",
         "Future technology", '["tech", "future", "innovation"]',
         "futuristic tech concept", "technology", "global", "en", "neutral"),
        ("https://images.unsplash.com/photo-1550751827-4bd374c3f58b",
         "未來科技", '["tech", "future", "AI"]',
         "AI and future technology", "technology", "global", "zh-tw", "excited"),
        ("https://images.unsplash.com/photo-1485827404703-89b55fcc595e",
         "人工智慧", '["AI", "machine learning", "tech"]',
         "artificial intelligence concept", "technology", "global", "zh-tw", "neutral"),
        
        # Food 主題 - 多文化
        ("https://images.unsplash.com/photo-1504674900247-0877df9cc836",
         "Delicious food", '["food", "cooking", "cuisine"]',
         "gourmet food presentation", "food", "global", "en", "happy"),
        ("https://images.unsplash.com/photo-1555939594-58d7cb561ad1",
         "台灣美食", '["food", "taiwanese", "cuisine"]',
         "taiwanese traditional food", "food", "taiwan", "zh-tw", "happy"),
        ("https://images.unsplash.com/photo-1540189549336-e6e99c3679fe",
         "日本料理", '["food", "japanese", "sushi"]',
         "japanese cuisine sushi", "food", "japan", "zh-tw", "happy"),
        
        # Art 主題
        ("https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b",
         "Abstract art", '["art", "abstract", "creative"]',
         "modern abstract artwork", "art", "global", "en", "surprised"),
        ("https://images.unsplash.com/photo-1549887534-1541e9326642",
         "Digital art", '["art", "digital", "creative"]',
         "digital art creation", "art", "global", "en", "excited"),
        
        # Architecture 主題 - 多地區
        ("https://images.unsplash.com/photo-1511818966892-d7d671e672a2",
         "Modern architecture", '["architecture", "modern", "building"]',
         "contemporary building design", "architecture", "global", "en", "neutral"),
        ("https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",
         "台北101", '["architecture", "taipei", "landmark"]',
         "taipei 101 building", "architecture", "taiwan", "zh-tw", "excited"),
        ("https://images.unsplash.com/photo-1548013146-72479768bada",
         "故宮博物院", '["architecture", "museum", "chinese"]',
         "palace museum architecture", "architecture", "taiwan", "zh-tw", "calm"),
        
        # Space 主題
        ("https://images.unsplash.com/photo-1419242902214-272b3f66ee7a",
         "Galaxy stars", '["space", "galaxy", "stars"]',
         "milky way galaxy view", "space", "global", "en", "surprised"),
        ("https://images.unsplash.com/photo-1446776811953-b23d57bd21aa",
         "Night sky", '["space", "astronomy", "stars"]',
         "starry night sky", "space", "global", "en", "calm"),
        
        # Sports 主題
        ("https://images.unsplash.com/photo-1461896836934-ffe607ba8211",
         "Sports action", '["sports", "action", "energy"]',
         "dynamic sports moment", "sports", "global", "en", "excited"),
        ("https://images.unsplash.com/photo-1517649763962-0c623066013b",
         "Basketball", '["sports", "basketball", "game"]',
         "basketball game action", "sports", "global", "en", "excited"),
        
        # Nature 主題 - 更多變化
        ("https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05",
         "Forest path", '["nature", "forest", "path"]',
         "peaceful forest trail", "nature", "global", "en", "calm"),
        ("https://images.unsplash.com/photo-1441974231531-c6227db76b6e",
         "Desert landscape", '["nature", "desert", "landscape"]',
         "desert sand dunes", "nature", "global", "en", "neutral"),
        ("https://images.unsplash.com/photo-1475924156734-496f6cac6ec1",
         "Cherry blossoms", '["nature", "flowers", "spring"]',
         "cherry blossom trees", "nature", "asia", "en", "happy"),
    ]
    
    # 插入擴充的圖像數據
    cur.executemany("""
        INSERT INTO rag_images_v2 
        (image_url, caption, tags, prompt, theme, region, language, emotion_tag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, expanded_images)
    
    # 同步到原 rag_images 表（保持向後兼容）
    cur.execute("""
        INSERT OR IGNORE INTO rag_images (query, image_url, description, relevance_score)
        SELECT prompt, image_url, caption, relevance_score
        FROM rag_images_v2
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ RAG 圖像資料庫已擴充！新增 {len(expanded_images)} 筆多主題、多語言、多地區圖像")
    print("📊 支援主題: nature, technology, food, art, architecture, space, sports, weather, wellness, entertainment")
    print("🌍 支援地區: global, taiwan, japan, asia")
    print("🗣️ 支援語言: en, zh-tw")
    print("😊 支援情緒: happy, sad, excited, calm, surprised, neutral")

if __name__ == "__main__":
    expand_rag_database()
