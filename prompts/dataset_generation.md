# Synthetic Dataset Generation + Evaluate-Iterate Prompt

Use this to grow `datasets/anti_artifact_examples.jsonl` with new synthetic
scenarios -- e.g. once you've picked a new content theme (a seasonal Pinterest
aesthetic, a new product category) and want labeled edge cases before you
start generating real Runway clips in that style.

## 1. Generation prompt

```
Generate 10 new video scenarios in the "[YOUR CONTENT THEME, e.g. cozy autumn
kitchen]" aesthetic. For each one, introduce exactly one object-continuity
artifact from this list: identity_inconsistency, temporal_flicker,
frozen_frame, frame_recreation_loop, semantic_rollback, extra_object,
object_count_error, geometry_violation, state_transition.

Cover a spread of artifact types across the 10 (don't repeat the same type
more than twice). Write each as a one-to-two sentence scenario description
in the same style as these existing examples:

- "A chef finishes slicing an onion into 6 pieces; at frame 50 the onion
  appears whole again, uncut." (semantic_rollback)
- "A wildflower meadow pan shows grass-blade shimmer flicker inconsistent
  with wind direction, frames 44-50." (temporal_flicker)

Output one JSON object per line (JSONL), matching this schema:
{"scenario": <string>, "artifact": <type>, "object": <string>,
"frame": <int> or "frame_range": [<int>,<int>]}
```

## 2. Evaluate-and-iterate loop

Run this after generating a batch, to decide whether to keep going or refine
the prompt (mirrors the report's stopping criteria in section 5.3):

1. **Label check** -- run each new scenario through
   `prompts/few_shot_labeling.md` or `prompts/chain_of_thought_labeling.md`
   with a *second* model/prompt and diff the labels against what the
   generation step produced. Disagreements point at ambiguous or
   badly-worded scenarios -- fix the wording or drop them.
2. **Coverage check** -- tally `artifact` types in the new batch plus
   `datasets/anti_artifact_examples.jsonl`. If any of the 9 types has
   noticeably fewer examples than the rest, bias the next generation prompt
   toward it.
3. **Novelty check** -- flag any new scenario whose `scenario` text is a
   near-duplicate (same object + same artifact type + similar wording) of an
   existing record; regenerate instead of appending duplicates.
4. **Append** -- once a batch passes 1-3, append the new lines to
   `datasets/anti_artifact_examples.jsonl` (keep `id` values sequential,
   `video_id` unique).
5. **Stop when:** three consecutive batches produce no scenario that a human
   reviewer disagrees with, and no new failure-mode wording shows up outside
   the 9 known artifact types.

## 3. Validator test prompt

Use this to sanity-check a labeled scenario against what
`scripts/validate_video.py` *should* flag if it saw the equivalent real
footage -- useful when you don't have the actual generated clip yet and just
want to pressure-test the label:

```
Evaluate this scenario: "[SCENARIO TEXT]"
Does it contain an object-continuity artifact? If so:
1. Name the artifact type (from the 9-type taxonomy).
2. Name the closest automated event_code from
   datasets/anti_artifact_taxonomy.json (event_codes.codes).
3. State which validator check would catch it: a temporal_checks check
   (frame hashing) or a detection_checks check (tracker/bbox-based).
```
