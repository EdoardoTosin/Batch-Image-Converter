<h1 align="center">
    <sub>
		<img src="https://raw.githubusercontent.com/EdoardoTosin/Batch-Image-Converter/main/assets/logo.png" height="38" width="38">
	</sub>
	Batch Image Converter
</h1>

<p align="center">
  <a href="https://github.com/EdoardoTosin/Batch-Image-Converter/releases/latest">
    <img src="https://raw.githubusercontent.com/EdoardoTosin/Batch-Image-Converter/main/assets/get-it-on-github.png" alt="Get it on GitHub" height=80px></a>
</p>

<p align="center">
    <a href="https://github.com/EdoardoTosin/Batch-Image-Converter/actions/workflows/build.yml">
        <img alt="Build status" src="https://img.shields.io/github/actions/workflow/status/edoardotosin/Batch-Image-Converter/build.yml?style=for-the-badge"></a>
    <a href="https://github.com/EdoardoTosin/Batch-Image-Converter/releases/latest">
        <img alt="Latest release" src="https://img.shields.io/github/v/release/EdoardoTosin/Batch-Image-Converter?label=Latest%20Release&style=for-the-badge"></a>
    <img alt="Total downloads" src="https://img.shields.io/github/downloads/edoardotosin/Batch-Image-Converter/total?style=for-the-badge">
    <a href="https://github.com/EdoardoTosin/Batch-Image-Converter/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/github/license/edoardotosin/Batch-Image-Converter?style=for-the-badge"></a>
</p>

Recursively batch-convert images to JPEG or PNG, resize to fit a pixel box, and embed DPI metadata. Available as a standalone binary (no Python required) or runnable directly with [uv](https://docs.astral.sh/uv/).

## Features

- **Automatic format selection** - JPEG for opaque images (RGB), PNG for images with any transparent or semi-transparent pixel (RGBA).
- **Resize without upscaling** - thumbnail fit within a configurable pixel box; aspect ratio always preserved.
- **DPI metadata** - written into every JPEG (JFIF header) and PNG (pHYs chunk).
- **Separate output directory** - mirrors the full folder hierarchy from the input directory.
- **In-place mode** - when no output directory is given, originals are overwritten; files that change format (e.g. `.tiff` → `.jpg`) are permanently deleted.
- **Case-insensitive extensions** - `.JPG`, `.Jpg`, `.jpg` all match.
- **Parallel processing** - `ThreadPoolExecutor` scales to all CPU cores.
- **CMYK → RGB** - uses ICC profiles when present, falls back to a simple conversion automatically.
- **GUI and CLI** in a single binary - no arguments opens the GUI, any argument uses the CLI.

## Download

Pre-built binaries for Windows, Linux, and macOS are on the [Releases](https://github.com/EdoardoTosin/Batch-Image-Converter/releases/latest) page. No Python or dependencies required.

- **Windows** - double-click `batch-image-converter.exe` for the GUI, or run from a terminal for the CLI.
- **Linux / macOS** - `chmod +x batch-image-converter && ./batch-image-converter`

## Run from source

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/EdoardoTosin/Batch-Image-Converter.git
cd Batch-Image-Converter
uv sync

uv run batch-image-converter                          # GUI
uv run batch-image-converter ./photos --dpi 300       # CLI, in-place
uv run batch-image-converter ./photos -o ./out --dpi 300  # CLI, separate output
```

## Build a binary

```bash
uv sync --all-groups
uv run python tools/build.py
# output: dist/batch-image-converter[.exe]
```

## CLI reference

```
Usage: batch-image-converter [OPTIONS] [INPUT_DIR]

  Convert every supported image under INPUT_DIR recursively.
  Output format per file: PNG (transparent pixels) or JPG (opaque).
  DPI metadata always written. Folder hierarchy preserved with -o.

Arguments:
  [INPUT_DIR]  Source directory  [default: current directory]

Options:
  -o, --output          PATH   Output directory (mirrors INPUT_DIR hierarchy).
                               Omit for in-place - originals overwritten;
                               originals deleted on format change.
  -d, --dpi             INT    DPI written into JPEG/PNG metadata [default: 72]
                               range: 1–1000
  -s, --size            INT    Longest side in pixels, downscale only
                               [default: 1000]  range: 1–10000
  -f, --filter          INT    Resampling filter [default: 0]  range: 0–5
                               0 Nearest  1 Lanczos   2 Bilinear
                               3 Bicubic  4 Box       5 Hamming
  -q, --quality         INT    JPEG output quality [default: 80]  range: 1–100
  -m, --max-megapixels  FLOAT  Skip inputs larger than N MP [default: 0 = off]
  --colorspace / --no-colorspace   ICC-profile CMYK→RGB  [default: no]
  --cs       / --no-cs             (alias)
  --optimize / --no-optimize       Palette optimisation   [default: yes]
  --alert    / --no-alert          Terminal bell on finish [default: no]
  --help
```

> **In-place warning** - the CLI prints a warning before converting in-place. The GUI shows a confirmation dialog with a Cancel button. Always keep a backup of files you cannot re-create.

## ICC colour profiles

Place `USWebCoatedSWOP.icc` and `sRGB.icc` next to the binary (or in the working directory when using `uv run`) to enable accurate CMYK → RGB conversion. Without them a simple fallback conversion is used automatically.

## Version

The single source of truth for the version is `src/batch_image_converter/__init__.py`. `pyproject.toml` and the build script both read it from there - update `__version__` in that one file to release a new version.

## Security Policy

See [SECURITY.md](https://github.com/EdoardoTosin/Batch-Image-Converter/blob/main/SECURITY.md).

## Contributing

See [CONTRIBUTING.md](https://github.com/EdoardoTosin/Batch-Image-Converter/blob/main/CONTRIBUTING.md).

## License

Released under the GNU General Public License v3.0. See [LICENSE](https://github.com/EdoardoTosin/Batch-Image-Converter/blob/main/LICENSE).
