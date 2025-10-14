from fastapi import FastAPI, UploadFile, File
import shutil # Python內建的函式庫，用於檔案操作

app = FastAPI()

@app.get("/")
def read_root():
    return {"Project": "AI Multisensory Intelligent Reader Backend is running!"}

# 建立一個新的 API 端點，專門用來處理圖片上傳
@app.post("/recognize-book")
async def recognize_book(image: UploadFile = File(...)):
    # 這裡定義了一個 "POST" 方法的端點
    # UploadFile 代表我們預期會收到一個上傳的檔案

    # 為了簡單起見，我們先將上傳的檔案儲存到本地
    # 檔案將被存為 "uploaded_image.jpg"
    with open("uploaded_image.jpg", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # 回傳一個成功的訊息，並附上收到的檔案名稱
    return {
        "status": "Image received successfully!",
        "filename": image.filename,
        "content_type": image.content_type
    }

