#!/usr/bin/env python3
"""Transcribe a video with word-level timestamps.

Writes <out>.json (segments and words) and <out>.srt (captions). Uses
faster-whisper if installed, otherwise openai-whisper.

  pip install faster-whisper      # recommended
Usage:
  transcribe.py cut.mp4 [--out cut] [--model small] [--max-words 6]
"""
import argparse
import json
import os
import subprocess
import sys


def load_audio(path):
    """Decode with ffmpeg to 16 kHz mono, sidestepping PyAV version clashes."""
    import numpy as np
    raw = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le",
         "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def run_faster_whisper(path, model_name):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name, compute_type="int8")
    segments, _ = model.transcribe(load_audio(path), word_timestamps=True,
                                   vad_filter=True)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"start": w.start, "end": w.end, "text": w.word.strip()})
    return words


def run_openai_whisper(path, model_name):
    import whisper
    result = whisper.load_model(model_name).transcribe(path, word_timestamps=True)
    return [{"start": w["start"], "end": w["end"], "text": w["word"].strip()}
            for seg in result["segments"] for w in seg.get("words", [])]


def ts(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def caption_chunks(words, max_words):
    """Short caption lines, broken at sentence ends or long pauses."""
    chunk = []
    for i, w in enumerate(words):
        chunk.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        pause = nxt and nxt["start"] - w["end"] > 0.4
        if len(chunk) >= max_words or w["text"][-1:] in ".?!" or pause or not nxt:
            yield chunk
            chunk = []


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("--out", help="output path without extension (default: input name)")
    p.add_argument("--model", default="small", help="whisper model (default small)")
    p.add_argument("--max-words", type=int, default=6,
                   help="words per caption line (default 6; use 3 for vertical shorts)")
    args = p.parse_args()
    out = args.out or os.path.splitext(args.input)[0]

    try:
        words = run_faster_whisper(args.input, args.model)
    except ImportError:
        try:
            words = run_openai_whisper(args.input, args.model)
        except ImportError:
            sys.exit("No transcriber installed. Run: pip install faster-whisper")

    with open(out + ".json", "w") as f:
        json.dump({"source": args.input, "words": words}, f, indent=2)
    with open(out + ".srt", "w") as f:
        for n, chunk in enumerate(caption_chunks(words, args.max_words), 1):
            text = " ".join(w["text"] for w in chunk)
            f.write(f"{n}\n{ts(chunk[0]['start'])} --> {ts(chunk[-1]['end'])}\n{text}\n\n")
    print(f"{len(words)} words. Wrote {out}.json and {out}.srt")


if __name__ == "__main__":
    main()
