"""
Desenha data/contributions.json como o calendário clássico 53 semanas × 7 dias,
com quadrados arredondados que entram em diagonal (keyframes CSS, tocam uma vez
e congelam), legenda Menos→Mais e um rodapé com estatísticas.

Uso:  python scripts/render_heatmap_svg.py
      STATIC=1 python scripts/render_heatmap_svg.py   # quadro estático
Saída: contrib-heatmap.svg
"""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"

# nenhum -> mais forte (nível 5 é um topo "neon" para os dias recordes)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
WEEKDAYS = {1: "seg", 3: "qua", 5: "sex"}  # linhas (domingo = 0)

W = 860
CELL, STEP = 12, 15
LEFT, TOP = 46, 62
BG, BORDER, FG, MUTED = "#0d1117", "#30363d", "#c9d1d9", "#8b949e"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    days, st = data["days"], data["stats"]

    # nível 5: os ~3% dias mais fortes entre os de nível 4
    top = sorted((d["count"] for d in days if d["level"] >= 4), reverse=True)
    cut = top[max(0, len(top) * 3 // 100 - 1)] if len(top) >= 10 else float("inf")

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # domingo = 0
    cells, month_cols = [], {}
    for i, d in enumerate(days):
        dt = date.fromisoformat(d["date"])
        col, row = divmod(i + offset, 7)
        lvl = 5 if d["level"] >= 4 and d["count"] >= cut else d["level"]
        cells.append((col, row, lvl, d))
        if dt.day <= 7 and row == 0 or i == 0:
            month_cols.setdefault((dt.year, dt.month), col)
    ncols = cells[-1][0] + 1

    grid_w = ncols * STEP
    left = LEFT + max(0, (W - 30 - LEFT - grid_w) // 2)
    H = TOP + 7 * STEP + 62

    css = f"text {{ font-family: {FONT}; fill: {MUTED}; font-size: 11px; }} .t {{ fill: {FG}; font-size: 14px; font-weight: 700; }} .h {{ fill: #39d353; }}"
    if not STATIC:
        css += (
            " .c { opacity: 0; transform-box: fill-box; transform-origin: center;"
            " animation: drop .5s cubic-bezier(.2,.8,.3,1) forwards; }"
            " @keyframes drop { from { opacity: 0; transform: translateY(-7px) scale(.6); }"
            " to { opacity: 1; transform: none; } }"
            " .f { opacity: 0; animation: fade .6s ease-out forwards; }"
            " @keyframes fade { to { opacity: 1; } }"
        )

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{fmt(st["total"])} contribuições no último ano">',
        f"<style>{css}</style>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        f'<text x="{left}" y="30" class="t"><tspan class="h">{fmt(st["total"])}</tspan> contribuições no último ano</text>',
    ]

    # meses
    last_x = -99
    for (_, m), col in sorted(month_cols.items(), key=lambda kv: kv[1]):
        x = left + col * STEP
        if x - last_x >= 30 and col < ncols - 1:
            o.append(f'<text x="{x}" y="{TOP - 8}">{MONTHS[m - 1]}</text>')
            last_x = x
    for r, name in WEEKDAYS.items():
        o.append(f'<text x="{left - 30}" y="{TOP + r * STEP + 10}">{name}</text>')

    # células
    for col, row, lvl, d in cells:
        x, y = left + col * STEP, TOP + row * STEP
        anim = "" if STATIC else f' class="c" style="animation-delay:{(col + row) * 0.022:.3f}s"'
        tip = f'{d["count"]} em {d["date"]}'
        o.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                 f'fill="{PALETTE[lvl]}"{anim}><title>{tip}</title></rect>')

    # rodapé: estatísticas + legenda
    end_delay = (ncols + 6) * 0.022
    fcls = "" if STATIC else f' class="f" style="animation-delay:{end_delay:.2f}s"'
    fy = TOP + 7 * STEP + 30
    bd = date.fromisoformat(st["best_day"]["date"])
    o.append(
        f"<g{fcls}><text x=\"{left}\" y=\"{fy}\">"
        f'sequência atual <tspan class="h">{st["current_streak"]}d</tspan>'
        f'  ·  maior sequência <tspan class="h">{st["longest_streak"]}d</tspan>'
        f'  ·  melhor dia <tspan class="h">{st["best_day"]["count"]}</tspan> ({bd:%d/%m})</text>'
    )
    lx = left + grid_w - (len(PALETTE) * 15 + 70)
    o.append(f'<text x="{lx}" y="{fy}">menos</text>')
    for k, c in enumerate(PALETTE):
        o.append(f'<rect x="{lx + 40 + k * 15}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    o.append(f'<text x="{lx + 44 + len(PALETTE) * 15}" y="{fy}">mais</text></g>')
    o.append("</svg>")

    dst = ROOT / "contrib-heatmap.svg"
    dst.write_text("\n".join(o), encoding="utf-8")
    print(f"salvo: {dst} ({ncols} semanas)")


if __name__ == "__main__":
    main()
