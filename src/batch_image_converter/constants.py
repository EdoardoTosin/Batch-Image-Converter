"""Shared constants."""

from __future__ import annotations

from PIL import Image

FILTER_NAMES: dict[int, str] = {
    0: "Nearest",
    1: "Lanczos",
    2: "Bilinear",
    3: "Bicubic",
    4: "Box",
    5: "Hamming",
}

FILTER_MAP: dict[int, Image.Resampling] = {
    0: Image.Resampling.NEAREST,
    1: Image.Resampling.LANCZOS,
    2: Image.Resampling.BILINEAR,
    3: Image.Resampling.BICUBIC,
    4: Image.Resampling.BOX,
    5: Image.Resampling.HAMMING,
}

FILETYPE: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
)

CMYK_PROFILE = "USWebCoatedSWOP.icc"
SRGB_PROFILE = "sRGB.icc"
