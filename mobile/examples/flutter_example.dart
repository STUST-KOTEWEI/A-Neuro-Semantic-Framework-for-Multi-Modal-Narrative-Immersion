import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/services.dart';

/// Modern Reader Flutter SDK
/// 現代閱讀器 Flutter 應用程式介面
class ModernReaderSDK {
  static const String _baseUrl = 'https://localhost:8443';
  String? _sessionToken;
  
  /// 登入方法
  Future<Map<String, dynamic>> login(String identifier, String password) async {
    final data = {'password': password};
    
    if (identifier.contains('@')) {
      data['email'] = identifier;
    } else {
      data['username'] = identifier;
    }
    
    final response = await _post('/auth/login', data);
    
    if (response['success'] == true) {
      _sessionToken = response['token'];
    }
    
    return response;
  }
  
  /// AI 文本增強
  Future<Map<String, dynamic>> enhanceText(String text, {String style = 'immersive'}) async {
    return await _post('/ai/enhance_text', {
      'text': text,
      'style': style,
      'use_google': false,
    });
  }
  
  /// 情感分析
  Future<Map<String, dynamic>> analyzeEmotion(String text) async {
    return await _post('/ai/analyze_emotion', {'text': text});
  }
  
  /// 觸覺反饋生成
  Future<Map<String, dynamic>> generateHaptics({
    String? text, 
    String? emotion, 
    double intensity = 0.5
  }) async {
    final data = {'intensity': intensity};
    if (text != null) data['text'] = text;
    if (emotion != null) data['emotion'] = emotion;
    
    return await _post('/generate_haptics', data);
  }
  
  /// 系統健康檢查
  Future<Map<String, dynamic>> healthCheck() async {
    return await _get('/health');
  }
  
  /// 私有方法：GET 請求
  Future<Map<String, dynamic>> _get(String endpoint) async {
    final response = await http.get(
      Uri.parse('$_baseUrl$endpoint'),
      headers: _getHeaders(),
    );
    
    return json.decode(response.body);
  }
  
  /// 私有方法：POST 請求  
  Future<Map<String, dynamic>> _post(String endpoint, Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('$_baseUrl$endpoint'),
      headers: _getHeaders(),
      body: json.encode(data),
    );
    
    return json.decode(response.body);
  }
  
  /// 私有方法：獲取請求標頭
  Map<String, String> _getHeaders() {
    final headers = {'Content-Type': 'application/json'};
    if (_sessionToken != null) {
      headers['Authorization'] = 'Bearer $_sessionToken';
    }
    return headers;
  }
}

/// Modern Reader Flutter 應用程式範例
class ModernReaderApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Modern Reader',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        brightness: Brightness.dark,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: ModernReaderHomePage(),
    );
  }
}

class ModernReaderHomePage extends StatefulWidget {
  @override
  _ModernReaderHomePageState createState() => _ModernReaderHomePageState();
}

class _ModernReaderHomePageState extends State<ModernReaderHomePage> {
  final ModernReaderSDK _sdk = ModernReaderSDK();
  final TextEditingController _textController = TextEditingController();
  
  String _result = '';
  bool _isLoading = false;
  
  /// 觸覺反饋觸發
  void _triggerHaptics() {
    HapticFeedback.lightImpact();
  }
  
  /// AI 文本增強
  Future<void> _enhanceText() async {
    if (_textController.text.isEmpty) return;
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      final result = await _sdk.enhanceText(_textController.text);
      setState(() {
        _result = result['enhanced_text'] ?? '增強結果不可用';
      });
      _triggerHaptics();
    } catch (e) {
      setState(() {
        _result = '錯誤: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  /// 情感分析
  Future<void> _analyzeEmotion() async {
    if (_textController.text.isEmpty) return;
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      final result = await _sdk.analyzeEmotion(_textController.text);
      final emotion = result['emotion_analysis']?['emotion'] ?? '未知';
      final confidence = result['emotion_analysis']?['confidence'] ?? 0.0;
      
      setState(() {
        _result = '情感: $emotion (信心度: ${(confidence * 100).toStringAsFixed(1)}%)';
      });
      _triggerHaptics();
    } catch (e) {
      setState(() {
        _result = '錯誤: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Modern Reader'),
        centerTitle: true,
        elevation: 0,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.blue[900]!, Colors.blue[600]!],
          ),
        ),
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                elevation: 8,
                child: Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      TextField(
                        controller: _textController,
                        decoration: InputDecoration(
                          labelText: '輸入文本',
                          hintText: '請輸入要分析或增強的文本...',
                          border: OutlineInputBorder(),
                        ),
                        maxLines: 3,
                      ),
                      SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _isLoading ? null : _enhanceText,
                              icon: Icon(Icons.auto_fix_high),
                              label: Text('AI 增強'),
                            ),
                          ),
                          SizedBox(width: 8),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _isLoading ? null : _analyzeEmotion,
                              icon: Icon(Icons.sentiment_very_satisfied),
                              label: Text('情感分析'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 16),
              Expanded(
                child: Card(
                  elevation: 8,
                  child: Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '結果',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        Divider(),
                        Expanded(
                          child: _isLoading
                              ? Center(child: CircularProgressIndicator())
                              : SingleChildScrollView(
                                  child: Text(
                                    _result.isEmpty ? '尚無結果' : _result,
                                    style: TextStyle(fontSize: 16),
                                  ),
                                ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          _triggerHaptics();
          _sdk.healthCheck().then((result) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('系統狀態: ${result['status'] ?? '未知'}'),
              ),
            );
          });
        },
        child: Icon(Icons.health_and_safety),
        tooltip: '健康檢查',
      ),
    );
  }
  
  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }
}