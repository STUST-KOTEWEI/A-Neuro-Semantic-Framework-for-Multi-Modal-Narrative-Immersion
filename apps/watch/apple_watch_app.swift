// Modern Reader - Apple Watch App
// 使用 WatchOS + SwiftUI 開發的智慧手錶應用

import SwiftUI
import WatchKit
import Foundation

// MARK: - Modern Reader Watch SDK (Lite)
class ModernReaderWatchSDK: ObservableObject {
    private let baseURL = "https://localhost:8443"
    private var sessionToken: String?
    
    @Published var isConnected = false
    @Published var isLoading = false
    
    // 簡化的文本分析（適用於手錶）
    func quickAnalyze(_ text: String) async throws -> (emotion: String, intensity: Double) {
        // 手錶版本使用本地簡化分析，減少網路依賴
        let words = text.lowercased().components(separatedBy: .whitespacesAndNewlines)
        
        // 簡單情感詞典
        let positiveWords = ["好", "棒", "愛", "喜歡", "開心", "快樂", "amazing", "great", "love", "happy"]
        let negativeWords = ["糟", "壞", "討厭", "難過", "生氣", "terrible", "bad", "hate", "sad", "angry"]
        
        var positiveCount = 0
        var negativeCount = 0
        
        for word in words {
            if positiveWords.contains(word) {
                positiveCount += 1
            } else if negativeWords.contains(word) {
                negativeCount += 1
            }
        }
        
        let emotion: String
        let intensity: Double
        
        if positiveCount > negativeCount {
            emotion = "正面"
            intensity = Double(positiveCount) / Double(words.count)
        } else if negativeCount > positiveCount {
            emotion = "負面"
            intensity = Double(negativeCount) / Double(words.count)
        } else {
            emotion = "中性"
            intensity = 0.5
        }
        
        return (emotion, min(intensity * 2, 1.0))
    }
    
    // 觸覺反饋
    func triggerHaptics(intensity: Double) {
        let hapticType: WKHapticType
        
        switch intensity {
        case 0.0..<0.3:
            hapticType = .notification
        case 0.3..<0.7:
            hapticType = .directionUp
        default:
            hapticType = .directionDown
        }
        
        WKInterfaceDevice.current().play(hapticType)
    }
    
    // 檢查連接狀態
    func checkConnection() async {
        // 簡化的連接檢查
        await MainActor.run {
            isConnected = true // 手錶版本預設為已連接
        }
    }
}

// MARK: - Watch App
@main
struct ModernReaderWatchApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

// MARK: - 主視圖
struct ContentView: View {
    @StateObject private var sdk = ModernReaderWatchSDK()
    @State private var currentTab = 0
    
    var body: some View {
        TabView(selection: $currentTab) {
            // 快速分析頁面
            QuickAnalyzeView(sdk: sdk)
                .tag(0)
            
            // 觸覺反饋頁面
            HapticsView(sdk: sdk)
                .tag(1)
            
            // 設置頁面
            SettingsView(sdk: sdk)
                .tag(2)
        }
        .tabViewStyle(PageTabViewStyle())
        .onAppear {
            Task {
                await sdk.checkConnection()
            }
        }
    }
}

// MARK: - 快速分析視圖
struct QuickAnalyzeView: View {
    @ObservedObject var sdk: ModernReaderWatchSDK
    @State private var inputText = ""
    @State private var result = ""
    @State private var emotion = ""
    @State private var showingInput = false
    
    var body: some View {
        VStack(spacing: 8) {
            // 標題
            Text("Quick Analyze")
                .font(.headline)
                .fontWeight(.bold)
            
            Text("快速分析")
                .font(.caption)
                .foregroundColor(.secondary)
            
            Spacer()
            
            // 結果顯示
            if !emotion.isEmpty {
                VStack(spacing: 4) {
                    Text(emotionEmoji)
                        .font(.largeTitle)
                    
                    Text(emotion)
                        .font(.title3)
                        .fontWeight(.semibold)
                    
                    Text(result)
                        .font(.caption)
                        .multilineTextAlignment(.center)
                }
            } else {
                Text("點擊下方開始分析")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            
            Spacer()
            
            // 輸入按鈕
            Button("📝 輸入文本") {
                showingInput = true
            }
            .buttonStyle(.bordered)
            .controlSize(.small)
        }
        .padding()
        .sheet(isPresented: $showingInput) {
            TextInputView { text in
                inputText = text
                Task {
                    await analyzeText()
                }
            }
        }
    }
    
    private var emotionEmoji: String {
        switch emotion {
        case "正面": return "😊"
        case "負面": return "😢"
        default: return "😐"
        }
    }
    
    private func analyzeText() async {
        guard !inputText.isEmpty else { return }
        
        do {
            let (detectedEmotion, intensity) = try await sdk.quickAnalyze(inputText)
            
            await MainActor.run {
                emotion = detectedEmotion
                result = String(format: "強度: %.0f%%", intensity * 100)
                
                // 觸發觸覺反饋
                sdk.triggerHaptics(intensity: intensity)
            }
        } catch {
            await MainActor.run {
                result = "分析失敗"
            }
        }
    }
}

// MARK: - 觸覺反饋視圖
struct HapticsView: View {
    @ObservedObject var sdk: ModernReaderWatchSDK
    
    var body: some View {
        VStack(spacing: 12) {
            Text("Haptic Feedback")
                .font(.headline)
                .fontWeight(.bold)
            
            Text("觸覺反饋")
                .font(.caption)
                .foregroundColor(.secondary)
            
            Spacer()
            
            // 觸覺反饋按鈕
            VStack(spacing: 8) {
                HapticButton(
                    title: "輕觸",
                    icon: "hand.point.up.left",
                    intensity: 0.2
                ) {
                    sdk.triggerHaptics(intensity: 0.2)
                }
                
                HapticButton(
                    title: "中等",
                    icon: "hand.point.up",
                    intensity: 0.5
                ) {
                    sdk.triggerHaptics(intensity: 0.5)
                }
                
                HapticButton(
                    title: "強烈",
                    icon: "hand.point.up.braille",
                    intensity: 0.8
                ) {
                    sdk.triggerHaptics(intensity: 0.8)
                }
            }
            
            Spacer()
        }
        .padding()
    }
}

// MARK: - 設置視圖
struct SettingsView: View {
    @ObservedObject var sdk: ModernReaderWatchSDK
    
    var body: some View {
        VStack(spacing: 8) {
            Text("Settings")
                .font(.headline)
                .fontWeight(.bold)
            
            Text("設置")
                .font(.caption)
                .foregroundColor(.secondary)
            
            Spacer()
            
            // 連接狀態
            HStack {
                Circle()
                    .fill(sdk.isConnected ? Color.green : Color.red)
                    .frame(width: 8, height: 8)
                
                Text(sdk.isConnected ? "已連接" : "未連接")
                    .font(.caption)
            }
            
            // 功能列表
            VStack(alignment: .leading, spacing: 4) {
                SettingRow(icon: "brain", title: "本地分析")
                SettingRow(icon: "waveform", title: "觸覺反饋")
                SettingRow(icon: "heart", title: "情感檢測")
                SettingRow(icon: "battery.25", title: "節能模式")
            }
            
            Spacer()
            
            // 版本資訊
            Text("Modern Reader v1.0")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

// MARK: - 輔助視圖組件
struct TextInputView: View {
    let onSubmit: (String) -> Void
    @State private var text = ""
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(spacing: 12) {
            Text("輸入文本")
                .font(.headline)
            
            TextField("輸入要分析的文本...", text: $text)
                .textFieldStyle(.roundedBorder)
            
            HStack {
                Button("取消") {
                    dismiss()
                }
                .buttonStyle(.bordered)
                
                Button("分析") {
                    onSubmit(text)
                    dismiss()
                }
                .buttonStyle(.borderedProminent)
                .disabled(text.isEmpty)
            }
        }
        .padding()
    }
}

struct HapticButton: View {
    let title: String
    let icon: String
    let intensity: Double
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
                Spacer()
                Text("\(Int(intensity * 100))%")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .buttonStyle(.bordered)
        .controlSize(.small)
    }
}

struct SettingRow: View {
    let icon: String
    let title: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .frame(width: 20)
                .foregroundColor(.blue)
            
            Text(title)
                .font(.caption)
            
            Spacer()
            
            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.green)
                .font(.caption)
        }
    }
}