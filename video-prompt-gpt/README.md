# Video Prompt Generator (Custom GPT)

A Custom GPT that interviews the user through a **Task → Context → References → Create → Iterate** framework and outputs ready-to-paste video prompts for Gemini (Veo), Runway, Pika, Kling, and Luma — engineered to avoid the artifacts those tools are most prone to.

The core design problem this solves: users usually can't name what went wrong in a bad AI video clip ("it looks melty," "the background is swimming"). The **Symptom Finder** table in `instructions.md` maps ~18 plain-language descriptions to the technical artifact and the specific prompt fix, so the GPT can diagnose without requiring vocabulary the user doesn't have. It also uses ChatGPT's built-in vision — if the user attaches a screenshot of the bad frame, the GPT reads it directly instead of asking for a description.

## Setup in ChatGPT

1. Go to **ChatGPT → Explore GPTs → Create**.
2. Skip the conversational builder and open the **Configure** tab directly.
3. Name it (e.g. "Video Prompt Generator") and add a short description.
4. Paste the full contents of [`instructions.md`](./instructions.md) into the **Instructions** field. It's ~7,500 characters, under the 8,000-character limit — leave some headroom, since paste formatting can add a few characters.
5. Turn off **Web Browsing**, **Code Interpreter**, and **DALL·E image generation** — none are needed and they add irrelevant tool-call options to the conversation. Leave image understanding as-is; it's on by default with no separate toggle, and the Symptom Finder relies on it.
6. Save/Publish (private to you, or shared, as you prefer).

## Updating the guidance

`instructions.md` is the single source of truth. When a video tool changes behavior (a model update fixes a known artifact, or a tool adds a native negative-prompt or consistency feature), update the relevant row in **Symptom Finder** or the matching bullet in **Tool-specific notes**, keep the file comfortably under 8,000 characters, and re-paste it into the GPT's Instructions field — the GPT builder does not sync from this repo automatically.
