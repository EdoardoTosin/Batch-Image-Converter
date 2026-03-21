"""Typer + Rich CLI for Batch Image Converter."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from .constants import FILTER_NAMES
from .converter import ConversionConfig, ConversionResult, convert

app = typer.Typer(
    name="batch-image-converter",
    help=(
        "Batch convert images to JPG (opaque) or PNG (transparent), "
        "resize to a pixel box, and write DPI metadata."
    ),
    add_completion=False,
    pretty_exceptions_enable=False,
)

console = Console()
err_console = Console(stderr=True)


def _require_dir(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_dir():
        err_console.print(f"[bold red]Error:[/] {label} is not a directory: {path}")
        raise typer.Exit(1)
    return resolved


@app.command()
def convert_images(
    input_dir: Annotated[
        Path,
        typer.Argument(
            help="Source directory (default: current directory)",
            show_default=False,
        ),
    ] = Path("."),
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help=(
                "Output directory. Folder hierarchy is mirrored from INPUT_DIR. "
                "Omit for in-place conversion (originals replaced / deleted on format change)."
            ),
        ),
    ] = None,
    dpi: Annotated[
        int,
        typer.Option(
            "--dpi", "-d", help="DPI written into JPEG/PNG metadata", min=1, max=1000
        ),
    ] = 72,
    size: Annotated[
        int,
        typer.Option(
            "--size",
            "-s",
            help="Longest side in pixels - images are only downscaled, never upscaled",
            min=1,
            max=10000,
        ),
    ] = 1000,
    filter: Annotated[
        int,
        typer.Option(
            "--filter",
            "-f",
            help=(
                "Resampling filter used when downscaling: "
                "0=Nearest  1=Lanczos  2=Bilinear  3=Bicubic  4=Box  5=Hamming"
            ),
            min=0,
            max=5,
        ),
    ] = 0,
    quality: Annotated[
        int,
        typer.Option("--quality", "-q", help="JPEG output quality", min=1, max=100),
    ] = 80,
    max_megapixels: Annotated[
        float,
        typer.Option(
            "--max-megapixels",
            "-m",
            help="Refuse to open inputs larger than this many megapixels (0 = unlimited)",
            min=0,
        ),
    ] = 0.0,
    colorspace: Annotated[
        bool,
        typer.Option(
            "--colorspace/--no-colorspace",
            "--cs/--no-cs",
            help="Use ICC profiles for CMYK → RGB conversion (falls back to simple convert)",
        ),
    ] = False,
    optimize: Annotated[
        bool,
        typer.Option(
            "--optimize/--no-optimize", help="Enable JPEG/PNG palette optimisation"
        ),
    ] = True,
    alert: Annotated[
        bool,
        typer.Option("--alert/--no-alert", help="Ring terminal bell when finished"),
    ] = False,
) -> None:
    """
    Convert every supported image under INPUT_DIR recursively.

    Output format is chosen per-file: PNG when the image contains transparent or
    semi-transparent pixels, JPG otherwise. DPI metadata is always written.
    Folder hierarchy is preserved when an output directory is given.
    """
    input_path = _require_dir(input_dir, "INPUT_DIR")

    if output_dir is not None:
        output_path: Path | None = output_dir.resolve()
        # Output dir need not exist yet - converter will create it
    else:
        output_path = None

    # ── Settings summary ──────────────────────────────────────────────────────
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="dim")
    table.add_column()
    table.add_row("Input", str(input_path))
    table.add_row(
        "Output",
        str(output_path) if output_path is not None else "[dim]in-place[/]",
    )
    table.add_row("DPI", str(dpi))
    table.add_row("Max dimension", f"{size} px")
    table.add_row("Filter", f"{filter} – {FILTER_NAMES[filter]}")
    table.add_row("Quality (JPEG)", str(quality))
    table.add_row(
        "Max input megapixels",
        "unlimited" if max_megapixels == 0 else f"{max_megapixels} MP",
    )
    table.add_row("CMYK→RGB (ICC)", "yes" if colorspace else "no")
    table.add_row("Optimise", "yes" if optimize else "no")

    console.print(Panel(table, title="[bold]Batch Image Converter[/]", expand=False))

    if output_path is None:
        console.print(
            "[yellow]Warning:[/] Running in in-place mode - originals will be overwritten. "
            "Files that change format (e.g. TIFF → JPEG) will be permanently deleted. "
            "Ensure you have a backup."
        )

    if quality > 95:
        console.print(
            "[yellow]Warning:[/] Quality > 95 rarely improves perceived quality "
            "and significantly increases file size."
        )

    # ── Conversion ────────────────────────────────────────────────────────────
    cfg = ConversionConfig(
        path=input_path,
        output_path=output_path,
        dpi=dpi,
        size=size,
        filter=filter,
        quality=quality,
        max_megapixels=max_megapixels,
        colorspace=colorspace,
        optimize=optimize,
    )

    result: ConversionResult | None = None

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    ) as progress_bar:
        task = progress_bar.add_task("Converting…", total=None)

        def log(msg: str) -> None:
            progress_bar.console.print(msg)

        def on_progress(done: int, total: int) -> None:
            progress_bar.update(task, completed=done, total=total)

        result = convert(cfg, log=log, progress=on_progress)

    # ── Summary ───────────────────────────────────────────────────────────────
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column(style="dim")
    summary.add_column()
    summary.add_row("Converted", f"[green]{result.converted}[/]")
    summary.add_row(
        "Failed",
        f"[red]{result.failed}[/]" if result.failed else "0",
    )
    summary.add_row("Elapsed", f"{result.elapsed:.1f}s")

    style = "green" if result.failed == 0 else "yellow"
    console.print(Panel(summary, title=f"[bold {style}]Done[/]", expand=False))

    if result.errors:
        console.print("\n[bold red]Failed files:[/]")
        for err in result.errors:
            console.print(f"  [red]✗[/] {err}")

    if alert:
        print("\a", end="", flush=True)

    if result.failed:
        raise typer.Exit(1)
