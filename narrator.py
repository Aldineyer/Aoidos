#!/usr/bin/env python3
"""
narrator.py — Convert a Project Gutenberg ebook into a narrated MP3 audiobook
using multiple TTS engines (Gemini, Microsoft Edge TTS, Piper).

Usage:
    python narrator.py --url "https://www.gutenberg.org/files/11/11-0.txt" --output "alice.mp3"
    python narrator.py --file "assets/default_book.txt" --output "cthulhu.mp3" --tts-engine edge
    python narrator.py --output "default.mp3" --tts-engine piper --piper-model ./piper/en_US-lessac-medium.onnx
"""

import argparse
import asyncio
import base64
import binascii
import logging
import os
import re
import shutil
import subprocess
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

import requests
from dotenv import load_dotenv
from pydub import AudioSegment  # type: ignore[import-untyped]

from google import genai

if TYPE_CHECKING:
    import edge_tts

# Type variable for retry decorator
T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        exponential_base: Base for exponential backoff.
        exceptions: Exception types to catch and retry.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            delay = base_delay
            last_exception: Exception | None = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay = min(delay * exponential_base, max_delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")

            assert last_exception is not None
            raise last_exception

        return wrapper

    return decorator


logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Narrator system prompt guiding tone and delivery
NARRATOR_PROMPT = (
    "Read the following book excerpt aloud clearly, at a measured pace, "
    "and with expressive tone like an audiobook narrator:\n\n"
)

# Regex patterns for Gutenberg standardized metadata markers
GUTENBERG_START_RE = re.compile(
    r"\*\*\* START OF THIS PROJECT GUTENBERG EBOOK.*?\*\*\*",
    re.IGNORECASE,
)
GUTENBERG_END_RE = re.compile(
    r"\*\*\* END OF THIS PROJECT GUTENBERG EBOOK.*?\*\*\*",
    re.IGNORECASE,
)


# =============================================================================
# TTS Engine Abstraction
# =============================================================================

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

    def cleanup(self) -> None:
        """Clean up resources (e.g., close connections, terminate processes)."""
        pass


class GeminiTTSEngine(TTSEngine):
    """Gemini TTS engine using Google's Gemini API."""

    def __init__(self, voice: str = "Algenib", api_key: str | None = None):
        """
        Initialize Gemini TTS engine.

        Args:
            voice: Voice name (e.g., "Algenib", "Kore", "Puck")
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        self._voice = voice
        self._client = genai.Client(api_key=api_key) if api_key else genai.Client()

    @property
    def sample_rate(self) -> int:
        return 24000

    @property
    def channels(self) -> int:
        return 1

    @property
    def sample_width(self) -> int:
        return 2  # 16-bit

    @retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        exceptions=(genai.errors.APIError, genai.errors.ClientError, requests.RequestException),
    )
    def synthesize(self, text: str) -> bytes:
        """Synthesize speech for a text chunk using the Gemini TTS API."""
        prompt = NARRATOR_PROMPT + text

        interaction = self._client.interactions.create(
            model="gemini-3.1-flash-tts-preview",
            input=prompt,
            response_format={"type": "audio"},
            generation_config={
                "speech_config": [
                    {"voice": self._voice}
                ]
            }
        )

        # Extract audio data from the interaction
        interaction_output_audio = getattr(interaction, "output_audio", None)
        if interaction_output_audio is None or getattr(interaction_output_audio, "data", None) is None:
            logger.warning("No audio data received from Gemini API")
            return b''

        audio_data = interaction_output_audio.data

        # Decode base64 audio data
        try:
            return base64.b64decode(audio_data)
        except (binascii.Error, ValueError) as e:
            logger.error(f"Failed to decode base64 audio data: {e}")
            return b''

    def cleanup(self) -> None:
        """No cleanup needed for Gemini client."""
        pass


class EdgeTTSEngine(TTSEngine):
    """Microsoft Edge TTS engine using edge-tts library."""

    def __init__(self, voice: str = "en-US-AvaNeural"):
        """
        Initialize Edge TTS engine.

        Args:
            voice: Edge TTS voice name (e.g., "en-US-AvaNeural", "en-US-AndrewNeural",
                   "sv-SE-SofieNeural", "sv-SE-MattiasNeural")
        """
        self._voice = voice
        self._communicate = None

    @property
    def sample_rate(self) -> int:
        return 24000

    @property
    def channels(self) -> int:
        return 1

    @property
    def sample_width(self) -> int:
        return 2  # 16-bit

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Edge TTS."""
        try:
            import edge_tts
        except ImportError:
            raise RuntimeError(
                "edge-tts not installed. Install with: pip install edge-tts"
            )

        # Run async synthesis in a new event loop
        return asyncio.run(self._synthesize_async(text, edge_tts))

    async def _synthesize_async(self, text: str, edge_tts_module) -> bytes:
        """Async synthesis using edge-tts streaming."""
        communicate = edge_tts_module.Communicate(text, self._voice)
        audio_chunks = []

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        # Edge TTS returns MP3 data, need to decode to PCM
        if not audio_chunks:
            logger.warning("No audio data received from Edge TTS")
            return b''

        mp3_data = b"".join(audio_chunks)

        # Decode MP3 to raw PCM using pydub
        from io import BytesIO
        audio_segment = AudioSegment.from_mp3(BytesIO(mp3_data))
        # Ensure correct format
        audio_segment = audio_segment.set_frame_rate(self.sample_rate).set_channels(self.channels).set_sample_width(self.sample_width)
        return audio_segment.raw_data

    def cleanup(self) -> None:
        """No persistent resources to clean up."""
        pass


class PiperTTSEngine(TTSEngine):
    """Piper TTS engine using local Piper binary via subprocess."""

    def __init__(
        self,
        model_path: str,
        exe_path: str | None = None,
        sample_rate: int = 24000,
    ):
        """
        Initialize Piper TTS engine.

        Args:
            model_path: Path to Piper .onnx model file
            exe_path: Path to Piper executable (auto-detected if None)
            sample_rate: Expected sample rate of the model (default 24000)
        """
        self._model_path = model_path
        self._sample_rate = sample_rate

        # Auto-detect Piper executable
        if exe_path is None:
            exe_path = self._find_piper_exe()
        self._exe_path = exe_path

        # Validate model files exist
        if not os.path.exists(self._model_path):
            raise FileNotFoundError(f"Piper model not found: {self._model_path}")
        config_path = self._model_path + ".json"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Piper config not found: {config_path}")

        if not os.path.exists(self._exe_path):
            raise FileNotFoundError(f"Piper executable not found: {self._exe_path}")

    def _find_piper_exe(self) -> str:
        """Find Piper executable in PATH or common locations."""
        # Check PATH first
        exe_name = "piper.exe" if os.name == "nt" else "piper"
        found = shutil.which(exe_name)
        if found:
            return found

        # Check common local locations
        local_paths = [
            "./piper/piper.exe" if os.name == "nt" else "./piper/piper",
            "./piper.exe" if os.name == "nt" else "./piper",
        ]
        for path in local_paths:
            if os.path.exists(path):
                return os.path.abspath(path)

        # Default fallback
        return exe_name

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def channels(self) -> int:
        return 1

    @property
    def sample_width(self) -> int:
        return 2  # 16-bit

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech using Piper CLI."""
        # Run Piper as subprocess, output raw PCM to stdout
        cmd = [
            self._exe_path,
            "--model", self._model_path,
            "--output_raw",
        ]

        logger.debug(f"Running Piper: {' '.join(cmd)}")

        process = subprocess.run(
            cmd,
            input=text.encode('utf-8'),
            capture_output=True,
            check=False,
        )

        if process.returncode != 0:
            stderr = process.stderr.decode('utf-8', errors='replace') if process.stderr else "Unknown error"
            logger.error(f"Piper synthesis failed (exit code {process.returncode}): {stderr}")
            return b''

        return process.stdout

    def cleanup(self) -> None:
        """No persistent resources to clean up."""
        pass


def create_tts_engine(
    engine_name: str,
    **kwargs
) -> TTSEngine:
    """
    Factory function to create a TTS engine instance.

    Args:
        engine_name: Engine name ("gemini", "edge", "piper")
        **kwargs: Engine-specific arguments

    Returns:
        TTSEngine instance

    Raises:
        ValueError: If engine_name is unknown
    """
    engine_name = engine_name.lower()

    if engine_name == "gemini":
        voice = kwargs.get("voice", "Algenib")
        api_key = kwargs.get("api_key")
        return GeminiTTSEngine(voice=voice, api_key=api_key)

    elif engine_name == "edge":
        voice = kwargs.get("voice", "en-US-AvaNeural")
        return EdgeTTSEngine(voice=voice)

    elif engine_name == "piper":
        model_path = kwargs.get("model_path")
        if not model_path:
            raise ValueError("Piper engine requires --piper-model argument")
        exe_path = kwargs.get("exe_path")
        sample_rate = kwargs.get("sample_rate", 24000)
        return PiperTTSEngine(model_path=model_path, exe_path=exe_path, sample_rate=sample_rate)

    else:
        raise ValueError(f"Unknown TTS engine: {engine_name}. Choose from: gemini, edge, piper")


# =============================================================================
# Text Processing Functions
# =============================================================================

def clean_gutenberg_text(text: str) -> str:
    """
    Strip Project Gutenberg standardized metadata headers/footers.

    Args:
        text: Raw ebook text that may contain START/END markers.

    Returns:
        Cleaned book text between the START and END markers.
    """
    start_match = GUTENBERG_START_RE.search(text)
    end_match = GUTENBERG_END_RE.search(text)

    if start_match and end_match:
        text = text[start_match.end():end_match.start()]

    return text.strip()


def fetch_text(url: str) -> str:
    """
    Download a Project Gutenberg ebook and strip standardized metadata
    headers/footers.

    Args:
        url: URL to the raw .txt file on Project Gutenberg.

    Returns:
        Cleaned book text between the START and END markers.
    """
    response = requests.get(url)
    response.raise_for_status()
    return clean_gutenberg_text(response.text)


def fetch_text_from_file(file_path: str) -> str:
    """
    Read a local text file and strip Project Gutenberg metadata
    headers/footers.

    Args:
        file_path: Path to a local .txt file.

    Returns:
        Cleaned book text between the START and END markers.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return clean_gutenberg_text(text)


def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    """
    Split text into paragraph-bounded chunks of roughly max_chars.

    Args:
        text: The cleaned book text.
        max_chars: Maximum characters per chunk.

    Returns:
        List of text chunks.
    """
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        cleaned_p = paragraph.replace("\n", " ").strip()
        if not cleaned_p:
            continue

        # If a single paragraph exceeds max_chars, split it into sentences
        if len(cleaned_p) > max_chars:
            # Flush current chunk first
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            # Split long paragraph by sentences
            sentences = re.split(r"(?<=[.!?])\s+", cleaned_p)
            sentence_chunk = ""
            for sentence in sentences:
                if len(sentence_chunk) + len(sentence) + 1 <= max_chars:
                    sentence_chunk += sentence + " "
                else:
                    if sentence_chunk:
                        chunks.append(sentence_chunk.strip())
                    sentence_chunk = sentence + " "
            if sentence_chunk:
                chunks.append(sentence_chunk.strip())
            continue

        if len(current_chunk) + len(cleaned_p) <= max_chars:
            current_chunk += cleaned_p + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = cleaned_p + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# =============================================================================
# Audiobook Building
# =============================================================================

def build_audiobook(
    gutenberg_url: str | None = None,
    book_file: str | None = None,
    output_filename: str = "audiobook.mp3",
    max_chars: int = 2000,
    tts_engine: TTSEngine | None = None,
) -> None:
    """
    Convert a Project Gutenberg ebook into a narrated audiobook.

    Either *gutenberg_url* or *book_file* may be specified.  If neither is
    given, the default book at ``assets/default_book.txt`` is used.

    Args:
        gutenberg_url: URL to the raw .txt file on Project Gutenberg.
        book_file: Path to a local .txt file to narrate.
        output_filename: Name of the output MP3 file.
        max_chars: Maximum characters per text chunk.
        tts_engine: TTS engine instance (created via create_tts_engine if None)
    """
    if tts_engine is None:
        tts_engine = create_tts_engine("gemini")

    if gutenberg_url:
        logger.info("Downloading book content...")
        book_text = fetch_text(gutenberg_url)
    elif book_file:
        logger.info(f"Reading book from file: {book_file}...")
        book_text = fetch_text_from_file(book_file)
    else:
        default_file = "assets/default_book.txt"
        logger.info(f"No source specified, using default file: {default_file}...")
        book_text = fetch_text_from_file(default_file)

    chunks = chunk_text(book_text, max_chars=max_chars)
    logger.info(f"Split text into {len(chunks)} chunks.")

    final_audio = AudioSegment.empty()

    try:
        for i, chunk in enumerate(chunks):
            logger.info(f"Synthesizing chunk {i + 1}/{len(chunks)}...")

            audio_bytes = tts_engine.synthesize(chunk)

            if not audio_bytes:
                logger.error(f"Failed to synthesize chunk {i + 1}, skipping...")
                continue

            chunk_segment = AudioSegment(
                data=audio_bytes,
                sample_width=tts_engine.sample_width,
                frame_rate=tts_engine.sample_rate,
                channels=tts_engine.channels,
            )
            final_audio += chunk_segment

            # Rate limiting for cloud APIs
            if isinstance(tts_engine, GeminiTTSEngine):
                time.sleep(1)
            elif isinstance(tts_engine, EdgeTTSEngine):
                time.sleep(0.5)  # Edge TTS is faster, shorter delay

    finally:
        tts_engine.cleanup()

    final_audio.export(output_filename, format="mp3")
    logger.info(f"Audiobook saved successfully as {output_filename}")


# =============================================================================
# CLI
# =============================================================================

def main() -> None:
    """Parse CLI arguments and run the audiobook pipeline."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Convert a Project Gutenberg ebook into a narrated MP3 audiobook using multiple TTS engines."
    )
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--url",
        help="URL to the raw .txt file on Project Gutenberg.",
    )
    source_group.add_argument(
        "--file",
        help="Path to a local .txt file to narrate.",
    )
    parser.add_argument(
        "--output",
        default="audiobook.mp3",
        help="Output MP3 filename (default: audiobook.mp3).",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=2000,
        help="Maximum characters per text chunk (default: 2000).",
    )

    # TTS Engine selection
    parser.add_argument(
        "--tts-engine",
        choices=["gemini", "edge", "piper"],
        default="gemini",
        help="TTS engine to use (default: gemini).",
    )

    # Engine-specific arguments
    parser.add_argument(
        "--voice",
        help="Voice name for the selected engine (default varies by engine).",
    )
    parser.add_argument(
        "--piper-model",
        help="Path to Piper .onnx model file (required for piper engine).",
    )
    parser.add_argument(
        "--piper-exe",
        help="Path to Piper executable (auto-detected if not specified).",
    )
    parser.add_argument(
        "--piper-sample-rate",
        type=int,
        default=24000,
        help="Sample rate of Piper model (default: 24000).",
    )

    args = parser.parse_args()

    # Validate engine-specific requirements
    if args.tts_engine == "piper" and not args.piper_model:
        parser.error("--piper-model is required when using --tts-engine piper")

    if args.tts_engine == "gemini" and not os.getenv("GOOGLE_API_KEY"):
        parser.error("GOOGLE_API_KEY environment variable not set. Please create a .env file with your API key from https://aistudio.google.com/apikey")

    # Build engine kwargs
    engine_kwargs = {}
    if args.voice:
        engine_kwargs["voice"] = args.voice
    if args.piper_model:
        engine_kwargs["model_path"] = args.piper_model
    if args.piper_exe:
        engine_kwargs["exe_path"] = args.piper_exe
    if args.piper_sample_rate:
        engine_kwargs["sample_rate"] = args.piper_sample_rate

    # Create TTS engine
    try:
        tts_engine = create_tts_engine(args.tts_engine, **engine_kwargs)
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        parser.error(str(e))

    # Run the pipeline
    build_audiobook(
        gutenberg_url=args.url,
        book_file=args.file,
        output_filename=args.output,
        max_chars=args.max_chars,
        tts_engine=tts_engine,
    )


if __name__ == "__main__":
    main()
