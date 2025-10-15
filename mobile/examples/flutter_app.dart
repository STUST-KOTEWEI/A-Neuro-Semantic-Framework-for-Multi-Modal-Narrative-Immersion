// Flutter Example App with Sync Integration
// 假設使用 http 與 web_socket_channel 套件
// 在 pubspec.yaml 加入：
// dependencies:
//   http: ^1.2.0
//   web_socket_channel: ^2.4.0

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const ModernReaderApp());
}

class ModernReaderApp extends StatefulWidget {
  const ModernReaderApp({super.key});

  @override
  State<ModernReaderApp> createState() => _ModernReaderAppState();
}

class _ModernReaderAppState extends State<ModernReaderApp> {
  final SyncManager _sync = SyncManager(baseUrl: 'http://localhost:8010');
  String _status = '初始化中...';
  List<SyncFileMeta> _files = [];

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    try {
      setState(() => _status = '同步中...');
      await _sync.initialSync();
      setState(() {
        _files = _sync.latestManifest?.files ?? [];
        _status = '同步完成 (files=${_files.length})';
      });
      _sync.listenRealtime(onUpdate: () async {
        setState(() => _status = '接收更新推播，重新同步...');
        await _sync.initialSync();
        setState(() {
          _files = _sync.latestManifest?.files ?? [];
          _status = '同步完成 (files=${_files.length})';
        });
      });
    } catch (e) {
      setState(() => _status = '同步失敗: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('Modern Reader Flutter Sync')),
        body: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_status),
              const SizedBox(height: 12),
              Expanded(
                child: ListView.builder(
                  itemCount: _files.length,
                  itemBuilder: (context, index) {
                    final f = _files[index];
                    return ListTile(
                      title: Text(f.path),
                      subtitle: Text('${f.sha256.substring(0, 8)}  mtime=${f.mtime}'),
                      trailing: Text(f.category),
                      onTap: () async {
                        final content = await _sync.readLocalContent(f.path);
                        if (!context.mounted) return;
                        showDialog(
                          context: context,
                          builder: (_) => AlertDialog(
                            title: Text(f.path),
                            content: SingleChildScrollView(child: Text(content ?? '<無內容>')),
                          ),
                        );
                      },
                    );
                  },
                ),
              )
            ],
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () async {
            setState(() => _status = '手動同步中...');
            await _sync.initialSync(force: true);
            setState(() {
              _files = _sync.latestManifest?.files ?? [];
              _status = '同步完成 (files=${_files.length})';
            });
          },
          child: const Icon(Icons.refresh),
        ),
      ),
    );
  }
}

// ------------------ Sync Layer ------------------
class SyncManifest {
  final String etag;
  final int fileCount;
  final List<SyncFileMeta> files;
  SyncManifest({required this.etag, required this.fileCount, required this.files});

  factory SyncManifest.fromJson(Map<String, dynamic> j) => SyncManifest(
        etag: j['etag'],
        fileCount: j['file_count'],
        files: (j['files'] as List).map((e) => SyncFileMeta.fromJson(e)).toList(),
      );
}

class SyncFileMeta {
  final String path;
  final String sha256;
  final int mtime;
  final int size;
  final String category;
  SyncFileMeta({required this.path, required this.sha256, required this.mtime, required this.size, required this.category});

  factory SyncFileMeta.fromJson(Map<String, dynamic> j) => SyncFileMeta(
        path: j['path'],
        sha256: j['sha256'],
        mtime: j['mtime'],
        size: j['size'],
        category: j['category'],
      );
}

class SyncManager {
  final String baseUrl;
  final Directory cacheDir;
  SyncManifest? latestManifest;
  String? _etag;
  WebSocketChannel? _channel;

  SyncManager({required this.baseUrl}) : cacheDir = Directory('.flutter-sync-cache') {
    if (!cacheDir.existsSync()) {
      cacheDir.createSync(recursive: true);
    }
  }

  File _manifestFile() => File('${cacheDir.path}/manifest.json');

  Future<void> initialSync({bool force = false}) async {
    if (!force && _manifestFile().existsSync()) {
      final data = jsonDecode(_manifestFile().readAsStringSync());
      _etag = data['etag'];
      latestManifest = SyncManifest.fromJson(data);
    }
    final uri = Uri.parse('$baseUrl/sync/manifest');
    final headers = <String, String>{};
    if (!force && _etag != null) headers['If-None-Match'] = _etag!;
    final resp = await http.get(uri, headers: headers);
    if (resp.statusCode == 304) {
      return; // unchanged
    }
    if (resp.statusCode != 200) {
      throw Exception('Manifest error ${resp.statusCode}');
    }
    final body = jsonDecode(resp.body);
    _etag = body['etag'];
    latestManifest = SyncManifest.fromJson(body);

    // Compare and download diffs
    final localIndex = <String, SyncFileMeta>{
      for (final f in (await _loadLocalManifestFiles())) f.path: f
    };

    for (final f in latestManifest!.files) {
      final local = localIndex[f.path];
      if (local == null || local.sha256 != f.sha256) {
        await _downloadFile(f.path);
      }
    }

    _manifestFile().writeAsStringSync(jsonEncode(body));
  }

  Future<List<SyncFileMeta>> _loadLocalManifestFiles() async {
    if (!_manifestFile().existsSync()) return [];
    try {
      final j = jsonDecode(_manifestFile().readAsStringSync());
      return (j['files'] as List).map((e) => SyncFileMeta.fromJson(e)).toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> _downloadFile(String relPath) async {
    final uri = Uri.parse('$baseUrl/sync/file?path=${Uri.encodeComponent(relPath)}');
    final resp = await http.get(uri);
    if (resp.statusCode != 200) throw Exception('download failed $relPath');
    final body = jsonDecode(resp.body);
    final target = File('${cacheDir.path}/$relPath');
    target.parent.createSync(recursive: true);
    target.writeAsStringSync(body['content']);
  }

  Future<String?> readLocalContent(String relPath) async {
    final f = File('${cacheDir.path}/$relPath');
    if (!f.existsSync()) return null;
    return f.readAsString();
  }

  void listenRealtime({required Future<void> Function() onUpdate}) {
    final wsUrl = baseUrl.replaceFirst('http', 'ws') + '/ws/sync';
    _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
    _channel!.stream.listen((event) async {
      try {
        final data = jsonDecode(event);
        if (data['type'] == 'update') {
          await onUpdate();
        }
      } catch (_) {}
    }, onError: (e) {
      // 可選：重試邏輯
    });
  }
}
