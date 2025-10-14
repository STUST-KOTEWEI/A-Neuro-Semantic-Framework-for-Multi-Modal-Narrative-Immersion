import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

// *** 重要：請將IP位址換成您Mac的區域網路IP ***
// 您可以在Mac的「系統設定」>「Wi-Fi」>「詳細資訊」中找到
const String serverIp = "172.20.10.3"; // <--- 在這裡修改！
const String serverUrl = "http://$serverIp:8000/recognize-book";

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Reader',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const ImageUploaderScreen(),
    );
  }
}

class ImageUploaderScreen extends StatefulWidget {
  const ImageUploaderScreen({super.key});

  @override
  State<ImageUploaderScreen> createState() => _ImageUploaderScreenState();
}

class _ImageUploaderScreenState extends State<ImageUploaderScreen> {
  File? _image;
  String _statusMessage = "請選擇一張圖片上傳";

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        _statusMessage = "已選擇圖片，準備上傳";
      });
    }
  }

  Future<void> _uploadImage() async {
    if (_image == null) {
      setState(() {
        _statusMessage = "尚未選擇圖片！";
      });
      return;
    }

    setState(() {
      _statusMessage = "上傳中...";
    });

    try {
      var request = http.MultipartRequest('POST', Uri.parse(serverUrl));
      request.files.add(await http.MultipartFile.fromPath('image', _image!.path));

      var response = await request.send();

      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        setState(() {
          _statusMessage = "上傳成功！\n伺服器回應: $responseBody";
        });
      } else {
        setState(() {
          _statusMessage = "上傳失敗，狀態碼: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = "無法連接到伺服器: $e\n\n請檢查IP位址是否正確，以及伺服器是否正在運行。";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI 多感官閱讀器'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Text(
                '第一步: 選擇書本封面',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 20),
              _image == null
                  ? Container(
                      height: 200,
                      width: 150,
                      color: Colors.grey[300],
                      child: const Icon(Icons.book, size: 50, color: Colors.grey),
                    )
                  : Image.file(_image!, height: 200),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                onPressed: _pickImage,
                icon: const Icon(Icons.photo_library),
                label: const Text('從相簿選擇'),
              ),
              const SizedBox(height: 40),
              ElevatedButton.icon(
                onPressed: _uploadImage,
                icon: const Icon(Icons.cloud_upload),
                label: const Text('上傳到伺服器'),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              ),
              const SizedBox(height: 20),
              Text(_statusMessage),
            ],
          ),
        ),
      ),
    );
  }
}
