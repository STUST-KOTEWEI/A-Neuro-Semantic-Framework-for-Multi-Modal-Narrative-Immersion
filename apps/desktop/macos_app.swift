// Modern Reader - macOS Desktop App
// 使用 SwiftUI 開發的 macOS 桌面應用程式

import SwiftUI
import Foundation
import Combine

// MARK: - Modern Reader macOS SDK
class ModernReaderMacSDK: ObservableObject {
    private let baseURL = "https://localhost:8443"
    private var sessionToken: String?
    
    @Published var isAuthenticated = false
    @Published var isLoading = false
    @Published var connectionStatus = "未連接"
    
    // 健康檢查
    func healthCheck() async {
        do {
            let response = try await makeRequest(endpoint: "/health", data: [:], method: "GET")
            await MainActor.run {
                connectionStatus = response["status"] as? String ?? "未知"
            }
        } catch {
            await MainActor.run {
                connectionStatus = "連接失敗"
            }
        }
    }
    
    // 登入方法
    func login(identifier: String, password: String) async throws -> Bool {
        isLoading = true
        defer { isLoading = false }
        
        let loginData: [String: Any] = identifier.contains("@") 
            ? ["email": identifier, "password": password]
            : ["username": identifier, "password": password]
        
        let response = try await makeRequest(endpoint: "/auth/login", data: loginData)
        
        if let success = response["success"] as? Bool, success,
           let token = response["token"] as? String {
            sessionToken = token
            isAuthenticated = true
            return true
        }
        
        return false
    }
    
    // AI 文本增強
    func enhanceText(_ text: String, style: String = "immersive") async throws -> String {
        let requestData = [
            "text": text,
            "style": style,
            "use_google": false
        ] as [String : Any]
        
        let response = try await makeRequest(endpoint: "/ai/enhance_text", data: requestData)
        return response["enhanced_text"] as? String ?? "增強失敗"
    }
    
    // 情感分析
    func analyzeEmotion(_ text: String) async throws -> (emotion: String, confidence: Double) {
        let requestData = ["text": text]
        let response = try await makeRequest(endpoint: "/ai/analyze_emotion", data: requestData)
        
        if let analysis = response["emotion_analysis"] as? [String: Any],
           let emotion = analysis["emotion"] as? String,
           let confidence = analysis["confidence"] as? Double {
            return (emotion, confidence)
        }
        
        return ("未知", 0.0)
    }
    
    // 私有方法：發送請求
    private func makeRequest(endpoint: String, data: [String: Any], method: String = "POST") async throws -> [String: Any] {
        var request = URLRequest(url: URL(string: "\(baseURL)\(endpoint)")!)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token = sessionToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if method == "POST" && !data.isEmpty {
            request.httpBody = try JSONSerialization.data(withJSONObject: data)
        }
        
        let (responseData, _) = try await URLSession.shared.data(for: request)
        return try JSONSerialization.jsonObject(with: responseData) as? [String: Any] ?? [:]
    }
}

// MARK: - macOS App
@main
struct ModernReaderMacApp: App {
    var body: some Scene {
        WindowGroup {
            MacContentView()
                .frame(minWidth: 800, minHeight: 600)
        }
        .windowStyle(DefaultWindowStyle())
        .windowToolbarStyle(UnifiedWindowToolbarStyle())
    }
}

struct MacContentView: View {
    @StateObject private var sdk = ModernReaderMacSDK()
    @State private var inputText = ""
    @State private var result = ""
    @State private var selectedStyle = "immersive"
    @State private var showingSettings = false
    @State private var sidebarVisibility: NavigationSplitViewVisibility = .automatic
    
    let styles = ["immersive", "dramatic", "poetic", "technical", "casual"]
    
    var body: some View {
        NavigationSplitView(visibility: $sidebarVisibility) {
            // 側邊欄
            VStack(alignment: .leading, spacing: 16) {
                Text("Modern Reader")
                    .font(.title2)
                    .fontWeight(.bold)
                    .padding(.bottom, 8)
                
                Text("現代閱讀器")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .padding(.bottom, 16)
                
                Divider()
                
                // 連接狀態
                HStack {
                    Circle()
                        .fill(sdk.connectionStatus == "ok" ? Color.green : Color.red)
                        .frame(width: 8, height: 8)
                    Text("狀態: \(sdk.connectionStatus)")
                        .font(.caption)
                }
                
                // 功能選項
                VStack(alignment: .leading, spacing: 8) {
                    Text("功能")
                        .font(.headline)
                        .padding(.top)
                    
                    Label("AI 文本增強", systemImage: "wand.and.rays")
                    Label("情感分析", systemImage: "heart")
                    Label("多模態體驗", systemImage: "eye")
                    Label("觸覺反饋", systemImage: "hand.point.up")
                }
                
                Spacer()
                
                // 設置按鈕
                Button("設置") {
                    showingSettings = true
                }
                .buttonStyle(.borderless)
            }
            .padding()
            .frame(minWidth: 200)
        } detail: {
            // 主要內容區域
            VStack(spacing: 20) {
                // 工具欄
                HStack {
                    Picker("增強風格", selection: $selectedStyle) {
                        ForEach(styles, id: \.self) { style in
                            Text(style.capitalized).tag(style)
                        }
                    }
                    .pickerStyle(.segmented)
                    .frame(maxWidth: 400)
                    
                    Spacer()
                    
                    Button("健康檢查") {
                        Task {
                            await sdk.healthCheck()
                        }
                    }
                }
                .padding()
                
                // 輸入和輸出區域
                HSplitView {
                    // 左側：輸入區域
                    VStack(alignment: .leading, spacing: 12) {
                        Text("輸入文本")
                            .font(.headline)
                        
                        TextEditor(text: $inputText)
                            .font(.system(.body, design: .default))
                            .background(Color(NSColor.textBackgroundColor))
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                            )
                        
                        // 按鈕行
                        HStack {
                            Button("🚀 AI 增強") {
                                Task {
                                    await enhanceText()
                                }
                            }
                            .buttonStyle(.borderedProminent)
                            .disabled(sdk.isLoading)
                            
                            Button("😊 情感分析") {
                                Task {
                                    await analyzeEmotion()
                                }
                            }
                            .buttonStyle(.bordered)
                            .disabled(sdk.isLoading)
                            
                            Spacer()
                            
                            if sdk.isLoading {
                                ProgressView()
                                    .scaleEffect(0.8)
                            }
                        }
                    }
                    .padding()
                    
                    // 右側：結果區域
                    VStack(alignment: .leading, spacing: 12) {
                        Text("結果")
                            .font(.headline)
                        
                        ScrollView {
                            Text(result.isEmpty ? "尚無結果\n\n在左側輸入文本，然後點擊按鈕來體驗 Modern Reader 的 AI 功能。" : result)
                                .font(.system(.body, design: .default))
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding()
                                .background(Color(NSColor.textBackgroundColor))
                                .cornerRadius(8)
                        }
                        .overlay(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                        )
                    }
                    .padding()
                }
                
                Spacer()
            }
        }
        .navigationSplitViewStyle(.balanced)
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
        .task {
            await sdk.healthCheck()
        }
    }
    
    // MARK: - 動作方法
    private func enhanceText() async {
        guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        do {
            let enhanced = try await sdk.enhanceText(inputText, style: selectedStyle)
            await MainActor.run {
                result = enhanced
            }
        } catch {
            await MainActor.run {
                result = "增強文本時發生錯誤: \(error.localizedDescription)"
            }
        }
    }
    
    private func analyzeEmotion() async {
        guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        do {
            let (emotion, confidence) = try await sdk.analyzeEmotion(inputText)
            await MainActor.run {
                result = """
                情感分析結果：
                
                檢測到的情感: \(emotion)
                信心度: \(String(format: "%.1f", confidence * 100))%
                
                建議：
                • 根據情感調整閱讀環境
                • 選擇適合的背景音樂
                • 調整觸覺反饋強度
                """
            }
        } catch {
            await MainActor.run {
                result = "情感分析時發生錯誤: \(error.localizedDescription)"
            }
        }
    }
}

// MARK: - 設置視圖
struct SettingsView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Modern Reader 設置")
                .font(.title2)
                .fontWeight(.bold)
            
            Form {
                Section("連接設置") {
                    TextField("服務器地址", text: .constant("https://localhost:8443"))
                    TextField("API 密鑰", text: .constant(""))
                }
                
                Section("功能設置") {
                    Toggle("啟用觸覺反饋", isOn: .constant(true))
                    Toggle("自動情感檢測", isOn: .constant(true))
                    Toggle("實時文本分析", isOn: .constant(false))
                }
                
                Section("介面設置") {
                    Picker("主題", selection: .constant("auto")) {
                        Text("自動").tag("auto")
                        Text("淺色").tag("light")
                        Text("深色").tag("dark")
                    }
                    
                    Slider(value: .constant(1.0), in: 0.8...1.2) {
                        Text("字體大小")
                    }
                }
            }
            
            HStack {
                Spacer()
                Button("取消") {
                    dismiss()
                }
                .buttonStyle(.borderless)
                
                Button("保存") {
                    dismiss()
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .frame(width: 500, height: 400)
    }
}