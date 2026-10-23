#!/usr/bin/env python3
"""Cut dead air out of raw footage.

Finds silences with ffmpeg's silencedetect, keeps everything else (plus a
little padding so words aren't clipped), and renders the result. Also writes
an edit decision list (EDL) so the cut can be reviewed or adjusted.

Usage:
  silence_cut.py raw.mp4 cut.mp4 [--noise -30] [--min-silence 0.6] [--pad 0.12]
"""
import argparse
import json
import re
import subprocess
import sys


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(out.strip())


def detect_silences(path, noise_db, min_silence):
    log = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn",
         "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}",
         "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def keep_segments(silences, duration, pad):
    keeps, cursor = [], 0.0
    for start, end in silences:
        end = duration if end is None else end
        seg_end = min(duration, max(0.0, start) + pad)
        if seg_end - cursor > 0.05:
            keeps.append((round(cursor, 3), round(seg_end, 3)))
        cursor = max(cursor, end - pad)
    if duration - cursor > 0.05:
        keeps.append((round(cursor, 3), round(duration, 3)))
    return keeps


def has_video(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
         "stream=index", "-of", "csv=p=0", path],
        capture_output=True, text=True,
    ).stdout
    return bool(out.strip())


def render(src, dst, keeps):
    video = has_video(src)
    parts, labels = [], []
    for i, (a, b) in enumerate(keeps):
        if video:
            parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
            labels.append(f"[v{i}]")
        parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}]")
        labels.append(f"[a{i}]")
    v = 1 if video else 0
    parts.append(f"{''.join(labels)}concat=n={len(keeps)}:v={v}:a=1"
                 + ("[v][a]" if video else "[a]"))
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", src,
           "-filter_complex", ";".join(parts)]
    if video:
        cmd += ["-map", "[v]"]
    cmd += ["-map", "[a]", dst]
    subprocess.run(cmd, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--noise", type=float, default=-30,
                   help="silence threshold in dB (default -30)")
    p.add_argument("--min-silence", type=float, default=0.6,
                   help="shortest pause to cut, in seconds (default 0.6)")
    p.add_argument("--pad", type=float, default=0.12,
                   help="seconds kept on each side of speech (default 0.12)")
    p.add_argument("--edl", help="where to write the EDL (default <output>.edl.json)")
    p.add_argument("--dry-run", action="store_true", help="write the EDL only")
    args = p.parse_args()

    duration = probe_duration(args.input)
    silences = detect_silences(args.input, args.noise, args.min_silence)
    keeps = keep_segments(silences, duration, args.pad)
    if not keeps:
        sys.exit("Nothing left after cutting: lower --noise (e.g. -40) or raise --min-silence.")

    kept = sum(b - a for a, b in keeps)
    edl = {"source": args.input, "source_duration": round(duration, 3),
           "output_duration": round(kept, 3), "removed": round(duration - kept, 3),
           "settings": {"noise_db": args.noise, "min_silence": args.min_silence,
                        "pad": args.pad},
           "keep": [{"start": a, "end": b} for a, b in keeps]}
    edl_path = args.edl or args.output + ".edl.json"
    with open(edl_path, "w") as f:
        json.dump(edl, f, indent=2)

    if not args.dry_run:
        render(args.input, args.output, keeps)
    print(f"{len(keeps)} segments kept, {duration - kept:.1f}s of {duration:.1f}s removed. "
          f"EDL: {edl_path}")


if __name__ == "__main__":
    main()
