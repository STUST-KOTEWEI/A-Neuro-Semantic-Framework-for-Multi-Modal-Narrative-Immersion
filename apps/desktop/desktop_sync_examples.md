# Desktop Sync Examples

跨 macOS / Windows / Linux 的同步核心概念：
1. 先用授權標頭 (X-API-Key) 呼叫 `/sync/manifest`
2. 比對本地快取的 etag 與檔案 sha256
3. 下載變更檔案 `/sync/file?path=...`
4. （可選）背景 WebSocket `/ws/sync` 收到 update 後再執行第 1~3 步

## macOS (Swift / URLSession)
```swift
struct SyncFile: Decodable { let path:String; let sha256:String; let mtime:Int; let size:Int; let category:String }
struct Manifest: Decodable { let etag:String; let file_count:Int; let files:[SyncFile] }

class SyncService {
    let base = URL(string: "http://localhost:8010")!
    let apiKey = "dev-key-123"
    var etag: String? = nil

    func fetchManifest(force: Bool = false) async throws -> Manifest? {
        var req = URLRequest(url: base.appending(path: "/sync/manifest"))
        req.addValue(apiKey, forHTTPHeaderField: "X-API-Key")
        if let etag = etag, !force { req.addValue(etag, forHTTPHeaderField: "If-None-Match") }
        let (data, resp) = try await URLSession.shared.data(for: req)
        guard let http = resp as? HTTPURLResponse else { return nil }
        if http.statusCode == 304 { return nil }
        if http.statusCode != 200 { throw NSError(domain: "sync", code: http.statusCode) }
        if let newTag = http.value(forHTTPHeaderField: "ETag") { etag = newTag }
        return try JSONDecoder().decode(Manifest.self, from: data)
    }

    func fetchFile(path: String) async throws -> String {
        var comp = URLComponents(url: base.appending(path: "/sync/file"), resolvingAgainstBaseURL: false)!
        comp.queryItems = [URLQueryItem(name: "path", value: path)]
        var req = URLRequest(url: comp.url!)
        req.addValue(apiKey, forHTTPHeaderField: "X-API-Key")
        let (data, _) = try await URLSession.shared.data(for: req)
        let json = try JSONSerialization.jsonObject(with: data) as! [String:Any]
        return json["content"] as? String ?? ""
    }
}
```

## Windows (C# / HttpClient)
```csharp
public class SyncClient {
    private readonly HttpClient _http = new HttpClient();
    private string? _etag;
    private string _base = "http://localhost:8010";
    private string _apiKey = "dev-key-123";

    public async Task<Manifest?> FetchManifest(bool force=false) {
        var req = new HttpRequestMessage(HttpMethod.Get, _base + "/sync/manifest");
        req.Headers.Add("X-API-Key", _apiKey);
        if(_etag != null && !force) req.Headers.TryAddWithoutValidation("If-None-Match", _etag);
        var resp = await _http.SendAsync(req);
        if(resp.StatusCode == System.Net.HttpStatusCode.NotModified) return null;
        if(!resp.IsSuccessStatusCode) throw new Exception("Manifest error" + resp.StatusCode);
        if(resp.Headers.ETag != null) _etag = resp.Headers.ETag!.Tag?.Trim('"');
        var json = await resp.Content.ReadAsStringAsync();
        return System.Text.Json.JsonSerializer.Deserialize<Manifest>(json);
    }

    public async Task<string> FetchFile(string path) {
        var url = _base + "/sync/file?path=" + Uri.EscapeDataString(path);
        var req = new HttpRequestMessage(HttpMethod.Get, url);
        req.Headers.Add("X-API-Key", _apiKey);
        var resp = await _http.SendAsync(req);
        resp.EnsureSuccessStatusCode();
        var json = await resp.Content.ReadAsStringAsync();
        using var doc = System.Text.Json.JsonDocument.Parse(json);
        return doc.RootElement.GetProperty("content").GetString() ?? string.Empty;
    }
}
```

## Linux (Rust / reqwest)
```rust
use reqwest::blocking::Client;
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct SyncFile { path: String, sha256: String, mtime: i64, size: i64, category: String }
#[derive(Deserialize, Debug)]
struct Manifest { etag: String, file_count: u32, files: Vec<SyncFile> }

fn fetch_manifest(client: &Client, base: &str, etag: &mut Option<String>) -> anyhow::Result<Option<Manifest>> {
    let mut req = client.get(format!("{}/sync/manifest", base)).header("X-API-Key", "dev-key-123");
    if let Some(tag) = etag { req = req.header("If-None-Match", tag); }
    let resp = req.send()?;
    if resp.status().as_u16() == 304 { return Ok(None); }
    if !resp.status().is_success() { anyhow::bail!("status {}", resp.status()); }
    if let Some(tag) = resp.headers().get("etag") { *etag = Some(tag.to_str()?.to_string()); }
    Ok(Some(resp.json::<Manifest>()?))
}

fn fetch_file(client: &Client, base: &str, path: &str) -> anyhow::Result<String> {
    let resp = client
        .get(format!("{}/sync/file", base))
        .query(&[("path", path)])
        .header("X-API-Key", "dev-key-123")
        .send()?;
    if !resp.status().is_success() { anyhow::bail!("status {}", resp.status()); }
    let v: serde_json::Value = resp.json()?;
    Ok(v["content"].as_str().unwrap_or("").to_string())
}
```

## WebSocket 提示
- macOS 可用 URLSessionWebSocketTask
- Windows 可用 ClientWebSocket
- Rust 可用 tokio-tungstenite

收到 `{"type":"update","etag":"..."}` 後再呼叫一次 manifest。
