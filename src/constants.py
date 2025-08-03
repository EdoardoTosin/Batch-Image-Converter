"""Constants used throughout the Batch Image Converter application."""

FILTER_NAMES = {
    0: "Nearest",
    1: "Lanczos",
    2: "Bilinear",
    3: "Bicubic",
    4: "Box",
    5: "Hamming",
}

CMYK_PROFILE_PATH = "USWebCoatedSWOP.icc"
SRGB_PROFILE_PATH = "sRGB.icc"

EXCEPTION_FILES = []

FILETYPE = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp")
