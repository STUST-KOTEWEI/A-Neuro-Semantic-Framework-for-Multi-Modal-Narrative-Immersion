#!/usr/bin/env python3
"""
Demo script for the MultisensoryReader Orchestrator

This script demonstrates how to use the orchestrator to create
an immersive multi-sensory reading experience.
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holo.orchestrator import Orchestrator


async def main():
    """Main demo function"""
    print("=" * 70)
    print("MultisensoryReader Orchestrator Demo")
    print("=" * 70)
    print()
    
    # Configure the orchestrator
    config = {
        'connectors': {
            'textPreprocessor': {
                'type': 'http',
                'url': 'https://your-backend/api/preprocess'
            },
            'vectorDB': {
                'type': 'pinecone',
                'index': 'user_sessions'
            },
            'emotionModelAPI': {
                'type': 'http',
                'url': 'https://your-backend/api/emotion/predict'
            },
            'TTS': {
                'type': 'http',
                'url': 'https://api.elevenlabs.io/v1/text-to-speech'
            },
            'bhapticsSDK': {
                'type': 'http',
                'url': 'https://your-backend/api/device/haptics'
            },
            'aromajoinAPI': {
                'type': 'http',
                'url': 'https://your-backend/api/device/scent'
            },
            'postgres': {
                'type': 'sql',
                'connection': 'postgres://localhost/holo'
            }
        }
    }
    
    # Initialize orchestrator
    print("Initializing orchestrator...")
    orchestrator = Orchestrator(config)
    print("✓ Orchestrator initialized\n")
    
    # Sample narrative text
    narrative = """
    The ancient forest stood silent under the moonlight. A gentle breeze 
    whispered through the towering trees, carrying with it the scent of 
    pine and earth.
    
    She felt a sense of calm wash over her as she walked along the 
    narrow path. The "tranquility" of this moment was precious, a rare 
    gift in her busy life.
    
    Suddenly, a distant sound caught her attention. Her heart began to 
    race with excitement as she realized what it meant - the festival 
    was beginning!
    """
    
    print("Narrative Text:")
    print("-" * 70)
    print(narrative.strip())
    print("-" * 70)
    print()
    
    # 1. Start playback
    print("1. Starting playback...")
    print()
    result = await orchestrator.play(narrative, user_id="demo_user")
    
    print(f"   Playback URL: {result['playback_url']}")
    print(f"   Total Segments: {result['metadata']['total_segments']}")
    print(f"   Detected Emotion: {result['metadata']['emotion']}")
    print(f"   Total Duration: {result['metadata']['total_duration']:.1f}s")
    print()
    
    print("   TTS Settings:")
    tts = result['metadata']['tts_settings']
    print(f"     - Voice: {tts['voice']}")
    print(f"     - Rate: {tts['rate']}x")
    print(f"     - Pitch: {tts['pitch']}x")
    print(f"     - Volume: {tts['volume']}x")
    print()
    
    print("   Device Outputs:")
    haptic_count = len(result['metadata']['haptic_events'])
    scent_count = len(result['metadata']['scent_events'])
    print(f"     - Haptic Events: {haptic_count}")
    print(f"     - Scent Events: {scent_count}")
    
    if scent_count > 0:
        scent = result['metadata']['scent_events'][0]['scent']
        print(f"     - Scent: {scent}")
    print()
    
    # 2. Simulate some playback time
    print("2. Simulating playback...")
    await asyncio.sleep(0.5)
    print("   ✓ Playing...")
    print()
    
    # 3. Pause
    print("3. Pausing playback...")
    pause_result = await orchestrator.pause()
    print(f"   Status: {pause_result['status']}")
    print(f"   Current Segment: {pause_result['current_segment']}")
    print(f"   Is Playing: {pause_result['is_playing']}")
    print()
    
    # 4. Seek to a different segment
    if result['metadata']['total_segments'] > 1:
        print("4. Seeking to segment 1...")
        seek_result = await orchestrator.seek(1)
        print(f"   Status: {seek_result['status']}")
        print(f"   Current Segment: {seek_result['current_segment']}")
        print(f"   Segment Duration: {seek_result['segment_duration']:.1f}s")
        print(f"   Segment Text: {seek_result['segment_text'][:50]}...")
        print()
    
    # 5. Get session summary
    print(f"{'5' if result['metadata']['total_segments'] > 1 else '4'}. Getting session summary...")
    summary_result = await orchestrator.summary()
    print(f"   Total Segments: {summary_result['total_segments']}")
    print(f"   Total Highlights: {summary_result['total_highlights']}")
    print(f"   Current Position: {summary_result['current_position']}")
    print(f"   Detected Emotion: {summary_result['emotion']}")
    print()
    print("   Summary:")
    print(f"   {summary_result['summary'][:150]}...")
    print()
    
    print("=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  - Start the FastAPI backend: cd web/backend && uvicorn main:app --reload")
    print("  - Visit the API docs: http://localhost:8000/docs")
    print("  - Test the endpoints with your own text!")
    print()


if __name__ == '__main__':
    asyncio.run(main())
