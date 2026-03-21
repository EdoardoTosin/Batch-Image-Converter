"""Core image conversion logic - no I/O besides filesystem operations."""

from __future__ import annotations

import dataclasses
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

from PIL import Image, ImageCms

from .constants import FILTER_MAP, FILETYPE, CMYK_PROFILE, SRGB_PROFILE


@dataclasses.dataclass(frozen=True)
class ConversionConfig:
    path: Path
    output_path: Path | None = None  # None = in-place
    dpi: int = 72
    size: int = 1000
    filter: int = 0
    quality: int = 80
    max_megapixels: float = 0.0
    colorspace: bool = False
    optimize: bool = True


@dataclasses.dataclass
class ConversionResult:
    converted: int = 0
    errors: list[str] = dataclasses.field(default_factory=list)
    elapsed: float = 0.0

    @property
    def failed(self) -> int:
        return len(self.errors)


# ── ICC helpers ────────────────────────────────────────────────────────────────


def _icc_dir() -> Path:
    """Return directory to search for ICC profiles (next to executable or package)."""
    import sys

    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent / "icc"


def _to_rgb(img: Image.Image) -> Image.Image:
    """Convert CMYK to RGB using ICC profiles if available, else simple convert."""
    cmyk = _icc_dir() / CMYK_PROFILE
    srgb = _icc_dir() / SRGB_PROFILE
    if cmyk.exists() and srgb.exists():
        try:
            transform = ImageCms.buildTransform(
                str(cmyk),
                str(srgb),
                "CMYK",
                "RGB",
                renderingIntent=ImageCms.Intent.PERCEPTUAL,
            )
            return ImageCms.applyTransform(img, transform)
        except Exception:
            pass
    return img.convert("RGB")


# ── Format selection ───────────────────────────────────────────────────────────


def _has_transparency(img: Image.Image) -> bool:
    """Return True if the image contains any fully or partially transparent pixel."""
    mode = img.mode
    if mode == "RGBA":
        return img.getextrema()[3][0] < 255
    if mode == "LA":
        return img.getextrema()[1][0] < 255
    if mode == "P" and "transparency" in img.info:
        # Palette transparency - check actual pixel coverage via RGBA conversion
        rgba = img.convert("RGBA")
        return rgba.getextrema()[3][0] < 255
    return False


# ── Path helpers ───────────────────────────────────────────────────────────────


def _is_inplace(cfg: ConversionConfig) -> bool:
    if cfg.output_path is None:
        return True
    return cfg.output_path.resolve() == cfg.path.resolve()


def _out_path(cfg: ConversionConfig, src: Path, suffix: str) -> Path:
    """Compute the destination path, preserving the folder hierarchy."""
    if _is_inplace(cfg):
        return src.with_suffix(suffix)
    relative = src.relative_to(cfg.path.resolve())
    return cfg.output_path.resolve() / relative.parent / (src.stem + suffix)


def _save_kwargs(suffix: str, dpi: int, quality: int, optimize: bool) -> dict:
    dpi_pair = (dpi, dpi)
    if suffix == ".jpg":
        return {"dpi": dpi_pair, "quality": quality, "optimize": optimize}
    if suffix == ".png":
        return {"dpi": dpi_pair, "optimize": optimize}
    return {"dpi": dpi_pair}


# ── Per-file worker ────────────────────────────────────────────────────────────


def _process(
    cfg: ConversionConfig,
    src: Path,
    log: Callable[[str], None],
) -> bool:
    """Process a single image file. Returns True on success."""
    try:
        with Image.open(src) as img:
            # 1. Normalise CMYK → RGB before any alpha check
            if img.mode == "CMYK":
                img = _to_rgb(img) if cfg.colorspace else img.convert("RGB")

            # 2. Choose output format: PNG for images with transparency, JPG otherwise
            if _has_transparency(img):
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                out_suffix = ".png"
            else:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                out_suffix = ".jpg"

            # 3. Downscale only - never upscale; aspect ratio preserved by thumbnail()
            if max(img.size) > cfg.size:
                img.thumbnail(
                    (cfg.size, cfg.size),
                    resample=FILTER_MAP[cfg.filter],
                )

            # 4. Resolve destination and ensure parent dirs exist
            out = _out_path(cfg, src, out_suffix)
            out.parent.mkdir(parents=True, exist_ok=True)

            # 5. Save with DPI metadata
            img.save(
                out,
                **_save_kwargs(out_suffix, cfg.dpi, cfg.quality, cfg.optimize),
            )

        # 6. In-place: delete original only when the path changed (format conversion)
        if _is_inplace(cfg) and out.resolve() != src.resolve():
            src.unlink()

        label = f"{src.name} → {out.name}" if out.name != src.name else src.name
        log(f"  ✓ {label}")
        return True

    except Exception as exc:  # noqa: BLE001
        log(f"  ✗ {src.name}: {exc}")
        return False


# ── Public API ─────────────────────────────────────────────────────────────────


def convert(
    cfg: ConversionConfig,
    log: Callable[[str], None],
    progress: Callable[[int, int], None] | None = None,
    is_cancelled: Callable[[], bool] | None = None,
) -> ConversionResult:
    """
    Batch-convert all supported images under cfg.path recursively.

    Args:
        cfg: Conversion settings.
        log: Per-line logging callback (thread-safe: Rich/Qt handle the locking).
        progress: Optional callback(completed, total) called after each file.
        is_cancelled: Optional callable; stops processing when it returns True.

    Returns:
        ConversionResult with counters and error list.
    """
    if cfg.max_megapixels > 0:
        Image.MAX_IMAGE_PIXELS = int(cfg.max_megapixels * 1_000_000)
    else:
        Image.MAX_IMAGE_PIXELS = None  # type: ignore[assignment]

    input_path = cfg.path.resolve()

    files = sorted(
        p for p in input_path.rglob("*") if p.suffix.lower() in FILETYPE and p.is_file()
    )

    if not files:
        log("No supported images found.")
        return ConversionResult()

    # Pre-create output root so workers only need to create subdirs
    if not _is_inplace(cfg) and cfg.output_path is not None:
        cfg.output_path.resolve().mkdir(parents=True, exist_ok=True)

    log(f"Found {len(files)} image(s) - starting conversion...")
    start = time.perf_counter()
    result = ConversionResult()

    with ThreadPoolExecutor() as pool:
        futures: dict[Future[bool], Path] = {
            pool.submit(_process, cfg, f, log): f for f in files
        }
        for future in as_completed(futures):
            if is_cancelled and is_cancelled():
                pool.shutdown(wait=False, cancel_futures=True)
                log("Cancelled by user.")
                break
            if future.result():
                result.converted += 1
            else:
                result.errors.append(str(futures[future]))
            if progress:
                progress(result.converted + result.failed, len(files))

    result.elapsed = time.perf_counter() - start
    return result
