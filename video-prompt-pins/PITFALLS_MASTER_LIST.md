# The Master List of AI Video Prompt Pitfalls

16 failure modes that show up across Runway, Sora, Kling, Veo, and every other current text/image-to-video model — what causes each one, what it looks like on screen, and the fix. This is the reference the pin series, the master prompt template, and the system prompt are all built from.

Framework: **Task → Context → References → Evaluate → Iterate**. Every pitfall below traces back to one pillar of the prompt (Subject, Environment, Lighting, Action, Motion, Objects, Camera, Style, Negative Prompt, or On-Screen Text) going unspecified. Fix the pillar responsible — never rewrite the whole prompt.

---

## Quick Reference

| # | Pitfall | Root Cause | Pillar to Fix |
|---|---------|------------|----------------|
| 1 | Face & Identity Drift | Character appearance undescribed after shot 1 | Subject |
| 2 | Warping & Geometry Smear | Multiple camera movements stacked in one generation | Camera |
| 3 | Limb & Texture Warping | Fast/rotational motion combined with fine detail or loose fabric/hair | Motion + Style |
| 4 | Morphing Scenery | Background described in a single vague word | Environment |
| 5 | Frame-to-Frame Flicker | Missing light source and color temperature | Lighting |
| 6 | Melting Hands & Clipping | Hand-object interaction under-specified | Action |
| 7 | Mid-Clip Style Drift | Vague style words ("cinematic," "artistic") with no fixed definition | Style |
| 8 | Uncontrolled Failure Modes | No negative prompt / exclusion terms at all | Negative Prompt |
| 9 | Rushed, Unnatural Motion | More than one major action packed into a single clip | Task / Pacing |
| 10 | Drift Across Cuts | Character/setting reworded instead of reused between shots | References |
| 11 | Garbled On-Screen Text | Model asked to render legible text | On-Screen Text |
| 12 | Stutter & Judder | Movement speed left unspecified | Motion |
| 13 | Object Teleporting & State Errors | Object position/count/state never anchored | Objects |
| 14 | Texture Boiling / Shimmer | Fine repetitive detail kept in sharp focus for a static/slow shot | Style / Environment |
| 15 | Clipping & Gravity Errors | Physical interaction described without its result | Action |
| 16 | Day-for-Night Flip Between Cuts | Lighting not explicitly carried over between shots | References + Lighting |

---

## The Full List

### 1. Face & Identity Drift
**Symptom:** The same character's face, hair, or outfit subtly (or not-so-subtly) changes from one moment to the next, or between shots in a sequence.
**Cause:** The subject's appearance was only described once, loosely, or not re-specified in later shots.
**Fix:** Give every recurring character a full, specific description — age, build, hair, exact outfit — and copy that description verbatim into every subsequent shot.

### 2. Warping & Geometry Smear
**Symptom:** Shapes stretch, bend, or smear, especially at the edges of the frame or around moving subjects.
**Cause:** The prompt asked for more than one camera movement at once (e.g. pan + zoom + dolly).
**Fix:** Specify exactly one camera movement, or explicitly request a locked-off static shot.

### 3. Limb & Texture Warping
**Symptom:** Arms, hair, or clothing distort or smear specifically during fast or spinning motion.
**Cause:** Fast/rotational motion was paired with high-detail texture, patterns, or loose hair/fabric — detail the model can't track at speed.
**Fix:** Slow the motion, simplify the texture (solid colors, minimal hair movement), or don't ask for both at once.

### 4. Morphing Scenery
**Symptom:** The background reshapes itself — trees rearrange, walls shift — over the course of a shot longer than a couple seconds.
**Cause:** The environment was described in one vague word ("a forest," "a room") with no concrete detail to hold onto.
**Fix:** Describe the environment with specific physical detail and lock the camera so the same elements stay visible throughout.

### 5. Frame-to-Frame Flicker
**Symptom:** Brightness or color temperature pulses or shifts between frames.
**Cause:** No light source, direction, or color temperature was specified.
**Fix:** Always name the light source, its direction, and a Kelvin value, and state that it doesn't change for the clip's duration.

### 6. Melting Hands & Clipping
**Symptom:** Fingers merge, extra digits appear, or a held object passes through the hand.
**Cause:** The hand-object interaction was described in a single vague verb ("picks up") with no detail on grip or motion.
**Fix:** Give every hand-object interaction at least one full clause: which fingers, what grip, how far, how fast.

### 7. Mid-Clip Style Drift
**Symptom:** The visual style — grain, color grade, lens look — shifts partway through the clip.
**Cause:** The prompt used an undefined style word like "cinematic" or "artistic," which the model reinterprets shot to shot.
**Fix:** Use concrete technical terms: film stock/grain, named color grade, lens/aperture, depth of field.

### 8. Uncontrolled Failure Modes
**Symptom:** Any combination of the artifacts on this list, showing up because nothing was explicitly excluded.
**Cause:** The prompt had no negative prompt at all.
**Fix:** Always include exclusions — at minimum: no text overlays, no extra limbs, no camera cuts, no background characters, no motion blur on the face.

### 9. Rushed, Unnatural Motion
**Symptom:** Motion looks sped-up, compressed, or physically implausible for the time given.
**Cause:** The prompt asked for more than one major action within a single short clip.
**Fix:** One action per generation. Split multi-action sequences into separate shots.

### 10. Drift Across Cuts
**Symptom:** A character or location subtly changes between shot 1 and shot 2 of the same sequence.
**Cause:** The description was reworded — even slightly — instead of reused.
**Fix:** Copy the Subject, Environment, and Style text from the prior shot verbatim; change only the Action line.

### 11. Garbled On-Screen Text
**Symptom:** Signs, labels, or captions render as illegible scribbled characters.
**Cause:** The model was asked to render legible text, which current video models can't reliably do.
**Fix:** Default to no on-screen text. If signage must appear, keep it out of focus and under 10% of frame width.

### 12. Stutter & Judder
**Symptom:** Motion skips between poses instead of flowing continuously; movement looks jerky.
**Cause:** Speed and pacing were left to the model's discretion.
**Fix:** State an explicit constant pace or named easing for every movement in the shot.

### 13. Object Teleporting & State Errors
**Symptom:** A prop jumps position, duplicates, changes appearance, or vanishes without an action causing it.
**Cause:** The object's position, count, or state was never anchored after being introduced.
**Fix:** Name every key prop's identity, position, and state, and state explicitly that it stays unchanged unless the action line changes it.

### 14. Texture Boiling / Shimmer
**Symptom:** Fine repetitive detail — brick, foliage, fabric weave — crawls or shimmers even when nothing is moving.
**Cause:** High-frequency static detail was kept in sharp focus for a static or slow shot; the model can't hold it steady frame to frame.
**Fix:** Keep fine repetitive detail softly out of focus, or hold a single fixed exposure/focus for the whole shot.

### 15. Clipping & Gravity Errors
**Symptom:** Objects pass through surfaces, float, or ignore momentum and gravity entirely.
**Cause:** A physical interaction (falling, bouncing, colliding) was described without stating its result.
**Fix:** Always state what happens on contact — compression, rebound height, settling — not just the action that leads to it.

### 16. Day-for-Night Flip Between Cuts
**Symptom:** Lighting or time of day jumps inconsistently between shots in the same sequence.
**Cause:** Lighting wasn't explicitly carried over between shots, so the model re-guesses it each time.
**Fix:** Restate the same key light, color temperature, and shadow direction in every shot unless a time-skip is explicitly written into the prompt.

---
Glow Content Co · Video Prompt Engineering — Right vs. Wrong Series
