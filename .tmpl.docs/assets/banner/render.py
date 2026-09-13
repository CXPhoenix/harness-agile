"""Render the README banner with Pillow and the supplied canvas-design font ZIP.

python3 render.py --font-archive /path/to/canvas-design.zip
The seed and dimensions are fixed so the same inputs reproduce the same PNG.
"""
import argparse
from io import BytesIO
import math
from pathlib import Path
import random
import zipfile

from PIL import Image, ImageDraw, ImageFont


def render(font_archive, output):
    scale = 2
    width, height = 2520, 1080
    rng = random.Random(913)
    paper = (242, 239, 230)
    ink = (29, 55, 48)
    muted = (99, 111, 99)
    canvas = Image.new('RGB', (width * scale, height * scale), paper)
    draw = ImageDraw.Draw(canvas)
    with zipfile.ZipFile(font_archive) as archive:
        fonts = {
            'sans': archive.read('canvas-design/canvas-fonts/InstrumentSans-Bold.ttf'),
            'mono': archive.read('canvas-design/canvas-fonts/GeistMono-Regular.ttf'),
        }

    def line(points, color, weight=1):
        draw.line([(round(x * scale), round(y * scale)) for x, y in points],
                  fill=color, width=max(1, round(weight * scale)))

    def label(x, y, value, size, family='mono', color=ink):
        font = ImageFont.truetype(BytesIO(fonts[family]), size * scale)
        draw.text((x * scale, y * scale), value, fill=color, font=font)

    # Sparse registration grid: the trajectories carry most of the visual weight.
    for x in range(1010, 2400, 64):
        for y in range(228, 850, 64):
            draw.ellipse((x * scale, y * scale, x * scale + 2, y * scale + 2),
                         fill=(197, 203, 188))

    # Sample a seeded family of paths. Disorder decays while lane spacing settles;
    # two color families share the same field and pass the same three checkpoints.
    for strand in range(116):
        lane = (strand - 57.5) / 57.5
        phase = rng.uniform(-math.pi, math.pi)
        frequency = rng.uniform(1.1, 2.1)
        amplitude = rng.uniform(28, 92)
        points = []
        for step in range(621):
            t = step / 620
            x = 990 + 1400 * t
            envelope = 250 * (1 - t) ** 1.35 + 37
            drift = 68 * math.sin(2 * math.pi * t) * (1 - t)
            wave = amplitude * math.sin(t * math.pi * 2 * frequency + phase) * (1 - t) ** 2.4
            y = 540 + lane * envelope + wave + drift
            points.append((x, y))
        pigment = (190, 96, 62) if strand < 42 else (52, 100, 81)
        opacity = rng.uniform(0.34, 0.75)
        color = tuple(round(p * opacity + b * (1 - opacity)) for p, b in zip(pigment, paper))
        line(points, color, 1.05)

    for index, (x, extent) in enumerate(((1310, 280), (1780, 205), (2240, 126)), 1):
        # Brackets frame review gates without obscuring the trajectories.
        for sign in (-1, 1):
            y = 540 + sign * extent
            line([(x - 18, y - sign * 22), (x - 18, y), (x + 18, y),
                  (x + 18, y - sign * 22)], ink, 1.6)
        label(x - 15, 188, f'0{index}', 23, color=muted)

    line([(128, 136), (2392, 136)], (184, 191, 175))
    line([(128, 920), (2392, 920)], (184, 191, 175))
    label(128, 83, 'CLAUDE CODE  /  CODEX', 24)
    label(1940, 83, 'A SHARED PRACTICE', 24)
    label(119, 316, 'harness', 150, 'sans')
    label(120, 470, 'agile', 150, 'sans')
    label(132, 707, 'FROM INTENT TO EVIDENCE.', 25)
    line([(132, 682), (208, 682)], (190, 96, 62), 5)
    label(128, 964, 'ONE CONTRACT. TWO RUNTIMES.', 23, color=muted)
    label(1188, 964, '01  CLARIFY', 22)
    label(1698, 964, '02  BUILD', 22)
    label(2160, 964, '03  VERIFY', 22)
    canvas.resize((width, height), Image.Resampling.LANCZOS).save(output, optimize=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font-archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('banner.png'))
    args = parser.parse_args()
    render(args.font_archive, args.output)
