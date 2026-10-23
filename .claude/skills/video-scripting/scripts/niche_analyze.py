#!/usr/bin/env python3
"""Find what works in a niche: outlier videos, their hooks, title patterns and pacing.

Step 1, fetch (needs yt-dlp; skip if you already have the files):
  niche_analyze.py fetch "ytsearch40:home espresso" -d research/espresso
  niche_analyze.py fetch "https://www.youtube.com/@channel/videos" -d research/espresso --limit 60
  -> research/espresso/<id>.info.json + <id>.en.vtt (auto captions), no video downloads

Step 2, analyze (pure Python; also accepts a CSV with columns id,title,views,duration,upload_date,channel[,transcript]):
  niche_analyze.py analyze research/espresso -o research/espresso/report [--top 15]
  -> report/niche_report.md   ranked outliers, hook transcripts, hook/title pattern stats, pacing
     report/hooks.json        structured data the scripting skill writes from

"Outlier score" = views / median views of the same channel in the sample (falls back to the
whole sample). A 10x outlier on a small channel says more about the idea than 2M views on a giant.
"""
import argparse
import csv
import glob
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date

HOOK_SECONDS = 20

HOOK_TYPES = [  # (name, regex on the first ~2 sentences); first match wins
    ("contrarian", r"\b(stop|don't|never|wrong|myth|lie|overrated|nobody tells you|mistake)\b"),
    ("result-first", r"\b(this is|here's|look at|i (made|built|got|turned)|went from|in (\d+|one|two|three) (days|weeks|months))\b"),
    ("stat-shock", r"(\d[\d,.]*\s?(%|percent|x|times|k|million|billion|dollars|\$))|\$\d"),
    ("question", r"\?"),
    ("challenge", r"\b(i tried|i spent|i tested|for (\d+|thirty|seven) days|challenge)\b"),
    ("story", r"^(so |when |last |a few|i was|my |in \d{4})"),
    ("list-promise", r"\b(\d+|three|five|seven|ten) (ways|things|tips|mistakes|reasons|steps|rules)\b"),
    ("direct-address", r"\b(if you|you're|you've|your)\b"),
]
TITLE_TYPES = [
    ("number-list", r"^\d+\s|\b\d+ (ways|things|tips|mistakes|reasons|steps)\b"),
    ("how-to", r"\bhow (to|i)\b"),
    ("question", r"\?$"),
    ("negative", r"\b(stop|never|worst|mistake|wrong|don't|avoid|bad)\b"),
    ("experiment", r"\b(i tried|i tested|for \d+ days|vs\.?|versus|challenge)\b"),
    ("curiosity", r"\b(this|why|secret|nobody|actually|truth)\b"),
    ("money/result", r"\$\d|\b\d+k\b|\bmillion\b"),
]


def fetch(a):
    if not shutil.which("yt-dlp"):
        sys.exit("yt-dlp not installed: pip install yt-dlp  (or export metadata to CSV and run `analyze` on it)")
    os.makedirs(a.dir, exist_ok=True)
    cmd = ["yt-dlp", a.source, "--skip-download", "--write-info-json", "--write-auto-subs", "--write-subs",
           "--sub-langs", a.lang, "--sub-format", "vtt", "--ignore-errors", "--no-overwrites",
           "-o", os.path.join(a.dir, "%(id)s.%(ext)s")]
    if a.limit:
        cmd += ["--playlist-end", str(a.limit)]
    subprocess.run(cmd)
    print(f"[fetch] {len(glob.glob(os.path.join(a.dir, '*.info.json')))} videos in {a.dir}")


def parse_vtt(path, limit):
    """Return deduplicated caption text spoken before `limit` seconds, plus total word count."""
    words_before, all_words, seen = [], 0, set()
    t = 0.0
    for line in open(path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        m = re.match(r"(\d+):(\d+):([\d.]+) -->", line) or re.match(r"(\d+):([\d.]+) -->", line)
        if m:
            g = m.groups()
            t = (int(g[0]) * 3600 + int(g[1]) * 60 + float(g[2])) if len(g) == 3 else int(g[0]) * 60 + float(g[1])
            continue
        if not line or "-->" in line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if not clean or clean in seen:  # auto-captions repeat each line while scrolling
            continue
        seen.add(clean)
        n = len(clean.split())
        all_words += n
        if t < limit:
            words_before.append(clean)
    return " ".join(words_before), all_words


def load_dir(d):
    vids = []
    for p in glob.glob(os.path.join(d, "*.info.json")):
        j = json.load(open(p))
        vid = {"id": j.get("id"), "title": j.get("title", ""), "views": j.get("view_count") or 0,
               "duration": j.get("duration") or 0, "upload_date": j.get("upload_date"),
               "channel": j.get("channel") or j.get("uploader") or "?", "url": j.get("webpage_url"),
               "likes": j.get("like_count"), "comments": j.get("comment_count"), "chapters": j.get("chapters") or []}
        subs = sorted(glob.glob(os.path.join(d, f"{vid['id']}*.vtt")))
        if subs:
            vid["hook"], vid["total_words"] = parse_vtt(subs[0], HOOK_SECONDS)
        vids.append(vid)
    return vids


def load_csv(p):
    vids = []
    for r in csv.DictReader(open(p)):
        tr = r.get("transcript", "")
        vids.append({"id": r.get("id"), "title": r.get("title", ""), "views": int(float(r.get("views") or 0)),
                     "duration": float(r.get("duration") or 0), "upload_date": r.get("upload_date"),
                     "channel": r.get("channel", "?"), "url": r.get("url"), "chapters": [],
                     "hook": " ".join(tr.split()[:55]) if tr else None, "total_words": len(tr.split()) or None})
    return vids


def classify(text, table):
    low = (text or "").lower()
    return [name for name, rx in table if re.search(rx, low)]


def age_days(d):
    try:
        return max(1, (date.today() - date(int(d[:4]), int(d[4:6]), int(d[6:8]))).days)
    except (TypeError, ValueError):
        return None


def analyze(a):
    vids = load_csv(a.input) if a.input.endswith(".csv") else load_dir(a.input)
    vids = [v for v in vids if v["views"]]
    if not vids:
        sys.exit("no videos with view counts found")
    by_ch = defaultdict(list)
    for v in vids:
        by_ch[v["channel"]].append(v["views"])
    overall = statistics.median(v["views"] for v in vids)
    for v in vids:
        peers = by_ch[v["channel"]]
        base = statistics.median(peers) if len(peers) >= 3 else overall
        v["outlier"] = round(v["views"] / max(base, 1), 2)
        ad = age_days(v.get("upload_date"))
        v["views_per_day"] = round(v["views"] / ad) if ad else None
        first = re.split(r"(?<=[.?!])\s+", v.get("hook") or "")
        v["hook_types"] = classify(" ".join(first[:2]), HOOK_TYPES) if v.get("hook") else []
        v["title_types"] = classify(v["title"], TITLE_TYPES)
        if v.get("total_words") and v["duration"]:
            v["wpm"] = round(v["total_words"] / (v["duration"] / 60))
    vids.sort(key=lambda v: -v["outlier"])
    top = vids[:a.top]
    rest = vids[a.top:]

    def share(group, key):
        c = Counter(t for v in group for t in v[key])
        n = max(1, len(group))
        return {k: round(c[k] / n, 2) for k in c}

    hook_top, hook_rest = share(top, "hook_types"), share(rest, "hook_types")
    title_top, title_rest = share(top, "title_types"), share(rest, "title_types")
    durs = sorted(v["duration"] for v in top if v["duration"])
    wpms = [v["wpm"] for v in top if v.get("wpm")]
    summary = {
        "sample": len(vids), "top_n": len(top),
        "hook_patterns_top_vs_rest": {k: [hook_top.get(k, 0), hook_rest.get(k, 0)] for k in set(hook_top) | set(hook_rest)},
        "title_patterns_top_vs_rest": {k: [title_top.get(k, 0), title_rest.get(k, 0)] for k in set(title_top) | set(title_rest)},
        "top_duration_median_s": statistics.median(durs) if durs else None,
        "top_duration_range_s": [durs[0], durs[-1]] if durs else None,
        "top_wpm_median": statistics.median(wpms) if wpms else None,
        "top_title_length_words": statistics.median(len(v["title"].split()) for v in top),
    }
    os.makedirs(a.output, exist_ok=True)
    json.dump({"summary": summary, "top": top, "rest": rest}, open(os.path.join(a.output, "hooks.json"), "w"), indent=1)

    L = [f"# Niche report: `{a.input}`", "", f"{len(vids)} videos analysed · top {len(top)} by outlier score", "",
         "## What over-performs (share of top vs rest)", "", "| Hook pattern | Top | Rest | Lift |", "|---|---|---|---|"]
    for k, (t, r) in sorted(summary["hook_patterns_top_vs_rest"].items(), key=lambda kv: -(kv[1][0] - kv[1][1])):
        L.append(f"| {k} | {t:.0%} | {r:.0%} | {t - r:+.0%} |")
    L += ["", "| Title pattern | Top | Rest | Lift |", "|---|---|---|---|"]
    for k, (t, r) in sorted(summary["title_patterns_top_vs_rest"].items(), key=lambda kv: -(kv[1][0] - kv[1][1])):
        L.append(f"| {k} | {t:.0%} | {r:.0%} | {t - r:+.0%} |")
    L += ["", "## Format", "",
          f"- Duration of top videos: median {summary['top_duration_median_s']}s, range {summary['top_duration_range_s']}",
          f"- Speaking pace of top videos: median {summary['top_wpm_median']} wpm",
          f"- Title length: median {summary['top_title_length_words']} words", "",
          "## Top outliers and their hooks (first ~20 s)", ""]
    for v in top:
        L += [f"### {v['outlier']}x · {v['title']}",
              f"{v['channel']} · {v['views']:,} views · {v['duration']}s"
              + (f" · {v['views_per_day']:,}/day" if v.get("views_per_day") else "")
              + (f" · {v['url']}" if v.get("url") else ""),
              f"- Hook types: {', '.join(v['hook_types']) or '—'} · Title types: {', '.join(v['title_types']) or '—'}",
              f"- Chapters: {' / '.join(c.get('title', '') for c in v['chapters'][:8])}" if v["chapters"] else "",
              f"> {v['hook']}" if v.get("hook") else "> (no captions)", ""]
    open(os.path.join(a.output, "niche_report.md"), "w").write("\n".join(l for l in L if l is not None) + "\n")
    print(f"[analyze] {len(vids)} videos -> {a.output}/niche_report.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("source")
    f.add_argument("-d", "--dir", required=True)
    f.add_argument("--limit", type=int)
    f.add_argument("--lang", default="en.*,en")
    n = sub.add_parser("analyze")
    n.add_argument("input", help="folder from `fetch` or a CSV")
    n.add_argument("-o", "--output", required=True)
    n.add_argument("--top", type=int, default=15)
    a = ap.parse_args()
    fetch(a) if a.cmd == "fetch" else analyze(a)


if __name__ == "__main__":
    main()
