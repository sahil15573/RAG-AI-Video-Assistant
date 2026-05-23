import yt_dlp
import os
import subprocess

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",

        "outtmpl": output_path,

        "quiet": False,

        "noplaylist": True,

        "geo_bypass": True,

        "nocheckcertificate": True,

        "ignoreerrors": False,

        "retries": 15,
        "fragment_retries": 15,

        # MOST IMPORTANT FIX
        "extractor_args": {
            "youtube": {
                "player_client": ["tv_embedded", "android"]
            }
        },

        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        },

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)

    filename = os.path.splitext(filename)[0] + ".wav"

    return filename


def convert_to_wav(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        output_path,
    ]

    subprocess.run(command, check=True)

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:

    import math

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    duration_command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        wav_path,
    ]

    result = subprocess.run(
        duration_command,
        capture_output=True,
        text=True
    )

    duration = float(result.stdout.strip())

    total_chunks = math.ceil(duration / (chunk_minutes * 60))

    for i in range(total_chunks):

        start_time = i * chunk_minutes * 60

        output_chunk = f"{wav_path}_chunk_{i}.wav"

        command = [
            "ffmpeg",
            "-y",
            "-i",
            wav_path,
            "-ss",
            str(start_time),
            "-t",
            str(chunk_minutes * 60),
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            output_chunk,
        ]

        subprocess.run(command, check=True)

        if os.path.exists(output_chunk):
            chunks.append(output_chunk)

    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)

    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks