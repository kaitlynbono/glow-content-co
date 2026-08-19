# Video Prompt Master Template

The reusable prompt scaffold behind the *Right vs. Wrong* pin series. Fill in every bracket before you generate — an empty or vague bracket is exactly what causes the artifacts the pin series warns about (drift, warping, flicker, morphing, melting hands, garbled text).

Framework: **Task → Context → References → Evaluate → Iterate**
- **Task** — the one action this specific generation must produce (see Pacing below: one action, nothing more)
- **Context** — Subject + Environment + Lighting + Style, held constant and reused verbatim across every shot in the sequence
- **References** — the exact wording from a prior shot's Subject/Environment/Style blocks, copied in unchanged, so identity doesn't drift between cuts
- **Evaluate** — watch the output against the checklist below before accepting it
- **Iterate** — when a check fails, fix only the section responsible (see "which pillar" column) and regenerate; don't rewrite the whole prompt

---

## The Template

```
SUBJECT: [age, build, hair color/length/style, exact outfit — every visual trait
that must not change, even if the subject appears in only one shot]

ENVIRONMENT: [specific location + concrete physical details — materials, textures,
what's in the background — nothing left as a single vague noun]

LIGHTING: [light source, direction, and color temperature in Kelvin — e.g.
"single warm key light, camera left, 45°, 3200K"]

ACTION: [one clause per motion, especially for hands/limbs — describe grip,
distance, speed, and body part explicitly; one action total, at a natural pace]

CAMERA: [exactly one movement type, or "locked-off static" — never combine
pan + zoom + dolly in the same generation]

STYLE: [concrete technical terms — film stock/grain, color grade, lens/aperture,
depth of field — never a bare adjective like "cinematic" or "artistic"]

NEGATIVE PROMPT: [explicit exclusions — no text overlays, no extra limbs,
no camera cuts, no background characters, no motion blur on the face, plus
anything specific to this shot]

ON-SCREEN TEXT: none — if signage must appear, keep it out of focus and
under 10% of frame width
```

For shot 2+ in a sequence: copy the SUBJECT, ENVIRONMENT, and STYLE lines from shot 1 **verbatim** — change only the ACTION line.

---

## Never Do This — No Exceptions

| # | Rule | Prevents |
|---|------|----------|
| 1 | Never leave a recurring character's appearance undescribed after the first shot. | Face & identity drift |
| 2 | Never stack more than one camera movement in a single generation. | Warping & geometry smear |
| 3 | Never pair fast or rotational motion with high-detail textures, patterns, or loose hair/fabric. | Limb & texture warping |
| 4 | Never describe a background in one vague word for any shot over 3 seconds. | Morphing scenery |
| 5 | Never omit a light source and color temperature. | Frame-to-frame flicker |
| 6 | Never describe a hand-object interaction in fewer than one full clause. | Melting hands & clipping |
| 7 | Never let "cinematic" (or similar) stand alone as a style instruction. | Mid-clip style drift |
| 8 | Never submit a generation with zero exclusion terms. | Every known failure mode |
| 9 | Never request more than one major action inside a single short clip. | Rushed, unnatural motion |
| 10 | Never reword a character or setting description between shots in one sequence. | Drift across cuts |
| 11 | Never ask a video model to render legible on-screen text. | Garbled text artifacts |

---

## Evaluate Checklist (run before accepting any generation)

- [ ] Does the subject's face/outfit match shot 1 exactly? → if not, fix **Subject**
- [ ] Any warping or smearing on limbs, hair, or fabric during motion? → fix **Action** or **Camera**
- [ ] Does the background stay stable, or does it redraw/morph? → fix **Environment**
- [ ] Any flicker in brightness or color between frames? → fix **Lighting**
- [ ] Hands/fingers intact through the whole grip-and-release? → fix **Action**
- [ ] Does the look stay consistent start to end, or shift style mid-clip? → fix **Style**
- [ ] Any of the 11 never-rules violated? → fix that pillar only, then regenerate

---

## Example — Filled Out

```
SUBJECT: 30-year-old woman, shoulder-length red curly hair, tan trench coat
ENVIRONMENT: rain-slicked city street at dusk, wet asphalt reflecting neon signage, camera fixed so the street layout stays constant
LIGHTING: mixed warm streetlamp key from camera left + cool blue ambient fill, fixed 3200K/6500K balance, no change through the clip
ACTION: she walks forward at a steady, even pace, arms swinging naturally, no rushing
CAMERA: locked-off static tripod shot, no camera movement
STYLE: 35mm film grain, muted teal-and-orange grade, shallow depth of field at f/2.8
NEGATIVE PROMPT: no text overlays, no extra limbs, no camera cuts, no background characters, no motion blur on the face
ON-SCREEN TEXT: none
```

---
Glow Content Co · Video Prompt Engineering — Right vs. Wrong Series
