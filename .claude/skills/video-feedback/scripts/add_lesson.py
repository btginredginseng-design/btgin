#!/usr/bin/env python3
"""Turn an editor's note into a permanent rule for a pipeline stage.

A lesson is written in three places so it changes future behaviour, not just this edit:
  1. the target skill's SKILL.md, inside its LEARNED-RULES block (read every time the skill runs)
  2. optionally the stage's defaults.json, when the fix is a number (--set max_pause=0.25)
  3. lessons.jsonl next to this script, the audit log (what, why, from which project, old -> new values)

Usage:
  add_lesson.py --stage motion-graphics --rule "Never center with transform: translate(-50%); use inset + flex" \
                --why "timeline tweens overwrite transform; headline drifted 120px right" --source demo/B01
  add_lesson.py --stage video-editing --rule "Keep pauses before punchlines" --why "..." --set max_pause=0.45
  add_lesson.py --stage video-editing --rule "Treat 'like' as filler for this creator" --why "..." --set fillers+=like
  add_lesson.py --list [--stage video-editing]
  add_lesson.py --retire L004 --why "superseded by L009"
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.abspath(os.path.join(HERE, "..", ".."))
LOG = os.path.join(HERE, "..", "lessons.jsonl")
STAGES = ["video-scripting", "video-editing", "video-design", "motion-graphics", "video-review", "video-pipeline"]
START, END = "<!-- LEARNED-RULES:START -->", "<!-- LEARNED-RULES:END -->"


def load_log():
    if not os.path.exists(LOG):
        return []
    return [json.loads(l) for l in open(LOG) if l.strip()]


def coerce(v):
    for f in (int, float):
        try:
            return f(v)
        except ValueError:
            pass
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if v.startswith("[") or v.startswith("{"):
        return json.loads(v)
    return v


def set_defaults(stage, assignments):
    path = os.path.join(SKILLS, stage, "defaults.json")
    if not os.path.exists(path):
        sys.exit(f"{stage} has no defaults.json; --set only works for stages with tunable defaults")
    cfg = json.load(open(path))
    changes = []
    for a in assignments:
        append = "+=" in a  # fillers+=like appends to a list
        key, _, val = a.partition("+=" if append else "=")
        node, parts = cfg, key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        if parts[-1] not in node:
            sys.exit(f"unknown key '{key}' in {path} (known: {', '.join(k for k in cfg if not k.startswith('_'))})")
        old = node[parts[-1]]
        new = coerce(val)
        if append:
            if not isinstance(old, list):
                sys.exit(f"'{key}' is not a list; use {key}=VALUE")
            new = old + [new]
        node[parts[-1]] = new
        changes.append({"key": key, "old": old, "new": new})
    json.dump(cfg, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    return changes


def revert_defaults(lesson):
    """Undo a retired lesson's --set changes, unless a later lesson has changed the value since."""
    if not lesson.get("changes"):
        return []
    path = os.path.join(SKILLS, lesson["stage"], "defaults.json")
    cfg = json.load(open(path))
    done = []
    for c in lesson["changes"]:
        node, parts = cfg, c["key"].split(".")
        for p in parts[:-1]:
            node = node[p]
        if node.get(parts[-1]) == c["new"]:
            node[parts[-1]] = c["old"]
            done.append(c["key"])
    json.dump(cfg, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    return done


def write_rules(stage):
    """Regenerate the LEARNED-RULES block of a SKILL.md from the active lessons in the log."""
    path = os.path.join(SKILLS, stage, "SKILL.md")
    text = open(path).read()
    if START not in text:
        text = text.rstrip() + f"\n\n## Learned rules\n\nRules added from review notes. They override the defaults above.\n\n{START}\n{END}\n"
    active = [l for l in load_log() if l["stage"] == stage and not l.get("retired")]
    lines = []
    for l in active:
        extra = "".join(f" `{c['key']}: {json.dumps(c['old'])} → {json.dumps(c['new'])}`" for c in l.get("changes", []))
        lines.append(f"- **{l['id']}** {l['rule']}. _Why: {l['why']}_{extra}")
    body = "\n".join(lines) if lines else "_None yet._"
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), START + "\n" + body + "\n" + END, text, flags=re.S)
    open(path, "w").write(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=STAGES)
    ap.add_argument("--rule")
    ap.add_argument("--why")
    ap.add_argument("--source", default="")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--retire", metavar="ID")
    a = ap.parse_args()

    log = load_log()
    if a.list:
        for l in log:
            if a.stage and l["stage"] != a.stage:
                continue
            flag = " (retired)" if l.get("retired") else ""
            print(f"{l['id']} [{l['stage']}] {l['date']}{flag}: {l['rule']}  (why: {l['why']})")
        return
    if a.retire:
        hit = [l for l in log if l["id"] == a.retire]
        if not hit:
            sys.exit(f"no lesson {a.retire}")
        hit[0]["retired"] = a.why or True
        reverted = revert_defaults(hit[0])
        open(LOG, "w").write("".join(json.dumps(l) + "\n" for l in log))
        write_rules(hit[0]["stage"])
        print(f"retired {a.retire}" + (f"; reverted {reverted}" if reverted else ""))
        return
    if not (a.stage and a.rule and a.why):
        sys.exit("--stage, --rule and --why are required (a rule without its reason gets misapplied later)")

    dup = [l for l in log if l["stage"] == a.stage and not l.get("retired")
           and l["rule"].strip().lower() == a.rule.strip().lower()]
    if dup:
        sys.exit(f"already recorded as {dup[0]['id']}")
    lesson = {"id": f"L{len(log) + 1:03d}", "date": datetime.date.today().isoformat(), "stage": a.stage,
              "rule": a.rule.strip().rstrip("."), "why": a.why.strip(), "source": a.source}
    if a.set:
        lesson["changes"] = set_defaults(a.stage, a.set)
    with open(LOG, "a") as f:
        f.write(json.dumps(lesson) + "\n")
    write_rules(a.stage)
    print(f"{lesson['id']} -> {a.stage}/SKILL.md" + (f" + defaults.json {lesson['changes']}" if a.set else ""))


if __name__ == "__main__":
    main()
