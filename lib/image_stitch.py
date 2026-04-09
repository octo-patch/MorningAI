"""Stitch multiple images into a single vertical long image.

Requires Pillow: pip install Pillow
"""

import sys
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None


def _log(msg: str):
    sys.stderr.write(f"[ImageStitch] {msg}\n")
    sys.stderr.flush()


def stitch_images(
    image_paths: List[str],
    output_path: str,
    *,
    gap: int = 20,
    padding: int = 30,
    bg_color: Tuple[int, int, int] = (245, 245, 240),
) -> str:
    """Stitch multiple images vertically into a single long image.

    Args:
        image_paths: Ordered list of image file paths to combine.
                     Non-existent paths are silently skipped.
        output_path: Path for the combined output PNG.
        gap: Pixel gap between images (filled with bg_color).
        padding: Top and bottom padding in pixels.
        bg_color: RGB background/gap color. Default matches
                  infographic style (#F5F5F0).

    Returns:
        Output file path on success.

    Raises:
        ImportError: If Pillow is not installed.
        ValueError: If no valid images found.
    """
    if Image is None:
        raise ImportError(
            "Pillow is required for image stitching. Install with: pip install Pillow"
        )

    # Filter to existing files
    valid_paths = [p for p in image_paths if Path(p).exists()]
    if not valid_paths:
        raise ValueError("No valid image files found to stitch")

    _log(f"Stitching {len(valid_paths)} images...")

    images = [Image.open(p) for p in valid_paths]

    # Uniform width (use max)
    max_width = max(img.width for img in images)

    resized = []
    for img in images:
        if img.width != max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)
        resized.append(img)

    # Canvas dimensions
    total_height = sum(img.height for img in resized) + gap * (len(resized) - 1) + padding * 2

    canvas = Image.new("RGB", (max_width, total_height), bg_color)
    y_offset = padding
    for img in resized:
        canvas.paste(img, (0, y_offset))
        y_offset += img.height + gap

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "PNG")

    # Close originals first, then any resized copies
    originals = set(id(img) for img in images)
    for img in images:
        img.close()
    for img in resized:
        if id(img) not in originals:
            img.close()
    canvas.close()

    _log(f"Combined image saved to {output_path} ({max_width}x{total_height})")
    return output_path
