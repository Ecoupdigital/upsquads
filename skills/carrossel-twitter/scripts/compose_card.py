#!/usr/bin/env python3
"""
Compose a social media post card as a standalone HTML file.

The entire card (avatar, name, handle, text, layout) is HTML/CSS.
Only the photo below the text comes from the Gemini API.

Text auto-resizes to fill the available space between header and image.

Usage:
    python compose_card.py --text "Texto com <b>bold</b>." \
                           --image photo.png \
                           --output slide.html
"""

import argparse
import base64
from pathlib import Path

DEFAULT_AVATAR = "/home/vault/06-conteúdo/Referencias Jonathan/avatar_instagram.jpg"


def img_to_b64(path):
    p = Path(path)
    if not p.exists():
        return ""
    ext = p.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(ext, "image/png")
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def generate_html(text, image_path, avatar_path=None):
    avatar_b64 = img_to_b64(avatar_path or DEFAULT_AVATAR)
    image_b64 = img_to_b64(image_path) if image_path and Path(image_path).exists() else ""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: #e5e5e5;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px;
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
    <img class="photo" src="{image_b64}" alt="photo">
  </div>
</div>

<script>
  // Auto-resize: ajusta a fonte do texto para preencher o espaço disponível
  function autoFitText() {{
    const card = document.querySelector('.card');
    const header = document.querySelector('.header');
    const text = document.getElementById('textContent');
    const photoWrapper = document.querySelector('.photo-wrapper');
    const photo = document.querySelector('.photo');

    // Esperar a imagem carregar pra saber a altura real
    if (!photo.complete) {{
      photo.onload = autoFitText;
      return;
    }}

    const cardStyle = getComputedStyle(card);
    const padTop = parseFloat(cardStyle.paddingTop);
    const padBot = parseFloat(cardStyle.paddingBottom);

    // Espaço total disponível dentro do card
    const cardInnerHeight = 1350 - padTop - padBot;

    // Altura fixa: header + gap entre texto e foto + foto
    const headerHeight = header.offsetHeight + 28; // + margin-bottom
    const gap = 12; // margin-bottom do texto

    // Foto: manter aspect ratio, largura = card inner width
    const cardInnerWidth = 1080 - 89 * 2;
    const photoRatio = photo.naturalHeight / photo.naturalWidth;
    const photoHeight = cardInnerWidth * photoRatio;

    // Espaço disponível para o texto
    const availableHeight = cardInnerHeight - headerHeight - gap - photoHeight;

    // Binary search pelo font-size ideal
    let min = 18;
    let max = 52;
    let best = 34;

    for (let i = 0; i < 20; i++) {{
      const mid = (min + max) / 2;
      text.style.fontSize = mid + 'px';

      if (text.scrollHeight <= availableHeight) {{
        best = mid;
        min = mid + 0.5;
      }} else {{
        max = mid - 0.5;
      }}
    }}

    text.style.fontSize = best + 'px';
  }}

  // Rodar quando a página carregar
  window.addEventListener('load', function() {{
    // Pequeno delay pra fonte Inter carregar
    setTimeout(autoFitText, 200);
  }});
</script>

</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Compose post card as HTML")
    parser.add_argument("--text", "-t", required=True, help="Text (HTML: use <b> for bold)")
    parser.add_argument("--image", "-i", required=True, help="Photo image path")
    parser.add_argument("--output", "-o", default="./card.html", help="Output HTML path")
    parser.add_argument("--avatar", "-a", default=None, help="Avatar path")

    args = parser.parse_args()
    html = generate_html(args.text, args.image, args.avatar)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Card saved: {out}")


if __name__ == "__main__":
    main()
