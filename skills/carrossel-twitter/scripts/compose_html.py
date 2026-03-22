#!/usr/bin/env python3
"""
Compose a social media post card as HTML.

Generates photo with Gemini, then creates an HTML file with the full card layout.
Open the HTML in a browser to view/screenshot.

Usage:
    python compose_html.py --text "Texto com <b>bold</b>." \
                           --image photo.png \
                           --output slide.html

    python compose_html.py --text "Texto com <b>bold</b>." \
                           --image-prompt "dark workspace with monitors" \
                           --output slide.html
"""

import argparse
import base64
import os
from pathlib import Path

DEFAULT_AVATAR = "/home/vault/06-conteúdo/Referencias Jonathan/avatar_instagram.jpg"


def image_to_base64(path):
    """Convert image file to base64 data URI."""
    p = Path(path)
    if not p.exists():
        return ""
    ext = p.suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp", "gif": "image/gif"}.get(ext.lstrip("."), "image/png")
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def generate_html(text, image_path, avatar_path=None):
    """Generate the HTML card."""
    avatar = avatar_path or DEFAULT_AVATAR
    avatar_b64 = image_to_base64(avatar)
    image_b64 = image_to_base64(image_path) if image_path and Path(image_path).exists() else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: #f0f0f0;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 40px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}

  .card {{
    width: 1080px;
    height: 1350px;
    background: #ffffff;
    border-radius: 4px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  .label-top {{
    position: absolute;
    top: 18px;
    left: 40px;
    font-size: 13px;
    color: #999;
    font-weight: 400;
  }}

  .label-bottom {{
    position: absolute;
    bottom: 18px;
    right: 40px;
    font-size: 13px;
    color: #999;
    font-weight: 400;
  }}

  .header {{
    display: flex;
    align-items: center;
    padding: 55px 40px 0 40px;
    gap: 14px;
  }}

  .avatar {{
    width: 52px;
    height: 52px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }}

  .name-block {{
    display: flex;
    flex-direction: column;
    gap: 1px;
  }}

  .name-row {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .name {{
    font-size: 18px;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.2;
  }}

  .checkmark {{
    width: 18px;
    height: 18px;
    display: inline-flex;
  }}

  .handle {{
    font-size: 15px;
    color: #888;
    font-weight: 400;
    line-height: 1.2;
  }}

  .content {{
    padding: 24px 40px 0 40px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }}

  .text {{
    font-size: 28px;
    line-height: 1.45;
    color: #1a1a1a;
    font-weight: 400;
    white-space: pre-line;
  }}

  .text b, .text strong {{
    font-weight: 700;
  }}

  .photo-container {{
    margin-top: 20px;
    padding: 0 40px;
    flex: 1;
    display: flex;
    align-items: flex-start;
  }}

  .photo {{
    width: 100%;
    border-radius: 12px;
    object-fit: cover;
    max-height: 500px;
  }}

  .icons {{
    display: flex;
    align-items: center;
    padding: 20px 40px;
    gap: 20px;
  }}

  .icons svg {{
    width: 26px;
    height: 26px;
    color: #333;
    cursor: pointer;
  }}

  .icons .spacer {{
    flex: 1;
  }}
</style>
</head>
<body>

<div class="card">
  <span class="label-top">· conteúdo</span>

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

  <div class="content">
    <div class="text">{text}</div>
  </div>

  {"" if not image_b64 else f'''
  <div class="photo-container">
    <img class="photo" src="{image_b64}" alt="photo">
  </div>
  '''}

  <div class="icons">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
    </svg>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
    </svg>
    <span class="spacer"></span>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
    </svg>
  </div>

  <span class="label-bottom">· conteúdo</span>
</div>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Compose post card as HTML")
    parser.add_argument("--text", "-t", required=True, help="Text content (HTML: use <b> for bold)")
    parser.add_argument("--image", "-i", default=None, help="Path to photo image")
    parser.add_argument("--output", "-o", default="./card.html", help="Output HTML path")
    parser.add_argument("--avatar", "-a", default=None, help="Avatar image path")

    args = parser.parse_args()

    html = generate_html(args.text, args.image, args.avatar)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"HTML card saved to: {out}")


if __name__ == "__main__":
    main()
