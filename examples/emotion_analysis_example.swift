//
//  emotion_analysis_example.swift
//  AI-Reader
//
//  Example demonstrating how to use EmotionAnalysisService
//

import Foundation

// MARK: - Example Usage in ViewController

/*
import UIKit

class EmotionAnalysisViewController: UIViewController {
    
    // MARK: - Properties
    
    private let emotionService = EmotionAnalysisService()
    
    @IBOutlet weak var inputTextView: UITextView!
    @IBOutlet weak var emotionLabel: UILabel!
    @IBOutlet weak var confidenceStackView: UIStackView!
    @IBOutlet weak var analyzeButton: UIButton!
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    // MARK: - UI Setup
    
    private func setupUI() {
        inputTextView.layer.borderWidth = 1
        inputTextView.layer.borderColor = UIColor.systemGray4.cgColor
        inputTextView.layer.cornerRadius = 8
        inputTextView.font = .systemFont(ofSize: 16)
        
        analyzeButton.layer.cornerRadius = 8
        analyzeButton.backgroundColor = .systemBlue
        analyzeButton.setTitleColor(.white, for: .normal)
    }
    
    // MARK: - Actions
    
    @IBAction func analyzeButtonTapped(_ sender: UIButton) {
        analyzeText()
    }
    
    // MARK: - Analysis
    
    private func analyzeText() {
        guard let text = inputTextView.text, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            showAlert(title: "錯誤", message: "請輸入要分析的文字")
            return
        }
        
        // Show loading indicator
        analyzeButton.isEnabled = false
        analyzeButton.setTitle("分析中...", for: .normal)
        
        // Perform analysis on background thread
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            
            // Get basic emotion
            let emotion = self.emotionService.analyze(text: text)
            
            // Get detailed confidence scores
            let confidences = self.emotionService.analyzeWithConfidence(text: text)
            
            // Update UI on main thread
            DispatchQueue.main.async {
                self.updateResults(emotion: emotion, confidences: confidences)
                self.analyzeButton.isEnabled = true
                self.analyzeButton.setTitle("分析情緒", for: .normal)
            }
        }
    }
    
    private func updateResults(emotion: String, confidences: [String: Double]) {
        // Update emotion label
        let emotionEmoji = getEmotionEmoji(for: emotion)
        emotionLabel.text = "檢測到的情緒: \(emotionEmoji) \(emotion.capitalized)"
        
        // Clear previous confidence views
        confidenceStackView.arrangedSubviews.forEach { $0.removeFromSuperview() }
        
        // Sort confidences by value (descending)
        let sortedConfidences = confidences.sorted { $0.value > $1.value }
        
        // Display confidence scores
        for (emotionType, confidence) in sortedConfidences {
            let view = createConfidenceView(emotion: emotionType, confidence: confidence)
            confidenceStackView.addArrangedSubview(view)
        }
    }
    
    private func createConfidenceView(emotion: String, confidence: Double) -> UIView {
        let containerView = UIView()
        containerView.translatesAutoresizingMaskIntoConstraints = false
        
        // Emotion label
        let label = UILabel()
        label.text = "\(getEmotionEmoji(for: emotion)) \(emotion.capitalized)"
        label.font = .systemFont(ofSize: 14, weight: .medium)
        label.translatesAutoresizingMaskIntoConstraints = false
        
        // Confidence value
        let valueLabel = UILabel()
        valueLabel.text = String(format: "%.1f%%", confidence * 100)
        valueLabel.font = .systemFont(ofSize: 14)
        valueLabel.textAlignment = .right
        valueLabel.translatesAutoresizingMaskIntoConstraints = false
        
        // Progress bar
        let progressView = UIProgressView(progressViewStyle: .default)
        progressView.progress = Float(confidence)
        progressView.progressTintColor = getEmotionColor(for: emotion)
        progressView.translatesAutoresizingMaskIntoConstraints = false
        
        containerView.addSubview(label)
        containerView.addSubview(valueLabel)
        containerView.addSubview(progressView)
        
        NSLayoutConstraint.activate([
            label.topAnchor.constraint(equalTo: containerView.topAnchor),
            label.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            
            valueLabel.centerYAnchor.constraint(equalTo: label.centerYAnchor),
            valueLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            
            progressView.topAnchor.constraint(equalTo: label.bottomAnchor, constant: 4),
            progressView.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            progressView.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            progressView.bottomAnchor.constraint(equalTo: containerView.bottomAnchor, constant: -8)
        ])
        
        return containerView
    }
    
    // MARK: - Helper Methods
    
    private func getEmotionEmoji(for emotion: String) -> String {
        switch emotion.lowercased() {
        case "joy": return "😊"
        case "sadness": return "😢"
        case "anger": return "😠"
        case "fear": return "😨"
        case "neutral": return "😐"
        default: return "❓"
        }
    }
    
    private func getEmotionColor(for emotion: String) -> UIColor {
        switch emotion.lowercased() {
        case "joy": return .systemYellow
        case "sadness": return .systemBlue
        case "anger": return .systemRed
        case "fear": return .systemPurple
        case "neutral": return .systemGray
        default: return .systemGray
        }
    }
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "確定", style: .default))
        present(alert, animated: true)
    }
}
*/

// MARK: - Example Usage in SwiftUI

/*
import SwiftUI

struct EmotionAnalysisView: View {
    
    @StateObject private var viewModel = EmotionAnalysisViewModel()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Input text area
                TextEditor(text: $viewModel.inputText)
                    .frame(height: 200)
                    .padding(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.gray.opacity(0.5), lineWidth: 1)
                    )
                    .padding(.horizontal)
                
                // Analyze button
                Button(action: {
                    viewModel.analyzeEmotion()
                }) {
                    Text(viewModel.isAnalyzing ? "分析中..." : "分析情緒")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(viewModel.isAnalyzing ? Color.gray : Color.blue)
                        .cornerRadius(10)
                }
                .disabled(viewModel.isAnalyzing || viewModel.inputText.isEmpty)
                .padding(.horizontal)
                
                // Results section
                if let emotion = viewModel.detectedEmotion {
                    VStack(spacing: 16) {
                        // Main emotion
                        HStack {
                            Text("檢測到的情緒:")
                                .font(.headline)
                            Spacer()
                            Text("\(getEmotionEmoji(for: emotion)) \(emotion.capitalized)")
                                .font(.title2)
                                .fontWeight(.bold)
                        }
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(10)
                        
                        // Confidence scores
                        VStack(spacing: 12) {
                            Text("置信度分數")
                                .font(.headline)
                                .frame(maxWidth: .infinity, alignment: .leading)
                            
                            ForEach(viewModel.sortedConfidences, id: \.key) { emotion, confidence in
                                ConfidenceRowView(emotion: emotion, confidence: confidence)
                            }
                        }
                        .padding()
                        .background(Color.gray.opacity(0.05))
                        .cornerRadius(10)
                    }
                    .padding(.horizontal)
                }
                
                Spacer()
            }
            .navigationTitle("情緒分析")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private func getEmotionEmoji(for emotion: String) -> String {
        switch emotion.lowercased() {
        case "joy": return "😊"
        case "sadness": return "😢"
        case "anger": return "😠"
        case "fear": return "😨"
        case "neutral": return "😐"
        default: return "❓"
        }
    }
}

struct ConfidenceRowView: View {
    let emotion: String
    let confidence: Double
    
    var body: some View {
        VStack(spacing: 4) {
            HStack {
                Text("\(getEmotionEmoji(for: emotion)) \(emotion.capitalized)")
                    .font(.subheadline)
                Spacer()
                Text(String(format: "%.1f%%", confidence * 100))
                    .font(.subheadline)
                    .fontWeight(.medium)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 8)
                        .cornerRadius(4)
                    
                    Rectangle()
                        .fill(getEmotionColor(for: emotion))
                        .frame(width: geometry.size.width * CGFloat(confidence), height: 8)
                        .cornerRadius(4)
                }
            }
            .frame(height: 8)
        }
    }
    
    private func getEmotionEmoji(for emotion: String) -> String {
        switch emotion.lowercased() {
        case "joy": return "😊"
        case "sadness": return "😢"
        case "anger": return "😠"
        case "fear": return "😨"
        case "neutral": return "😐"
        default: return "❓"
        }
    }
    
    private func getEmotionColor(for emotion: String) -> Color {
        switch emotion.lowercased() {
        case "joy": return .yellow
        case "sadness": return .blue
        case "anger": return .red
        case "fear": return .purple
        case "neutral": return .gray
        default: return .gray
        }
    }
}

class EmotionAnalysisViewModel: ObservableObject {
    @Published var inputText = ""
    @Published var detectedEmotion: String?
    @Published var confidences: [String: Double] = [:]
    @Published var isAnalyzing = false
    
    private let emotionService = EmotionAnalysisService()
    
    var sortedConfidences: [(key: String, value: Double)] {
        confidences.sorted { $0.value > $1.value }
    }
    
    func analyzeEmotion() {
        guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return
        }
        
        isAnalyzing = true
        
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            
            let emotion = self.emotionService.analyze(text: self.inputText)
            let confidences = self.emotionService.analyzeWithConfidence(text: self.inputText)
            
            DispatchQueue.main.async {
                self.detectedEmotion = emotion
                self.confidences = confidences
                self.isAnalyzing = false
            }
        }
    }
}
*/

// MARK: - Simple Console Example

/*
// For testing in a command-line tool or playground

let emotionService = EmotionAnalysisService()

// Test cases
let testTexts = [
    "I am so happy today! This is the best day ever!",
    "I feel terrible and sad. Everything is going wrong.",
    "This makes me so angry! I can't believe this happened!",
    "I'm scared and worried about what might happen.",
    "The weather is normal. Nothing special today."
]

for text in testTexts {
    print("\n📝 Text: \"\(text)\"")
    
    // Basic analysis
    let emotion = emotionService.analyze(text: text)
    print("🎯 Detected emotion: \(emotion)")
    
    // Detailed analysis
    let confidences = emotionService.analyzeWithConfidence(text: text)
    print("📊 Confidence scores:")
    for (emotion, confidence) in confidences.sorted(by: { $0.value > $1.value }) {
        print("   \(emotion): \(String(format: "%.2f%%", confidence * 100))")
    }
}
*/
