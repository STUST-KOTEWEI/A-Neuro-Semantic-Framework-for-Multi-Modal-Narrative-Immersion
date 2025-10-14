//
//  EmotionAnalysisService.swift
//  AI-Reader
//
//  情緒分析服務
//  負責使用 CoreML 模型進行文字情緒分析
//

import Foundation
import CoreML

/// 情緒分析服務
/// 使用 CoreML 模型對文字進行即時情緒偵測
class EmotionAnalysisService {
    
    // MARK: - Properties
    
    /// CoreML 模型實例
    private var model: MLModel?
    
    /// 情緒標籤對應表
    private let emotionLabels: [String] = ["happy", "sad", "angry", "neutral", "surprise", "fear"]
    
    /// 最大序列長度（需與模型訓練時一致）
    private let maxSequenceLength: Int = 128
    
    /// 詞彙表大小（需與模型訓練時一致）
    private let vocabSize: Int = 10000
    
    // MARK: - Initialization
    
    init() {
        loadModel()
    }
    
    // MARK: - Model Loading
    
    /// 載入 CoreML 模型
    private func loadModel() {
        do {
            // 嘗試載入 EmotionLSTM 模型
            // 注意: 實際使用時需要將 EmotionLSTM.mlpackage 加入到專案中
            guard let modelURL = Bundle.main.url(forResource: "EmotionLSTM", withExtension: "mlmodelc") else {
                print("⚠️ 警告: 無法找到 EmotionLSTM 模型檔案")
                print("請確認已將 EmotionLSTM.mlpackage 加入到 Xcode 專案中")
                return
            }
            
            let config = MLModelConfiguration()
            config.computeUnits = .all // 使用所有可用的運算單元（CPU, GPU, Neural Engine）
            
            model = try MLModel(contentsOf: modelURL, configuration: config)
            print("✓ EmotionLSTM 模型載入成功")
            
        } catch {
            print("❌ 模型載入失敗: \(error.localizedDescription)")
        }
    }
    
    // MARK: - Public API
    
    /// 分析文字的情緒
    /// - Parameter text: 要分析的文字
    /// - Returns: 分析出的情緒字串，如果失敗則返回 nil
    func analyze(text: String) -> String? {
        guard let model = model else {
            print("❌ 模型尚未載入")
            return nil
        }
        
        // 1. 預處理: 將文字轉換為模型輸入格式
        guard let inputArray = preprocess(text: text) else {
            print("❌ 文字預處理失敗")
            return nil
        }
        
        // 2. 進行預測
        guard let prediction = predict(inputArray: inputArray) else {
            print("❌ 模型預測失敗")
            return nil
        }
        
        // 3. 後處理: 將模型輸出轉換為可讀的情緒字串
        let emotion = postprocess(prediction: prediction)
        
        return emotion
    }
    
    // MARK: - Preprocessing
    
    /// 預處理文字，轉換為模型輸入格式
    /// - Parameter text: 原始文字
    /// - Returns: MLMultiArray 格式的輸入，如果失敗則返回 nil
    private func preprocess(text: String) -> MLMultiArray? {
        do {
            // 創建 MLMultiArray 作為模型輸入
            // 形狀: [1, maxSequenceLength] - 批次大小為 1，序列長度為 maxSequenceLength
            let shape = [1, maxSequenceLength] as [NSNumber]
            let inputArray = try MLMultiArray(shape: shape, dataType: .int32)
            
            // 簡單的文字轉換策略
            // 注意: 實際應用中需要使用與訓練時相同的分詞器和詞彙表
            let tokens = tokenize(text: text)
            
            // 將 token 填入 MLMultiArray
            for i in 0..<min(tokens.count, maxSequenceLength) {
                inputArray[i] = NSNumber(value: tokens[i])
            }
            
            // 填充剩餘部分為 0（padding）
            for i in tokens.count..<maxSequenceLength {
                inputArray[i] = 0
            }
            
            return inputArray
            
        } catch {
            print("❌ 預處理錯誤: \(error.localizedDescription)")
            return nil
        }
    }
    
    /// 簡單的分詞函式
    /// - Parameter text: 原始文字
    /// - Returns: token ID 陣列
    private func tokenize(text: String) -> [Int] {
        // 這是一個簡化的分詞實作
        // 實際應用中應該使用與模型訓練時相同的分詞器
        
        // 將文字轉為小寫並按空格分割
        let words = text.lowercased().components(separatedBy: .whitespacesAndNewlines)
        
        // 將每個字詞轉換為 token ID（使用簡單的 hash 方法）
        return words.compactMap { word -> Int? in
            guard !word.isEmpty else { return nil }
            // 使用 hash 值並限制在詞彙表大小內
            let hash = abs(word.hash % vocabSize)
            return hash
        }
    }
    
    // MARK: - Prediction
    
    /// 使用模型進行預測
    /// - Parameter inputArray: 預處理後的輸入
    /// - Returns: 模型的輸出，如果失敗則返回 nil
    private func predict(inputArray: MLMultiArray) -> MLMultiArray? {
        guard let model = model else { return nil }
        
        do {
            // 創建模型輸入
            let input = EmotionLSTMInput(text_input: inputArray)
            
            // 執行預測
            let output = try model.prediction(from: input)
            
            // 取得輸出特徵
            if let outputFeature = output.featureValue(for: "output")?.multiArrayValue {
                return outputFeature
            }
            
            return nil
            
        } catch {
            print("❌ 預測錯誤: \(error.localizedDescription)")
            return nil
        }
    }
    
    // MARK: - Postprocessing
    
    /// 後處理模型輸出，轉換為情緒字串
    /// - Parameter prediction: 模型的原始輸出
    /// - Returns: 情緒字串
    private func postprocess(prediction: MLMultiArray) -> String {
        // 找出機率最高的類別
        var maxIndex = 0
        var maxValue = prediction[0].doubleValue
        
        for i in 1..<prediction.count {
            let value = prediction[i].doubleValue
            if value > maxValue {
                maxValue = value
                maxIndex = i
            }
        }
        
        // 根據索引返回對應的情緒標籤
        if maxIndex < emotionLabels.count {
            let emotion = emotionLabels[maxIndex]
            print("✓ 偵測到情緒: \(emotion) (信心度: \(String(format: "%.2f", maxValue * 100))%)")
            return emotion
        }
        
        return "unknown"
    }
}

// MARK: - MLFeatureProvider Implementation

/// EmotionLSTM 模型輸入
/// 提供符合 MLFeatureProvider 協議的輸入
class EmotionLSTMInput: MLFeatureProvider {
    
    var text_input: MLMultiArray
    
    var featureNames: Set<String> {
        return ["text_input"]
    }
    
    func featureValue(for featureName: String) -> MLFeatureValue? {
        if featureName == "text_input" {
            return MLFeatureValue(multiArray: text_input)
        }
        return nil
    }
    
    init(text_input: MLMultiArray) {
        self.text_input = text_input
    }
}

// MARK: - Usage Example
/*
 
 使用範例:
 
 let emotionService = EmotionAnalysisService()
 
 if let emotion = emotionService.analyze(text: "I am so happy today!") {
     print("偵測到的情緒: \(emotion)")
 }
 
 */
