# Plan: Add Microsoft Edge TTS and Piper as TTS Engine Options

## Objective
Extend the existing `narrator.py` to support multiple TTS engines:
1. **Gemini TTS** (current, default)
2. **Microsoft Edge TTS** (cloud-based, free, high quality)
3. **Piper** (local/offline, fast, open-source)

## Architecture Overview

### TTS Engine Abstraction
Create a base class/interface for TTS engines with a common interface:

```python
class TTSEngine(ABC):
    """Abstract base class for TTS engines."""
    
    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """Output sample rate in Hz."""
        pass
    
    @property
    @abstractmethod
    def channels(self) -> int:
        """Number of audio channels."""
        pass
    
    @property
    @abstractmethod
    def sample_width(self) -> int:
        """Sample width in bytes (e.g., 2 for 16-bit)."""
        pass
    
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Synthesize text to raw PCM audio bytes."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources (e.g., close connections, terminate processes)."""
        pass
```

### Engine Implementations

#### 1. GeminiTTSEngine (existing, refactored)
- Uses `google-genai` SDK
- Output: 24 kHz, 16-bit, mono PCM
- Requires `GOOGLE_API_KEY` environment variable

#### 2. EdgeTTSEngine (new)
- Uses `edge-tts` Python library
- Output: 24 kHz, 16-bit, mono PCM (MP3 decoded)
- No API key required
- Voice options: `en-US-AvaNeural`, `en-US-AndrewNeural`, etc.
- Supports streaming via WebSocket

#### 3. PiperTTSEngine (new)
- Uses Piper CLI binary via subprocess
- Output: Sample rate depends on model (typically 22050 or 24000 Hz)
- Requires local model files (`.onnx` + `.onnx.json`)
- Fully offline
- Voice options: Many voices available from Piper repository

## Dependencies to Add

```toml
[project.optional-dependencies]
edge-tts = ["edge-tts>=6.1.0", "pydub>=0.25.1"]
piper = ["piper-tts>=1.2.0"]  # or use subprocess approach
all = ["edge-tts>=6.1.0", "piper-tts>=1.2.0"]
```

Note: For Piper, the subprocess approach (calling the binary) is more robust on Windows than Python bindings.

## CLI Changes

Add `--tts-engine` argument:
```python
parser.add_argument(
    "--tts-engine",
    choices=["gemini", "edge", "piper"],
    default="gemini",
    help="TTS engine to use (default: gemini)."
)
```

Add engine-specific arguments:
- `--edge-voice` for Edge TTS voice selection
- `--piper-model` and `--piper-exe` for Piper model/executable paths

## Configuration

Engine-specific configuration via environment variables or CLI:
- Edge TTS: `EDGE_TTS_VOICE` (default: `en-US-AvaNeural`)
- Piper: `PIPER_MODEL_PATH`, `PIPER_EXE_PATH`

## Implementation Steps

1. **Add dependencies** to `pyproject.toml`
2. **Create TTS engine base class** in `narrator.py` (or separate module)
3. **Implement EdgeTTSEngine** using `edge-tts` library
4. **Implement PiperTTSEngine** using subprocess approach
5. **Refactor Gemini TTS** into `GeminiTTSEngine` class
6. **Add factory function** to create engine from CLI args
7. **Update `build_audiobook`** to use selected engine
8. **Add CLI arguments** for engine selection and engine-specific options
9. **Update README.md** with new engine documentation
10. **Test all three engines**

## Audio Format Handling

Each engine may output different audio formats:
- **Gemini**: Raw PCM (24 kHz, 16-bit, mono)
- **Edge TTS**: MP3 stream (needs decoding to PCM)
- **Piper**: Raw PCM (sample rate varies by model)

The `TTSEngine` base class properties (`sample_rate`, `channels`, `sample_width`) allow `build_audiobook` to correctly create `AudioSegment` objects regardless of engine.

## Fallback Strategy (Future Enhancement)

While not in initial scope, the architecture supports fallback:
```python
def create_engine_with_fallback(primary: str, fallback: str) -> TTSEngine:
    """Create engine that falls back to another on failure."""
    pass
```

## Voice Options

### Edge TTS Voices (popular ones)
- `en-US-AvaNeural` (female, default)
- `en-US-AndrewNeural` (male)
- `en-US-BrianNeural` (male)
- `en-US-EmmaNeural` (female)
- `sv-SE-SofieNeural` (Swedish female)
- `sv-SE-MattiasNeural` (Swedish male)

### Piper Voices (examples)
- `en_US-lessac-medium` (English, medium quality)
- `en_US-amy-medium` (English, female)
- `sv_SE-ilsa-medium` (Swedish, female)
- Many more at https://github.com/rhasspy/piper/blob/master/VOICES.md

## Testing Plan

1. Test Gemini TTS (existing functionality)
2. Test Edge TTS with various voices
3. Test Piper with downloaded models
4. Verify audio output quality and format consistency
5. Test CLI argument parsing for all engines
6. Test error handling for missing dependencies/models