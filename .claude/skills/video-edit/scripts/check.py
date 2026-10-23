#!/usr/bin/env python3
"""Technical QA on a rendered video. Prints a JSON report; exits 1 on failures.

Checks: streams present, resolution/aspect, black frames, leftover dead air,
loudness (target about -14 LUFS for YouTube/TikTok), and clipping.

Usage:
  check.py final.mp4 [--aspect 9:16] [--max-gap 1.0]
"""
import argparse
import json
import re
import subprocess
import sys


def ffmpeg_log(path, *filters):
    args = ["ffmpeg", "-hide_banner", "-nostats", "-i", path]
    for f in filters:
        args += list(f)
    return subprocess.run(args + ["-f", "null", "-"],
                          capture_output=True, text=True).stderr


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("--aspect", help="expected aspect, e.g. 16:9 or 9:16")
    p.add_argument("--max-gap", type=float, default=1.0,
                   help="longest allowed silence in seconds (default 1.0)")
    args = p.parse_args()

    info = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json",
         args.input], capture_output=True, text=True, check=True).stdout)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    report = {"file": args.input, "duration": round(float(info["format"]["duration"]), 2),
              "issues": []}
    issues = report["issues"]

    if not audio:
        issues.append("no audio stream")
    if video:
        w, h = video["width"], video["height"]
        report["resolution"] = f"{w}x{h}"
        if args.aspect:
            aw, ah = (int(x) for x in args.aspect.split(":"))
            if abs(w / h - aw / ah) > 0.01:
                issues.append(f"aspect is {w}x{h}, expected {args.aspect}")
        log = ffmpeg_log(args.input, ("-an", "-vf", "blackdetect=d=0.3:pix_th=0.1"))
        blacks = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)
        report["black_frames"] = [[float(a), float(b)] for a, b in blacks]
        if blacks:
            issues.append(f"{len(blacks)} black section(s); see black_frames")
    else:
        issues.append("no video stream")

    if audio:
        log = ffmpeg_log(args.input, ("-vn", "-af",
                                      f"silencedetect=noise=-35dB:d={args.max_gap}"))
        gaps = re.findall(r"silence_duration: ([\d.]+)", log)
        report["long_silences"] = len(gaps)
        if gaps:
            issues.append(f"{len(gaps)} pause(s) longer than {args.max_gap}s")

        log = ffmpeg_log(args.input, ("-vn", "-af", "loudnorm=print_format=json"))
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", log)
        if m:
            ln = json.loads(m.group(0))
            lufs, peak = float(ln["input_i"]), float(ln["input_tp"])
            report["loudness_lufs"], report["true_peak_db"] = lufs, peak
            if not -16.5 <= lufs <= -11.5:
                issues.append(f"loudness {lufs} LUFS; aim for about -14")
            if peak > -1.0:
                issues.append(f"true peak {peak} dB may clip; keep below -1")

    report["pass"] = not issues
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
