import fs from 'fs';
import path from 'path';

function patchIOS() {
  const plistPath = path.join('ios', 'App', 'App', 'Info.plist');
  if (!fs.existsSync(plistPath)) {
    console.warn(`[iOS] Skip: ${plistPath} not found.`);
    return;
  }
  let content = fs.readFileSync(plistPath, 'utf8');
  const needs = [
    'NSCameraUsageDescription',
    'NSMicrophoneUsageDescription',
    'NSPhotoLibraryUsageDescription',
    'NSPhotoLibraryAddUsageDescription',
  ];
  const missing = needs.filter(k => !content.includes(`<key>${k}</key>`));
  if (missing.length === 0) {
    console.log('[iOS] Info.plist already contains required keys.');
    return;
  }
  const inject = `\n  <key>NSCameraUsageDescription</key>\n  <string>需要相機權限以拍攝書籍封面與進行情緒辨識（模擬）。</string>\n  <key>NSMicrophoneUsageDescription</key>\n  <string>需要麥克風以錄音（未啟用；若未來支援 ASR 需要）。</string>\n  <key>NSPhotoLibraryUsageDescription</key>\n  <string>需要存取相簿以上傳封面圖片。</string>\n  <key>NSPhotoLibraryAddUsageDescription</key>\n  <string>需要儲存分析結果或圖片至相簿。</string>\n`;
  if (content.includes('</dict>')) {
    content = content.replace('</dict>', `${inject}</dict>`);
    fs.writeFileSync(plistPath, content, 'utf8');
    console.log('[iOS] Injected usage descriptions into Info.plist');
  } else {
    console.warn('[iOS] Unexpected Info.plist structure, please update manually.');
  }
}

function patchAndroid() {
  const manifestPath = path.join('android', 'app', 'src', 'main', 'AndroidManifest.xml');
  if (!fs.existsSync(manifestPath)) {
    console.warn(`[Android] Skip: ${manifestPath} not found.`);
    return;
  }
  let content = fs.readFileSync(manifestPath, 'utf8');
  const snippets = [
    '<uses-permission android:name="android.permission.CAMERA" />',
    '<uses-permission android:name="android.permission.RECORD_AUDIO" />',
    '<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />',
    '<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />',
    '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />',
  ];
  const missing = snippets.filter(s => !content.includes(s));
  if (missing.length === 0) {
    console.log('[Android] Manifest already contains required permissions.');
    return;
  }
  // Insert before <application
  const idx = content.indexOf('<application');
  if (idx === -1) {
    console.warn('[Android] Unexpected AndroidManifest.xml structure, please update manually.');
    return;
  }
  const before = content.slice(0, idx);
  const after = content.slice(idx);
  const inject = '\n  ' + missing.join('\n  ') + '\n';
  fs.writeFileSync(manifestPath, before + inject + after, 'utf8');
  console.log('[Android] Injected permissions into AndroidManifest.xml');
}

patchIOS();
patchAndroid();
console.log('Permission patching completed.');
