// Modern Reader - Wear OS App
// 使用 Jetpack Compose for Wear OS 開發的 Android 智慧手錶應用

package com.modernreader.wearos

import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.wear.compose.material.*
import androidx.wear.compose.navigation.SwipeDismissableNavHost
import androidx.wear.compose.navigation.composable
import androidx.wear.compose.navigation.rememberSwipeDismissableNavController
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// MARK: - Modern Reader Watch SDK (Lite)
class ModernReaderWatchSDK {
    
    // 簡化的文本分析（適用於手錶）
    suspend fun quickAnalyze(text: String): Pair<String, Double> {
        // 模擬分析延遲
        delay(500)
        
        val words = text.lowercase().split(Regex("\\s+"))
        
        // 簡單情感詞典
        val positiveWords = listOf("好", "棒", "愛", "喜歡", "開心", "快樂", "amazing", "great", "love", "happy")
        val negativeWords = listOf("糟", "壞", "討厭", "難過", "生氣", "terrible", "bad", "hate", "sad", "angry")
        
        var positiveCount = 0
        var negativeCount = 0
        
        words.forEach { word ->
            when {
                positiveWords.contains(word) -> positiveCount++
                negativeWords.contains(word) -> negativeCount++
            }
        }
        
        val (emotion, intensity) = when {
            positiveCount > negativeCount -> "正面" to (positiveCount.toDouble() / words.size)
            negativeCount > positiveCount -> "負面" to (negativeCount.toDouble() / words.size)
            else -> "中性" to 0.5
        }
        
        return emotion to minOf(intensity * 2, 1.0)
    }
    
    // 觸覺反饋
    fun triggerHaptics(context: android.content.Context, intensity: Double) {
        val vibrator = context.getSystemService(Vibrator::class.java)
        
        val vibrationEffect = when {
            intensity < 0.3 -> VibrationEffect.createOneShot(100, 50)
            intensity < 0.7 -> VibrationEffect.createOneShot(200, 100)
            else -> VibrationEffect.createOneShot(300, 255)
        }
        
        vibrator?.vibrate(vibrationEffect)
    }
}

// MARK: - ViewModel
class WatchViewModel : ViewModel() {
    private val sdk = ModernReaderWatchSDK()
    
    var emotion by mutableStateOf("")
    var intensity by mutableStateOf(0.0)
    var result by mutableStateOf("")
    var isLoading by mutableStateOf(false)
    var isConnected by mutableStateOf(true) // 手錶版本預設已連接
    
    fun analyzeText(text: String, context: android.content.Context) {
        if (text.isBlank()) return
        
        viewModelScope.launch {
            isLoading = true
            try {
                val (detectedEmotion, detectedIntensity) = sdk.quickAnalyze(text)
                emotion = detectedEmotion
                intensity = detectedIntensity
                result = String.format("強度: %.0f%%", detectedIntensity * 100)
                
                // 觸發觸覺反饋
                sdk.triggerHaptics(context, detectedIntensity)
            } catch (e: Exception) {
                result = "分析失敗"
            } finally {
                isLoading = false
            }
        }
    }
    
    fun triggerHaptics(context: android.content.Context, intensity: Double) {
        sdk.triggerHaptics(context, intensity)
    }
}

// MARK: - MainActivity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setContent {
            ModernReaderWearTheme {
                WearApp()
            }
        }
    }
}

// MARK: - 主題
@Composable
fun ModernReaderWearTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colors = Colors(
            primary = Color(0xFF2563EB),
            primaryVariant = Color(0xFF1E40AF),
            secondary = Color(0xFF7C3AED),
            background = Color.Black,
            surface = Color(0xFF1F1F1F),
            onPrimary = Color.White,
            onSecondary = Color.White,
            onBackground = Color.White,
            onSurface = Color.White
        ),
        content = content
    )
}

// MARK: - 主應用
@Composable
fun WearApp() {
    val navController = rememberSwipeDismissableNavController()
    
    SwipeDismissableNavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToAnalyze = { navController.navigate("analyze") },
                onNavigateToHaptics = { navController.navigate("haptics") },
                onNavigateToSettings = { navController.navigate("settings") }
            )
        }
        
        composable("analyze") {
            AnalyzeScreen()
        }
        
        composable("haptics") {
            HapticsScreen()
        }
        
        composable("settings") {
            SettingsScreen()
        }
    }
}

// MARK: - 首頁
@Composable
fun HomeScreen(
    onNavigateToAnalyze: () -> Unit,
    onNavigateToHaptics: () -> Unit,
    onNavigateToSettings: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Modern Reader",
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White,
            textAlign = TextAlign.Center
        )
        
        Text(
            text = "現代閱讀器",
            fontSize = 12.sp,
            color = Color.Gray,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Column(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Chip(
                onClick = onNavigateToAnalyze,
                label = { Text("📝 快速分析", fontSize = 12.sp) },
                modifier = Modifier.fillMaxWidth(0.8f)
            )
            
            Chip(
                onClick = onNavigateToHaptics,
                label = { Text("🖐 觸覺反饋", fontSize = 12.sp) },
                modifier = Modifier.fillMaxWidth(0.8f)
            )
            
            Chip(
                onClick = onNavigateToSettings,
                label = { Text("⚙️ 設置", fontSize = 12.sp) },
                modifier = Modifier.fillMaxWidth(0.8f)
            )
        }
    }
}

// MARK: - 分析頁面
@Composable
fun AnalyzeScreen() {
    val viewModel = remember { WatchViewModel() }
    val context = LocalContext.current
    var showingInput by remember { mutableStateOf(false) }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "快速分析",
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (viewModel.emotion.isNotEmpty()) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = getEmotionEmoji(viewModel.emotion),
                    fontSize = 32.sp
                )
                
                Text(
                    text = viewModel.emotion,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = Color.White
                )
                
                Text(
                    text = viewModel.result,
                    fontSize = 12.sp,
                    color = Color.Gray
                )
            }
        } else {
            Text(
                text = "點擊下方開始分析",
                fontSize = 12.sp,
                color = Color.Gray,
                textAlign = TextAlign.Center
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (viewModel.isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp),
                color = Color(0xFF2563EB)
            )
        } else {
            Button(
                onClick = {
                    // 簡化輸入 - 使用預設文本進行演示
                    val demoTexts = listOf(
                        "今天天氣真好！我很開心",
                        "這個產品太糟糕了",
                        "普通的一天，沒什麼特別的"
                    )
                    val randomText = demoTexts.random()
                    viewModel.analyzeText(randomText, context)
                },
                modifier = Modifier.size(80.dp),
                colors = ButtonDefaults.buttonColors(backgroundColor = Color(0xFF2563EB))
            ) {
                Text(
                    text = "分析",
                    fontSize = 12.sp,
                    color = Color.White
                )
            }
        }
    }
}

// MARK: - 觸覺反饋頁面
@Composable
fun HapticsScreen() {
    val viewModel = remember { WatchViewModel() }
    val context = LocalContext.current
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "觸覺反饋",
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Column(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            HapticButton(
                text = "輕觸",
                intensity = 0.2
            ) {
                viewModel.triggerHaptics(context, 0.2)
            }
            
            HapticButton(
                text = "中等",
                intensity = 0.5
            ) {
                viewModel.triggerHaptics(context, 0.5)
            }
            
            HapticButton(
                text = "強烈",
                intensity = 0.8
            ) {
                viewModel.triggerHaptics(context, 0.8)
            }
        }
    }
}

// MARK: - 設置頁面
@Composable
fun SettingsScreen() {
    val viewModel = remember { WatchViewModel() }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "設置",
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // 連接狀態
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .background(
                        if (viewModel.isConnected) Color.Green else Color.Red,
                        CircleShape
                    )
            )
            
            Text(
                text = if (viewModel.isConnected) "已連接" else "未連接",
                fontSize = 12.sp,
                color = Color.White
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // 功能列表
        Column(
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            SettingItem("本地分析", true)
            SettingItem("觸覺反饋", true)
            SettingItem("情感檢測", true)
            SettingItem("節能模式", false)
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Modern Reader v1.0",
            fontSize = 10.sp,
            color = Color.Gray
        )
    }
}

// MARK: - 輔助組件
@Composable
fun HapticButton(
    text: String,
    intensity: Double,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth(0.8f)
            .height(40.dp),
        colors = ButtonDefaults.buttonColors(backgroundColor = Color(0xFF7C3AED))
    ) {
        Row(
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(
                text = text,
                fontSize = 12.sp,
                color = Color.White
            )
            
            Text(
                text = "${(intensity * 100).toInt()}%",
                fontSize = 10.sp,
                color = Color.Gray
            )
        }
    }
}

@Composable
fun SettingItem(title: String, enabled: Boolean) {
    Row(
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(
            text = title,
            fontSize = 12.sp,
            color = Color.White
        )
        
        if (enabled) {
            Text(
                text = "✓",
                fontSize = 12.sp,
                color = Color.Green
            )
        }
    }
}

// MARK: - 輔助函數
fun getEmotionEmoji(emotion: String): String {
    return when (emotion) {
        "正面" -> "😊"
        "負面" -> "😢"
        else -> "😐"
    }
}