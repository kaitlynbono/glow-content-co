#!/usr/bin/env python3
"""Render the video-prompt right-vs-wrong pin set to PNG via headless Chromium."""
import json
import html
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
CONTENT = json.loads((HERE / "content.json").read_text())
CHROMIUM = "/opt/pw-browsers/chromium"
WIDTH, HEIGHT = 1000, 1500
DATE = "2026-08-19"

TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ background: #0b0f17; }}
  body {{
    width: {width}px; height: {height}px;
    overflow: hidden;
    background: linear-gradient(160deg, #0b0f17 0%, #0f1420 55%, #0b0f17 100%);
    font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    color: #e8ecf3;
    display: flex; flex-direction: column;
    padding: 56px 56px 44px;
  }}
  .kicker {{
    font-size: 21px; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: #7dd3fc; margin-bottom: 10px;
  }}
  .framework {{
    font-size: 15px; font-weight: 600; letter-spacing: 1.5px;
    color: #4b5468; text-transform: uppercase; margin-bottom: 26px;
  }}
  .framework span {{ color: #7dd3fc; }}
  .badge {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 64px; height: 64px; border-radius: 16px;
    background: #1c2333; border: 1px solid #2c3550;
    font-size: 26px; font-weight: 800; color: #7dd3fc;
    margin-bottom: 22px;
  }}
  h1 {{
    font-size: 54px; font-weight: 800; line-height: 1.1;
    letter-spacing: -0.5px; margin-bottom: 38px;
  }}
  .card {{
    border-radius: 20px; padding: 36px 34px;
    border: 2px solid; position: relative;
  }}
  .card .tag {{
    font-size: 19px; font-weight: 800; letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 18px; display: flex; align-items: center; gap: 12px;
  }}
  .mark {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 30px; height: 30px; border-radius: 50%;
    font-size: 18px; font-weight: 900; color: #0b0f17; flex: none;
  }}
  .wrong {{ background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.45); }}
  .wrong .tag {{ color: #f87171; }}
  .wrong .mark {{ background: #f87171; }}
  .right {{ background: rgba(34,197,94,0.08); border-color: rgba(34,197,94,0.45); }}
  .right .tag {{ color: #4ade80; }}
  .right .mark {{ background: #4ade80; }}
  .prompt {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 25px; line-height: 1.5; color: #f1f4f9;
  }}
  .divider {{
    display: flex; align-items: center; gap: 18px;
    margin: 26px 0; color: #3a4258;
  }}
  .divider .line {{ flex: 1; height: 2px; background: #232b3d; }}
  .divider .vs {{
    font-size: 16px; font-weight: 900; letter-spacing: 2px;
    color: #7dd3fc; background: #131a29; border: 1px solid #2c3550;
    border-radius: 999px; padding: 8px 18px;
  }}
  .never {{
    margin-top: 30px;
    background: #dc2626; border-radius: 20px; padding: 34px 34px 36px;
    box-shadow: 0 12px 34px rgba(220,38,38,0.35);
  }}
  .never .tag {{
    font-size: 19px; font-weight: 900; letter-spacing: 1.5px;
    color: #fff5f5; margin-bottom: 14px; display:flex; align-items:center; gap:12px;
  }}
  .never .noicon {{
    display:inline-flex; align-items:center; justify-content:center;
    width:28px; height:28px; border-radius:50%;
    border: 4px solid #ffffff; position: relative; flex: none;
  }}
  .never .noicon::after {{
    content: ""; position: absolute; width: 4px; height: 30px;
    background: #ffffff; transform: rotate(45deg);
  }}
  .never .body {{
    font-size: 26px; font-weight: 600; line-height: 1.46; color: #ffffff;
  }}
  .prevents {{
    margin-top: 26px; display: flex; align-items: center; gap: 14px;
  }}
  .prevents .label {{
    font-size: 15px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;
    color: rgba(255,255,255,0.6);
  }}
  .prevents .chip {{
    font-size: 18px; font-weight: 800; color: #b91c1c;
    background: #ffffff;
    border-radius: 999px; padding: 8px 20px;
  }}
  .footer {{
    margin-top: 28px; padding-top: 22px; display: flex; justify-content: space-between; align-items: center;
    font-size: 18px; color: #5b6478; letter-spacing: 0.5px;
    border-top: 1px solid #1c2333;
  }}
</style></head>
<body>
  <div class="kicker">Video Prompt Engineering</div>
  <div class="framework">Task <span>&rarr;</span> Context <span>&rarr;</span> References <span>&rarr;</span> Evaluate <span>&rarr;</span> Iterate</div>
  <div class="badge">{num}</div>
  <h1>{topic}: The Right Way vs. The Wrong Way</h1>

  <div class="card wrong">
    <div class="tag"><span class="mark">&times;</span> Wrong</div>
    <div class="prompt">&ldquo;{wrong}&rdquo;</div>
  </div>

  <div class="divider"><div class="line"></div><div class="vs">VS</div><div class="line"></div></div>

  <div class="card right">
    <div class="tag"><span class="mark">&#10003;</span> Right</div>
    <div class="prompt">&ldquo;{right}&rdquo;</div>
  </div>

  <div class="never">
    <div class="tag"><span class="noicon"></span> Never Do This &mdash; No Exceptions</div>
    <div class="body">{never}</div>
    <div class="prevents">
      <span class="label">Prevents</span>
      <span class="chip">{prevents}</span>
    </div>
  </div>

  <div class="footer">
    <span>Glow Content Co</span>
    <span>Right vs. Wrong Prompting Series</span>
  </div>
</body></html>
"""


def esc(s):
    return html.escape(s, quote=False)


def main():
    out_dir = HERE
    for item in CONTENT:
        page = TEMPLATE.format(
            width=WIDTH,
            height=HEIGHT,
            num=esc(item["num"]),
            topic=esc(item["topic"]),
            wrong=esc(item["wrong"]),
            right=esc(item["right"]),
            never=esc(item["never"]),
            prevents=esc(item["prevents"]),
        )
        html_path = out_dir / f"_render_{item['num']}.html"
        html_path.write_text(page)

        out_path = out_dir / f"video-prompt-pin-{item['num']}-{DATE}.png"
        subprocess.run(
            [
                CHROMIUM,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                f"--screenshot={out_path}",
                f"--window-size={WIDTH},{HEIGHT}",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                html_path.resolve().as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        html_path.unlink()
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
