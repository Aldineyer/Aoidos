#!/usr/bin/env python3
"""
narrator.py — Convert a Project Gutenberg ebook into a narrated MP3 audiobook
using the Gemini API (gemini-2.5-flash with audio/mp3 output).

Usage:
    python narrator.py --url "https://www.gutenberg.org/files/11/11-0.txt" --output "alice.mp3"
"""

import argparse
import os
import re
import tempfile
import time

import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydub import AudioSegment

# Load environment variables (.env) for GEMINI_API_KEY
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
    text = response.text

    start_match = GUTENBERG_START_RE.search(text)
    end_match = GUTENBERG_END_RE.search(text)

    if start_match and end_match:
        text = text[start_match.end():end_match.start()]

    return text.strip()


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

        if len(current_chunk) + len(cleaned_p) < max_chars:
            current_chunk += cleaned_p + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = cleaned_p + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def synthesize_audio(chunk: str, client: genai.Client) -> bytes:
    """
    Synthesize speech for a text chunk using the Gemini API.

    Args:
        chunk: Text to synthesize.
        client: An initialized google.genai.Client instance.

    Returns:
        Raw MP3 audio bytes.
    """
    prompt = NARRATOR_PROMPT + chunk

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="audio/mp3"
        ),
    )

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            return part.inline_data.data

    raise RuntimeError("No audio data found in Gemini API response.")


def build_audiobook(
    gutenberg_url: str,
    output_filename: str = "audiobook.mp3",
    max_chars: int = 2000,
) -> None:
    """
    Convert a Project Gutenberg ebook into a narrated audiobook.

    Args:
        gutenberg_url: URL to the raw .txt file on Project Gutenberg.
        output_filename: Name of the output MP3 file.
        max_chars: Maximum characters per text chunk.
    """
    client = genai.Client()

    print("Downloading book content...")
    book_text = fetch_text(gutenberg_url)

    chunks = chunk_text(book_text, max_chars=max_chars)
    print(f"Split text into {len(chunks)} chunks.")

    final_audio = AudioSegment.empty()

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, chunk in enumerate(chunks):
            print(f"Synthesizing chunk {i + 1}/{len(chunks)}...")

            audio_bytes = synthesize_audio(chunk, client)

            temp_chunk_path = os.path.join(tmpdir, f"chunk_{i}.mp3")
            with open(temp_chunk_path, "wb") as f:
                f.write(audio_bytes)

            chunk_segment = AudioSegment.from_file(temp_chunk_path, format="mp3")
            final_audio += chunk_segment

            time.sleep(1)  # Respect rate limits between calls

    final_audio.export(output_filename, format="mp3")
    print(f"Audiobook saved successfully as {output_filename}")


def main() -> None:
    """Parse CLI arguments and run the audiobook pipeline."""
    parser = argparse.ArgumentParser(
        description="Convert a Project Gutenberg ebook into a narrated MP3 audiobook."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="URL to the raw .txt file on Project Gutenberg.",
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
        output_filename=args.output,
        max_chars=args.max_chars,
    )


if __name__ == "__main__":
    main()
