"""
HTTPS Server Setup for AI Reader
Creates a self-signed certificate and runs the server with HTTPS
"""

import ssl
import uvicorn
from pathlib import Path
import subprocess
import os

def create_self_signed_cert():
    """Create a self-signed SSL certificate"""
    cert_dir = Path("certificates")
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    # Check if certificates already exist
    if cert_file.exists() and key_file.exists():
        print("SSL certificates already exist")
        return str(cert_file), str(key_file)
    
    # Create self-signed certificate
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096", 
        "-keyout", str(key_file), "-out", str(cert_file),
        "-days", "365", "-nodes", "-subj", 
        "/C=TW/ST=Taiwan/L=Taipei/O=AI-Reader/OU=Development/CN=localhost"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"SSL certificates created: {cert_file}, {key_file}")
        return str(cert_file), str(key_file)
    except subprocess.CalledProcessError as e:
        print(f"Failed to create SSL certificates: {e}")
        return None, None
    except FileNotFoundError:
        print("OpenSSL not found. Please install OpenSSL or use ngrok for HTTPS")
        return None, None

def run_https_server():
    """Run the integrated FastAPI server with HTTPS"""
    cert_file, key_file = create_self_signed_cert()
    
    if cert_file and key_file:
        print("\n🔒 Starting HTTPS server (Integrated Server)...")
        print(f"🌐 HTTPS URL: https://localhost:8443")
        print(f"🌐 HTTP URL:  http://localhost:8010")
        print("\n📋 可用端點:")
        print("   • https://localhost:8443/health")
        print("   • https://localhost:8443/web/multisensory_reader.html")
        print("   • https://localhost:8443/data/rag-images/search?q=科技")
        print("\n⚠️  自簽憑證安全警告:")
        print("   瀏覽器會顯示不安全警告，點擊「進階」→「繼續前往 localhost」")
        print("   這在本地開發環境是正常且安全的。\n")
        
        # Run HTTPS server with integrated_server
        uvicorn.run(
            "integrated_server:app",
            host="0.0.0.0",
            port=8443,
            ssl_keyfile=key_file,
            ssl_certfile=cert_file,
            reload=False
        )
    else:
        print("⚠️ 無法建立 HTTPS 伺服器，改用 HTTP...")
        print(f"🌐 HTTP URL: http://localhost:8010")
        uvicorn.run(
            "integrated_server:app",
            host="0.0.0.0",
            port=8010,
            reload=False
        )

if __name__ == "__main__":
    run_https_server()