// Modern Reader - Android Kotlin App
// 使用 Jetpack Compose 開發的原生 Android 應用

package com.modernreader.app

import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException

// MARK: - Modern Reader SDK for Android
class ModernReaderSDK {
    private val baseUrl = "https://localhost:8443"
    private var sessionToken: String? = null
    private val client = OkHttpClient()
    
    // 登入方法
    suspend fun login(identifier: String, password: String): Boolean = withContext(Dispatchers.IO) {
        val loginData = if (identifier.contains("@")) {
            JSONObject().apply {
                put("email", identifier)
                put("password", password)
            }
        } else {
            JSONObject().apply {
                put("username", identifier)
                put("password", password)
            }
        }
        
        val requestBody = loginData.toString().toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/auth/login")
            .post(requestBody)
            .build()
        
        try {
            val response = client.newCall(request).execute()
            val responseData = response.body?.string()
            val jsonResponse = JSONObject(responseData ?: "")
            
            if (jsonResponse.optBoolean("success", false)) {
                sessionToken = jsonResponse.optString("token")
                return@withContext true
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        
        return@withContext false
    }
    
    // AI 文本增強
    suspend fun enhanceText(text: String, style: String = "immersive"): String = withContext(Dispatchers.IO) {
        val requestData = JSONObject().apply {
            put("text", text)
            put("style", style)
            put("use_google", false)
        }
        
        val response = makeRequest("/ai/enhance_text", requestData)
        return@withContext response?.optString("enhanced_text") ?: "增強失敗"
    }
    
    // 情感分析
    suspend fun analyzeEmotion(text: String): Pair<String, Double> = withContext(Dispatchers.IO) {
        val requestData = JSONObject().apply {
            put("text", text)
        }
        
        val response = makeRequest("/ai/analyze_emotion", requestData)
        val analysis = response?.optJSONObject("emotion_analysis")
        
        val emotion = analysis?.optString("emotion") ?: "未知"
        val confidence = analysis?.optDouble("confidence") ?: 0.0
        
        return@withContext Pair(emotion, confidence)
    }
    
    // 觸覺反饋生成
    suspend fun generateHaptics(text: String? = null, emotion: String? = null, intensity: Double = 0.5): Boolean = withContext(Dispatchers.IO) {
        val requestData = JSONObject().apply {
            put("intensity", intensity)
            text?.let { put("text", it) }
            emotion?.let { put("emotion", it) }
        }
        
        val response = makeRequest("/generate_haptics", requestData)
        return@withContext response != null
    }
    
    // 私有方法：發送請求
    private suspend fun makeRequest(endpoint: String, data: JSONObject): JSONObject? = withContext(Dispatchers.IO) {
        try {
            val requestBody = data.toString().toRequestBody("application/json".toMediaType())
            val requestBuilder = Request.Builder()
                .url("$baseUrl$endpoint")
                .post(requestBody)
            
            sessionToken?.let { token ->
                requestBuilder.addHeader("Authorization", "Bearer $token")
            }
            
            val request = requestBuilder.build()
            val response = client.newCall(request).execute()
            val responseData = response.body?.string()
            
            return@withContext if (responseData != null) JSONObject(responseData) else null
        } catch (e: Exception) {
            e.printStackTrace()
            return@withContext null
        }
    }
}

// MARK: - ViewModel
class ModernReaderViewModel : ViewModel() {
    private val sdk = ModernReaderSDK()
    
    var inputText by mutableStateOf("")
    var result by mutableStateOf("")
    var isLoading by mutableStateOf(false)
    var isAuthenticated by mutableStateOf(false)
    
    fun enhanceText() {
        if (inputText.isBlank()) return
        
        viewModelScope.launch {
            isLoading = true
            try {
                val enhanced = sdk.enhanceText(inputText)
                result = enhanced
            } catch (e: Exception) {
                result = "錯誤: ${e.message}"
            } finally {
                isLoading = false
            }
        }
    }
    
    fun analyzeEmotion() {
        if (inputText.isBlank()) return
        
        viewModelScope.launch {
            isLoading = true
            try {
                val (emotion, confidence) = sdk.analyzeEmotion(inputText)
                result = "情感: $emotion\n信心度: ${String.format("%.1f", confidence * 100)}%"
            } catch (e: Exception) {
                result = "錯誤: ${e.message}"
            } finally {
                isLoading = false
            }
        }
    }
    
    fun triggerHaptics() {
        viewModelScope.launch {
            isLoading = true
            try {
                val success = sdk.generateHaptics(text = if (inputText.isNotEmpty()) inputText else null)
                result = if (success) "觸覺反饋已觸發！" else "觸覺反饋失敗"
            } catch (e: Exception) {
                result = "錯誤: ${e.message}"
            } finally {
                isLoading = false
            }
        }
    }
}

// MARK: - MainActivity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ModernReaderTheme {
                ModernReaderApp()
            }
        }
    }
}

// MARK: - Composable Functions
@Composable
fun ModernReaderTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Color(0xFF2563EB),
            secondary = Color(0xFF7C3AED),
            background = Color(0xFF0A0E27),
            surface = Color(0xFF1E293B)
        ),
        content = content
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ModernReaderApp() {
    val viewModel = remember { ModernReaderViewModel() }
    val context = LocalContext.current
    val vibrator = context.getSystemService(Vibrator::class.java)
    
    // 觸覺反饋幫助函數
    fun triggerVibration() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            vibrator?.vibrate(VibrationEffect.createOneShot(100, VibrationEffect.DEFAULT_AMPLITUDE))
        } else {
            @Suppress("DEPRECATION")
            vibrator?.vibrate(100)
        }
    }
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Color(0xFF0A0E27),
                        Color(0xFF1E293B)
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // 標題
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.padding(vertical = 32.dp)
            ) {
                Text(
                    text = "Modern Reader",
                    fontSize = 32.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
                Text(
                    text = "現代閱讀器",
                    fontSize = 16.sp,
                    color = Color.White.copy(alpha = 0.7f)
                )
            }
            
            // 輸入區域
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF1E293B))
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "輸入文本",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color.White,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    
                    OutlinedTextField(
                        value = viewModel.inputText,
                        onValueChange = { viewModel.inputText = it },
                        placeholder = { Text("請輸入要分析或增強的文本...") },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(120.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFF2563EB),
                            unfocusedBorderColor = Color(0xFF334155)
                        )
                    )
                }
            }
            
            // 按鈕區域
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ActionButton(
                    text = "🚀 AI增強",
                    backgroundColor = Color(0xFF2563EB),
                    modifier = Modifier.weight(1f),
                    enabled = !viewModel.isLoading
                ) {
                    viewModel.enhanceText()
                    triggerVibration()
                }
                
                ActionButton(
                    text = "😊 情感分析",
                    backgroundColor = Color(0xFF7C3AED),
                    modifier = Modifier.weight(1f),
                    enabled = !viewModel.isLoading
                ) {
                    viewModel.analyzeEmotion()
                    triggerVibration()
                }
            }
            
            // 結果區域
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF1E293B))
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "結果",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color.White,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(
                                color = Color(0xFF0F172A),
                                shape = RoundedCornerShape(8.dp)
                            )
                            .padding(16.dp)
                            .heightIn(min = 100.dp)
                    ) {
                        if (viewModel.isLoading) {
                            Box(
                                modifier = Modifier.fillMaxWidth(),
                                contentAlignment = Alignment.Center
                            ) {
                                CircularProgressIndicator(
                                    color = Color(0xFF2563EB)
                                )
                            }
                        } else {
                            Text(
                                text = if (viewModel.result.isEmpty()) "尚無結果" else viewModel.result,
                                color = Color.White,
                                fontSize = 16.sp
                            )
                        }
                    }
                }
            }
            
            // 觸覺反饋按鈕
            ActionButton(
                text = "🖐 觸覺反饋",
                backgroundColor = Color(0xFF059669),
                modifier = Modifier.fillMaxWidth(),
                enabled = !viewModel.isLoading
            ) {
                viewModel.triggerHaptics()
                triggerVibration()
            }
        }
    }
}

@Composable
fun ActionButton(
    text: String,
    backgroundColor: Color,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(48.dp),
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor = backgroundColor,
            disabledContainerColor = backgroundColor.copy(alpha = 0.5f)
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Text(
            text = text,
            fontSize = 16.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}