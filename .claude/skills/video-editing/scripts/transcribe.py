#!/usr/bin/env python3
"""Transcribe raw footage with Whisper and write word-level timestamps.

Output (transcript.json):
{
  "source": "raw/take1.mp4",
  "language": "en",
  "duration": 312.4,
  "backend": "faster-whisper",
  "segments": [
    {"start": 0.52, "end": 3.9, "text": "...",
     "words": [{"start": 0.52, "end": 0.8, "word": "So", "prob": 0.98}, ...]}
  ]
}

Backends (first available wins, or force with --backend):
  faster-whisper   pip install faster-whisper          (recommended, fast on CPU)
  openai-whisper   pip install openai-whisper
  whisper.cpp      `whisper-cli` (or `main`) on PATH + --model-path to a ggml model

Usage:
  transcribe.py raw/take1.mp4 -o work/transcript.json [--model medium] [--language en]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def extract_audio(src, dst):
    # 16 kHz mono PCM is what every Whisper backend expects.
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000",
                    "-c:a", "pcm_s16le", dst], check=True)


def run_faster_whisper(wav, model, language):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="auto", compute_type="auto")
    segs, info = m.transcribe(wav, language=language, word_timestamps=True,
                              vad_filter=False,  # keep silences: plan_cuts decides what to drop
                              condition_on_previous_text=False)  # reduces hallucinated repeats on retakes
    out = []
    for s in segs:
        out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                    "words": [{"start": w.start, "end": w.end, "word": w.word.strip(),
                               "prob": w.probability} for w in (s.words or [])]})
    return out, info.language


def run_openai_whisper(wav, model, language):
    import whisper
    m = whisper.load_model(model)
    r = m.transcribe(wav, language=language, word_timestamps=True,
                     condition_on_previous_text=False)
    out = []
    for s in r["segments"]:
        out.append({"start": s["start"], "end": s["end"], "text": s["text"].strip(),
                    "words": [{"start": w["start"], "end": w["end"], "word": w["word"].strip(),
                               "prob": w.get("probability", 1.0)} for w in s.get("words", [])]})
    return out, r.get("language", language)


def run_whisper_cpp(wav, model_path, language):
    exe = shutil.which("whisper-cli") or shutil.which("main")
    if not exe or not model_path:
        raise RuntimeError("whisper.cpp needs `whisper-cli` on PATH and --model-path")
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "out")
        # -ml 1 = one token per segment, which gives us word-level timing.
        cmd = [exe, "-m", model_path, "-f", wav, "-oj", "-of", base, "-ml", "1", "-sow"]
        if language:
            cmd += ["-l", language]
        subprocess.run(cmd, check=True, capture_output=True)
        data = json.load(open(base + ".json"))
    words = []
    for t in data.get("transcription", []):
        txt = t["text"].strip()
        if not txt:
            continue
        words.append({"start": t["offsets"]["from"] / 1000, "end": t["offsets"]["to"] / 1000,
                      "word": txt, "prob": 1.0})
    return group_words(words), data.get("result", {}).get("language", language)


def group_words(words, gap=0.6):
    """Group a flat word list into segments at pauses or sentence ends."""
    segs, cur = [], []
    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap or cur[-1]["word"][-1:] in ".?!"):
            segs.append(cur)
            cur = []
        cur.append(w)
    if cur:
        segs.append(cur)
    return [{"start": s[0]["start"], "end": s[-1]["end"],
             "text": " ".join(w["word"] for w in s), "words": s} for s in segs]


BACKENDS = {
    "faster-whisper": ("faster_whisper", run_faster_whisper),
    "openai-whisper": ("whisper", run_openai_whisper),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--model", default="medium", help="whisper model size (tiny..large-v3)")
    ap.add_argument("--model-path", help="ggml model file for whisper.cpp")
    ap.add_argument("--language", default=None)
    ap.add_argument("--backend", choices=["auto", "faster-whisper", "openai-whisper", "whisper.cpp"],
                    default="auto")
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        wav = os.path.join(td, "audio.wav")
        extract_audio(a.media, wav)
        order = [a.backend] if a.backend != "auto" else ["faster-whisper", "openai-whisper", "whisper.cpp"]
        segments = lang = used = None
        errors = []
        for name in order:
            try:
                if name == "whisper.cpp":
                    segments, lang = run_whisper_cpp(wav, a.model_path, a.language)
                else:
                    mod, fn = BACKENDS[name]
                    __import__(mod)
                    segments, lang = fn(wav, a.model, a.language)
                used = name
                break
            except Exception as e:  # try the next backend
                errors.append(f"{name}: {e}")
        if used is None:
            sys.exit("No Whisper backend worked:\n  " + "\n  ".join(errors) +
                     "\nInstall one: pip install faster-whisper")

    result = {"source": a.media, "language": lang, "duration": probe_duration(a.media),
              "backend": used, "segments": segments}
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    json.dump(result, open(a.output, "w"), indent=1)
    n = sum(len(s["words"]) for s in segments)
    print(f"[transcribe] {used}: {len(segments)} segments, {n} words -> {a.output}")


if __name__ == "__main__":
    main()
