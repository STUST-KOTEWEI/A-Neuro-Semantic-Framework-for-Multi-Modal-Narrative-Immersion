# MultisensoryReader-Orchestrator

A sophisticated orchestration system for creating immersive, multi-sensory reading experiences. The orchestrator coordinates text processing, emotion detection, text-to-speech synthesis, and haptic/scent device control to create a fully immersive narrative experience.

## Overview

The MultisensoryReader-Orchestrator orchestrates the following workflow:

```
text → segments → emotion detection → TTS synthesis → haptics/scent triggers
```

It supports:
- Emotion-aware voice style adaptation
- User preference and memory lookup
- Segmented playback with highlight extraction
- Real-time device feedback (haptics and scent)

## Architecture

### Agents

The system consists of five specialized agents:

#### 1. ReaderAgent
**Responsibilities:**
- Text ingestion (epub/txt/URL)
- Segmentation (paragraph/sentence)
- Highlight extraction (tf-idf + transformer attention)
- Generate segment metadata (start/end timestamps, highlight positions)

**Tools:** `vectorDB`, `textPreprocessor`

#### 2. EmotionAgent
**Responsibilities:**
- Predict emotional tone from user voice sample or text
- Map emotion labels to TTS voice presets and prosody settings

**Tools:** `emotionModelAPI`

**Supported Emotions:**
- happy → cheerful voice, faster rate, higher pitch
- sad → melancholic voice, slower rate, lower pitch
- angry → intense voice, fast rate, high volume
- calm → soothing voice, normal pitch, soft volume
- excited → energetic voice, fast rate, elevated pitch
- neutral → normal voice settings

#### 3. DeviceAgent
**Responsibilities:**
- Map segment highlights/emotion events to haptics patterns
- Call HAPTICS SDK / SCENT API

**Tools:** `bhapticsSDK`, `aromajoinAPI`

**Haptic Patterns:**
- happy → gentle_pulse
- sad → slow_wave
- angry → sharp_burst
- calm → smooth_wave
- excited → rapid_pulse

**Scent Mapping:**
- happy → citrus
- sad → lavender
- angry → peppermint
- calm → chamomile
- excited → eucalyptus

#### 4. MemoryAgent
**Responsibilities:**
- User preferences (speed, favorite voice, saved bookmarks)
- RAG: search vector DB for past sessions

**Tools:** `pinecone`, `postgres`

#### 5. Orchestrator
**Entry Points:** `play`, `pause`, `seek`, `summary`

The orchestrator coordinates all agents and implements the main workflow logic.

### Connectors

The system uses connectors to communicate with external services:

#### HTTPConnector
For REST API communication with:
- `textPreprocessor`: Text preprocessing service
- `emotionModelAPI`: Emotion prediction service
- `TTS`: Text-to-speech synthesis (e.g., ElevenLabs)
- `bhapticsSDK`: Haptic device control
- `aromajoinAPI`: Scent device control

#### PineconeConnector
Vector database for:
- Storing and retrieving past reading sessions
- RAG-based session search
- User preference vectors

#### PostgresConnector
Relational database for:
- User profiles and preferences
- Bookmarks and reading history
- Session metadata

## API Endpoints

### POST /orchestrator/play
Start playback of text with multisensory experience.

**Request:**
```json
{
  "text": "Your story text here...",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "playback_url": "https://api.tts.example.com/audio/user123/segment_0.mp3",
  "metadata": {
    "total_segments": 5,
    "current_segment": 0,
    "emotion": "calm",
    "tts_settings": {
      "voice": "soothing",
      "rate": 0.95,
      "pitch": 1.0,
      "volume": 0.9
    },
    "haptic_events": [...],
    "scent_events": [...],
    "total_duration": 120.5
  }
}
```

### POST /orchestrator/pause
Pause current playback.

**Response:**
```json
{
  "status": "paused",
  "current_segment": 2,
  "is_playing": false
}
```

### POST /orchestrator/seek
Seek to a specific segment.

**Request:**
```json
{
  "segment_index": 3
}
```

**Response:**
```json
{
  "status": "seeked",
  "current_segment": 3,
  "playback_url": "https://api.tts.example.com/audio/segment_3.mp3",
  "segment_text": "Text of segment 3...",
  "segment_duration": 25.3
}
```

### GET /orchestrator/summary
Get summary of current session.

**Response:**
```json
{
  "summary": "Summary text of the reading session...",
  "total_segments": 5,
  "total_highlights": 12,
  "emotion": "calm",
  "current_position": 2,
  "is_playing": false
}
```

## Sample Flow

1. **User initiates playback:**
   - `orchestrator.play()` is called with text content
   
2. **Orchestrator coordinates:**
   - Calls `memory.getUserPrefs()` to get user preferences
   - Calls `reader.segment(text)` to split text into segments
   - Calls `emotion.predict()` on text or voice sample
   - Calls `TTS.synthesize()` with emotion-based voice preset
   - Calls `device.triggerHaptics()` based on highlight timestamps
   - Returns playback URL and metadata to frontend

3. **User can:**
   - Pause/resume playback
   - Seek to specific segments
   - Get session summary
   - Experience synchronized haptics and scents

## Usage Example

```python
from holo.orchestrator import Orchestrator

# Initialize orchestrator with configuration
config = {
    'connectors': {
        'textPreprocessor': {'type': 'http', 'url': 'https://api.example.com/preprocess'},
        'vectorDB': {'type': 'pinecone', 'index': 'user_sessions'},
        'emotionModelAPI': {'type': 'http', 'url': 'https://api.example.com/emotion'},
        'TTS': {'type': 'http', 'url': 'https://api.elevenlabs.io/v1/text-to-speech'},
        'bhapticsSDK': {'type': 'http', 'url': 'https://api.example.com/haptics'},
        'aromajoinAPI': {'type': 'http', 'url': 'https://api.example.com/scent'},
        'postgres': {'type': 'sql', 'connection': 'postgres://...'}
    }
}

orchestrator = Orchestrator(config)

# Start playback
result = await orchestrator.play(
    text="Your narrative text here...",
    user_id="user123"
)

# Pause
await orchestrator.pause()

# Seek to segment
await orchestrator.seek(segment_index=2)

# Get summary
summary = await orchestrator.summary()
```

## Configuration

The orchestrator is configured through a dictionary that defines connectors:

```python
{
    'connectors': {
        'service_name': {
            'type': 'http|pinecone|sql',
            'url': 'service_url',
            # Additional service-specific config
        }
    }
}
```

## Future Enhancements

- [ ] Support for EPUB and PDF file ingestion
- [ ] Advanced highlight extraction with transformer models
- [ ] Real-time emotion detection from voice
- [ ] Multi-language support
- [ ] Adaptive reading speed based on user engagement
- [ ] Collaborative reading sessions
- [ ] Enhanced RAG with semantic search
- [ ] Integration with more TTS providers
- [ ] Support for additional haptic devices
- [ ] Scent intensity adjustment based on environment

## Testing

Run the test suite:

```bash
cd /home/runner/work/AI-Reader/AI-Reader
python -m pytest holo/orchestrator/tests/
```

Test the orchestrator directly:

```python
python /tmp/test_orchestrator.py
```

## License

See the main project LICENSE file.
