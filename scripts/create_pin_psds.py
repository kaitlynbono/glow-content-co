#!/usr/bin/env python3
"""Automate Pinterest pin PSD creation from CSV data.

Reads pin data from a CSV file (Title, Description, Link, Image URL),
downloads each image, and creates a layered PSD file per pin with:
  - a background pixel layer containing the pin image
  - a title pixel layer with the pin title rendered as text

Usage:
    python scripts/create_pin_psds.py <csv_file> [--output-dir <dir>]

Example:
    python scripts/create_pin_psds.py pinterest_pins_2026-03-06.csv
    python scripts/create_pin_psds.py pinterest_pins_2026-03-06.csv --output-dir psds/march
"""

import argparse
import csv
import re
import sys
import textwrap
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
from psd_tools import PSDImage

# Standard Pinterest pin dimensions (2:3 ratio)
PIN_WIDTH = 1000
PIN_HEIGHT = 1500

# Text overlay settings
TITLE_FONT_SIZE = 52
TITLE_MAX_CHARS_PER_LINE = 30
TITLE_PADDING = 60  # pixels from edges
TITLE_BANNER_OPACITY = 180  # 0–255


def slugify(text: str, max_len: int = 60) -> str:
    """Convert a string to a safe filename slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:max_len]


def load_image(url_or_path: str, timeout: int = 30) -> Image.Image:
    """Load an image from a URL or a local file path and return it as an RGB PIL Image."""
    if url_or_path.startswith(("http://", "https://")):
        response = requests.get(url_or_path, timeout=timeout)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    # Treat as a local file path
    return Image.open(url_or_path).convert("RGB")


def fit_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Resize *image* to fill *width* x *height*, cropping the centre."""
    src_ratio = image.width / image.height
    tgt_ratio = width / height

    if src_ratio > tgt_ratio:
        # Image is wider than target — scale to height, crop sides
        new_h = height
        new_w = int(height * src_ratio)
    else:
        # Image is taller than target — scale to width, crop top/bottom
        new_w = width
        new_h = int(width / src_ratio)

    image = image.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - width) // 2
    top = (new_h - height) // 2
    return image.crop((left, top, left + width, top + height))


def build_title_layer(title: str, width: int, height: int) -> Image.Image:
    """Render *title* text onto a transparent RGBA canvas.

    Returns an RGBA PIL Image the same size as the pin.
    """
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Attempt to load a system font; fall back to Pillow's default
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", TITLE_FONT_SIZE)
    except OSError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", TITLE_FONT_SIZE)
        except OSError:
            font = ImageFont.load_default()

    # Wrap the title text
    lines = textwrap.wrap(title, width=TITLE_MAX_CHARS_PER_LINE)

    # Measure total text block height
    line_height = TITLE_FONT_SIZE + 8
    block_height = len(lines) * line_height

    # Position: bottom of image with padding
    banner_top = height - block_height - TITLE_PADDING * 2
    banner_bottom = height - TITLE_PADDING // 2

    # Semi-transparent dark banner behind text for legibility
    draw.rectangle(
        [(0, banner_top), (width, banner_bottom)],
        fill=(0, 0, 0, TITLE_BANNER_OPACITY),
    )

    # Draw each line of text centred horizontally
    y = banner_top + TITLE_PADDING // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2
        draw.text((x, y), line, fill=(255, 255, 255, 255), font=font)
        y += line_height

    return overlay


def create_pin_psd(
    title: str,
    image: Image.Image,
    output_path: Path,
) -> None:
    """Create a layered PSD at *output_path* from *image* and *title*."""
    bg = fit_image(image, PIN_WIDTH, PIN_HEIGHT)

    # Build the PSD canvas
    psd = PSDImage.new("RGB", (PIN_WIDTH, PIN_HEIGHT))

    # Layer 1 – background image
    psd.create_pixel_layer(bg, name="Background")

    # Layer 2 - title text overlay (composite onto RGBA then convert)
    title_rgba = build_title_layer(title, PIN_WIDTH, PIN_HEIGHT)
    # Flatten the overlay onto a copy of the background for the text layer
    bg_copy = bg.copy().convert("RGBA")
    bg_copy.paste(title_rgba, mask=title_rgba)
    title_layer_img = bg_copy.convert("RGB")
    # We only want the text band visible, so store the composited text region
    # as its own pixel layer at y=0 (full canvas size)
    psd.create_pixel_layer(title_layer_img, name=f"Title - {title[:40]}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    psd.save(str(output_path))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Pinterest pin PSD files from a CSV of pin data."
    )
    parser.add_argument(
        "csv_file",
        help="Path to the CSV file (columns: Title, Description, Link, Image URL).",
    )
    parser.add_argument(
        "--output-dir",
        default="psds",
        help="Directory to write PSD files into (default: psds/).",
    )
    parser.add_argument(
        "--prefix",
        default="pin",
        help="Filename prefix for generated PSDs (default: pin).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []

    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    print(f"Creating PSDs for {len(rows)} pin(s) → {output_dir}/")

    for i, row in enumerate(rows, 1):
        title = row.get("Title", "").strip()
        image_url = row.get("Image URL", "").strip()

        if not image_url:
            msg = f"Pin {i}: missing Image URL — skipped."
            print(f"  WARNING: {msg}")
            errors.append(msg)
            continue

        slug = slugify(title) if title else f"{args.prefix}-{i:03d}"
        output_path = output_dir / f"{args.prefix}-{i:03d}-{slug}.psd"

        print(f"  [{i}/{len(rows)}] {title[:60] or '(no title)'} …", end=" ", flush=True)
        try:
            image = load_image(image_url)
            create_pin_psd(title, image, output_path)
            print(f"saved → {output_path.name}")
        except requests.HTTPError as exc:
            msg = f"Pin {i}: HTTP error downloading image: {exc}"
            print(f"ERROR\n    {msg}")
            errors.append(msg)
        except (OSError, ValueError, TypeError) as exc:
            msg = f"Pin {i}: {exc}"
            print(f"ERROR\n    {msg}")
            errors.append(msg)

    if errors:
        print(f"\n{len(errors)} error(s) occurred:")
        for err in errors:
            print(f"  • {err}")
        return 1

    print(f"\nDone — {len(rows) - len(errors)} PSD(s) written to {output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
