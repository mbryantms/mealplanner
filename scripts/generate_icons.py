#!/usr/bin/env python3
"""
Generate PWA icons from the base SVG icon.

Requirements:
    pip install cairosvg pillow

Usage:
    python scripts/generate_icons.py
"""

import os
from pathlib import Path

try:
    import cairosvg
    from PIL import Image
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("Warning: cairosvg and/or pillow not installed.")
    print("Install with: pip install cairosvg pillow")
    print("Generating placeholder icons instead.")

# Icon sizes needed for PWA
ICON_SIZES = [16, 32, 72, 96, 128, 144, 152, 167, 180, 192, 384, 512]

# iOS splash screen sizes (width x height)
SPLASH_SIZES = [
    (640, 1136),   # iPhone 5/SE
    (750, 1334),   # iPhone 6/7/8
    (1242, 2208),  # iPhone 6+/7+/8+
    (1125, 2436),  # iPhone X/XS
    (1170, 2532),  # iPhone 12/13
    (1284, 2778),  # iPhone 12/13 Pro Max
]

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = BASE_DIR / "static" / "icons"
SVG_PATH = ICONS_DIR / "icon.svg"


def generate_png_from_svg(svg_path: Path, output_path: Path, size: int):
    """Convert SVG to PNG at specified size."""
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(output_path),
        output_width=size,
        output_height=size,
    )
    print(f"Generated: {output_path.name}")


def generate_splash_screen(output_path: Path, width: int, height: int, bg_color: str = "#3b82f6"):
    """Generate a splash screen with the icon centered."""
    from PIL import Image, ImageDraw

    # Create background
    img = Image.new("RGB", (width, height), bg_color)

    # Load and resize icon (about 25% of the smaller dimension)
    icon_size = min(width, height) // 4

    # Generate icon PNG temporarily
    temp_icon = ICONS_DIR / "temp_splash_icon.png"
    cairosvg.svg2png(
        url=str(SVG_PATH),
        write_to=str(temp_icon),
        output_width=icon_size,
        output_height=icon_size,
    )

    # Open and paste icon
    icon = Image.open(temp_icon).convert("RGBA")

    # Center the icon
    x = (width - icon_size) // 2
    y = (height - icon_size) // 2

    # Paste icon onto background
    img.paste(icon, (x, y), icon)

    # Save
    img.save(output_path, "PNG")
    print(f"Generated: {output_path.name}")

    # Cleanup temp file
    temp_icon.unlink()


def generate_placeholder_icons():
    """Generate simple colored placeholder icons without external dependencies."""
    from PIL import Image, ImageDraw

    # Base blue color matching theme
    bg_color = (59, 130, 246)  # #3b82f6

    for size in ICON_SIZES:
        img = Image.new("RGB", (size, size), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw a simple plate circle
        margin = size // 8
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(255, 255, 255),
            outline=None
        )

        # Draw inner circle
        inner_margin = size // 4
        draw.ellipse(
            [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
            fill=bg_color,
            outline=None
        )

        output_path = ICONS_DIR / f"icon-{size}x{size}.png"
        img.save(output_path, "PNG")
        print(f"Generated placeholder: {output_path.name}")

    # Generate apple-touch-icon (180x180)
    img = Image.new("RGB", (180, 180), bg_color)
    draw = ImageDraw.Draw(img)
    margin = 180 // 8
    draw.ellipse([margin, margin, 180 - margin, 180 - margin], fill=(255, 255, 255))
    inner_margin = 180 // 4
    draw.ellipse([inner_margin, inner_margin, 180 - inner_margin, 180 - inner_margin], fill=bg_color)
    img.save(ICONS_DIR / "apple-touch-icon.png", "PNG")
    print("Generated placeholder: apple-touch-icon.png")

    # Generate favicons
    for size in [16, 32]:
        img = Image.new("RGB", (size, size), bg_color)
        img.save(ICONS_DIR / f"favicon-{size}x{size}.png", "PNG")
        print(f"Generated placeholder: favicon-{size}x{size}.png")


def main():
    """Generate all PWA icons."""
    os.makedirs(ICONS_DIR, exist_ok=True)

    if not HAS_DEPS:
        # Generate basic placeholder icons using PIL only
        try:
            from PIL import Image
            generate_placeholder_icons()
        except ImportError:
            print("Error: PIL/Pillow is required. Install with: pip install pillow")
            return
        return

    if not SVG_PATH.exists():
        print(f"Error: SVG icon not found at {SVG_PATH}")
        return

    # Generate app icons
    for size in ICON_SIZES:
        output_path = ICONS_DIR / f"icon-{size}x{size}.png"
        generate_png_from_svg(SVG_PATH, output_path, size)

    # Generate apple-touch-icon (180x180 is standard)
    generate_png_from_svg(SVG_PATH, ICONS_DIR / "apple-touch-icon.png", 180)

    # Generate favicons
    generate_png_from_svg(SVG_PATH, ICONS_DIR / "favicon-16x16.png", 16)
    generate_png_from_svg(SVG_PATH, ICONS_DIR / "favicon-32x32.png", 32)

    # Generate splash screens
    for width, height in SPLASH_SIZES:
        output_path = ICONS_DIR / f"splash-{width}x{height}.png"
        generate_splash_screen(output_path, width, height)

    print("\nAll icons generated successfully!")
    print(f"Icons directory: {ICONS_DIR}")


if __name__ == "__main__":
    main()
