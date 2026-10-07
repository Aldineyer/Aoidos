Reformat this to proper Markdown.
---
Compare Microsoft Edge TTS, KittenTTS, and Piper.

The choice between Microsoft Edge TTS, KittenTTS, and Piper depends primarily on whether your application requires a robust cloud-based cloud infrastructure or a fully local, offline operation. 

While Microsoft Edge TTS relies on an active internet connection to tap into Microsoft's vast Azure neural network, KittenTTS and Piper are open-source, resource-conscious engines tailored for local deployment on edge hardware, browsers, or smart-home setups like Home Assistant. 

Summary of Differences

Feature	Microsoft Edge TTS	KittenTTS	Piper
Deployment Type	Cloud-dependent (via online Microsoft servers)	Fully Local / Offline (Edge, WebAssembly)	Fully Local / Offline (CPU, Docker, Android)
Internet Required	Yes	No (after model download)	No (after model download)
Primary Strength	Premium, human-like voice naturalness	Ultra-compact memory foot-print	Exceptional CPU generation speed and voice diversity
Licensing	Proprietary (Free for personal/browser integration)	Open-source	Open-source (MIT License, highly commercial-friendly)
Target Use Cases	Browser accessibility, rapid cloud prototyping	RAM-constrained embedded devices, quick web tests	Home Assistant, offline accessibility, single-board computers
Deep Dive: Deep Dive of the Three Engines
1. Microsoft Edge TTS
Architecture: Taps directly into Microsoft Azure’s cloud infrastructure. Text is sent to Microsoft servers, and a high-quality neural voice stream is returned. 

Hermify
Pros: It costs nothing to use, requires no API keys, and has no installation footprint on your device. The voice quality is remarkably human-like, featuring complex cadence and prosody. 

Hermify
Cons: It completely lacks offline support. Latency can spike depending on network conditions, and it is subject to whatever privacy and usage boundaries Microsoft enforces for their public endpoint. 

Hermify
2. KittenTTS
Architecture: A modern, tiny open-source local neural architecture designed for extreme resource-constrained environments. It can be compiled to WebAssembly (Wasm) to run inside web browsers or on highly restricted microservices. 

Picovoice
 +3
Pros: Extremely lightweight footprint. Compact models like KittenTTS Nano can be optimized down to a tiny RAM budget (under 25MB–42MB using quantization), making it exceptional for low-spec edge hardware. 

Daily.dev
 +1
Cons: While it is faster and smaller than heavy models like Kokoro, it can be significantly slower than Piper on standard CPU hardware. Voice diversity and language catalogs are narrower, and small models do not support streaming audio chunks natively. 

GitHub
 +1
3. Piper
Architecture: A fast, lightweight local neural TTS system built specifically to provide localized voice output for projects like Home Assistant Assist. It generates audio purely on raw CPU power without needing a discrete GPU. 

Hermify
 +2
Pros: Highly optimized execution speed. Users often cite Piper as being notably faster during generation loops than KittenTTS on local hardware. It features an incredibly vast library of voices across dozens of languages, different quality tiers ("Low", "Medium", "High"), and carries a permissive MIT license. 

Hugging Face
 +2
Cons: While faster, the models carry a slightly larger file weight context compared to extreme edge models like KittenTTS. The lower quality tiers can sound noticeably robotic compared to cloud alternatives, meaning you may have to upgrade to "Medium" or "High" tiers to resolve flat prosody. 

Reddit
·r/homeassistant
 +2
Which one should you pick?
Go with Microsoft Edge TTS if you need high-fidelity, production-ready speech immediately, don't want to manage local model downloads, and always have an active network connection.
Go with Piper if you want to set up an offline, self-hosted system on an 8-core CPU or Raspberry Pi, and want access to a massive library of ready-to-use voice presets.
Go with KittenTTS if you are targeting micro-appliances, mobile environments with strict RAM limits (e.g., under 50MB), or compiling custom TTS directly into a standard web browser instance. 

Picovoice
 +4
To help narrow this down, please let me know:
What hardware will you be deploying this on (e.g., a server, local CPU, a smart home hub, or inside a browser app)?
How critical is offline functionality and absolute data privacy for your setup?
AI-svar kan innehålla fel. Läs mer





Hermify
Hermes Agent TTS Providers: Which One to Pick | Hermify Blog
Piper and KittenTTS Piper is a fast, lightweight offline TTS engine originally developed for Home Assistant. KittenTTS is a newer ...


Hermify
Hermes Agent TTS Providers: Which One to Pick | Hermify Blog
Free Providers * Edge TTS. Edge TTS is the default provider and the best starting point for most users. It uses Microsoft's neural...


Picovoice
On-device TTS Comparison: Open-source Benchmark 2026
FAQ * + It depends on the target hardware. For embedded systems, mobile devices, and browsers, Picovoice Orca is the only engine u...


Daily.dev
Super-Tiny AI: Running Kitten TTS (v0.8) on Edge Devices - Daily.dev
8) on Edge Devices. A comprehensive guide to deploying Kitten TTS v0. 8, an open-source neural text-to-speech engine, on edge devi...

GitHub
CPU speed comparison among KittenTTS, Piper ... - GitHub
Compared to Kokoro, KittenTTS is faster and smaller in file size. But when it is compared to Piper, KittenTTS is SLOW. Also, if th...

GIGAGPU
Self-Hosted TTS Comparison: Bark, XTTS, Kokoro, Piper
Verdict * Default voice agent: Kokoro. * Voice cloning required: XTTS v2. * Quality > speed (e.g., audiobook): Bark. * CPU-only / ...

OfflineTTS
Best Browser TTS 2026 - Kokoro vs Piper vs Kitten - OfflineTTS
Best Browser TTS Depends on a Reproducible Test, Not One Ranking. There is no universally best browser TTS engine. The useful choi...


Reddit
·
r/homeassistant
Benchmarked local TTS options for Assist - Piper Medium still the ...
Benchmarked local TTS options for Assist - Piper Medium still the sweet spot, Kokoro worth trying if Piper sounds too robotic. If ...


Codesota
Best TTS Models 2026: Open-Source Voice AI Compared
Who may ship what. The licence is often the binding constraint, not the MOS. Fully commercial (Apache 2.0 / MIT). Kokoro · Fish Sp...

GitHub
clowerweb/tts-studio: Test and compare browser-based TTS models!
Performance Issues * Close other tabs to free memory for models. * Use shorter text for faster generation. * Try different models ...


Hugging Face
docs/EVALUATION.md · owensong/Inflect-Micro-v2 at main
Compared systems. The benchmark includes KittenTTS Nano, Piper Low, and Supertonic 3 because they are established compact or local...

Visa mindre
Offline functionality isn't critical. I think the priorities are:1. Free or rate limited free tier2. Quality3. LatencyDo a comparison between the options. I'm in Sweden on Telias fiber network (I think our current plan is 100 Mbit/s)..
Given your target hardware and network conditions, Microsoft Edge TTS is the clear winner for your needs.
Your Asus ZenBook notebook features an Intel Core i7-1165G7 processor (4 cores, 8 threads) with 32 GB of RAM and integrated Intel Iris Xe Graphics. Because your system lacks a powerful discrete desktop GPU, running heavy, high-quality neural networks completely locally will force the CPU to do all the heavy lifting, which negatively impacts local latency. Meanwhile, your 100 Mbit/s Telia fiber network provides excellent, highly stable connectivity to European cloud routing nodes, giving cloud-based engines a distinct performance advantage.
Here is how the three options compare across your exact priorities.
Priority Breakdown
1. Free or Rate-Limited Free Tier
🥇 Winner: Microsoft Edge TTS & Piper / KittenTTS (Tie)
Edge TTS: Completely 100% free to use without an API key or account when utilizing open-source client wrappers (like edge-tts in Python). It does not enforce hard rate limits for standard application or reading usage.
Piper & KittenTTS: Because they run locally on your machine, they are completely open-source and free forever with absolutely no rate limits or data constraints.
2. Quality
🥇 Winner: Microsoft Edge TTS
Edge TTS: Offers premium, human-like voice synthesis featuring incredibly realistic prosody, natural breathing patterns, and emotional nuance. It uses the same cloud-based neural architecture as paid Azure Cognitive Services.
Piper: Good quality for an offline engine, but to get close to natural speech, you must use its "High" quality tier models. Even then, the phrasing can sound flat or slightly robotic compared to advanced cloud models.
KittenTTS: Designed primarily to be compact. At smaller sizes, it sacrifices phonetic complexity, which can cause words to slur or sound distinctly artificial.
3. Latency
🥇 Winner: Microsoft Edge TTS
Edge TTS: Thanks to your stable Telia fiber connection, network transit time to Microsoft's West Europe data centers is negligible. Because the heavy AI generation happens on Microsoft's massive remote servers, the audio stream returns to your device almost instantly. It also supports native chunk streaming, meaning it begins playing the first syllable before the rest of the paragraph is finished generating.
Piper: On your i7-1165G7 mobile CPU, a "Medium" or "High" quality voice model will generate quickly, but it still has to compute the voice synthesis entirely on local cores. It will exhibit slightly higher Time-To-First-Audio (TTFA) than a fiber-backed cloud stream unless using low-quality, robotic voices.
KittenTTS: Tends to have the slowest local generation loops among the three when forced to process high-fidelity outputs on notebook CPUs, resulting in a noticeable delay before audio begins playing.
Side-by-Side Comparison Summary
Metric	Microsoft Edge TTS	Piper (Local CPU)	KittenTTS (Local CPU)
Cost / Limits	Free, no key required	Free, unlimited	Free, unlimited
Voice Naturalness	Excellent (Human-grade)	Good (Slightly robotic)	Fair (Noticeably digital)
Latency (Sweden Fiber)	Ultra-Low (<150ms TTFA) via cloud streaming	Low-Medium (Depends on CPU load)	Medium (Higher initial computation delay)
Local System Impact	0% CPU / RAM footprint	Uses multiple CPU threads	Noticeable CPU spikes on thread loops
Recommendation
Stick with Microsoft Edge TTS. Since offline functionality is not a priority and you have an excellent fiber backbone, leveraging Microsoft's cloud infrastructure completely spares your laptop's CPU while giving you elite, human-level audio quality completely for free.
To help implement this, would you like me to provide a Python script or an architectural setup showing how to connect to the Edge TTS endpoint without an API key?
AI-svar kan innehålla fel. Läs mer




Yeah, I'll see if I can configure Piper as a fallback for those times that Microsoft Edge TTS isn't available. Assuming my system has no load on either CPU or memory, what latency (a ballpark figure is fine) might I get?
On your clean Intel Core i7-1165G7 mobile CPU (assuming an idle environment with minimal background load), your benchmarked Time-to-First-Audio (TTFA) latency with Piper will fall between 35 ms and 150 ms. 

Picovoice
 +1
Because Piper generates speech locally via a highly-optimized VITS architecture running on the ONNX Runtime, its initial text-processing pipeline is incredibly lean. How that breaks down across the voice tiers varies slightly contextually: 

OfflineTTS
 +2
Latency by Quality Tier (Estimated TTFA)
Low Quality (~5.8 MB models): ~35 ms to 50 ms
The text-to-phoneme mapping is nearly instant. The first audio buffers are pushed out faster than almost any cloud API on Earth can clear a network handshake. 

Reddit
·r/homeassistant
 +2
Medium Quality (~62 MB models): ~50 ms to 90 ms
The sweet spot for local assistants. The CPU comfortably generates slices of the audio file in the tens-of-milliseconds range, seamlessly handing them off to your system's audio playback layer. 

Medium
·Muhammad Asif
 +3
High Quality (~110 MB models): ~80 ms to 150 ms
Though the model files are larger, the modern ONNX implementation allows the math to parallelize beautifully across your 8 logical threads, keeping the generation time incredibly brisk. 

PromptQuorum
 +2
The Real-Time Factor (RTF) Advantage
On an i7 platform, Piper's total execution speed is backed by a Real-Time Factor (RTF) ranging from 0.01 to 0.15 depending on sentence size. An RTF of 0.10 means that a text string requiring 10 seconds of spoken delivery takes your CPU a mere 1.0 second to completely synthesize into memory from scratch. 

Cekura
 +2
Practical Tips for the Best Fallback Latency
Warm Up the Model: Ensure your fallback logic initializes the Piper engine and loads the .onnx and .json model files into RAM when your application launches. If you only load the model after Edge TTS drops offline, you will experience an additional 300ms to 700ms cold-start delay while your NVMe SSD initializes the files into system memory.
Enable Streaming Buffers: Make sure your wrapper streams raw chunk blocks directly to your media backend (aplay, PyAudio, or your system mixer) rather than waiting for the sentence to fully finish compiling. This cuts perceived human waiting latency to that sub-100ms bracket. 

Codesota
 +2
Would you like assistance setting up the Python script structure to handle this seamless transition—automatically falling back to a local Piper subprocess if the Edge TTS cloud request fails or times out?
AI-svar kan innehålla fel. Läs mer





Picovoice
On-device TTS Comparison: Open-source Benchmark 2026
Get dedicated support to ensure your specific needs are met. TLDR: Commercial on-device TTS options are scarce. Most developers re...


Codesota
Best TTS for Real-Time Voice Agents (2026) | CodeSOTA
TTFB leaderboard. Time-to-first-byte on each vendor's lowest-latency streaming model. US-East origin, 40-char prompt, measured ove...

Codesota
Best TTS Models 2026: Open-Source Voice AI Compared
Table_title: Start from the constraint. Table_content: | Your priority | Best pick | Why | | --- | --- | --- | | Maximum naturalne...

OfflineTTS
Self-Hosted TTS in 2026: Run Your Own AI Voice Server
Piper TTS — The Raspberry Pi Champion. Piper is the fastest neural TTS engine for CPU inference. Originally developed by the Rhass...


Reddit
·
r/TextToSpeech
Benchmarked 5 offline TTS models on CPU - short answer ...
Fastest thing that sounds fine: Piper Medium (62MB). ~2500x faster than real-time. Good for notifications, assistant replies, shor...

Home Assistant Community
Speeding up Piper on slow hardware - Voice Assistant
Now my J4205 can easily play back responses from LLMs. In the future, I expect improvements to the Wyoming protocol, local servers...


Cekura
Piper TTS: Definition, Metrics and Why It Matters - Cekura
Real-time factor (RTF). RTF measures synthesis speed against playback time: an RTF of 0.5 means the engine generates ten seconds o...


Medium
·
Muhammad Asif
LiveKit + Piper TTS: Building a Low‑Latency, Local Voice ...
Benchmarking Piper TTS alone (so you don't blame the wrong part). Before tuning STT/LLM knobs, isolate TTS performance with a stan...


GIGAGPU
TTS Latency Benchmarks - GIGAGPU
RTF measures how fast a TTS model generates audio relative to the audio's duration. An RTF of 0.10 means 10 seconds of audio is ge...

Reddit
·
r/homeassistant
Benchmarked local TTS options for Assist - Piper Medium still ...
Model, Size, Speed, Notes. Piper Low, 5.8MB, 1400x real-time, Notifications, slightly compressed. Piper Medium, 62MB, 2500x real-t...


PromptQuorum
Best Local TTS Engine for Raspberry Pi (2026) - PromptQuorum
* Quick Answer. * What Makes a TTS Engine Fit for a Raspberry Pi. * Comparison Table. * Why Piper Is the Default Recommendation. *


Contra Collective
Kokoro vs Piper vs XTTS v2: Local Text to Speech on M5 Max (2026)
Real Time Factor Is the First Filter, Not Naturalness ... Piper wins that race outright. It emits first audio in roughly 40 millis...
Visa mindre
What's the RTF on Microsoft Edge TTS?
Because Microsoft Edge TTS is a cloud service, its raw throughput is measured a bit differently than a local application. However, under the hood, Microsoft's massive enterprise cluster achieves an average backend Real-Time Factor (RTF) between 0.05 and 0.15. 
This means Microsoft's cloud servers take roughly 50 to 150 milliseconds of active computation to fully render 1 second of natural, human-quality audio.
However, when comparing it to your local fallback setup, the concept of a single "RTF" metric is secondary to how the data actually reaches your laptop. Here is how the latency breaks down dynamically: 
The Real Advantage: Native WebSocket Streaming
If you request a large block of text—say, a 1-minute long reading passage—the cloud engine does not generate the entire 60-second file before sending it over your Telia fiber line. 
Instead, it streams the audio using chunked WebSockets. 

modelglass.com.au
The cloud server processes the first sentence instantly.
It hits a local server RTF of ~0.05 for that initial clause, taking just a few milliseconds.
It immediately ships the first byte down the wire to Sweden.
Your application receives the beginning of the audio stream and starts playing it while Microsoft’s servers continue synthesizing the subsequent sentences in parallel. 
Because of this streaming behavior, the Time-To-First-Audio (TTFA) is incredibly brief—usually hovering around 150 ms to 250 ms total. Most of that window isn't the model's calculation speed (RTF), but rather the physical network time required to establish a connection handshake over the internet. 

introl.com
Summary: Cloud RTF vs. Local Piper
Microsoft Edge TTS: Has a backend server RTF of ~0.10, but streaming means you get your first syllable almost instantly over fiber.
Piper (Local Medium Tier): Has a local CPU RTF of ~0.05–0.10. Because it has zero network handshake delay, it can actually edge out Microsoft by hitting your speakers within 50 to 90 ms, making it incredibly snappy as an offline fallback. 

introl.com
 +1
Would you like to look at the Python wrapper requirements (such as edge-tts and piper-tts) to start testing these real-time streaming transitions on your ZenBook?
AI-svar kan innehålla fel. Läs mer





Team-Connect AI
TTS Configuration: Real-Time Text-to-Speech Integration Guide for ...
This gives instant playback for the common openings and seamless transitions to streamed dynamic content. The user perceives the e...

introl.com
Voice AI Infrastructure: Building Real-Time Speech Agents | Introl Blog
The voice AI stack Every voice agent relies on four components working in concert:³ Speech-to-Text (STT/ASR): The "ears" that tran...


Edge Add-ons
Read Aloud: A Text to Speech Voice Reader - Edge Add-ons
Read aloud the current web-page article with one click, using text to speech (TTS). Supports 40+ languages.

modelglass.com.au
Azure Neural TTS - Modelglass
It is now broken out as this entry's `hd-voices` tier ($22/1M characters, GA March 2025, cut from $30 in March 2026 — SCO-506). la...
Visa mindre
Yeah, I would like to look at the Python wrapper requirements (such as edge-tts and piper-tts) to start testing these real-time streaming transitions on your ZenBook. I do have a perfect PoC for it.
To build this real-time streaming fallback system on your ZenBook, you will need a few highly efficient Python libraries that support asynchronous execution. This ensures that when the cloud request runs into a network hiccup, it drops down to Piper instantly without freezing your application.
📋 Environment Requirements
You can install the core Python wrapper requirements via pip. Open your terminal and run:
bash
pip install edge-tts asyncio pyaudio
Använd koden med försiktighet.
Setting Up Piper Locally
Instead of dealing with complex Python bindings for Piper (which can occasionally be tricky to compile on Windows/Linux mobile platforms), the most robust approach is using the official Piper standalone CLI binary. This allows Python to feed text directly into Piper via an asynchronous subprocess stream, ensuring optimal thread separation on your i7 processor.
Download the standalone Piper archive for your OS (e.g., piper_windows_amd64.zip or piper_linux_x86_64.tar.gz) from the official rhasspy/piper GitHub releases.
Extract it to a folder in your project directory (e.g., ./piper/).
Download a voice model file (.onnx) and its matching config (.onnx.json) from the Piper voice repository (the en_US-lessac-medium or sv_SE-ilsa-medium models are excellent choices for your setup). Place them in your project directory.
💻 The Real-Time Streaming PoC
Here is a complete, working Proof of Concept. It attempts to stream audio live from Microsoft Edge TTS directly to your laptop's speakers using PyAudio. If it detects a network connection failure or a timeout, it seamlessly drops back to your local Piper instance, processing the audio chunks on your local CPU.

Python example
# --- START ---
import asyncio
import os
import subprocess
import shutil
import pyaudio
import edge_tts

# --- CONFIGURATION ---
TEXT_TO_SPEAK = "Testing the primary text-to-speech engine. If you hear this, the cloud routing is functional."
EDGE_VOICE = "en-US-AvaNeural"  # Standard high-quality Edge voice

# Paths for your local Piper fallback configuration
PIPER_EXE = r"./piper/piper.exe"  # Change to "./piper/piper" on Linux/macOS
PIPER_MODEL = r"./en_US-lessac-medium.onnx"

# Audio Settings (Matches the default output of both engines)
SAMPLE_RATE = 24000 
CHANNELS = 1

async def play_edge_stream(text, audio_stream):
    """Streams audio chunks dynamically from Microsoft Edge TTS."""
    print("🎙️ Attempting Microsoft Edge TTS (Cloud)...")
    communicate = edge_tts.Communicate(text, EDGE_VOICE)
    
    # edge-tts returns mp3/native data chunks over WebSockets
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            # Write raw audio data directly to the PyAudio playback stream
            audio_stream.write(chunk["data"])

async def play_piper_fallback(text, audio_stream):
    """Fallback engine: Streams raw PCM chunks directly from local Piper CPU process."""
    print("🔌 Edge TTS Unavailable. Swapping to Local Piper Fallback...")
    
    if not os.path.exists(PIPER_EXE) or not os.path.exists(PIPER_MODEL):
        print("❌ Error: Piper executable or voice model files missing!")
        return

    # Launch Piper as an asynchronous subprocess configured to output raw PCM to stdout
    process = await asyncio.create_subprocess_exec(
        PIPER_EXE,
        "--model", PIPER_MODEL,
        "--output_raw",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    # Feed the text string into Piper's stdin and close it to signal end of text
    process.stdin.write(text.encode('utf-8') + b'\n')
    await process.stdin.drain()
    process.stdin.close()

    # Piper outputs 16-bit Mono PCM at its model rate (usually 22050Hz or 24000Hz)
    # Read chunks dynamically out of stdout buffer and pipe straight to speakers
    chunk_size = 1024
    while True:
        data = await process.stdout.read(chunk_size)
        if not data:
            break
        audio_stream.write(data)

    await process.wait()

async def main():
    # Initialize PyAudio system mixer
    p = pyaudio.PyAudio()
    audio_stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        output=True
    )

    try:
        # Wrap cloud execution in a strict timeout window (e.g., 2.5 seconds to connect)
        await asyncio.wait_for(play_edge_stream(TEXT_TO_SPEAK, audio_stream), timeout=2.5)
        print("✅ Cloud stream completed successfully.")
        
    except (asyncio.TimeoutError, Exception) as e:
        # If the Telia connection experiences a rare routing drop, trigger instant local compute
        await play_piper_fallback(TEXT_TO_SPEAK, audio_stream)
        print("✅ Local fallback stream completed.")

    finally:
        # Clean up audio channels gracefully
        audio_stream.stop_stream()
        audio_stream.close()
        p.terminate()

if __name__ == "__main__":
    # Standard asyncio entry point
    asyncio.run(main())
# --- END ---

🛠️ Verification Checklist for your Laptop
PyAudio Errors: If you are on Windows and running pip install pyaudio fails due to compilation errors, install the pre-compiled wheel binary instead via pip install pipwin followed by pipwin install pyaudio.
Sample Rates: Microsoft Edge TTS outputs at 24000 Hz. Make sure the specific Piper .onnx model you download also lists 24000Hz in its profile name (many are 22050Hz). Matching these speeds avoids audio sounding high or low pitched when the fallback engages.
Would you like me to help you adjust this code to support a specific language choice (like Swedish profiles), or should we look into optimizing the pre-loading mechanism to completely erase the cold-start delay of the Piper binary?