# Modern Reader - iOS App
# 使用 SwiftUI 開發的原生 iOS 應用

import SwiftUI
import Foundation
import Combine

// MARK: - Modern Reader SDK for iOS
class ModernReaderSDK: ObservableObject {
    private let baseURL = "https://localhost:8443"
    private var sessionToken: String?
    
    @Published var isAuthenticated = false
    @Published var isLoading = false
    
    // 登入方法
    func login(identifier: String, password: String) async throws -> Bool {
        isLoading = true
        defer { isLoading = false }
        
        var request = URLRequest(url: URL(string: "\(baseURL)/auth/login")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let loginData: [String: Any] = identifier.contains("@") 
            ? ["email": identifier, "password": password]
            : ["username": identifier, "password": password]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: loginData)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        
        if let success = response?["success"] as? Bool, success,
           let token = response?["token"] as? String {
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
    
    // 觸覺反饋
    func generateHaptics(text: String? = nil, emotion: String? = nil, intensity: Double = 0.5) async throws {
        var requestData: [String: Any] = ["intensity": intensity]
        if let text = text { requestData["text"] = text }
        if let emotion = emotion { requestData["emotion"] = emotion }
        
        _ = try await makeRequest(endpoint: "/generate_haptics", data: requestData)
        
        // 觸發本地觸覺反饋
        DispatchQueue.main.async {
            let impactFeedback = UIImpactFeedbackGenerator(style: .medium)
            impactFeedback.impactOccurred()
        }
    }
    
    // 私有方法：發送請求
    private func makeRequest(endpoint: String, data: [String: Any]) async throws -> [String: Any] {
        var request = URLRequest(url: URL(string: "\(baseURL)\(endpoint)")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token = sessionToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        request.httpBody = try JSONSerialization.data(withJSONObject: data)
        
        let (responseData, _) = try await URLSession.shared.data(for: request)
        return try JSONSerialization.jsonObject(with: responseData) as? [String: Any] ?? [:]
    }
}

// MARK: - SwiftUI Views
struct ModernReaderApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @StateObject private var sdk = ModernReaderSDK()
    @State private var inputText = ""
    @State private var result = ""
    @State private var showingAlert = false
    @State private var alertMessage = ""
    
    var body: some View {
        NavigationView {
            ZStack {
                // 背景漸變
                LinearGradient(
                    gradient: Gradient(colors: [Color.blue.opacity(0.8), Color.purple.opacity(0.6)]),
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // 標題
                        VStack {
                            Text("Modern Reader")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                            
                            Text("現代閱讀器")
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.8))
                        }
                        .padding(.top, 20)
                        
                        // 輸入區域
                        VStack(alignment: .leading, spacing: 12) {
                            Text("輸入文本")
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            TextEditor(text: $inputText)
                                .frame(minHeight: 100)
                                .padding(12)
                                .background(Color.white.opacity(0.1))
                                .cornerRadius(12)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(Color.white.opacity(0.3), lineWidth: 1)
                                )
                        }
                        .padding(.horizontal)
                        
                        // 按鈕區域
                        HStack(spacing: 12) {
                            ActionButton(
                                title: "🚀 AI增強",
                                backgroundColor: .blue
                            ) {
                                await enhanceText()
                            }
                            
                            ActionButton(
                                title: "😊 情感分析",
                                backgroundColor: .purple
                            ) {
                                await analyzeEmotion()
                            }
                        }
                        .padding(.horizontal)
                        
                        // 結果區域
                        VStack(alignment: .leading, spacing: 12) {
                            Text("結果")
                                .font(.headline)
                                .foregroundColor(.white)
                            
                            Text(result.isEmpty ? "尚無結果" : result)
                                .padding(16)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.white.opacity(0.1))
                                .cornerRadius(12)
                                .foregroundColor(.white)
                        }
                        .padding(.horizontal)
                        
                        // 觸覺反饋按鈕
                        ActionButton(
                            title: "🖐 觸覺反饋",
                            backgroundColor: .green
                        ) {
                            await triggerHaptics()
                        }
                        .padding(.horizontal)
                        
                        Spacer(minLength: 20)
                    }
                }
            }
            .navigationBarHidden(true)
        }
        .alert("訊息", isPresented: $showingAlert) {
            Button("確定") { }
        } message: {
            Text(alertMessage)
        }
        .overlay(
            Group {
                if sdk.isLoading {
                    LoadingView()
                }
            }
        )
    }
    
    // MARK: - 動作方法
    private func enhanceText() async {
        guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        do {
            let enhanced = try await sdk.enhanceText(inputText)
            await MainActor.run {
                result = enhanced
            }
        } catch {
            await showAlert("增強文本時發生錯誤: \(error.localizedDescription)")
        }
    }
    
    private func analyzeEmotion() async {
        guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        do {
            let (emotion, confidence) = try await sdk.analyzeEmotion(inputText)
            await MainActor.run {
                result = "情感: \(emotion)\n信心度: \(String(format: "%.1f", confidence * 100))%"
            }
        } catch {
            await showAlert("情感分析時發生錯誤: \(error.localizedDescription)")
        }
    }
    
    private func triggerHaptics() async {
        do {
            try await sdk.generateHaptics(text: inputText.isEmpty ? nil : inputText)
            await showAlert("觸覺反饋已觸發！")
        } catch {
            await showAlert("觸覺反饋失敗: \(error.localizedDescription)")
        }
    }
    
    private func showAlert(_ message: String) async {
        await MainActor.run {
            alertMessage = message
            showingAlert = true
        }
    }
}

// MARK: - 自定義組件
struct ActionButton: View {
    let title: String
    let backgroundColor: Color
    let action: () async -> Void
    
    var body: some View {
        Button(action: {
            Task {
                await action()
            }
        }) {
            Text(title)
                .font(.headline)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(backgroundColor)
                .cornerRadius(12)
        }
    }
}

struct LoadingView: View {
    var body: some View {
        ZStack {
            Color.black.opacity(0.3)
                .ignoresSafeArea()
            
            VStack {
                ProgressView()
                    .scaleEffect(1.5)
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                
                Text("處理中...")
                    .foregroundColor(.white)
                    .padding(.top, 8)
            }
            .padding(20)
            .background(Color.black.opacity(0.7))
            .cornerRadius(12)
        }
    }
}