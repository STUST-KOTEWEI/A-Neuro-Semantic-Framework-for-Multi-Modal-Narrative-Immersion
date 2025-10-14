# AI Reader Mobile (Capacitor)

將 `reader.html` 原型包裝成 iOS/Android App。此目錄包含 Capacitor 專案設定與 web 資產（`web/index.html`）。

## 需求

- Node.js 18+
- Xcode 15+（iOS）
- Android Studio（Android）

## 安裝與初始化

1. 安裝依賴
2. 產生 iOS/Android 專案
3. 打開原生專案以執行

### 步驟

```sh
# 進入行動專案目錄
cd mobile

# 安裝依賴
npm install

# 同步 Web 資產到原生平台
npx cap sync

# 新增平台（僅首次）
npx cap add ios
npx cap add android

# 開啟原生專案
npx cap open ios
npx cap open android
```

首次啟動 App 後，點右上角「⚙️」設定你的 Google Gemini API Key，App 會儲存在本機 `localStorage`。

## 權限

- 相機：拍攝書籍封面/臉部辨識（模擬）。
- 麥克風：目前未啟用錄音，但若未來需要 ASR 可加入。

## 說明

- Web 入口：`web/index.html`
- Capacitor 設定：`capacitor.config.ts`

如需修改語音合成模型或語音名稱，請搜尋 `voiceName: "Kore"` 調整。

## 發行

- iOS：於 Xcode 設定 Bundle ID、簽署，打包上架 App Store Connect。
- Android：於 Android Studio 產出簽署 APK/AAB，上架 Google Play Console。

```sh
# 更新 web 後，請記得同步
npx cap copy
npx cap sync
```
