# Video Prompt Generator (Custom GPT)

A Custom GPT that interviews the user through a **Task → Context → References → Create → Iterate** framework and outputs ready-to-paste video prompts for Gemini (Veo), Runway, Pika, Kling, and Luma — engineered to avoid the artifacts those tools are most prone to (flicker, morphing limbs, identity drift, camera warping, garbled on-screen text, etc.).

## Setup in ChatGPT

1. Go to **ChatGPT → Explore GPTs → Create**.
2. Skip the conversational builder and open the **Configure** tab directly.
3. Name it (e.g. "Video Prompt Generator") and add a short description.
4. Paste the full contents of [`instructions.md`](./instructions.md) into the **Instructions** field. It's ~7,000 characters, under the 8,000-character limit.
5. Turn off **Web Browsing**, **Code Interpreter**, and **DALL·E image generation** — none are needed and they add irrelevant tool-call options to the conversation.
6. Save/Publish (private to you, or shared, as you prefer).

## Updating the artifact-mitigation guidance

`instructions.md` is the single source of truth. When a video tool changes its behavior (e.g. a new model version fixes a known artifact, or a tool adds a native negative-prompt field), edit the relevant bullet under **Tool-specific notes** or **Artifact knowledge base**, keep the file under 8,000 characters, and re-paste it into the GPT's Instructions field — the GPT builder does not sync from this repo automatically.
