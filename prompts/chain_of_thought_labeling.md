# Chain-of-Thought Artifact Labeling Prompt

Use this for ambiguous or multi-artifact clips where a one-shot label is
likely to be wrong -- e.g. a scene with several objects, or one where it's
unclear whether a change is a real continuity break or just an intentional
edit/cut.

```
Task: Determine whether the following video scenario contains any
object-continuity artifacts. Reason step by step, then give a structured
label (or a list of labels if there is more than one artifact).

Scenario: "A chef is chopping vegetables. In frame 10, the knife splits into
two knives, each moving separately."

Answer:
Step 1: Identify the objects in the scene -- the chef and the knife.
Step 2: Check for known failure patterns: does an object change identity,
freeze, loop, roll back to an earlier state, gain/lose a copy of itself,
warp its geometry, or teleport?
Step 3: The knife splitting into two moving independently is physically
impossible and matches the "extra_object" pattern (an object duplicates
without a valid in-scene cause).
Step 4: Confirm it isn't better explained by a cut/edit or occlusion --
there's no scene change or hand blocking the view, so it's a genuine
artifact.
Conclusion: object-continuity artifact confirmed.
Label: {"scenario": "A chef is chopping vegetables. In frame 10, the knife
splits into two knives, each moving separately.", "artifact": "extra_object",
"object": "knife", "frame": 10, "details": "knife split into two independently
moving instances"}

Scenario: "[INSERT YOUR SCENARIO HERE]"

Answer:
Step 1:
```

**Label schema:** same as `prompts/few_shot_labeling.md` --
`artifact` must be one of the 9 types in `datasets/anti_artifact_taxonomy.json`
(`artifact_types[].id`); use `"artifact": "none"` with a one-line justification
if step 4 rules the change out as a real edit rather than an artifact.

**When to use:** complex or borderline cases, multi-object scenes, or when
you want the reasoning trace kept (e.g. to show a reviewer why something was
or wasn't flagged) rather than just the final label.
