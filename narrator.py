#!/usr/bin/env python3
"""
narrator.py — Convert a Project Gutenberg ebook into a narrated MP3 audiobook
using the Gemini TTS API (gemini-3.1-flash-tts-preview with response_format={"type": "audio"} output).

Usage:
    python narrator.py --url "https://www.gutenberg.org/files/11/11-0.txt" --output "alice.mp3"
    python narrator.py --file "assets/default_book.txt" --output "cthulhu.mp3"
    python narrator.py --output "default.mp3"  # uses assets/default_book.txt
"""

import argparse
import base64
import binascii
import logging
import os
import re
import time
from collections.abc import Callable
from typing import TypeVar

import requests
from dotenv import load_dotenv
from pydub import AudioSegment  # type: ignore[import-untyped]

from google import genai

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

# Validate API key is set
if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError(
        "GOOGLE_API_KEY environment variable not set. "
        "Please create a .env file with your API key from https://aistudio.google.com/apikey"
    )

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


@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    exceptions=(genai.errors.APIError, genai.errors.ClientError, requests.RequestException),
)
def synthesize_audio(chunk: str, client: genai.Client) -> bytes:
    """
    Synthesize speech for a text chunk using the Gemini TTS API.

    Args:
        chunk: Text to synthesize.
        client: An initialized google.genai.Client instance.

    Returns:
        Raw PCM audio bytes (16-bit, 24 kHz, mono).
    """
    prompt = NARRATOR_PROMPT + chunk

    interaction = client.interactions.create(
        model="gemini-3.1-flash-tts-preview",
        input=prompt,
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": "Algenib"}
            ]
        }
    )

    # Extract audio data from the interaction (synchronous API returns Interaction object)
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


def build_audiobook(
    gutenberg_url: str | None = None,
    book_file: str | None = None,
    output_filename: str = "audiobook.mp3",
    max_chars: int = 2000,
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
    """
    client = genai.Client()

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

    for i, chunk in enumerate(chunks):
        logger.info(f"Synthesizing chunk {i + 1}/{len(chunks)}...")

        audio_bytes = synthesize_audio(chunk, client)

        if not audio_bytes:
            logger.error(f"Failed to synthesize chunk {i + 1}, skipping...")
            continue

        chunk_segment = AudioSegment(
            # raw audio data (bytes)
            data=audio_bytes,

            # 2 byte (16 bit) samples
            sample_width=2,

            # 24 kHz frame rate (Gemini TTS output)
            frame_rate=24000,

            # mono
            channels=1
        )
        final_audio += chunk_segment

        time.sleep(1)  # Respect rate limits between calls

    final_audio.export(output_filename, format="mp3")
    logger.info(f"Audiobook saved successfully as {output_filename}")


def main() -> None:
    """Parse CLI arguments and run the audiobook pipeline."""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Convert a Project Gutenberg ebook into a narrated MP3 audiobook."
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

    args = parser.parse_args()

    build_audiobook(
        gutenberg_url=args.url,
        book_file=args.file,
        output_filename=args.output,
        max_chars=args.max_chars,
    )


if __name__ == "__main__":
    main()
