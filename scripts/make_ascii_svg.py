"""
Converte source-prepped.png em um retrato ASCII monocromático que se "digita"
linha a linha (animação SMIL — o GitHub reproduz dentro de <img>).

Uso:  python scripts/make_ascii_svg.py
      STATIC=1 python scripts/make_ascii_svg.py   # quadro estático p/ preview
Saída: portrait-ascii.svg
"""
import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

from config import ASCII_COLS, ASCII_RAMP, ASCII_INVERT

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

CW, LH = 6.0, 11.0          # largura do caractere / altura da linha (px)
PAD = 14
FG = "#c9d1d9"              # cinza claro único (monocromático)
BG = "#0d1117"
ROW_DELAY = 0.045           # escalonamento entre linhas (s)
ROW_DUR = 0.35              # duração do "wipe" de cada linha (s)


def to_grid(img: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    """Devolve (brilho 0..1 equalizado dentro do assunto, máscara do fundo)."""
    w, h = img.size
    rows = max(1, round(ASCII_COLS * (h / w) * (CW / LH)))
    size = (ASCII_COLS, rows)
    gray = np.asarray(img.convert("L").resize(size, Image.LANCZOS), dtype=np.float32)
    if "A" in img.getbands():
        alpha = np.asarray(img.getchannel("A").resize(size, Image.LANCZOS), dtype=np.float32)
        bg = alpha < 140
    else:
        bg = gray >= 250

    # equalização por ranking só nos pixels da pessoa: usa a escala toda
    level = np.zeros_like(gray)
    subj = ~bg
    if subj.any():
        vals = gray[subj]
        level[subj] = np.searchsorted(np.sort(vals), vals, side="right") / vals.size
    return level, bg


def grid_to_lines(grid: tuple[np.ndarray, np.ndarray]) -> list[str]:
    level, bg = grid
    n = len(ASCII_RAMP) - 1
    if not ASCII_INVERT:
        level = 1 - level  # mapeamento do artigo: escuro -> denso
    # assunto usa os caracteres 1..n (nunca fica vazio); fundo vira espaço
    idx = 1 + np.round(level ** 1.2 * (n - 1))
    idx = np.where(bg, 0, idx).astype(int)
    return ["".join(ASCII_RAMP[i] for i in row).rstrip() for row in idx]


def build_svg(lines: list[str]) -> str:
    width = ASCII_COLS * CW + PAD * 2
    height = len(lines) * LH + PAD * 2
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}" role="img" aria-label="Retrato em ASCII">',
        f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>',
        "<defs>",
    ]
    rows = []  # (i, x0, largura) de cada linha com conteúdo
    for i, line in enumerate(lines):
        if line.strip():
            start = len(line) - len(line.lstrip())
            rows.append((i, PAD + start * CW, (len(line) - start) * CW))
    if not STATIC:
        for i, x0, lw in rows:
            b = i * ROW_DELAY
            out.append(
                f'<clipPath id="c{i}"><rect x="{x0:.1f}" y="{PAD + i * LH:.1f}" width="0" height="{LH:.1f}">'
                f'<animate attributeName="width" from="0" to="{lw:.1f}" begin="{b:.3f}s" '
                f'dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
            )
    out.append("</defs>")
    out.append(
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" '
        f'font-size="10" fill="{FG}">'
    )
    for i, x0, lw in rows:
        y = PAD + i * LH + LH * 0.8
        clip = "" if STATIC else f' clip-path="url(#c{i})"'
        out.append(f"<g{clip}>")
        # cada trecho sem espaços vai na coluna exata: imune à fonte do sistema
        for m in re.finditer(r"[^ ]+", lines[i]):
            run = m.group()
            out.append(
                f'<text x="{PAD + m.start() * CW:.1f}" y="{y:.1f}" '
                f'textLength="{len(run) * CW:.1f}" lengthAdjust="spacingAndGlyphs">{escape(run)}</text>'
            )
        out.append("</g>")
        if not STATIC:
            # "cursor" em bloco que acompanha a borda do wipe e some no fim
            b = i * ROW_DELAY
            out.append(
                f'<rect x="{x0:.1f}" y="{PAD + i * LH + 1:.1f}" width="{CW:.0f}" height="{LH - 2:.1f}" '
                f'fill="#39d353" opacity="0">'
                f'<set attributeName="opacity" to="0.9" begin="{b:.3f}s"/>'
                f'<animate attributeName="x" from="{x0:.1f}" to="{x0 + lw:.1f}" begin="{b:.3f}s" '
                f'dur="{ROW_DUR}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0" begin="{b + ROW_DUR:.3f}s"/></rect>'
            )
    out.append("</g></svg>")
    return "\n".join(out)


def main():
    src = ROOT / "source-prepped.png"
    lines = grid_to_lines(to_grid(Image.open(src)))
    # remove linhas vazias do topo/fundo
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    dst = ROOT / "portrait-ascii.svg"
    dst.write_text(build_svg(lines), encoding="utf-8")
    print(f"salvo: {dst} ({len(lines)} linhas)")


if __name__ == "__main__":
    main()
