import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

// Data model for a single word with its timing information.
class WordTimestamp {
  final String word;
  final double startTime;
  final double endTime;

  WordTimestamp({required this.word, required this.startTime, required this.endTime});
}

// Data model for the combined result of synthesis.
class SynthesisResult {
  final Uint8List audioData;
  final List<WordTimestamp> timestamps;

  SynthesisResult({required this.audioData, required this.timestamps});
}

class ElevenLabsService {
  final String apiKey;
  final String _baseUrl = 'https://api.elevenlabs.io/v1';

  ElevenLabsService({required this.apiKey});

  // This is the new method to get audio and timestamps.
  Future<SynthesisResult> synthesizeAndGetTimestamps(
    String text, {
    String voiceId = '21m00Tcm4TlvDq8ikWAM',
  }) async {
    final url = '$_baseUrl/text-to-speech/$voiceId/with-timestamps';
    final headers = {
      'Content-Type': 'application/json',
      'xi-api-key': apiKey,
    };
    final body = json.encode({
      'text': text,
      'model_id': 'eleven_multilingual_v2',
    });

    final response = await http.post(Uri.parse(url), headers: headers, body: body);

    if (response.statusCode == 200) {
      final jsonResponse = json.decode(utf8.decode(response.bodyBytes));
      final audioBase64 = jsonResponse['audio_base64'] as String;
      final audioData = base64Decode(audioBase64);
      
      final timestamps = _processCharacterTimestamps(text, jsonResponse);

      return SynthesisResult(audioData: audioData, timestamps: timestamps);
    } else {
      throw Exception('Failed to synthesize with timestamps. Error: ${response.body}');
    }
  }

  List<WordTimestamp> _processCharacterTimestamps(String text, Map<String, dynamic> jsonResponse) {
    final List<WordTimestamp> wordTimestamps = [];
    if (jsonResponse['character_start_times_seconds'] == null) {
      return [];
    }

    final charStartTimes = (jsonResponse['character_start_times_seconds'] as List).cast<double>();
    final words = text.split(RegExp(r'\s+'));
    int charIndex = 0;

    for (String word in words) {
      if (word.isEmpty) continue;

      final wordStartIndex = charIndex;
      final wordEndIndex = wordStartIndex + word.length - 1;

      if (wordEndIndex < charStartTimes.length) {
        final startTime = charStartTimes[wordStartIndex];
        // The end time of a word is the start time of the next character, or the end of the last char
        final endTime = (wordEndIndex + 1 < charStartTimes.length) 
            ? charStartTimes[wordEndIndex + 1] 
            : charStartTimes[wordEndIndex] + 0.2; // Estimate duration for last word

        wordTimestamps.add(WordTimestamp(word: word, startTime: startTime, endTime: endTime));
      }
      charIndex += word.length + 1; // +1 for the space
    }

    return wordTimestamps;
  }

  // This is the old method, kept for compatibility if needed.
  Future<Uint8List> textToSpeech(
    String text, {
    String voiceId = '21m00Tcm4TlvDq8ikWAM',
    String? emotion,
  }) async {
    final url = '$_baseUrl/text-to-speech/$voiceId';
    final headers = {
      'Content-Type': 'application/json',
      'xi-api-key': apiKey,
    };

    double stability = 0.5;
    if (emotion != null) {
      switch (emotion.toLowerCase()) {
        case 'happy': stability = 0.4; break;
        case 'sad': stability = 0.6; break;
        case 'angry': stability = 0.3; break;
      }
    }

    final body = json.encode({
      'text': text,
      'model_id': 'eleven_multilingual_v2',
      'voice_settings': {
        'stability': stability,
        'similarity_boost': 0.75,
      },
    });

    final response = await http.post(Uri.parse(url), headers: headers, body: body);

    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw Exception('Failed to generate audio. Error: ${response.body}');
    }
  }
}