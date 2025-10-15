"""初始化 ModernReader 資料庫，包含所有功能所需的資料表與範例數據"""
import sqlite3
import json
from datetime import datetime

def init_database():
    conn = sqlite3.connect("modernreader.db")
    cur = conn.cursor()
    
    # 1. 用戶資料表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            subscription_tier TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. 書籍封面資料表 (ISBN)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS book_covers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            cover_image_url TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. 播客內容資料表 (TTS)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS podcast_contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            audio_url TEXT,
            duration INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 4. 情感偵測資料表 (STT)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS emotion_detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_text TEXT NOT NULL,
            emotion TEXT NOT NULL,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 5. NLP 分析結果資料表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nlp_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            analysis_type TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 6. RAG 搜圖資料表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rag_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            image_url TEXT NOT NULL,
            description TEXT,
            relevance_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 插入範例數據
    
    # 用戶範例
    sample_users = [
        ("demo1@example.com", "demo1", "hashed_password_1", "free"),
        ("demo2@example.com", "demo2", "hashed_password_2", "pro"),
        ("demo3@example.com", "demo3", "hashed_password_3", "plus"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO users (email, username, password_hash, subscription_tier) VALUES (?, ?, ?, ?)",
        sample_users
    )
    
    # 書籍封面範例
    sample_books = [
        ("9780134685991", "Effective Java", "Joshua Bloch", 
         "https://covers.openlibrary.org/b/isbn/9780134685991-L.jpg",
         "Java 程式設計最佳實踐指南"),
        ("9781491950357", "Programming Rust", "Jim Blandy",
         "https://covers.openlibrary.org/b/isbn/9781491950357-L.jpg",
         "Rust 系統程式設計完全指南"),
        ("9780134757599", "Refactoring", "Martin Fowler",
         "https://covers.openlibrary.org/b/isbn/9780134757599-L.jpg",
         "重構：改善既有程式的設計"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO book_covers (isbn, title, author, cover_image_url, description) VALUES (?, ?, ?, ?, ?)",
        sample_books
    )
    
    # 播客內容範例
    sample_podcasts = [
        ("AI 技術趨勢", "探討最新的人工智慧技術發展，包含 GPT、DALL-E、Stable Diffusion 等。", 
         "/audio/ai_trends.mp3", 1200),
        ("量子計算入門", "深入淺出介紹量子計算的基本概念與未來應用。",
         "/audio/quantum_computing.mp3", 1800),
        ("區塊鏈與 Web3", "解析區塊鏈技術如何重塑網路生態。",
         "/audio/blockchain_web3.mp3", 1500),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO podcast_contents (title, content, audio_url, duration) VALUES (?, ?, ?, ?)",
        sample_podcasts
    )
    
    # 情感偵測範例
    sample_emotions = [
        ("今天天氣真好，心情很開心！", "快樂", 0.92),
        ("這個專案進度落後讓我很焦慮", "焦慮", 0.85),
        ("終於完成這個困難的任務了", "成就感", 0.88),
        ("這個結果讓我有點失望", "失望", 0.78),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO emotion_detections (audio_text, emotion, confidence) VALUES (?, ?, ?)",
        sample_emotions
    )
    
    # NLP 分析範例
    sample_nlp = [
        ("人工智慧正在改變世界", "sentiment", json.dumps({"sentiment": "positive", "score": 0.89})),
        ("Machine learning is a subset of AI", "entity_recognition", 
         json.dumps({"entities": [{"text": "Machine learning", "type": "TECH"}, {"text": "AI", "type": "TECH"}]})),
        ("今天台北市氣溫28度", "entity_recognition",
         json.dumps({"entities": [{"text": "台北市", "type": "LOCATION"}, {"text": "28度", "type": "QUANTITY"}]})),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO nlp_analyses (text, analysis_type, result) VALUES (?, ?, ?)",
        sample_nlp
    )
    
    # RAG 搜圖範例
    sample_rag_images = [
        ("sunset beach", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e", 
         "美麗的海灘日落景色", 0.95),
        ("modern architecture", "https://images.unsplash.com/photo-1511818966892-d7d671e672a2",
         "現代建築設計", 0.88),
        ("space galaxy", "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a",
         "壯麗的銀河星空", 0.92),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO rag_images (query, image_url, description, relevance_score) VALUES (?, ?, ?, ?)",
        sample_rag_images
    )
    
    conn.commit()
    conn.close()
    print("✅ ModernReader 資料庫初始化完成！")
    print("📊 已建立 6 個資料表並插入範例數據")

if __name__ == "__main__":
    init_database()
