import 'dart:async';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';

import 'services/gutenberg_service.dart';
import 'services/elevenlabs_service.dart';

class ReaderScreen extends StatefulWidget {
  final Book book;
  final String apiKey;

  const ReaderScreen({required this.book, required this.apiKey, super.key});

  @override
  State<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends State<ReaderScreen> {
  // Services and Controllers
  final GutenbergService _gutenbergService = GutenbergService();
  late final ElevenLabsService _elevenLabsService;
  final AudioPlayer _audioPlayer = AudioPlayer();

  // State variables
  String? _bookText;
  List<WordTimestamp> _timestamps = [];
  bool _isLoadingText = true;
  bool _isSynthesizing = false;
  int _currentWordIndex = -1;
  String? _error;
  StreamSubscription? _positionSubscription;

  @override
  void initState() {
    super.initState();
    _elevenLabsService = ElevenLabsService(apiKey: widget.apiKey);
    _fetchText();
    _positionSubscription = _audioPlayer.positionStream.listen((position) {
      final currentSeconds = position.inMilliseconds / 1000.0;
      final index = _timestamps.indexWhere((ts) => currentSeconds >= ts.startTime && currentSeconds < ts.endTime);
      if (index != -1 && index != _currentWordIndex) {
        setState(() {
          _currentWordIndex = index;
        });
      }
    });
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    _positionSubscription?.cancel();
    super.dispose();
  }

  Future<void> _fetchText() async {
    try {
      final text = await _gutenbergService.fetchBookText(widget.book.textUrl);
      setState(() {
        _bookText = text;
        _isLoadingText = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load book text.';
        _isLoadingText = false;
      });
    }
  }

  Future<void> _playText(String text) async {
    if (text.isEmpty || _isSynthesizing) return;
    setState(() => _isSynthesizing = true);

    try {
      final textToRead = text.length > 1000 ? text.substring(0, 1000) : text; // Limit text for demo
      final result = await _elevenLabsService.synthesizeAndGetTimestamps(textToRead);
      
      setState(() {
        _timestamps = result.timestamps;
        _currentWordIndex = -1;
      });

      final audioSource = AudioSource.uri(
        Uri.dataFromBytes(result.audioData, mimeType: 'audio/mpeg'),
      );
      await _audioPlayer.setAudioSource(audioSource);
      _audioPlayer.play();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('語音合成失敗: ${e.toString()}')));
      }
    } finally {
      if (mounted) setState(() => _isSynthesizing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.book.title)),
      floatingActionButton: FloatingActionButton(
        onPressed: (_bookText == null || _isSynthesizing) ? null : () => _playText(_bookText!),
        child: _isSynthesizing ? const CircularProgressIndicator(color: Colors.white) : const Icon(Icons.volume_up),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoadingText) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(child: Text(_error!, style: const TextStyle(color: Colors.red)));
    }
    if (_bookText == null) {
      return const Center(child: Text('無法載入書籍內容。'));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: RichText(
        text: TextSpan(
          style: const TextStyle(color: Colors.black, fontSize: 18, height: 1.5),
          children: _buildTextSpans(),
        ),
      ),
    );
  }

  List<TextSpan> _buildTextSpans() {
    if (_timestamps.isEmpty) {
      return [TextSpan(text: _bookText!)];
    }

    List<TextSpan> spans = [];
    for (int i = 0; i < _timestamps.length; i++) {
      final ts = _timestamps[i];
      spans.add(
        TextSpan(
          text: '${ts.word} ',
          style: TextStyle(
            backgroundColor: i == _currentWordIndex ? Colors.yellow : Colors.transparent,
          ),
        ),
      );
    }
    return spans;
  }
}