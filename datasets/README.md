# Anti-Artifact Object-Continuity Dataset & Prompts

A working dataset + prompt library for QA-ing AI-generated video (e.g. Runway
clips destined for Pinterest/Etsy content) for continuity glitches -- identity
swaps, flicker, freezes, loops, rollbacks, extra/missing objects, geometry
warps, and teleports -- before publishing.

Built from the prompt-engineering framework in the "Anti-Artifact
Object-Continuity Detection in Video" report (sections 2-8): the taxonomy,
few-shot/CoT prompt templates, JSONL label schema, and validator design are
all real, not the dummy placeholder spreadsheet data that was mixed into the
same source document.

## Files

| File | What it is |
|---|---|
| `anti_artifact_taxonomy.json` | The 9 artifact types, the event-code/severity table, the label schema, and the validator pipeline design. Source of truth the other files are checked against. |
| `anti_artifact_examples.jsonl` | 63 labeled synthetic scenarios (7 per artifact type), validated against the taxonomy. Use as few-shot examples, as a labeling eval set, or as seed data to expand from. |
| `../prompts/few_shot_labeling.md` | Ready-to-paste prompt for labeling a new scenario in one shot. |
| `../prompts/chain_of_thought_labeling.md` | Ready-to-paste prompt for ambiguous/multi-artifact scenarios, with reasoning steps. |
| `../prompts/dataset_generation.md` | Prompt + evaluate-iterate loop for growing the dataset with new scenarios in a given content theme. |
| `../scripts/validate_video.py` | Runnable Python validator implementing the taxonomy's event codes against real video files (needs `pip install numpy opencv-python`, plus `ultralytics` if you want the detector-based checks). |

## Quick start

```bash
# Validate the dataset still matches the taxonomy (types, event codes, severities)
python3 - <<'PY'
import json, collections
taxonomy = json.load(open('datasets/anti_artifact_taxonomy.json'))
valid_codes = set(taxonomy['event_codes']['codes'])
valid_types = {t['id'] for t in taxonomy['artifact_types']}
rows = [json.loads(l) for l in open('datasets/anti_artifact_examples.jsonl')]
assert all(r['artifact'] in valid_types and r['event_code'] in valid_codes for r in rows)
print(len(rows), "records OK;", collections.Counter(r['artifact'] for r in rows))
PY

# Run the validator against a real clip (needs opencv-python; ultralytics optional)
pip install numpy opencv-python ultralytics
python3 scripts/validate_video.py --video clip.mp4 --out clip.events.jsonl \
    --model yolo11n.pt --expected "person:1,knife:1"
```

## How the pieces fit together

1. Generate or receive a clip (e.g. from Runway).
2. Run `scripts/validate_video.py` -- cheap frame-hash checks run on every
   frame, detector-based checks run every `--detect-stride` frames.
3. For each flagged event, look up its `event_code` in
   `anti_artifact_taxonomy.json` to get the human-readable artifact type and
   severity.
4. For borderline flags, feed a text description of the segment through
   `prompts/chain_of_thought_labeling.md` to get a second opinion with
   reasoning.
5. Append confirmed real artifacts (and clean near-miss non-artifacts) to
   `anti_artifact_examples.jsonl` using `prompts/dataset_generation.md`'s
   evaluate-iterate loop, so the few-shot examples keep improving.
