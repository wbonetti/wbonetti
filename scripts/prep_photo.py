"""
Prepara a foto para virar ASCII:
  1. remove o fundo (rembg, se instalado)
  2. aumenta o contraste local (CLAHE do OpenCV)
  3. compõe sobre branco puro (fundo vira espaço no ASCII)

Uso: python scripts/prep_photo.py source-photo.jpg
Saída: source-prepped.png (tons de cinza + transparência)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def main():
    src = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "source-photo.jpg")
    img = Image.open(src).convert("RGBA")

    try:
        from rembg import new_session, remove
        # modelo leve (~170 MB) treinado para recortar pessoas
        img = remove(img, session=new_session("u2net_human_seg"))
        print("fundo removido com rembg")
    except ImportError:
        print("aviso: rembg não instalado — mantendo o fundo original")

    rgba = np.array(img).astype(np.float32)
    alpha = rgba[..., 3:4] / 255.0
    gray = cv2.cvtColor(rgba[..., :3].astype(np.uint8), cv2.COLOR_RGB2GRAY)

    # contraste local: dá luz e sombra a um rosto com iluminação chapada
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray).astype(np.float32)

    # compõe sobre branco
    out = gray * alpha[..., 0] + 255.0 * (1 - alpha[..., 0])

    # recorta ao redor do assunto (bounding box do alpha) com uma margem
    ys, xs = np.where(alpha[..., 0] > 0.1)
    if len(xs):
        pad = int(0.04 * max(out.shape))
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, out.shape[0])
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, out.shape[1])
        out = out[y0:y1, x0:x1]

        a = alpha[y0:y1, x0:x1, 0]
    else:
        a = alpha[..., 0]

    # salva cinza + transparência (LA): o próximo script usa a máscara
    # para saber exatamente onde está o fundo
    gray8 = out.clip(0, 255).astype(np.uint8)
    alpha8 = (a * 255).clip(0, 255).astype(np.uint8)
    dst = ROOT / "source-prepped.png"
    Image.merge("LA", (Image.fromarray(gray8), Image.fromarray(alpha8))).save(dst)
    print(f"salvo: {dst}")


if __name__ == "__main__":
    main()
