"""Main CLI and backend image conversion logic for the Batch Image Converter."""

import os
import sys
import re
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import messagebox

from packaging import version
import requests
from tqdm import tqdm
import colorama
from colorama import Fore, Back, Style
from PIL import Image, ImageCms

from constants import (
    FILTER_NAMES,
    CMYK_PROFILE_PATH,
    SRGB_PROFILE_PATH,
    EXCEPTION_FILES,
    FILETYPE,
)


__author__ = "Edoardo Tosin"
__copyright__ = "Copyright (C) 2022-25 Edoardo Tosin"
__credits__ = "Edoardo Tosin"
__license__ = "GPL-3.0"
__version__ = "1.4.0"

colorama.init(autoreset=True)

Image.MAX_IMAGE_PIXELS = 9e9

# Global variable to track if running in GUI mode
GUI_MODE = False
GUI_LOG_CALLBACK = None


def set_gui_mode(enabled=True, log_callback=None):
    """Set GUI mode and logging callback."""
    global GUI_MODE, GUI_LOG_CALLBACK
    GUI_MODE = enabled
    GUI_LOG_CALLBACK = log_callback


def log_message(message, color="white"):
    """Log message to either console or GUI depending on mode."""
    if GUI_MODE and GUI_LOG_CALLBACK:
        GUI_LOG_CALLBACK(message)
    else:
        # Console mode - use colorama colors
        color_map = {
            "blue": Fore.BLUE,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "red": Fore.RED,
            "white": Fore.WHITE,
        }
        print(f"{color_map.get(color, Fore.WHITE)}{message}{Style.RESET_ALL}")


def str_filetypes(list_types):
    """
    Convert a list of file extensions into a comma-separated
    string without leading dots.
    """
    return ", ".join(t.strip(".") for t in list_types)


parser = argparse.ArgumentParser(
    description="Python script that converts images to a certain dpi, "
    "max long side resolution and RGB color space. "
    f"Filetype: {str_filetypes(FILETYPE)}.",
    prog=f".{os.sep}" + __file__.rsplit(os.sep, maxsplit=1)[-1],
)
group_img = parser.add_argument_group("commands", "Image conversion properties")
group_opt = parser.add_argument_group(
    "other options", "Customize script behavior (alert and wait)"
)

parser.add_argument("-v", "--version", action="version", version=__version__)
parser.add_argument(
    "--update", action="store_true", help="check latest version available"
)


def dir_path(path):
    """Validate that a given path is a directory."""
    if os.path.isdir(path):
        return path
    raise argparse.ArgumentTypeError(f'"{path}" is not a valid path')


current_path = sys.argv[0].rsplit(os.sep, 1)[0]

group_img.add_argument(
    "-p",
    "--path",
    type=dir_path,
    default=current_path,
    help=f'path where images are located (default: "{current_path}")',
)
group_img.add_argument(
    "-d",
    "--dpi",
    type=int,
    choices=range(1, 1001),
    metavar="[1-1000]",
    default=72,
    help="pixel density in dpi (default: 72)",
)
group_img.add_argument(
    "-s",
    "--size",
    type=int,
    choices=range(1, 10001),
    metavar="[1-10000]",
    default=1000,
    help="max resolution of image (long side) in pixels (default: 1000)",
)
group_img.add_argument(
    "-f",
    "--filter",
    type=int,
    choices=range(0, 6),
    metavar="[0-5]",
    default=0,
    help="type of filter used for downscaling (default: 0 = Nearest)",
)
group_img.add_argument(
    "--colorspace",
    "--cs",
    type=bool,
    default=False,
    action=argparse.BooleanOptionalAction,
    help="convert all images to RGB color space",
)
group_img.add_argument(
    "-q",
    "--quality",
    type=int,
    choices=range(1, 101),
    metavar="[1-100]",
    default=80,
    help="quality of output images (default: 80)",
)
group_img.add_argument(
    "-m",
    "--max-image-mpixels",
    type=int,
    choices=range(0, 10001),
    metavar="[0-10000]",
    default=0,
    help="maximum image resolution allowed in Megapixels (default: 0 [None])",
)
group_img.add_argument(
    "--optimize",
    type=bool,
    default=True,
    action=argparse.BooleanOptionalAction,
    help="attempt to compress the palette by eliminating unused colors",
)
group_opt.add_argument(
    "--alert",
    type=bool,
    default=True,
    action=argparse.BooleanOptionalAction,
    help="play alert sound when finished the conversion",
)
group_opt.add_argument(
    "--wait",
    type=bool,
    default=True,
    action=argparse.BooleanOptionalAction,
    help="wait for user keypress (Enter) when finished the conversion",
)


def get_update():
    """Check GitHub for the latest version of the application."""
    try:
        release_path = "/EdoardoTosin/Batch-Image-Converter/releases/latest"
        api_url = "https://api.github.com/repos" + release_path
        response = requests.get(api_url, timeout=10)
        latest_release = response.json()["tag_name"].strip("v")
        if version.parse(__version__) < version.parse(latest_release):
            latest_page_url = "https://github.com" + release_path
            log_message(f"New Version {latest_release}: {latest_page_url}", "yellow")
        else:
            log_message(
                f"Available version: {latest_release}, Current version: {__version__}"
            )
            log_message(f"Batch-Image-Converter is up to date ({__version__})")
    except (ValueError, OSError) as _:
        log_message("Unable to check latest version", "yellow")
    sys.exit()


def print_init(args):
    """Display initial settings and warnings before conversion starts."""
    log_message("=== Conversion Settings ===", "blue")
    log_message(f"Root folder: {args.path}", "blue")
    log_message(f"DPI value: {args.dpi}", "blue")
    log_message(f"Max pixel long side: {args.size}", "blue")
    log_message(f"Downscaling filter: {FILTER_NAMES.get(args.filter)}", "blue")
    log_message(f"Output image quality: {args.quality}", "blue")

    if args.quality > 95:
        log_message(
            "WARNING: Values above 95 might not decrease file size with hardly any gain in image quality!",
            "yellow",
        )

    log_message(f"Color space conversion: {args.colorspace}", "blue")

    if args.colorspace:
        if not os.path.exists(CMYK_PROFILE_PATH) or not os.path.exists(
            SRGB_PROFILE_PATH
        ):
            log_message(
                "WARNING: ICC profile files not found. Skipping CMYK to sRGB conversion.",
                "yellow",
            )
        else:
            log_message(
                "WARNING: Colorspace conversion from CMYK to RGB may not be accurate!",
                "yellow",
            )

    log_message(f"Play alert when finished: {args.alert}", "blue")
    log_message(f"Wait after end of conversion: {args.wait}", "blue")
    log_message("=== Starting Conversion ===", "green")


def convert_to_srgb(img):
    """Convert CMYK image to sRGB color profile using ICC profiles."""
    img = ImageCms.profileToProfile(
        img, CMYK_PROFILE_PATH, SRGB_PROFILE_PATH, outputMode="RGB"
    )
    return img


def process_image(args, root, filename, converted_counter):
    """
    Process a single image: resizing, converting color, saving with
    quality and DPI settings.
    """
    if args.max_image_mpixels > 0:
        Image.MAX_IMAGE_PIXELS = args.max_image_mpixels
    max_size = (args.size, args.size)
    dpi = (args.dpi, args.dpi)

    image_path = os.path.join(root, filename)

    try:
        img = Image.open(image_path)
    except (ValueError, OSError) as _:
        EXCEPTION_FILES.append([root, filename])
    else:
        if args.colorspace and img.mode == "CMYK":
            img = convert_to_srgb(img)

        img.thumbnail(max_size, Image.Resampling(args.filter))
        if args.colorspace:
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                new_image_path = os.path.splitext(image_path)[0] + ".jpg"
                img.save(
                    new_image_path,
                    dpi=dpi,
                    quality=args.quality,
                    optimize=args.optimize,
                )
                img.close()
                os.remove(image_path)
            else:
                img.save(
                    image_path, dpi=dpi, quality=args.quality, optimize=args.optimize
                )
                img.close()
        else:
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                new_image_path = os.path.splitext(image_path)[0] + ".jpg"
                img.save(
                    new_image_path,
                    dpi=dpi,
                    quality=args.quality,
                    optimize=args.optimize,
                )
                img.close()
                os.remove(image_path)
            else:
                img.save(
                    image_path, dpi=dpi, quality=args.quality, optimize=args.optimize
                )
                img.close()
        converted_counter["count"] += 1


def wait_keypress(val):
    """Pause the program and wait for a keypress from the user."""
    if not GUI_MODE:  # Only wait for keypress in CLI mode
        try:
            print(
                f"\n{Fore.YELLOW}Press {Back.BLACK}{Style.BRIGHT}"
                f"Enter{Style.NORMAL}{Back.RESET} to {val}{Style.RESET_ALL}",
                end="",
            )
            input()
        except SyntaxError:
            pass


def main(args):
    """Execute the batch image conversion process using given arguments."""
    print_init(args)
    other_files = []

    # Check for ICC profiles if colorspace conversion is enabled
    if args.colorspace and not (
        os.path.exists(CMYK_PROFILE_PATH) and os.path.exists(SRGB_PROFILE_PATH)
    ):
        args.colorspace = False

    # Find all files in the directory
    for root, _, filenames in os.walk(args.path):
        for filename in filenames:
            if not filename.lower().endswith(FILETYPE):
                other_files.append([root, filename])

    # Clear exception files list for this run
    EXCEPTION_FILES.clear()
    converted_counter = {"count": 0}
    start_time = datetime.now()

    log_message("Processing images...", "green")

    # Process images with threading
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(process_image, args, root, filename, converted_counter): (
                root,
                filename,
            )
            for root, _, filenames in os.walk(args.path)
            for filename in filenames
            if filename.lower().endswith(FILETYPE)
        }

        if not GUI_MODE:
            # Show progress bar in CLI mode
            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                unit_divisor=100,
                colour="green",
                bar_format="{desc}: {percentage:3.0f}% | {bar} | {n_fmt}/{total_fmt}"
                " Files | Elapsed: {elapsed} | Remaining: {remaining}",
            ):
                root, filename = futures[future]
                try:
                    future.result()
                except (ValueError, OSError) as _:
                    EXCEPTION_FILES.append([root, filename])
        else:
            # Process without progress bar in GUI mode
            for future in as_completed(futures):
                root, filename = futures[future]
                try:
                    future.result()
                except (ValueError, OSError) as _:
                    EXCEPTION_FILES.append([root, filename])

    # Calculate execution time
    time_exec = datetime.now() - start_time
    str_time = (
        re.match(r"(.+)\.(.+)", str(time_exec), re.M | re.I)
        .group(1)
        .replace(":", "h ", 1)
        .replace(":", "m ", 1)
        + "s"
    )

    # Log results
    log_message("=== Conversion Results ===", "green")
    log_message(f"Time to complete: {str_time}", "green")
    log_message(
        f"Total number of converted images: {converted_counter['count']}", "blue"
    )

    # Log corrupted files
    if EXCEPTION_FILES:
        plural_s = "" if len(EXCEPTION_FILES) == 1 else "s"
        log_message(f"{len(EXCEPTION_FILES)} Corrupted image{plural_s}:", "red")
        for excpt in EXCEPTION_FILES:
            log_message(f"  -> {excpt[1]} found in {excpt[0]}", "red")
    else:
        log_message("No corrupted images found.", "green")

    # Log other files
    if other_files:
        log_message("Other files (not converted):", "yellow")
        for other in other_files:
            if other[1] != os.path.basename(__file__):
                log_message(f"  -> {other[1]} found in {other[0]}", "yellow")
    else:
        log_message("No other files found.", "green")

    # Alert and wait handling
    if args.alert:
        print("\a", end="")  # Bell sound

    if args.wait and not GUI_MODE:
        wait_keypress("exit")
    elif GUI_MODE:
        # Show completion message in GUI mode
        messagebox.showinfo(
            "Conversion Complete",
            f"Image conversion completed successfully!\n\n"
            f"Converted {converted_counter['count']} images in {str_time}",
        )


if __name__ == "__main__":
    try:
        cli_args = parser.parse_args()
        if cli_args.update:
            get_update()
        main(cli_args)
    except KeyboardInterrupt:
        sys.exit()
