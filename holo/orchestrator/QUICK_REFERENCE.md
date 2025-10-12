# MultisensoryReader-Orchestrator Quick Reference

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Orchestrator                            │
│  Entry Points: play, pause, seek, summary                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├─── Coordinates ───┐
                              │                   │
        ┌─────────────────────┼───────────────────┼──────────┐
        │                     │                   │          │
        ▼                     ▼                   ▼          ▼
┌──────────────┐      ┌──────────────┐    ┌──────────────┐ ┌──────────────┐
│ ReaderAgent  │      │EmotionAgent  │    │ DeviceAgent  │ │ MemoryAgent  │
├──────────────┤      ├──────────────┤    ├──────────────┤ ├──────────────┤
│• Segment text│      │• Detect      │    │• Haptics     │ │• Preferences │
│• Extract     │      │  emotion     │    │  patterns    │ │• Bookmarks   │
│  highlights  │      │• Map to TTS  │    │• Scent       │ │• RAG search  │
│• Metadata    │      │  settings    │    │  triggers    │ │              │
└──────────────┘      └──────────────┘    └──────────────┘ └──────────────┘
        │                     │                   │                 │
        └─────────────────────┴───────────────────┴─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │    Connectors     │
                    ├───────────────────┤
                    │• HTTPConnector    │
                    │• PineconeConnector│
                    │• PostgresConnector│
                    └───────────────────┘
```

## Emotion Mappings

| Emotion  | TTS Voice     | Rate | Pitch | Volume | Haptic Pattern | Scent       |
|----------|---------------|------|-------|--------|----------------|-------------|
| happy    | cheerful      | 1.1  | 1.1   | 1.0    | gentle_pulse   | citrus      |
| sad      | melancholic   | 0.9  | 0.9   | 0.8    | slow_wave      | lavender    |
| angry    | intense       | 1.2  | 1.0   | 1.1    | sharp_burst    | peppermint  |
| calm     | soothing      | 0.95 | 1.0   | 0.9    | smooth_wave    | chamomile   |
| excited  | energetic     | 1.15 | 1.05  | 1.0    | rapid_pulse    | eucalyptus  |
| neutral  | normal        | 1.0  | 1.0   | 1.0    | subtle_tap     | vanilla     |

## API Endpoints Quick Reference

### Play
```bash
curl -X POST http://localhost:8000/orchestrator/play \
  -H "Content-Type: application/json" \
  -d '{"text": "Your story here", "user_id": "user123"}'
```

**Response:**
- `playback_url`: Audio file URL
- `metadata`: Segments, emotion, TTS settings, device outputs, duration

### Pause
```bash
curl -X POST http://localhost:8000/orchestrator/pause
```

**Response:**
- `status`: "paused"
- `current_segment`: Current position
- `is_playing`: false

### Seek
```bash
curl -X POST http://localhost:8000/orchestrator/seek \
  -H "Content-Type: application/json" \
  -d '{"segment_index": 2}'
```

**Response:**
- `status`: "seeked" or "error"
- `current_segment`: New position
- `playback_url`: New audio URL
- `segment_text`: Text of the segment
- `segment_duration`: Duration in seconds

### Summary
```bash
curl http://localhost:8000/orchestrator/summary
```

**Response:**
- `summary`: Text summary
- `total_segments`: Total number of segments
- `total_highlights`: Number of highlights
- `emotion`: Detected emotion
- `current_position`: Current segment index
- `is_playing`: Playback status

## Python Usage

```python
from holo.orchestrator import Orchestrator

# Initialize
config = {
    'connectors': {
        'TTS': {'type': 'http', 'url': 'https://api.tts.example.com'},
        # ... other connectors
    }
}
orchestrator = Orchestrator(config)

# Play
result = await orchestrator.play("Your text here", user_id="user123")

# Pause
await orchestrator.pause()

# Seek
await orchestrator.seek(segment_index=2)

# Summary
summary = await orchestrator.summary()
```

## Workflow

```
1. User calls orchestrator.play(text, user_id)
   │
   ├─→ MemoryAgent.getUserPrefs(user_id)
   │
   ├─→ ReaderAgent.segment(text)
   │   └─→ Returns: segments with highlights and metadata
   │
   ├─→ EmotionAgent.predict(text)
   │   └─→ Returns: emotion + TTS settings
   │
   ├─→ DeviceAgent.triggerHaptics(highlights, emotion)
   │   └─→ Returns: haptic_events + scent_events
   │
   └─→ Returns: playback_url + metadata
```

## Testing

```bash
# Run all tests
pytest holo/orchestrator/tests/

# Run specific test file
pytest holo/orchestrator/tests/test_orchestrator.py -v

# Run demo
python examples/orchestrator_demo.py

# Start backend
cd web/backend && uvicorn main:app --reload
```

## Configuration Example

```python
config = {
    'connectors': {
        'textPreprocessor': {
            'type': 'http',
            'url': 'https://api.example.com/preprocess',
            'headers': {'Authorization': 'Bearer TOKEN'}
        },
        'vectorDB': {
            'type': 'pinecone',
            'index': 'user_sessions',
            'api_key': 'YOUR_API_KEY'
        },
        'emotionModelAPI': {
            'type': 'http',
            'url': 'https://api.example.com/emotion'
        },
        'TTS': {
            'type': 'http',
            'url': 'https://api.elevenlabs.io/v1/text-to-speech',
            'headers': {'xi-api-key': 'YOUR_API_KEY'}
        },
        'bhapticsSDK': {
            'type': 'http',
            'url': 'https://api.example.com/haptics'
        },
        'aromajoinAPI': {
            'type': 'http',
            'url': 'https://api.example.com/scent'
        },
        'postgres': {
            'type': 'sql',
            'connection': 'postgres://user:pass@localhost/dbname'
        }
    }
}
```

## Common Tasks

### Add a new emotion
1. Update `EmotionAgent.EMOTION_PRESETS` with TTS settings
2. Update `DeviceAgent.EMOTION_HAPTICS` with haptic pattern
3. Update `DeviceAgent.EMOTION_SCENTS` with scent mapping
4. Add detection keywords to `EmotionAgent._predict_emotion()`

### Add a new connector
1. Create new connector class extending `BaseConnector`
2. Implement `connect()` and `disconnect()` methods
3. Add service-specific methods
4. Update orchestrator connector initialization

### Customize text segmentation
1. Modify `ReaderAgent._segment_text()` method
2. Add new segmentation types (e.g., 'chapter', 'scene')
3. Update highlight extraction logic if needed

## Troubleshooting

### Issue: Import errors
**Solution:** Ensure project root is in Python path:
```python
import sys
sys.path.insert(0, '/path/to/AI-Reader')
```

### Issue: Connector timeout
**Solution:** Increase timeout in connector initialization:
```python
HTTPConnector(config={'url': '...', 'timeout': 60.0})
```

### Issue: No segments generated
**Solution:** Check text format and segmentation type:
- Use '\n\n' for paragraph separation
- Ensure text is not empty
- Try different segmentation_type ('sentence' vs 'paragraph')

### Issue: Emotion not detected correctly
**Solution:** 
- Add more emotion keywords to `EMOTION_PRESETS`
- Provide more context in text
- Consider using emotion model API instead of keyword matching
