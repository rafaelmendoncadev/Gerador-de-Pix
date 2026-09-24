"""Gera ícones visuais para o aplicativo Gerador Pix."""

import os
from PIL import Image, ImageDraw


def generate_pix_icon(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    ico_path = os.path.join(output_dir, "icon.ico")
    png_path = os.path.join(output_dir, "icon.png")

    # Dimensão para ícone de alta resolução
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo arredondado turquesa Pix (#32BCAD)
    pix_teal = (50, 188, 173, 255)
    dark_slate = (24, 24, 37, 255)
    white = (255, 255, 255, 255)

    # Círculo / squircle de fundo
    margin = 8
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=54,
        fill=dark_slate,
    )

    # Losango estilizado do Pix
    cx, cy = size // 2, size // 2
    diamond_size = 72

    # Desenha símbolo em estilo cruzamento Pix
    points = [
        (cx, cy - diamond_size),
        (cx + diamond_size, cy),
        (cx, cy + diamond_size),
        (cx - diamond_size, cy),
    ]
    draw.polygon(points, fill=pix_teal)

    # Losango interno branco
    inner_size = 32
    inner_points = [
        (cx, cy - inner_size),
        (cx + inner_size, cy),
        (cx, cy + inner_size),
        (cx - inner_size, cy),
    ]
    draw.polygon(inner_points, fill=white)

    # Centro dark
    center_size = 14
    center_points = [
        (cx, cy - center_size),
        (cx + center_size, cy),
        (cx, cy + center_size),
        (cx - center_size, cy),
    ]
    draw.polygon(center_points, fill=dark_slate)

    # Salva PNG
    img.save(png_path, format="PNG")

    # Salva ICO em múltiplos tamanhos
    img.save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    return ico_path, png_path


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base, "src", "assets")
    generate_pix_icon(assets_dir)
