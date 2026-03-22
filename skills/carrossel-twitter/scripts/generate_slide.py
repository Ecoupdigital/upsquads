#!/usr/bin/env python3
"""
Generate a complete carousel slide: photo via Gemini API + card via HTML + screenshot via Playwright.

Usage:
    python generate_slide.py \
      --text "Texto com <b>bold</b>." \
      --photo-prompt "dark workspace with monitors" \
      --output ./slide-1.png

    # With custom avatar
    python generate_slide.py \
      --text "Texto." \
      --photo-prompt "terminal with code" \
      --output ./slide.png \
      --avatar ./custom.jpg
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
GEMINI_SCRIPT = Path.home() / ".claude" / "skills" / "gemini" / "scripts" / "generate_image.py"
DEFAULT_AVATAR = "/home/vault/06-conteúdo/Referencias Jonathan/avatar_instagram.jpg"
DEFAULT_MODEL = "gemini-2.5-flash-image"  # Cheapest


def img_to_b64(path):
    p = Path(path)
    if not p.exists():
        return ""
    ext = p.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(ext, "image/png")
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def generate_photo(prompt, output_path, model=None):
    """Generate photo via Gemini API."""
    m = model or os.environ.get("NANOBANANA_MODEL", DEFAULT_MODEL)
    cmd = [
        sys.executable, str(GEMINI_SCRIPT),
        prompt, str(output_path),
        "--aspect-ratio", "16:9",
        "--size", "1K",
        "-m", m
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        print(f"Photo generation failed: {result.stderr}", file=sys.stderr)
        return False
    return True


def build_html(text, photo_b64, avatar_b64):
    """Build the card HTML with auto-resize text."""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .card {{
    width: 1080px;
    height: 1350px;
    background: #ffffff;
    display: flex;
    flex-direction: column;
    padding: 99px 89px 89px 89px;
    overflow: hidden;
  }}
  .header {{
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 28px;
    flex-shrink: 0;
  }}
  .avatar {{
    width: 68px;
    height: 68px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }}
  .name-block {{
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}
  .name-row {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .name {{
    font-size: 26px;
    font-weight: 700;
    color: #0f0f0f;
    letter-spacing: -0.01em;
  }}
  .checkmark {{
    width: 24px;
    height: 24px;
  }}
  .handle {{
    font-size: 20px;
    color: #71767b;
    font-weight: 400;
  }}
  .text-content {{
    line-height: 1.5;
    color: #0f0f0f;
    font-weight: 400;
    margin-bottom: 12px;
    letter-spacing: -0.01em;
    flex-shrink: 0;
  }}
  .text-content b, .text-content strong {{
    font-weight: 700;
  }}
  .photo-wrapper {{
    flex: 1;
    display: flex;
    align-items: flex-end;
    min-height: 0;
  }}
  .photo {{
    width: 100%;
    border-radius: 16px;
    object-fit: cover;
    display: block;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <img class="avatar" src="{avatar_b64}" alt="avatar">
    <div class="name-block">
      <div class="name-row">
        <span class="name">Jonathan Renan</span>
        <svg class="checkmark" viewBox="0 0 22 22" fill="none">
          <circle cx="11" cy="11" r="11" fill="#1D9BF0"/>
          <path d="M9.5 14.25L6.75 11.5L7.81 10.44L9.5 12.13L14.19 7.44L15.25 8.5L9.5 14.25Z" fill="white"/>
        </svg>
      </div>
      <span class="handle">@jonathanrenan.ia</span>
    </div>
  </div>
  <div class="text-content" id="textContent">
    {text}
  </div>
  <div class="photo-wrapper">
    <img class="photo" src="{photo_b64}" alt="photo">
  </div>
</div>
<script>
  function autoFitText() {{
    const card = document.querySelector('.card');
    const header = document.querySelector('.header');
    const text = document.getElementById('textContent');
    const photo = document.querySelector('.photo');
    if (!photo.complete) {{ photo.onload = autoFitText; return; }}
    const cardStyle = getComputedStyle(card);
    const padTop = parseFloat(cardStyle.paddingTop);
    const padBot = parseFloat(cardStyle.paddingBottom);
    const cardInnerHeight = 1350 - padTop - padBot;
    const headerHeight = header.offsetHeight + 28;
    const gap = 12;
    const cardInnerWidth = 1080 - 89 * 2;
    const photoRatio = photo.naturalHeight / photo.naturalWidth;
    const photoHeight = cardInnerWidth * photoRatio;
    const availableHeight = cardInnerHeight - headerHeight - gap - photoHeight;
    let min = 18, max = 52, best = 34;
    for (let i = 0; i < 20; i++) {{
      const mid = (min + max) / 2;
      text.style.fontSize = mid + 'px';
      if (text.scrollHeight <= availableHeight) {{ best = mid; min = mid + 0.5; }}
      else {{ max = mid - 0.5; }}
    }}
    text.style.fontSize = best + 'px';
  }}
  window.addEventListener('load', function() {{ setTimeout(autoFitText, 100); }});
</script>
</body>
</html>"""


def html_to_png(html_path, output_path):
    """Screenshot HTML to PNG using Playwright."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(1500)  # Wait for font load + auto-resize
        card = page.query_selector(".card")
        card.screenshot(path=str(output_path))
        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Generate carousel slide (photo + HTML → PNG)")
    parser.add_argument("--text", "-t", required=True, help="Text content (HTML: <b> for bold)")
    parser.add_argument("--photo-prompt", "-p", required=True, help="Prompt for the photo image")
    parser.add_argument("--output", "-o", default="./slide.png", help="Output PNG path")
    parser.add_argument("--avatar", "-a", default=None, help="Avatar image path")
    parser.add_argument("--model", "-m", default=None, help="Gemini model for photo")

    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1. Generate photo
    photo_path = out.with_suffix(".photo.png")
    print(f"[1/3] Generating photo...")
    if not generate_photo(args.photo_prompt, photo_path, args.model):
        sys.exit(1)

    # 2. Build HTML
    print(f"[2/3] Building HTML card...")
    avatar_b64 = img_to_b64(args.avatar or DEFAULT_AVATAR)
    photo_b64 = img_to_b64(str(photo_path))
    html = build_html(args.text, photo_b64, avatar_b64)

    html_path = out.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")

    # 3. Screenshot
    print(f"[3/3] Screenshot → PNG...")
    html_to_png(str(html_path.resolve()), str(out))

    # Cleanup temp files
    photo_path.unlink(missing_ok=True)
    html_path.unlink(missing_ok=True)

    size_kb = out.stat().st_size / 1024
    print(f"Done! {out} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
