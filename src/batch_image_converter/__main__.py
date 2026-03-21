"""Entry point: no arguments → GUI, any argument → CLI."""

from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) > 1:
        from batch_image_converter.cli import app

        app()
    else:
        from batch_image_converter.gui import launch

        launch()


if __name__ == "__main__":
    main()
