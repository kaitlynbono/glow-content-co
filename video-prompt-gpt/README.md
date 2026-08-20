# Video Prompt Generator (Custom GPT)

A Custom GPT that interviews the user through a **Task → Context → References → Create → Iterate** framework and outputs ready-to-paste video prompts for Gemini (Veo), Runway, Pika, Kling, and Luma — engineered to avoid the artifacts those tools are most prone to.

The core design problem this solves: users usually can't name what went wrong in a bad AI video clip ("it looks melty," "the background is swimming"). The **Symptom Finder** table in `instructions.md` maps ~18 plain-language descriptions to the technical artifact and the specific prompt fix. It also uses ChatGPT's built-in vision — if the user attaches a screenshot of the bad frame, the GPT reads it directly instead of asking for a description.

`knowledge/lifestyle-visual-reference.csv` is a second, complementary layer: a structured dataset of ~30 everyday lifestyle actions (packing a suitcase, skincare routines, cutting fruit, cooking, cleaning, fitness, fashion, desk work, seasonal moments), each with a recommended shot type, camera move, motion beats, its specific artifact risks, whether it loops cleanly, and a ready-to-use example prompt. It's written from prompt-engineering principles and the same failure patterns in the Symptom Finder, not from footage testing against each tool — treat it as a strong, editable starting point rather than a guarantee. It exists so the GPT can ground a "pack a suitcase" or "cut a mango" request in a specific, tested shot breakdown instead of improvising one from a generic description, and it's easy to extend: add a row for any action that comes up often.

Note: **actual reference photos/videos aren't included.** This is a text dataset, not an image library — sourcing real photos raises licensing questions, and Custom GPT Knowledge retrieval doesn't reliably search image content anyway. If you want true visual references for a specific action, attach a photo directly in a chat with the GPT; vision reads it live.

## Setup in ChatGPT

1. Go to **ChatGPT → Explore GPTs → Create**.
2. Skip the conversational builder and open the **Configure** tab directly.
3. Name it (e.g. "Video Prompt Generator") and add a short description.
4. Paste the full contents of [`instructions.md`](./instructions.md) into the **Instructions** field. It's ~7,700 characters, under the 8,000-character limit — leave headroom, since paste formatting can add a few characters.
5. Under **Knowledge**, upload `knowledge/lifestyle-visual-reference.csv`.
6. Turn ON **Code Interpreter & Data Analysis** — the GPT needs it to load and precisely filter the CSV by action; without it, ChatGPT's default file search does fuzzy text retrieval over the file, which is far less reliable for picking one exact row out of ~30. Turn off **Web Browsing** and **DALL·E image generation** — not needed here. Leave image understanding as-is; it's on by default with no separate toggle, and the Symptom Finder relies on it.
7. Save/Publish (private to you, or shared, as you prefer).

## Updating the guidance

`instructions.md` is the single source of truth for behavior; `knowledge/lifestyle-visual-reference.csv` is the source of truth for lifestyle-action shot data. When a video tool changes behavior, update the relevant row in **Symptom Finder** or **Tool-specific notes** and re-paste `instructions.md` into the GPT's Instructions field (keep it comfortably under 8,000 characters). To add or correct a lifestyle action, edit the CSV and re-upload it under Knowledge — the GPT builder does not sync from this repo automatically either way.
