//
//  EmotionAnalysisService.swift
//  App
//
//  Created by AI-Reader Team
//  Service for performing emotion analysis on text using CoreML
//

import Foundation
import CoreML

/// Service for analyzing emotions in text using a CoreML model
class EmotionAnalysisService {
    
    // MARK: - Properties
    
    /// The CoreML model for emotion analysis
    private var model: MLModel?
    
    /// Emotion labels corresponding to model output indices
    private let emotionLabels = ["joy", "sadness", "anger", "fear", "neutral"]
    
    /// Maximum sequence length for text input
    private let maxSequenceLength = 128
    
    /// Vocabulary for tokenization (simplified - should match training)
    private var vocabulary: [String: Int] = [:]
    
    // MARK: - Initialization
    
    init() {
        loadModel()
        setupVocabulary()
    }
    
    // MARK: - Model Loading
    
    /// Load the EmotionLSTM CoreML model
    private func loadModel() {
        do {
            // Attempt to load the model from the bundle
            guard let modelURL = Bundle.main.url(forResource: "EmotionLSTM", withExtension: "mlpackagec") ??
                                  Bundle.main.url(forResource: "EmotionLSTM", withExtension: "mlmodelc") else {
                print("⚠️ EmotionLSTM model not found in bundle")
                return
            }
            
            let config = MLModelConfiguration()
            config.computeUnits = .all // Use Neural Engine when available
            
            model = try MLModel(contentsOf: modelURL, configuration: config)
            print("✅ EmotionLSTM model loaded successfully")
        } catch {
            print("❌ Failed to load EmotionLSTM model: \(error.localizedDescription)")
        }
    }
    
    /// Setup a basic vocabulary for tokenization
    /// In a production app, this should match the vocabulary used during training
    private func setupVocabulary() {
        // This is a simplified vocabulary. In production, load from a file that matches training
        let commonWords = [
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "should",
            "could", "may", "might", "can", "i", "you", "he", "she", "it", "we",
            "they", "my", "your", "his", "her", "its", "our", "their", "this",
            "that", "these", "those", "good", "bad", "happy", "sad", "angry",
            "love", "hate", "like", "feel", "think", "know", "want", "need",
            "great", "terrible", "amazing", "awful", "wonderful", "horrible"
        ]
        
        for (index, word) in commonWords.enumerated() {
            vocabulary[word] = index + 1 // Reserve 0 for padding
        }
    }
    
    // MARK: - Text Preprocessing
    
    /// Preprocess text input into MLMultiArray format expected by the model
    /// - Parameter text: Input text to analyze
    /// - Returns: MLMultiArray containing tokenized and padded text, or nil if preprocessing fails
    private func preprocess(text: String) -> MLMultiArray? {
        // Tokenize the text
        let tokens = tokenize(text: text)
        
        // Convert tokens to IDs
        let tokenIds = tokens.map { vocabulary[$0.lowercased()] ?? 0 }
        
        // Pad or truncate to maxSequenceLength
        var paddedIds = tokenIds
        if paddedIds.count > maxSequenceLength {
            paddedIds = Array(paddedIds.prefix(maxSequenceLength))
        } else {
            paddedIds += Array(repeating: 0, count: maxSequenceLength - paddedIds.count)
        }
        
        // Create MLMultiArray
        do {
            let shape = [1, maxSequenceLength] as [NSNumber]
            let mlArray = try MLMultiArray(shape: shape, dataType: .int32)
            
            for (index, id) in paddedIds.enumerated() {
                mlArray[index] = NSNumber(value: id)
            }
            
            return mlArray
        } catch {
            print("❌ Failed to create MLMultiArray: \(error.localizedDescription)")
            return nil
        }
    }
    
    /// Simple tokenizer that splits text into words
    /// - Parameter text: Input text
    /// - Returns: Array of tokens
    private func tokenize(text: String) -> [String] {
        // Remove punctuation and split by whitespace
        let cleanedText = text.components(separatedBy: CharacterSet.alphanumerics.inverted)
            .joined(separator: " ")
        
        return cleanedText.split(separator: " ").map { String($0) }
    }
    
    // MARK: - Prediction
    
    /// Perform emotion prediction on the model output
    /// - Parameter mlArray: Model input array
    /// - Returns: MLFeatureProvider containing model predictions, or nil if prediction fails
    private func predict(input mlArray: MLMultiArray) -> MLFeatureProvider? {
        guard let model = model else {
            print("❌ Model not loaded")
            return nil
        }
        
        do {
            // Create input feature provider
            let inputFeatures = try MLDictionaryFeatureProvider(dictionary: [
                "text_input": MLFeatureValue(multiArray: mlArray)
            ])
            
            // Perform prediction
            let output = try model.prediction(from: inputFeatures)
            return output
        } catch {
            print("❌ Prediction failed: \(error.localizedDescription)")
            return nil
        }
    }
    
    // MARK: - Postprocessing
    
    /// Postprocess model output to extract the emotion with highest probability
    /// - Parameter output: Model output feature provider
    /// - Returns: String representing the detected emotion, or "unknown" if postprocessing fails
    private func postprocess(output: MLFeatureProvider?) -> String {
        guard let output = output else {
            return "unknown"
        }
        
        // Try to get the output array
        guard let emotionOutput = output.featureValue(for: "emotion_output")?.multiArrayValue else {
            print("❌ Failed to get emotion_output from model")
            return "unknown"
        }
        
        // Find the index with maximum probability
        var maxIndex = 0
        var maxValue: Double = 0.0
        
        for i in 0..<emotionOutput.count {
            let value = emotionOutput[i].doubleValue
            if value > maxValue {
                maxValue = value
                maxIndex = i
            }
        }
        
        // Return the corresponding emotion label
        if maxIndex < emotionLabels.count {
            let emotion = emotionLabels[maxIndex]
            print("✅ Detected emotion: \(emotion) (confidence: \(String(format: "%.2f", maxValue)))")
            return emotion
        }
        
        return "unknown"
    }
    
    // MARK: - Public API
    
    /// Analyze the emotion in the given text
    /// - Parameter text: Input text to analyze
    /// - Returns: String representing the detected emotion (e.g., "joy", "sadness", "anger", "fear", "neutral")
    func analyze(text: String) -> String {
        print("🔍 Analyzing emotion for text: \"\(text.prefix(50))...\"")
        
        // Step 1: Preprocess the text
        guard let preprocessedInput = preprocess(text: text) else {
            print("❌ Preprocessing failed")
            return "unknown"
        }
        
        // Step 2: Run prediction
        let output = predict(input: preprocessedInput)
        
        // Step 3: Postprocess the output
        let emotion = postprocess(output: output)
        
        return emotion
    }
    
    /// Analyze emotion with detailed confidence scores for all emotions
    /// - Parameter text: Input text to analyze
    /// - Returns: Dictionary mapping emotion labels to confidence scores
    func analyzeWithConfidence(text: String) -> [String: Double] {
        print("🔍 Analyzing emotion with confidence for text: \"\(text.prefix(50))...\"")
        
        var result: [String: Double] = [:]
        
        // Step 1: Preprocess the text
        guard let preprocessedInput = preprocess(text: text) else {
            print("❌ Preprocessing failed")
            return result
        }
        
        // Step 2: Run prediction
        guard let output = predict(input: preprocessedInput) else {
            return result
        }
        
        // Step 3: Extract all confidence scores
        guard let emotionOutput = output.featureValue(for: "emotion_output")?.multiArrayValue else {
            print("❌ Failed to get emotion_output from model")
            return result
        }
        
        // Map each emotion to its confidence score
        for i in 0..<min(emotionOutput.count, emotionLabels.count) {
            let emotion = emotionLabels[i]
            let confidence = emotionOutput[i].doubleValue
            result[emotion] = confidence
        }
        
        return result
    }
}
