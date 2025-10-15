import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  Vibration,
  ActivityIndicator,
} from 'react-native';

// Modern Reader React Native SDK
class ModernReaderSDK {
  constructor(baseUrl = 'https://localhost:8443') {
    this.baseUrl = baseUrl;
    this.sessionToken = null;
  }

  // 登入方法
  async login(identifier, password) {
    const data = { password };
    
    if (identifier.includes('@')) {
      data.email = identifier;
    } else {
      data.username = identifier;
    }

    const response = await this._post('/auth/login', data);
    
    if (response.success) {
      this.sessionToken = response.token;
    }
    
    return response;
  }

  // AI 文本增強
  async enhanceText(text, style = 'immersive') {
    return await this._post('/ai/enhance_text', {
      text,
      style,
      use_google: false,
    });
  }

  // 情感分析
  async analyzeEmotion(text) {
    return await this._post('/ai/analyze_emotion', { text });
  }

  // 觸覺反饋生成
  async generateHaptics({ text, emotion, intensity = 0.5 } = {}) {
    const data = { intensity };
    if (text) data.text = text;
    if (emotion) data.emotion = emotion;
    
    return await this._post('/generate_haptics', data);
  }

  // 系統健康檢查
  async healthCheck() {
    return await this._get('/health');
  }

  // 私有方法：GET 請求
  async _get(endpoint) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: this._getHeaders(),
    });
    
    return await response.json();
  }

  // 私有方法：POST 請求
  async _post(endpoint, data) {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this._getHeaders(),
      body: JSON.stringify(data),
    });
    
    return await response.json();
  }

  // 私有方法：獲取請求標頭
  _getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (this.sessionToken) {
      headers['Authorization'] = `Bearer ${this.sessionToken}`;
    }
    return headers;
  }
}

// Modern Reader React Native 應用程式範例
const ModernReaderApp = () => {
  const [sdk] = useState(() => new ModernReaderSDK());
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // 觸覺反饋觸發
  const triggerHaptics = useCallback(() => {
    Vibration.vibrate(100);
  }, []);

  // AI 文本增強
  const enhanceText = useCallback(async () => {
    if (!inputText.trim()) return;

    setIsLoading(true);
    try {
      const response = await sdk.enhanceText(inputText);
      setResult(response.enhanced_text || '增強結果不可用');
      triggerHaptics();
    } catch (error) {
      setResult(`錯誤: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [inputText, sdk, triggerHaptics]);

  // 情感分析
  const analyzeEmotion = useCallback(async () => {
    if (!inputText.trim()) return;

    setIsLoading(true);
    try {
      const response = await sdk.analyzeEmotion(inputText);
      const emotion = response.emotion_analysis?.emotion || '未知';
      const confidence = response.emotion_analysis?.confidence || 0;
      
      setResult(`情感: ${emotion} (信心度: ${(confidence * 100).toFixed(1)}%)`);
      triggerHaptics();
    } catch (error) {
      setResult(`錯誤: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [inputText, sdk, triggerHaptics]);

  // 健康檢查
  const performHealthCheck = useCallback(async () => {
    try {
      const response = await sdk.healthCheck();
      Alert.alert('系統狀態', `狀態: ${response.status || '未知'}`);
      triggerHaptics();
    } catch (error) {
      Alert.alert('錯誤', `健康檢查失敗: ${error.message}`);
    }
  }, [sdk, triggerHaptics]);

  return (
    <View style={styles.container}>
      {/* 標題欄 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Modern Reader</Text>
        <Text style={styles.headerSubtitle}>現代閱讀器</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 輸入區域 */}
        <View style={styles.inputSection}>
          <Text style={styles.sectionTitle}>輸入文本</Text>
          <TextInput
            style={styles.textInput}
            multiline
            numberOfLines={4}
            placeholder="請輸入要分析或增強的文本..."
            placeholderTextColor="#666"
            value={inputText}
            onChangeText={setInputText}
          />
          
          {/* 按鈕區域 */}
          <View style={styles.buttonRow}>
            <TouchableOpacity
              style={[styles.button, styles.primaryButton]}
              onPress={enhanceText}
              disabled={isLoading}
            >
              <Text style={styles.buttonText}>🚀 AI 增強</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[styles.button, styles.secondaryButton]}
              onPress={analyzeEmotion}
              disabled={isLoading}
            >
              <Text style={styles.buttonText}>😊 情感分析</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 結果區域 */}
        <View style={styles.resultSection}>
          <Text style={styles.sectionTitle}>結果</Text>
          <View style={styles.resultContainer}>
            {isLoading ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={styles.loadingText}>處理中...</Text>
              </View>
            ) : (
              <Text style={styles.resultText}>
                {result || '尚無結果'}
              </Text>
            )}
          </View>
        </View>

        {/* 健康檢查按鈕 */}
        <TouchableOpacity
          style={[styles.button, styles.healthButton]}
          onPress={performHealthCheck}
        >
          <Text style={styles.buttonText}>🏥 系統健康檢查</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    backgroundColor: '#1E293B',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#94A3B8',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  inputSection: {
    marginTop: 20,
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#E2E8F0',
    marginBottom: 12,
  },
  textInput: {
    backgroundColor: '#0F172A',
    color: '#E2E8F0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: '#334155',
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: 16,
    gap: 12,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#2563EB',
  },
  secondaryButton: {
    backgroundColor: '#7C3AED',
  },
  healthButton: {
    backgroundColor: '#059669',
    marginTop: 20,
    marginBottom: 30,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  resultSection: {
    marginTop: 20,
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 16,
  },
  resultContainer: {
    backgroundColor: '#0F172A',
    borderRadius: 8,
    padding: 16,
    minHeight: 120,
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 120,
  },
  loadingText: {
    color: '#94A3B8',
    marginTop: 12,
    fontSize: 16,
  },
  resultText: {
    color: '#E2E8F0',
    fontSize: 16,
    lineHeight: 24,
  },
});

export default ModernReaderApp;