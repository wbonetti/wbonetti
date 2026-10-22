"""
Gera um card estilo `neofetch`: barra de título + linhas chave/valor coloridas
que aparecem uma a uma (keyframes CSS dentro do SVG — o GitHub reproduz).

Uso:  python scripts/make_info_card.py
      STATIC=1 python scripts/make_info_card.py   # quadro estático p/ preview
Saída: info-card.svg
Conteúdo: edite INFO em scripts/config.py
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

from config import INFO, PROMPT_USER

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

W = 490
PAD_X = 22
TITLE_H = 34
LINE_H = 20
FONT = 13.5
KEY_W = 112                    # largura da coluna dos rótulos
STAGGER = 0.12                 # atraso entre linhas (s)
START = 0.3

BG, BORDER, BAR = "#0d1117", "#30363d", "#161b22"
FG, MUTED = "#c9d1d9", "#8b949e"
KEY_COLORS = ["#39d353", "#58a6ff", "#d2a8ff", "#ffa657", "#79c0ff", "#ff7b72", "#56d4dd"]


def build() -> str:
    head = f"{PROMPT_USER}@github"
    rows = []  # (tipo, conteúdo)
    rows.append(("head", head))
    rows.append(("rule", "-" * len(head)))
    for i, (key, value) in enumerate(INFO):
        values = value if isinstance(value, list) else [value]
        color = KEY_COLORS[i % len(KEY_COLORS)]
        for j, v in enumerate(values):
            rows.append(("kv", (key if j == 0 else "", v, color)))
    rows.append(("blank", ""))  # respiro antes da paleta
    rows.append(("palette", ""))

    body_top = TITLE_H + 20
    H = body_top + len(rows) * LINE_H + 16

    css = f"""
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; font-size: {FONT}px; }}
    .k {{ font-weight: 700; }}
    .v {{ fill: {FG}; }}
    .m {{ fill: {MUTED}; }}
    """
    if not STATIC:
        css += """
    .l { opacity: 0; animation: in .45s ease-out forwards; }
    @keyframes in { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: none; } }
    .cur { animation: blink 1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    """

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="Card de informações">',
        f"<style>{css}</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        f'<path d="M0.5 10.5 a10 10 0 0 1 10 -10 h{W - 21} a10 10 0 0 1 10 10 v{TITLE_H - 10} h-{W - 1} z" fill="{BAR}"/>',
        f'<line x1="0.5" y1="{TITLE_H + .5}" x2="{W - .5}" y2="{TITLE_H + .5}" stroke="{BORDER}"/>',
    ]
    for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        o.append(f'<circle cx="{20 + k * 18}" cy="{TITLE_H / 2}" r="5.5" fill="{c}"/>')
    o.append(f'<text x="{W / 2}" y="{TITLE_H / 2 + 4.5}" text-anchor="middle" class="m">'
             f"{escape(PROMPT_USER)}@github: ~ — neofetch</text>")

    for i, (kind, data) in enumerate(rows):
        y = body_top + i * LINE_H
        style = "" if STATIC else f' style="animation-delay:{START + i * STAGGER:.2f}s"'
        cls = "" if STATIC else ' class="l"'
        if kind == "head":
            user, _, host = data.partition("@")
            o.append(f'<g{cls}{style}><text x="{PAD_X}" y="{y}" class="k">'
                     f'<tspan fill="#39d353">{escape(user)}</tspan><tspan class="v">@</tspan>'
                     f'<tspan fill="#39d353">{escape(host)}</tspan></text></g>')
        elif kind == "rule":
            o.append(f'<g{cls}{style}><text x="{PAD_X}" y="{y}" class="m">{data}</text></g>')
        elif kind == "kv":
            key, val, color = data
            parts = [f'<g{cls}{style}>']
            if key:
                parts.append(f'<text x="{PAD_X}" y="{y}" class="k" fill="{color}">{escape(key)}</text>')
            parts.append(f'<text x="{PAD_X + KEY_W}" y="{y}" class="v">{escape(val)}</text></g>')
            o.append("".join(parts))
        elif kind == "palette":
            sw = ["#484f58", "#ff7b72", "#39d353", "#e3b341", "#58a6ff", "#d2a8ff", "#56d4dd", "#c9d1d9"]
            blocks = "".join(
                f'<rect x="{PAD_X + j * 26}" y="{y - 13}" width="24" height="16" rx="2" fill="{c}"/>'
                for j, c in enumerate(sw)
            )
            cursor = "" if STATIC else (
                f'<rect class="cur" x="{PAD_X + len(sw) * 26 + 10}" y="{y - 13}" width="9" height="16" fill="#39d353"/>'
            )
            o.append(f'<g{cls}{style}>{blocks}{cursor}</g>')
    o.append("</svg>")
    return "\n".join(o)


def main():
    dst = ROOT / "info-card.svg"
    dst.write_text(build(), encoding="utf-8")
    print(f"salvo: {dst}")


if __name__ == "__main__":
    main()
