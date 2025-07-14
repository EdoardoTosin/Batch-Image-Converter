#!/usr/bin/env python3

import argparse
import os
import sys
from tqdm import tqdm
from PIL import Image, ImageCms
from datetime import datetime
import re
import colorama
from colorama import Fore, Back, Style
import requests
from packaging import version
from concurrent.futures import ThreadPoolExecutor, as_completed

from customtkinter import *

__author__ = "Edoardo Tosin"
__copyright__ = "Copyright (C) 2022-25 Edoardo Tosin"
__credits__ = "Edoardo Tosin"
__license__ = "GPL-3.0"
__version__ = "1.4.0"

colorama.init(autoreset=True)

filetype = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp")
Image.MAX_IMAGE_PIXELS = 9e9

cmyk_profile_path = "USWebCoatedSWOP.icc"
srgb_profile_path = "sRGB.icc"

exception_files = []
converted_count = 0


def str_filetypes(list_types):
    return ", ".join(t.strip(".") for t in list_types)


parser = argparse.ArgumentParser(
    description=f"Python script that converts images to a certain dpi, max long side resolution and RGB color space. Filetype: {str_filetypes(filetype)}.",
    prog=f".{os.sep}" + __file__.split(os.sep)[-1],
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
    if os.path.isdir(path):
        return path
    else:
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
    try:
        release_path = "/EdoardoTosin/Batch-Image-Converter/releases/latest"
        api_url = "https://api.github.com/repos" + release_path
        response = requests.get(api_url)
        latest_release = response.json()["tag_name"].strip("v")
        if version.parse(__version__) < version.parse(latest_release):
            latest_page_url = "https://github.com" + release_path
            print(f"New Version {latest_release}: {Fore.YELLOW}{latest_page_url}")
        else:
            print(
                f"Available version: {latest_release}, Current version: {__version__}"
            )
            print(f"Batch-Image-Converter is up to date ({__version__})")
    except:
        print(f"{Fore.YELLOW}Unable to check latest version")
    sys.exit()


def print_init(args):
    win = CTk()
    win.title("Convering proccess")
    win.geometry("500x500")

    filter_names = {
        0: "Nearest",
        1: "Lanczos",
        2: "Bilinear",
        3: "Bicubic",
        4: "Box",
        5: "Hamming",
    }

    CTkLabel(
        win, text=f"\nRoot folder: {args.path}", text_color="blue", font=("Arial", 16)
    ).pack()

    CTkLabel(
        win, text=f"Dpi value: {args.dpi}", text_color="blue", font=("Arial", 16)
    ).pack()

    CTkLabel(
        win,
        text=f"Max pixel long side: {args.size}",
        text_color="blue",
        font=("Arial", 16),
    ).pack()

    CTkLabel(
        win,
        text=f"Downscaling filter: {filter_names.get(args.filter)}",
        text_color="blue",
        font=("Arial", 16),
    ).pack()

    CTkLabel(
        win,
        text=f"Output image quality: {args.quality}",
        text_color="blue",
        font=("Arial", 16),
    ).pack()

    if args.quality > 95:
        CTkLabel(
            win,
            text=f" -> WARNING: values above 95 might not decrease file size with hardly any gain in image quality!",
            text_color="yellow",
            font=("Arial", 18),
        ).pack()

    else:
        print("")

    CTkLabel(
        win,
        text=f"Color space conversion: {args.colorspace}",
        text_color="blue",
        font=("Arial", 16),
    ).pack()

    if args.colorspace:
        if not os.path.exists(cmyk_profile_path) or not os.path.exists(
            srgb_profile_path
        ):
            CTkLabel(
                win,
                text=f" -> WARNING: ICC profile files not found. Skipping CMYK to sRGB conversion.",
                text_color="yellow",
                font=("Arial", 18),
            ).pack()

        else:
            CTkLabel(
                win,
                text=f" -> WARNING: Colorspace conversion from CMYK to RGB may not be accurate!",
                text_color="yellow",
                font=("Arial", 18),
            ).pack()
    else:
        print("")

    CTkLabel(
        win,
        text=f"Mute alert when finished: {args.alert}",
        text_color="blue",
        font=("Arial", 14),
    ).pack()

    CTkLabel(
        win,
        text=f"Wait after end of conversion: {args.wait}",
        text_color="blue",
        font=("Arial", 14),
    ).pack()

    if args.wait:
        # CTkLabel(win , text=f" -> Press enter to confirm exit when finished." , text_color="green" , font=("Arial" , 17)).pack()
        pass
    else:
        print("")

    close_btn = CTkButton(
        win,
        fg_color="green",
        text_color="white",
        width=250,
        height=33,
        font=("Arial", 15),
        text="Ok",
        corner_radius=10,
        hover=False,
        command=win.destroy,
    )
    close_btn.pack(pady=30)

    win.mainloop()


def convert_to_srgb(img):
    global cmyk_profile_path
    global srgb_profile_path
    img = ImageCms.profileToProfile(
        img, cmyk_profile_path, srgb_profile_path, outputMode="RGB"
    )
    return img


def process_image(args, root, filename):
    global converted_count
    if args.max_image_mpixels > 0:
        Image.MAX_IMAGE_PIXELS = args.max_image_mpixels
    MAX_SIZE = (args.size, args.size)
    DPI = (args.dpi, args.dpi)

    image_path = os.path.join(root, filename)

    try:
        img = Image.open(image_path)
    except:
        exception_files.append([root, filename])
    else:
        if args.colorspace and img.mode == "CMYK":
            img = convert_to_srgb(img)

        img.thumbnail(MAX_SIZE, Image.Resampling(args.filter))
        if args.colorspace:
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                new_image_path = os.path.splitext(image_path)[0] + ".jpg"
                img.save(
                    new_image_path,
                    dpi=DPI,
                    quality=args.quality,
                    optimize=args.optimize,
                )
                img.close()
                os.remove(image_path)
            else:
                img.save(
                    image_path, dpi=DPI, quality=args.quality, optimize=args.optimize
                )
                img.close()
        else:
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                new_image_path = os.path.splitext(image_path)[0] + ".jpg"
                img.save(
                    new_image_path,
                    dpi=DPI,
                    quality=args.quality,
                    optimize=args.optimize,
                )
                img.close()
                os.remove(image_path)
            else:
                img.save(
                    image_path, dpi=DPI, quality=args.quality, optimize=args.optimize
                )
                img.close()
        converted_count += 1


def wait_keypress(val):
    try:
        print(
            f"\n{Fore.YELLOW}Press {Back.BLACK}{Style.BRIGHT}Enter{Style.NORMAL}{Back.RESET} to {val}{Style.RESET_ALL}",
            end="",
        )
        input()
    except SyntaxError:
        pass


def main(args):
    global cmyk_profile_path
    global srgb_profile_path
    info = print_init(args)
    other_files = []

    win2 = CTk()
    win2.title("Converting process")
    win2.geometry("500x500")

    if args.colorspace and not (
        os.path.exists(cmyk_profile_path) and os.path.exists(srgb_profile_path)
    ):
        args.colorspace = False

    for root, _, filenames in os.walk(args.path):
        for filename in filenames:
            if not filename.lower().endswith(filetype):
                other_files.append([root, filename])

    CTkLabel(win2, text="continue or CTRL+C to abort", font=("Arial", 25)).pack(pady=20)

    # wait_keypress(
    #     f"continue or {Back.BLACK}{Style.BRIGHT}CTRL+C{Style.NORMAL}{Back.RESET} to abort"
    # )

    CTkLabel(
        win2, text="Processing images", text_color="green", font=("Arial", 17)
    ).pack()

    start_time = datetime.now()

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_image, args, root, filename)
            for root, _, filenames in os.walk(args.path)
            for filename in filenames
            if filename.lower().endswith(filetype)
        ]
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            unit_divisor=100,
            colour="green",
            bar_format="{desc}: {percentage:3.0f}% | {bar} | {n_fmt}/{total_fmt} Files | Elapsed: {elapsed} | Remaining: {remaining}",
        ):
            try:
                future.result()
            except Exception as exc:
                exception_files.append([root, filename])

    time_exec = datetime.now() - start_time
    str_time = (
        re.match(r"(.+)\.(.+)", str(time_exec), re.M | re.I)
        .group(1)
        .replace(":", "h ", 1)
        .replace(":", "m ", 1)
        + "s"
    )

    CTkLabel(
        win2,
        text=f"Time to complete: {str_time}",
        text_color="green",
        font=("Arial", 15),
    ).pack()
    CTkLabel(
        win2,
        text=f"Total number of converted images: {converted_count}",
        text_color="blue",
        font=("Arial", 17),
    ).pack()

    if exception_files:
        plural_s = "" if len(exception_files) == 1 else "s"
        CTkLabel(
            win2,
            text=f"{len(exception_files)} Corrupted image{plural_s}",
            text_color="pink",
            font=("Arial", 14),
        ).pack()
        for excpt in exception_files:
            CTkLabel(
                win2,
                text=f"-> {excpt[1]} found in {excpt[0]}",
                text_color="pink",
                font=("Arial", 14),
            ).pack()
    else:
        CTkLabel(
            win2,
            text="No corrupted images found.",
            text_color="red",
            font=("Arial", 16),
        ).pack()

    if len(other_files) == 1:
        CTkLabel(
            win2, text="No other files found.", text_color="red", font=("Arial", 16)
        ).pack()
    else:
        CTkLabel(
            win2,
            text="Other files (not converted):",
            text_color="red",
            font=("Arial", 16),
        ).pack()
        for other in other_files:
            if other[1] != os.path.basename(__file__):
                CTkLabel(
                    win2,
                    text=f"-> {other[1]} found in {other[0]}",
                    text_color="blue",
                    font=("Arial", 16),
                ).pack()

    if args.alert:
        print("\a", end="")
    if args.wait:
        wait_keypress(f"exit")

    win2.mainloop()


if __name__ == "__main__":
    try:
        args = parser.parse_args()
        if args.update:
            get_update()
        main(args)
    except KeyboardInterrupt:
        sys.exit()
