// Modern Reader - Linux Desktop App
// 使用 GTK4 + Rust 開發的 Linux 桌面應用程式

use gtk4::prelude::*;
use gtk4::{glib, Application, ApplicationWindow, Button, Box, TextView, Entry, Label, ProgressBar};
use reqwest;
use serde_json::{json, Value};
use std::sync::Arc;
use tokio::sync::Mutex;

// MARK: - Modern Reader Linux SDK
#[derive(Clone)]
pub struct ModernReaderLinuxSDK {
    base_url: String,
    session_token: Arc<Mutex<Option<String>>>,
    client: reqwest::Client,
}

impl ModernReaderLinuxSDK {
    pub fn new() -> Self {
        Self {
            base_url: "https://localhost:8443".to_string(),
            session_token: Arc::new(Mutex::new(None)),
            client: reqwest::Client::new(),
        }
    }

    // 登入方法
    pub async fn login(&self, identifier: &str, password: &str) -> Result<bool, Box<dyn std::error::Error>> {
        let login_data = if identifier.contains("@") {
            json!({
                "email": identifier,
                "password": password
            })
        } else {
            json!({
                "username": identifier,
                "password": password
            })
        };

        let response = self.make_request("/auth/login", Some(login_data)).await?;
        
        if let Some(success) = response["success"].as_bool() {
            if success {
                if let Some(token) = response["token"].as_str() {
                    let mut session_token = self.session_token.lock().await;
                    *session_token = Some(token.to_string());
                    return Ok(true);
                }
            }
        }

        Ok(false)
    }

    // AI 文本增強
    pub async fn enhance_text(&self, text: &str, style: &str) -> Result<String, Box<dyn std::error::Error>> {
        let request_data = json!({
            "text": text,
            "style": style,
            "use_google": false
        });

        let response = self.make_request("/ai/enhance_text", Some(request_data)).await?;
        
        Ok(response["enhanced_text"]
            .as_str()
            .unwrap_or("增強失敗")
            .to_string())
    }

    // 情感分析
    pub async fn analyze_emotion(&self, text: &str) -> Result<(String, f64), Box<dyn std::error::Error>> {
        let request_data = json!({ "text": text });
        let response = self.make_request("/ai/analyze_emotion", Some(request_data)).await?;

        let emotion = response["emotion_analysis"]["emotion"]
            .as_str()
            .unwrap_or("未知")
            .to_string();
        let confidence = response["emotion_analysis"]["confidence"]
            .as_f64()
            .unwrap_or(0.0);

        Ok((emotion, confidence))
    }

    // 健康檢查
    pub async fn health_check(&self) -> Result<String, Box<dyn std::error::Error>> {
        let response = self.make_request("/health", None).await?;
        
        Ok(response["status"]
            .as_str()
            .unwrap_or("連接失敗")
            .to_string())
    }

    // 私有方法：發送請求
    async fn make_request(&self, endpoint: &str, data: Option<Value>) -> Result<Value, Box<dyn std::error::Error>> {
        let url = format!("{}{}", self.base_url, endpoint);
        let mut request = self.client.post(&url);

        // 添加認證標頭
        if let Some(token) = &*self.session_token.lock().await {
            request = request.bearer_auth(token);
        }

        // 添加請求體
        if let Some(data) = data {
            request = request.json(&data);
        }

        let response = request.send().await?;
        let json: Value = response.json().await?;
        
        Ok(json)
    }
}

// MARK: - GTK4 應用程式
fn main() -> glib::ExitCode {
    let app = Application::builder()
        .application_id("com.modernreader.linux")
        .build();

    app.connect_activate(build_ui);
    app.run()
}

fn build_ui(app: &Application) {
    let window = ApplicationWindow::builder()
        .application(app)
        .title("Modern Reader - 現代閱讀器")
        .default_width(900)
        .default_height(700)
        .build();

    let sdk = ModernReaderLinuxSDK::new();

    // 主要容器
    let main_box = Box::new(gtk4::Orientation::Vertical, 12);
    main_box.set_margin_top(20);
    main_box.set_margin_bottom(20);
    main_box.set_margin_start(20);
    main_box.set_margin_end(20);

    // 標題區域
    let title_box = Box::new(gtk4::Orientation::Vertical, 8);
    let title_label = Label::new(Some("Modern Reader"));
    title_label.add_css_class("title-1");
    let subtitle_label = Label::new(Some("現代閱讀器 - Linux 版本"));
    subtitle_label.add_css_class("subtitle");
    title_box.append(&title_label);
    title_box.append(&subtitle_label);

    // 輸入區域
    let input_frame = gtk4::Frame::new(Some("輸入文本"));
    input_frame.set_margin_top(16);
    let input_box = Box::new(gtk4::Orientation::Vertical, 8);
    input_box.set_margin_top(12);
    input_box.set_margin_bottom(12);
    input_box.set_margin_start(12);
    input_box.set_margin_end(12);

    let text_view = TextView::new();
    text_view.set_height_request(120);
    let text_buffer = text_view.buffer();

    // 風格選擇
    let style_box = Box::new(gtk4::Orientation::Horizontal, 8);
    let style_label = Label::new(Some("增強風格:"));
    let style_combo = gtk4::ComboBoxText::new();
    style_combo.append_text("immersive");
    style_combo.append_text("dramatic");
    style_combo.append_text("poetic");
    style_combo.append_text("technical");
    style_combo.append_text("casual");
    style_combo.set_active(Some(0));
    style_box.append(&style_label);
    style_box.append(&style_combo);

    input_box.append(&text_view);
    input_box.append(&style_box);
    input_frame.set_child(Some(&input_box));

    // 按鈕區域
    let button_box = Box::new(gtk4::Orientation::Horizontal, 12);
    button_box.set_margin_top(16);
    
    let enhance_button = Button::with_label("🚀 AI 增強");
    enhance_button.add_css_class("suggested-action");
    
    let analyze_button = Button::with_label("😊 情感分析");
    
    let health_button = Button::with_label("🏥 健康檢查");
    
    let progress_bar = ProgressBar::new();
    progress_bar.set_visible(false);

    button_box.append(&enhance_button);
    button_box.append(&analyze_button);
    button_box.append(&health_button);
    button_box.append(&progress_bar);

    // 結果區域
    let result_frame = gtk4::Frame::new(Some("結果"));
    result_frame.set_margin_top(16);
    let result_text_view = TextView::new();
    result_text_view.set_height_request(200);
    result_text_view.set_editable(false);
    let result_buffer = result_text_view.buffer();
    result_buffer.set_text("尚無結果");
    result_frame.set_child(Some(&result_text_view));

    // 狀態欄
    let status_box = Box::new(gtk4::Orientation::Horizontal, 8);
    status_box.set_margin_top(16);
    let status_label = Label::new(Some("狀態: 未連接"));
    status_label.add_css_class("dim-label");
    status_box.append(&status_label);

    // 組裝界面
    main_box.append(&title_box);
    main_box.append(&input_frame);
    main_box.append(&button_box);
    main_box.append(&result_frame);
    main_box.append(&status_box);

    window.set_child(Some(&main_box));

    // 按鈕事件處理
    let sdk_clone = sdk.clone();
    let text_buffer_clone = text_buffer.clone();
    let result_buffer_clone = result_buffer.clone();
    let style_combo_clone = style_combo.clone();
    let progress_bar_clone = progress_bar.clone();
    let enhance_button_clone = enhance_button.clone();

    enhance_button.connect_clicked(move |_| {
        let sdk = sdk_clone.clone();
        let text_buffer = text_buffer_clone.clone();
        let result_buffer = result_buffer_clone.clone();
        let style_combo = style_combo_clone.clone();
        let progress_bar = progress_bar_clone.clone();
        let button = enhance_button_clone.clone();

        glib::spawn_future_local(async move {
            let text = text_buffer.text(&text_buffer.start_iter(), &text_buffer.end_iter(), false);
            if text.trim().is_empty() {
                return;
            }

            // 顯示進度條
            progress_bar.set_visible(true);
            progress_bar.pulse();
            button.set_sensitive(false);

            let style = style_combo.active_text()
                .map(|s| s.as_str().to_string())
                .unwrap_or_else(|| "immersive".to_string());

            match sdk.enhance_text(&text, &style).await {
                Ok(enhanced) => {
                    result_buffer.set_text(&enhanced);
                }
                Err(err) => {
                    result_buffer.set_text(&format!("錯誤: {}", err));
                }
            }

            // 隱藏進度條
            progress_bar.set_visible(false);
            button.set_sensitive(true);
        });
    });

    // 情感分析按鈕
    let sdk_clone = sdk.clone();
    let text_buffer_clone = text_buffer.clone();
    let result_buffer_clone = result_buffer.clone();
    let progress_bar_clone = progress_bar.clone();
    let analyze_button_clone = analyze_button.clone();

    analyze_button.connect_clicked(move |_| {
        let sdk = sdk_clone.clone();
        let text_buffer = text_buffer_clone.clone();
        let result_buffer = result_buffer_clone.clone();
        let progress_bar = progress_bar_clone.clone();
        let button = analyze_button_clone.clone();

        glib::spawn_future_local(async move {
            let text = text_buffer.text(&text_buffer.start_iter(), &text_buffer.end_iter(), false);
            if text.trim().is_empty() {
                return;
            }

            progress_bar.set_visible(true);
            progress_bar.pulse();
            button.set_sensitive(false);

            match sdk.analyze_emotion(&text).await {
                Ok((emotion, confidence)) => {
                    let result = format!("情感: {}\n信心度: {:.1}%", emotion, confidence * 100.0);
                    result_buffer.set_text(&result);
                }
                Err(err) => {
                    result_buffer.set_text(&format!("錯誤: {}", err));
                }
            }

            progress_bar.set_visible(false);
            button.set_sensitive(true);
        });
    });

    // 健康檢查按鈕
    let sdk_clone = sdk.clone();
    let status_label_clone = status_label.clone();

    health_button.connect_clicked(move |_| {
        let sdk = sdk_clone.clone();
        let status_label = status_label_clone.clone();

        glib::spawn_future_local(async move {
            match sdk.health_check().await {
                Ok(status) => {
                    status_label.set_text(&format!("狀態: {}", status));
                }
                Err(_) => {
                    status_label.set_text("狀態: 連接失敗");
                }
            }
        });
    });

    // 初始健康檢查
    let sdk_clone = sdk.clone();
    let status_label_clone = status_label.clone();
    glib::spawn_future_local(async move {
        match sdk_clone.health_check().await {
            Ok(status) => {
                status_label_clone.set_text(&format!("狀態: {}", status));
            }
            Err(_) => {
                status_label_clone.set_text("狀態: 連接失敗");
            }
        }
    });

    window.present();
}

// Cargo.toml 依賴項
/*
[dependencies]
gtk4 = "0.7"
reqwest = { version = "0.11", features = ["json"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
*/