#!/usr/bin/env bash
# End-to-end check of the pipeline tooling on synthetic media (no Whisper or network needed).
# Generates a test clip + a transcript with a retake, a filler, a stutter and a "scratch that" cue,
# then runs plan -> render -> beat map -> scaffold -> render graphics -> composite -> QC.
#   bash .claude/skills/video-pipeline/scripts/smoke_test.sh [workdir]
set -euo pipefail
S="$(cd "$(dirname "$0")/../.." && pwd)"
W="${1:-$(mktemp -d)}"; mkdir -p "$W"; cd "$W"
echo "[smoke] working in $W"

ffmpeg -y -v error -f lavfi -i testsrc2=size=1280x720:rate=30:duration=20 -f lavfi -i "sine=f=220:d=20" \
  -filter_complex "[1:a]volume='if(between(mod(t,2),0,1.4),1,0)':eval=frame[a]" \
  -map 0:v -map "[a]" -c:v libx264 -pix_fmt yuv420p -c:a aac raw.mp4
cat > transcript.json <<'JSON'
{"duration":20,"segments":[
{"words":[{"start":0.0,"end":0.4,"word":"So"},{"start":0.45,"end":0.9,"word":"today"},{"start":0.95,"end":1.4,"word":"we're"}]},
{"words":[{"start":2.0,"end":2.4,"word":"So"},{"start":2.45,"end":2.9,"word":"today"},{"start":2.95,"end":3.2,"word":"we're"},{"start":3.2,"end":3.4,"word":"going"}]},
{"words":[{"start":4.0,"end":4.5,"word":"um"},{"start":4.6,"end":5.0,"word":"to"},{"start":5.0,"end":5.4,"word":"build."}]},
{"words":[{"start":6.0,"end":6.4,"word":"the"},{"start":6.45,"end":6.8,"word":"the"},{"start":6.9,"end":7.4,"word":"first"}]},
{"words":[{"start":8.0,"end":8.6,"word":"scratch"},{"start":8.7,"end":9.4,"word":"that."}]},
{"words":[{"start":10.0,"end":10.6,"word":"Step"},{"start":10.7,"end":11.4,"word":"one."}]},
{"words":[{"start":14.0,"end":14.6,"word":"Save"},{"start":14.7,"end":15.4,"word":"300%."}]}]}
JSON
printf '## Hook\nSo today we are going to build.\n## Steps\nStep one.\n## Payoff\nSave **300%%**.\n' > script.md

python3 "$S/video-editing/scripts/plan_cuts.py" transcript.json raw.mp4 -o work
grep -q "retake cue" work/cuts_report.md && grep -q "filler" work/cuts_report.md || { echo "[smoke] FAIL: detectors"; exit 1; }
python3 "$S/video-editing/scripts/render_cuts.py" work/edl.json -o work/edit.mp4 2>/dev/null
python3 "$S/video-design/scripts/beat_map.py" work/transcript.edited.json -o work --script script.md
python3 "$S/motion-graphics/scripts/scaffold_graphics.py" work/beat_map.json work/transcript.edited.json -o graphics
for d in graphics/*/; do node "$S/motion-graphics/scripts/render_html.mjs" "$d/index.html" -o "$d/out.mov"; done
python3 "$S/motion-graphics/scripts/composite.py" work/edit.mp4 graphics -o out/final.mp4 2>/dev/null
python3 "$S/video-review/scripts/qc.py" out/final.mp4 --edit work/edit.mp4 --graphics out/final.graphics.json \
  --transcript work/transcript.edited.json --render-meta work/edit.render.json -o out/qc
echo "[smoke] PASS: outputs in $W"
