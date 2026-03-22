#!/usr/bin/env python3
"""
Generate a news-style carousel slide: photo via Gemini + HTML card + Playwright screenshot.

Layout: image top 50% with gradient overlay → title large uppercase → body text → footer

Usage:
    python generate_slide.py \
      --title "TÍTULO GRANDE" \
      --body "Texto explicativo aqui." \
      --photo-prompt "dramatic scene description" \
      --output ./slide-1.png

    # Last slide (CTA)
    python generate_slide.py \
      --title "CONTEÚDO NÃO ACABOU" \
      --body "Texto CTA." \
      --photo-prompt "scene" \
      --output ./slide-6.png \
      --cta "SALVE PARA DEPOIS"

    # Custom title color
    python generate_slide.py \
      --title "A MULTA..." \
      --body "Texto." \
      --photo-prompt "scene" \
      --output ./slide.png \
      --title-color "#ff3333"

    # Sources/credits (slide 1 style)
    python generate_slide.py \
      --title "TÍTULO" \
      --photo-prompt "scene" \
      --output ./slide.png \
      --sources "Fontes: CNN Brasil, Metrópoles"
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GEMINI_SCRIPT = Path.home() / ".claude" / "skills" / "gemini" / "scripts" / "generate_image.py"
DEFAULT_MODEL = "gemini-2.5-flash-image"
DEFAULT_HANDLE = "@jonathanrenan.ia"


def img_to_b64(path):
    p = Path(path)
    if not p.exists():
        return ""
    ext = p.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(ext, "image/png")
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def generate_photo(prompt, output_path, model=None):
    m = model or os.environ.get("NANOBANANA_MODEL", DEFAULT_MODEL)
    cmd = [
        sys.executable, str(GEMINI_SCRIPT),
        prompt, str(output_path),
        "--aspect-ratio", "1:1",
        "--size", "1K",
        "-m", m
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        print(f"Photo generation failed: {result.stderr}", file=sys.stderr)
        return False
    return True


def build_html(title, body, photo_b64, title_color="#ffffff", sources=None,
               cta="ARRASTA PRO LADO >>>", handle=DEFAULT_HANDLE):
    sources_html = f'<div class="sources">{sources}</div>' if sources else ""
    body_html = f'<div class="body-text">{body}</div>' if body else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ margin: 0; padding: 0; }}

  .card {{
    width: 1080px;
    height: 1350px;
    background: #000000;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* ===== IMAGEM + GRADIENTE ===== */
  .image-section {{
    position: relative;
    width: 100%;
    height: 50%;
    flex-shrink: 0;
  }}

  .image-section img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}

  .gradient-overlay {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60%;
    background: linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0) 0%,
      rgba(0, 0, 0, 0.4) 30%,
      rgba(0, 0, 0, 0.85) 70%,
      rgba(0, 0, 0, 1) 100%
    );
  }}

  /* ===== CONTEÚDO TEXTO ===== */
  .content-section {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 0 64px;
    padding-bottom: 24px;
    position: relative;
    z-index: 2;
  }}

  .title {{
    font-family: 'Inter', sans-serif;
    font-weight: 900;
    color: {title_color};
    text-transform: uppercase;
    line-height: 1.08;
    letter-spacing: -0.02em;
    margin-top: -80px;
    margin-bottom: 20px;
    position: relative;
    z-index: 3;
  }}

  .body-text {{
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    color: #e0e0e0;
    line-height: 1.5;
    letter-spacing: -0.01em;
  }}

  .sources {{
    font-family: 'Inter', sans-serif;
    font-size: 19px;
    color: #999;
    line-height: 1.4;
    margin-top: 12px;
  }}

  /* ===== RODAPÉ ===== */
  .footer {{
    padding: 20px 64px 40px;
    text-align: center;
    flex-shrink: 0;
  }}

  .cta {{
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #888;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}

  .handle {{
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #666;
    letter-spacing: 0.05em;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="image-section">
    <img src="{photo_b64}" alt="photo">
    <div class="gradient-overlay"></div>
  </div>

  <div class="content-section">
    <div class="title" id="title">{title}</div>
    {body_html}
    {sources_html}
  </div>

  <div class="footer">
    <div class="cta">{cta}</div>
    <div class="handle">{handle}</div>
  </div>
</div>

<script>
  function autoFit() {{
    const content = document.querySelector('.content-section');
    const title = document.getElementById('title');
    const body = document.querySelector('.body-text');
    const footer = document.querySelector('.footer');
    const imageSection = document.querySelector('.image-section');

    // Espaço disponível: card - imagem - footer
    const available = 1350 - imageSection.offsetHeight - footer.offsetHeight - 24;

    // Binary search pro título (+20% range)
    let minT = 53, maxT = 106, bestT = 79;
    const bodyEl = body;
    const hasBody = !!bodyEl;

    for (let i = 0; i < 15; i++) {{
      const mid = (minT + maxT) / 2;
      title.style.fontSize = mid + 'px';
      if (hasBody) bodyEl.style.fontSize = Math.max(24, mid * 0.42) + 'px';

      const totalH = content.scrollHeight;
      if (totalH <= available) {{
        bestT = mid;
        minT = mid + 0.5;
      }} else {{
        maxT = mid - 0.5;
      }}
    }}

    title.style.fontSize = bestT + 'px';
    if (hasBody) bodyEl.style.fontSize = Math.max(24, bestT * 0.42) + 'px';
  }}

  window.addEventListener('load', function() {{
    setTimeout(autoFit, 200);
  }});
</script>

</body>
</html>"""


def html_to_png(html_path, output_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(1500)
        card = page.query_selector(".card")
        card.screenshot(path=str(output_path))
        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Generate news-style carousel slide")
    parser.add_argument("--title", "-t", required=True, help="Title text (uppercase, large)")
    parser.add_argument("--body", "-b", default=None, help="Body text (smaller, explanatory)")
    parser.add_argument("--photo-prompt", "-p", required=True, help="Prompt for the background image")
    parser.add_argument("--output", "-o", default="./slide.png", help="Output PNG path")
    parser.add_argument("--title-color", "-c", default="#ffffff", help="Title color (hex)")
    parser.add_argument("--sources", "-s", default=None, help="Sources/credits text")
    parser.add_argument("--cta", default="ARRASTA PRO LADO >>>", help="Footer CTA text")
    parser.add_argument("--handle", default=DEFAULT_HANDLE, help="Handle text")
    parser.add_argument("--model", "-m", default=None, help="Gemini model")

    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1. Generate photo
    photo_path = out.with_suffix(".photo.png")
    print(f"[1/3] Generating photo...")
    if not generate_photo(args.photo_prompt, photo_path, args.model):
        sys.exit(1)

    # 2. Build HTML
    print(f"[2/3] Building HTML...")
    photo_b64 = img_to_b64(str(photo_path))
    html = build_html(
        title=args.title,
        body=args.body,
        photo_b64=photo_b64,
        title_color=args.title_color,
        sources=args.sources,
        cta=args.cta,
        handle=args.handle
    )
    html_path = out.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")

    # 3. Screenshot
    print(f"[3/3] Screenshot → PNG...")
    html_to_png(str(html_path.resolve()), str(out))

    # Cleanup
    photo_path.unlink(missing_ok=True)
    html_path.unlink(missing_ok=True)

    size_kb = out.stat().st_size / 1024
    print(f"Done! {out} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
