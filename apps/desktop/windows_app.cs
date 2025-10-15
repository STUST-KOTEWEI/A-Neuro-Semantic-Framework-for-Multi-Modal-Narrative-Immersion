// Modern Reader - Windows Desktop App
// 使用 WinUI 3 開發的 Windows 桌面應用程式

using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Windows.ApplicationModel;
using Windows.Storage;

namespace ModernReader.Windows
{
    // MARK: - Modern Reader Windows SDK
    public class ModernReaderWinSDK
    {
        private readonly string baseUrl = "https://localhost:8443";
        private string? sessionToken;
        private readonly HttpClient httpClient;

        public ModernReaderWinSDK()
        {
            httpClient = new HttpClient();
        }

        // 登入方法
        public async Task<bool> LoginAsync(string identifier, string password)
        {
            var loginData = identifier.Contains("@")
                ? new { email = identifier, password = password }
                : new { username = identifier, password = password };

            var response = await MakeRequestAsync("/auth/login", loginData);
            
            if (response != null && response.TryGetProperty("success", out var success) && success.GetBoolean())
            {
                if (response.TryGetProperty("token", out var token))
                {
                    sessionToken = token.GetString();
                    return true;
                }
            }

            return false;
        }

        // AI 文本增強
        public async Task<string> EnhanceTextAsync(string text, string style = "immersive")
        {
            var requestData = new
            {
                text = text,
                style = style,
                use_google = false
            };

            var response = await MakeRequestAsync("/ai/enhance_text", requestData);
            
            if (response != null && response.TryGetProperty("enhanced_text", out var enhanced))
            {
                return enhanced.GetString() ?? "增強失敗";
            }

            return "增強失敗";
        }

        // 情感分析
        public async Task<(string emotion, double confidence)> AnalyzeEmotionAsync(string text)
        {
            var requestData = new { text = text };
            var response = await MakeRequestAsync("/ai/analyze_emotion", requestData);

            if (response != null && response.TryGetProperty("emotion_analysis", out var analysis))
            {
                var emotion = analysis.TryGetProperty("emotion", out var e) ? e.GetString() : "未知";
                var confidence = analysis.TryGetProperty("confidence", out var c) ? c.GetDouble() : 0.0;
                return (emotion ?? "未知", confidence);
            }

            return ("未知", 0.0);
        }

        // 健康檢查
        public async Task<string> HealthCheckAsync()
        {
            var response = await MakeRequestAsync("/health", null, "GET");
            
            if (response != null && response.TryGetProperty("status", out var status))
            {
                return status.GetString() ?? "未知";
            }

            return "連接失敗";
        }

        // 私有方法：發送請求
        private async Task<JsonElement?> MakeRequestAsync(string endpoint, object? data, string method = "POST")
        {
            try
            {
                var request = new HttpRequestMessage(
                    method == "GET" ? HttpMethod.Get : HttpMethod.Post,
                    $"{baseUrl}{endpoint}"
                );

                request.Headers.Add("Accept", "application/json");
                
                if (!string.IsNullOrEmpty(sessionToken))
                {
                    request.Headers.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", sessionToken);
                }

                if (method == "POST" && data != null)
                {
                    var json = JsonSerializer.Serialize(data);
                    request.Content = new StringContent(json, Encoding.UTF8, "application/json");
                }

                var response = await httpClient.SendAsync(request);
                var responseContent = await response.Content.ReadAsStringAsync();

                return JsonSerializer.Deserialize<JsonElement>(responseContent);
            }
            catch
            {
                return null;
            }
        }
    }

    // MARK: - MainWindow
    public sealed partial class MainWindow : Window
    {
        private readonly ModernReaderWinSDK sdk;
        private bool isLoading;

        public MainWindow()
        {
            this.InitializeComponent();
            sdk = new ModernReaderWinSDK();
            
            // 設定視窗
            this.Title = "Modern Reader - 現代閱讀器";
            this.SetTitleBar(TitleBarTextBlock);
            
            // 初始化
            _ = InitializeAsync();
        }

        private async Task InitializeAsync()
        {
            StatusTextBlock.Text = "正在連接...";
            var status = await sdk.HealthCheckAsync();
            StatusTextBlock.Text = $"狀態: {status}";
        }

        // AI 文本增強
        private async void EnhanceButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(InputTextBox.Text) || isLoading) return;

            SetLoading(true);
            try
            {
                var style = (StyleComboBox.SelectedItem as ComboBoxItem)?.Content?.ToString()?.ToLower() ?? "immersive";
                var enhanced = await sdk.EnhanceTextAsync(InputTextBox.Text, style);
                ResultTextBlock.Text = enhanced;
            }
            catch (Exception ex)
            {
                ResultTextBlock.Text = $"錯誤: {ex.Message}";
            }
            finally
            {
                SetLoading(false);
            }
        }

        // 情感分析
        private async void AnalyzeButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(InputTextBox.Text) || isLoading) return;

            SetLoading(true);
            try
            {
                var (emotion, confidence) = await sdk.AnalyzeEmotionAsync(InputTextBox.Text);
                ResultTextBlock.Text = $"情感: {emotion}\n信心度: {confidence:P1}";
            }
            catch (Exception ex)
            {
                ResultTextBlock.Text = $"錯誤: {ex.Message}";
            }
            finally
            {
                SetLoading(false);
            }
        }

        // 健康檢查
        private async void HealthButton_Click(object sender, RoutedEventArgs e)
        {
            var status = await sdk.HealthCheckAsync();
            StatusTextBlock.Text = $"狀態: {status}";
        }

        // 設定載入狀態
        private void SetLoading(bool loading)
        {
            isLoading = loading;
            LoadingProgressRing.IsActive = loading;
            LoadingProgressRing.Visibility = loading ? Visibility.Visible : Visibility.Collapsed;
            
            EnhanceButton.IsEnabled = !loading;
            AnalyzeButton.IsEnabled = !loading;
        }
    }

    // MARK: - App
    public partial class App : Application
    {
        public App()
        {
            this.InitializeComponent();
        }

        protected override void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
        {
            m_window = new MainWindow();
            m_window.Activate();
        }

        private Window? m_window;
    }
}

<!-- MainWindow.xaml -->
<Window x:Class="ModernReader.Windows.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    
    <Grid Background="{ThemeResource AcrylicBackgroundFillColorDefaultBrush}">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="Auto"/>
        </Grid.RowDefinitions>
        
        <!-- 標題欄 -->
        <Grid Grid.Row="0" Height="48" Background="{ThemeResource SolidBackgroundFillColorSecondaryBrush}">
            <TextBlock x:Name="TitleBarTextBlock" 
                       Text="Modern Reader - 現代閱讀器"
                       VerticalAlignment="Center"
                       HorizontalAlignment="Center"
                       FontWeight="Bold"
                       FontSize="16"/>
        </Grid>
        
        <!-- 主要內容 -->
        <ScrollViewer Grid.Row="1" Padding="20">
            <StackPanel Spacing="24">
                
                <!-- 輸入區域 -->
                <Border Background="{ThemeResource CardBackgroundFillColorDefaultBrush}"
                        CornerRadius="8"
                        Padding="16">
                    <StackPanel Spacing="12">
                        <TextBlock Text="輸入文本" 
                                   FontWeight="SemiBold" 
                                   FontSize="18"/>
                        
                        <TextBox x:Name="InputTextBox"
                                 PlaceholderText="請輸入要分析或增強的文本..."
                                 TextWrapping="Wrap"
                                 AcceptsReturn="True"
                                 MinHeight="120"/>
                        
                        <!-- 風格選擇 -->
                        <StackPanel Orientation="Horizontal" Spacing="12">
                            <TextBlock Text="增強風格:" VerticalAlignment="Center"/>
                            <ComboBox x:Name="StyleComboBox" SelectedIndex="0" MinWidth="120">
                                <ComboBoxItem Content="Immersive"/>
                                <ComboBoxItem Content="Dramatic"/>
                                <ComboBoxItem Content="Poetic"/>
                                <ComboBoxItem Content="Technical"/>
                                <ComboBoxItem Content="Casual"/>
                            </ComboBox>
                        </StackPanel>
                        
                        <!-- 按鈕 -->
                        <StackPanel Orientation="Horizontal" Spacing="12">
                            <Button x:Name="EnhanceButton"
                                    Content="🚀 AI 增強"
                                    Style="{StaticResource AccentButtonStyle}"
                                    Click="EnhanceButton_Click"/>
                            
                            <Button x:Name="AnalyzeButton"
                                    Content="😊 情感分析"
                                    Click="AnalyzeButton_Click"/>
                            
                            <ProgressRing x:Name="LoadingProgressRing"
                                          IsActive="False"
                                          Visibility="Collapsed"
                                          Width="24"
                                          Height="24"/>
                        </StackPanel>
                    </StackPanel>
                </Border>
                
                <!-- 結果區域 -->
                <Border Background="{ThemeResource CardBackgroundFillColorDefaultBrush}"
                        CornerRadius="8"
                        Padding="16">
                    <StackPanel Spacing="12">
                        <TextBlock Text="結果" 
                                   FontWeight="SemiBold" 
                                   FontSize="18"/>
                        
                        <Border Background="{ThemeResource ControlFillColorDefaultBrush}"
                                CornerRadius="4"
                                Padding="16"
                                MinHeight="120">
                            <ScrollViewer>
                                <TextBlock x:Name="ResultTextBlock"
                                           Text="尚無結果"
                                           TextWrapping="Wrap"
                                           FontFamily="Consolas"/>
                            </ScrollViewer>
                        </Border>
                    </StackPanel>
                </Border>
                
            </StackPanel>
        </ScrollViewer>
        
        <!-- 狀態欄 -->
        <Border Grid.Row="2" 
                Background="{ThemeResource SolidBackgroundFillColorSecondaryBrush}"
                Padding="12,8">
            <StackPanel Orientation="Horizontal" Spacing="16">
                <TextBlock x:Name="StatusTextBlock" Text="狀態: 未連接"/>
                <Button x:Name="HealthButton"
                        Content="🏥 健康檢查"
                        Style="{StaticResource SubtleButtonStyle}"
                        Click="HealthButton_Click"/>
            </StackPanel>
        </Border>
        
    </Grid>
</Window>