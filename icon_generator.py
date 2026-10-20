#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del icono oficial de RepackForge (SVG vectorial + PNG de alta resolución).
Diseña un escudo hexagonal neon-gaming con un mando (gamepad) y un rayo de descompresión.
"""

import shutil
from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QGuiApplication,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)


PROJECT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_DIR / "assets"


SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1526"/>
      <stop offset="50%" stop-color="#131f36"/>
      <stop offset="100%" stop-color="#090e18"/>
    </linearGradient>
    <linearGradient id="shieldBorder" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00f2fe"/>
      <stop offset="50%" stop-color="#3fb950"/>
      <stop offset="100%" stop-color="#1f6feb"/>
    </linearGradient>
    <linearGradient id="shieldFill" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1a2c47"/>
      <stop offset="100%" stop-color="#0d1626"/>
    </linearGradient>
    <linearGradient id="padGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#58a6ff"/>
      <stop offset="100%" stop-color="#2ea043"/>
    </linearGradient>
    <linearGradient id="boltGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffe066"/>
      <stop offset="100%" stop-color="#ff922b"/>
    </linearGradient>
  </defs>
  <rect x="20" y="20" width="472" height="472" rx="108" fill="url(#bgGrad)" stroke="url(#shieldBorder)" stroke-width="10"/>
  <polygon points="256,64 416,134 396,320 256,442 116,320 96,134" fill="url(#shieldFill)" stroke="url(#shieldBorder)" stroke-width="14" stroke-linejoin="round"/>
  <path d="M168,210 H344 C370,210 388,235 380,275 L366,332 C360,356 334,362 318,342 L292,310 H220 L194,342 C178,362 152,356 146,332 L132,275 C124,235 142,210 168,210 Z" fill="url(#padGrad)" stroke="#e6edf3" stroke-width="8" stroke-linejoin="round"/>
  <rect x="174" y="254" width="42" height="14" rx="4" fill="#0d1526"/>
  <rect x="188" y="240" width="14" height="42" rx="4" fill="#0d1526"/>
  <circle cx="332" cy="248" r="9" fill="#0d1526"/>
  <circle cx="332" cy="276" r="9" fill="#0d1526"/>
  <circle cx="318" cy="262" r="9" fill="#0d1526"/>
  <circle cx="346" cy="262" r="9" fill="#0d1526"/>
  <polygon points="274,116 210,236 258,236 236,348 314,214 264,214" fill="url(#boltGrad)" stroke="#0d1526" stroke-width="8" stroke-linejoin="round"/>
</svg>
"""


def render_icon_image(size: int = 512) -> QImage:
    img = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)

    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    scale = size / 512.0
    p.scale(scale, scale)

    bg_rect = QRectF(20, 20, 472, 472)
    bg_grad = QLinearGradient(20, 20, 492, 492)
    bg_grad.setColorAt(0.0, QColor("#0d1627"))
    bg_grad.setColorAt(0.5, QColor("#15243d"))
    bg_grad.setColorAt(1.0, QColor("#090d16"))

    border_grad = QLinearGradient(20, 20, 492, 492)
    border_grad.setColorAt(0.0, QColor("#00f2fe"))
    border_grad.setColorAt(0.5, QColor("#3fb950"))
    border_grad.setColorAt(1.0, QColor("#1f6feb"))

    p.setBrush(bg_grad)
    p.setPen(QPen(border_grad, 10))
    p.drawRoundedRect(bg_rect, 108, 108)

    glow = QRadialGradient(QPointF(256, 250), 210)
    glow.setColorAt(0.0, QColor(0, 242, 254, 65))
    glow.setColorAt(0.6, QColor(46, 160, 67, 30))
    glow.setColorAt(1.0, QColor(0, 0, 0, 0))
    p.setBrush(glow)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(256, 250), 210, 210)

    shield_poly = QPolygonF([
        QPointF(256, 62),
        QPointF(414, 130),
        QPointF(392, 322),
        QPointF(256, 444),
        QPointF(120, 322),
        QPointF(98, 130),
    ])
    shield_fill = QLinearGradient(256, 62, 256, 444)
    shield_fill.setColorAt(0.0, QColor("#1b2e4b"))
    shield_fill.setColorAt(1.0, QColor("#0c1424"))

    p.setBrush(shield_fill)
    p.setPen(QPen(border_grad, 13, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.drawPolygon(shield_poly)

    pad_path = QPainterPath()
    pad_path.moveTo(172, 206)
    pad_path.lineTo(340, 206)
    pad_path.cubicTo(372, 206, 390, 232, 380, 276)
    pad_path.lineTo(366, 334)
    pad_path.cubicTo(358, 360, 330, 364, 314, 342)
    pad_path.lineTo(290, 308)
    pad_path.lineTo(222, 308)
    pad_path.lineTo(198, 342)
    pad_path.cubicTo(182, 364, 154, 360, 146, 334)
    pad_path.lineTo(132, 276)
    pad_path.cubicTo(122, 232, 140, 206, 172, 206)
    pad_path.closeSubpath()

    pad_grad = QLinearGradient(130, 206, 380, 355)
    pad_grad.setColorAt(0.0, QColor("#388bfd"))
    pad_grad.setColorAt(0.55, QColor("#2ea043"))
    pad_grad.setColorAt(1.0, QColor("#238636"))

    p.setBrush(pad_grad)
    p.setPen(QPen(QColor("#e6edf3"), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.drawPath(pad_path)

    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#0d1526"))
    p.drawRoundedRect(QRectF(168, 250, 44, 15), 4, 4)
    p.drawRoundedRect(QRectF(182.5, 235.5, 15, 44), 4, 4)

    btn_specs = [
        (QPointF(330, 240), QColor("#ffd43b")),
        (QPointF(330, 274), QColor("#51cf66")),
        (QPointF(313, 257), QColor("#339af0")),
        (QPointF(347, 257), QColor("#ff6b6b")),
    ]
    for pt, col in btn_specs:
        p.setBrush(QColor("#0d1526"))
        p.drawEllipse(pt, 9.5, 9.5)
        p.setBrush(col)
        p.drawEllipse(pt, 6.5, 6.5)

    bolt_poly = QPolygonF([
        QPointF(276, 108),
        QPointF(208, 234),
        QPointF(256, 234),
        QPointF(234, 356),
        QPointF(316, 214),
        QPointF(266, 214),
    ])
    bolt_grad = QLinearGradient(210, 108, 310, 356)
    bolt_grad.setColorAt(0.0, QColor("#fff3bf"))
    bolt_grad.setColorAt(0.45, QColor("#fcc419"))
    bolt_grad.setColorAt(1.0, QColor("#f76707"))

    p.setBrush(bolt_grad)
    p.setPen(QPen(QColor("#0d1526"), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.drawPolygon(bolt_poly)

    font = QFont("DejaVu Sans", 18, QFont.Weight.ExtraBold)
    p.setFont(font)
    p.setPen(QColor("#79c0ff"))
    p.drawText(QRectF(186, 376, 140, 36), Qt.AlignmentFlag.AlignCenter, "REPACK")

    p.end()
    return img


def generate_all_icons() -> Path:
    app = QGuiApplication.instance() or QGuiApplication(["icon_gen", "-platform", "offscreen"])
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    svg_path = ASSETS_DIR / "repackforge.svg"
    svg_path.write_text(SVG_CONTENT, encoding="utf-8")

    png_512 = ASSETS_DIR / "repackforge.png"
    img = render_icon_image(512)
    img.save(str(png_512), "PNG")

    hicolor_base = Path.home() / ".local/share/icons/hicolor"
    for sz in (512, 256, 128, 64, 48):
        target_dir = hicolor_base / f"{sz}x{sz}" / "apps"
        target_dir.mkdir(parents=True, exist_ok=True)
        scaled = render_icon_image(sz)
        scaled.save(str(target_dir / "repackforge.png"), "PNG")

    scalable_dir = hicolor_base / "scalable" / "apps"
    scalable_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(svg_path, scalable_dir / "repackforge.svg")

    return png_512


if __name__ == "__main__":
    out = generate_all_icons()
    print(f"Iconos generados correctamente en: {out}")
