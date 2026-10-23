#!/usr/bin/env python3
"""Turn beat-map entries into ready-to-render compositions (one folder per graphic).

For every beat with "graphic": true (or the --beats you name), copies the template for its
treatment, fills in text and word timings from the edited transcript, and writes:

  graphics/tokens.css          (from the project's design tokens if --tokens is given)
  graphics/hf-timeline.js
  graphics/<ID>/index.html     Hyperframes composition
  graphics/<ID>/graphic.json   timing + QC expectations, read by composite.py and qc.py

Sub-agents then refine each index.html against design.md; this gives them a correct,
correctly-timed starting point rather than a blank page.

Usage:
  scaffold_graphics.py work/beat_map.json work/transcript.edited.json -o graphics/ [--tokens design/tokens.css] [--beats B03,B09]
"""
import argparse
import html
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "templates")

# lead = seconds the graphic starts before the beat; hold = seconds on screen after the beat word
TIMING = {
    "kinetic-headline": (0.05, 0.5),
    "number-counter": (0.8, 1.8),
    "keyword-pop": (0.05, 1.2),
    "list-card": (0.1, 2.2),
    "section-title": (0.0, 1.8),
    "question-card": (0.05, 1.6),
}
TEMPLATE_FOR = {"question-card": "keyword-pop"}  # reuse until a dedicated template exists
ALIGN = {"kinetic-headline": "center", "number-counter": "right", "keyword-pop": "center",
         "list-card": "left", "section-title": "left", "question-card": "center"}


def words_between(words, t0, t1):
    return [w for w in words if w["start"] >= t0 - 0.02 and w["end"] <= t1 + 0.05]


def parse_number(s):
    m = re.match(r"^([^\d]*)([\d,.]+)(.*)$", s)
    if not m:
        return "", 0, s
    return m.group(1), float(m.group(2).replace(",", "")), m.group(3)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("beat_map")
    ap.add_argument("transcript")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("--tokens")
    ap.add_argument("--beats", help="comma-separated beat IDs (default: all graphic beats)")
    a = ap.parse_args()

    bm = json.load(open(a.beat_map))
    words = json.load(open(a.transcript))["words"]
    want = set(a.beats.split(",")) if a.beats else None
    os.makedirs(a.outdir, exist_ok=True)
    shutil.copy(a.tokens or os.path.join(TPL, "tokens.css"), os.path.join(a.outdir, "tokens.css"))
    shutil.copy(os.path.join(TPL, "hf-timeline.js"), os.path.join(a.outdir, "hf-timeline.js"))

    section_n = 0
    made = []
    for b in bm["beats"]:
        if b["type"] == "section":
            section_n += 1
        if (want and b["id"] not in want) or (not want and not b.get("graphic")):
            continue
        tr = b["treatment"]
        if tr not in TIMING:
            print(f"[scaffold] {b['id']}: treatment '{tr}' has no template (punch-in/caption are edit-level); skipped")
            continue
        lead, hold = TIMING[tr]
        start = max(0.0, b["in"] - lead)
        end = (b["end"] if tr in ("kinetic-headline", "list-card") else b["t"]) + hold
        dur = round(end - start, 3)
        fill = {"ID": b["id"], "DURATION": f"{dur}"}
        if tr == "kinetic-headline":
            ws = words_between(words, b["t"], b["end"])
            spans = []
            longest = max(ws, key=lambda w: len(w["word"]), default=None)
            for w in ws:
                cls = "w key" if w is longest else "w"
                spans.append(f'<span class="{cls}" data-at="{max(0, w["start"] - start):.3f}">{html.escape(w["word"])}</span>')
            fill["WORDS_HTML"] = "".join(spans)
        elif tr == "number-counter":
            pre, val, suf = parse_number(b.get("keyword", "0"))
            fill.update(PREFIX=html.escape(pre), VALUE=f"{val:g}", SUFFIX=html.escape(suf),
                        LAND_AT=f"{b['t'] - start:.3f}", LABEL=html.escape(b["text"][:48]))
        elif tr in ("keyword-pop", "question-card"):
            fill["KEYWORD"] = html.escape(b.get("keyword") or b["text"][:28])
        elif tr == "list-card":
            fill["ITEMS_HTML"] = f'<div class="item" data-at="0.15"><b>{section_n or 1}</b>{html.escape(b["text"][:40])}</div>'
        elif tr == "section-title":
            fill.update(INDEX=f"{section_n:02d}", TITLE=html.escape(b["text"]))
        src = open(os.path.join(TPL, TEMPLATE_FOR.get(tr, tr) + ".html")).read()
        for k, v in fill.items():
            src = src.replace("{{" + k + "}}", str(v))
        left = re.findall(r"\{\{\w+\}\}", src)
        if left:
            print(f"[scaffold] {b['id']}: unfilled placeholders {sorted(set(left))}")
        d = os.path.join(a.outdir, b["id"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(src)
        json.dump({"id": b["id"], "beat": b["id"], "treatment": tr, "in": round(start, 3), "duration": dur,
                   "file": "out.mov", "layer": 10, "align": ALIGN.get(tr, "center"), "safe": "title",
                   "text": b.get("keyword") or b["text"], "why": b["why"]},
                  open(os.path.join(d, "graphic.json"), "w"), indent=1)
        made.append(b["id"])
    print(f"[scaffold] {len(made)} graphics -> {a.outdir}: {', '.join(made)}")


if __name__ == "__main__":
    main()
