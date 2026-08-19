# Few-Shot Artifact Labeling Prompt

Use this to have an LLM label a new video scenario (or a shot-by-shot description
you write yourself after watching a Runway/AI-generated clip) with a structured
artifact record. Swap the three examples below for ones closer to your own
content if you want tighter style matching -- more are in
`datasets/anti_artifact_examples.jsonl`.

```
Task: Identify object-continuity artifacts in a video sequence. For each
scenario, output one JSON object per artifact found, using this schema:
{"scenario": <string>, "artifact": <one of identity_inconsistency |
temporal_flicker | frozen_frame | frame_recreation_loop | semantic_rollback |
extra_object | object_count_error | geometry_violation | state_transition>,
"object": <string>, "frame": <int> or "frame_range": [<int>,<int>],
"details": <string, optional>}
If there is no artifact, output {"artifact": "none"}.

Example 1:
Video Description: "A barista steams milk. In frame 12 a second, unexplained
coffee cup appears beside the first."
Label: {"scenario": "A barista steams milk. In frame 12 a second, unexplained
coffee cup appears beside the first.", "artifact": "extra_object", "object":
"cup", "frame": 12}

Example 2:
Video Description: "A cyclist rides through a park; frames 80-84 are
identical, showing no wheel rotation or background motion."
Label: {"scenario": "A cyclist rides through a park; frames 80-84 are
identical, showing no wheel rotation or background motion.", "artifact":
"frozen_frame", "object": "cyclist", "frame_range": [80, 84]}

Example 3:
Video Description: "A chef finishes slicing an onion into 6 pieces; at frame
50 the onion appears whole again, uncut."
Label: {"scenario": "A chef finishes slicing an onion into 6 pieces; at frame
50 the onion appears whole again, uncut.", "artifact": "semantic_rollback",
"object": "onion", "frame": 50}

Video Description: "[INSERT YOUR SCENARIO HERE]"
Label:
```

**When to use:** fast, cheap labeling of scenarios you're fairly confident
about (a human already spotted the glitch while reviewing a clip and just
needs it turned into a structured record for `datasets/anti_artifact_examples.jsonl`).
