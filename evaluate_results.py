import csv
import json
import re
from collections import defaultdict
from pathlib import Path

CORE = {"claim_type", "summary", "missing_information"}
FULL = CORE | {"priority", "needs_human_review", "rationale"}


def norm(t):
    return re.sub(r"[^a-z0-9 ]", "", str(t).lower())


def parse(raw):
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


def recall_hit(required, found_items):
    words = norm(required).split()
    blob = norm(" ".join(map(str, found_items)))
    return all(w in blob for w in words) or any(
        w in blob for w in words if len(w) > 4
    )


rows = [
    json.loads(l)
    for l in Path("results.jsonl").read_text(encoding="utf-8").splitlines()
    if l.strip()
]
stats = defaultdict(lambda: defaultdict(float))

for r in rows:
    v = stats[r["version"]]
    v["n"] += 1
    v["latency"] += r["latency_seconds"]
    obj = parse(r["raw_output"])
    if obj is None:
        continue
    if CORE <= obj.keys():
        v["valid_core"] += 1
    if (
        FULL <= obj.keys()
        and isinstance(obj.get("missing_information"), list)
        and isinstance(obj.get("needs_human_review"), bool)
    ):
        v["valid_full"] += 1
    if norm(obj.get("claim_type", "")) == norm(r["expected_category"]):
        v["correct"] += 1
    found = obj.get("missing_information", [])
    found = found if isinstance(found, list) else [found]
    v["req_total"] += len(r["required_missing"])
    v["req_hit"] += sum(recall_hit(x, found) for x in r["required_missing"])

print(f"{'metric':30}" + "".join(f"{k:>14}" for k in sorted(stats)))


def line(name, fn):
    print(f"{name:30}" + "".join(f"{fn(stats[k]):>14}" for k in sorted(stats)))


line("claims run", lambda s: int(s["n"]))
line("classification accuracy", lambda s: f"{s['correct']/s['n']:.0%}")
line("missing-info recall", lambda s: f"{s['req_hit']/s['req_total']:.0%}")
line("valid output (core fields)", lambda s: f"{s['valid_core']/s['n']:.0%}")
line("valid output (full schema)", lambda s: f"{s['valid_full']/s['n']:.0%}")
line("mean latency (s)", lambda s: f"{s['latency']/s['n']:.2f}")