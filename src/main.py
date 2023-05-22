#!/usr/bin/env python3

import argparse
from io import open
import os, sys
from tqdm import tqdm
from PIL import Image#, ImageCms
from datetime import datetime
import re
import colorama
from colorama import Fore, Back, Style
import requests
from packaging import version

__author__      = "Edoardo Tosin"
__copyright__   = "Copyright (C) 2022-23 Edoardo Tosin"
__credits__     = "Edoardo Tosin"
__license__     = "GPL-3.0"
__version__     = "1.2.1"

colorama.init(autoreset=True)

filetype = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp', '.psd', '.psb')

Image.MAX_IMAGE_PIXELS = 9e9

def str_filetypes(list_types):
    text = ''
    spacing = ', '
    for single_type in list_types:
        text = text + single_type.strip('.') + spacing
    return text[0:len(text)-len(spacing)]

parser = argparse.ArgumentParser(description=f'Python script that convert images to a certain dpi, max long side resolution and rgb color space. Filetype: {str_filetypes(filetype)}.', prog=f".{os.sep}"+__file__.split(os.sep)[-1])
group_img = parser.add_argument_group('commands', 'Image conversion properties')
group_opt = parser.add_argument_group('other options', 'Customize script behaviour (alert and wait)')

parser.add_argument(
    "-v",
    "--version",
    action='version',
    version= __version__,
)

parser.add_argument(
    "--update",
    action='store_true',
    help="check latest version available"
)

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"\"{path}\" is not a valid path")

current_path = sys.argv[0].rsplit(os.sep, 1)[0]

group_img.add_argument(
    "-p",
    "--path",
    type=dir_path,
    default=current_path,
    nargs=None,
    help=f"path where images are located (default: \"{current_path}\")",
)

group_img.add_argument(
    "-d",
    "--dpi",
    type=int,
    choices=range(1, 1001),
    metavar="[1-1000]",
    default=72,
    nargs=None,
    help="pixel density in pixels per inch (dpi), must be in range 1-1000 (default: 72)",
)

group_img.add_argument(
    "-s",
    "--size",
    type=int,
    choices=range(1, 10001),
    metavar="[1-10000]",
    default=1000,
    nargs=None,
    help="max resolution of image (long side) in pixel (downscaling only), must be in range 1-10000 (default: 1000)",
)

group_img.add_argument(
    "-f",
    "--filter",
    type=int,
    choices=range(0, 6),
    metavar="[0 = Nearest, 4 = Box, 2 = Bilinear, 5 = Hamming, 3 = Bicubic, 1 = Lanczos]",
    default=0,
    nargs=None,
    help="type of filter used for downscaling, must be an integer in range 0-5 (default: 0 = Nearest)",
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
    nargs=None,
    help="quality of output images, must be in range 1-100 (values above 95 should be avoided) (default: 80)",
)

group_img.add_argument(
    "-m",
    "--max-image-mpixels",
    type=int,
    choices=range(0, 10001),
    metavar="[0-10000]",
    default=0,
    nargs=None,
    help="maximum images resolution allowed in Megapixel, (default: 0 [None])",
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
    help="wait user keypress (Enter) when finished the conversion",
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
            print(f"Available version: {latest_release}, Current version: {__version__}")
            print(f"Batch-Image-Converter is up to date ({__version__})")
    except requests.ConnectionError:
        print(f"{Fore.YELLOW}Unable to check latest version")
    sys.exit()

def print_init(args):
    
    print(f"\nRoot folder: {Fore.BLUE}{args.path}\n")
    print(f"Dpi value: {Fore.BLUE}{args.dpi}")
    print(f"Max pixel long side: {Fore.BLUE}{args.size}{Style.RESET_ALL}")
    switcher = {
        0: 'Nearest',
        4: 'Box',
        2: 'Bilinear',
        5: 'Hamming',
        3: 'Bicubic',
        1: 'Lanczos',
    }
    filter_name = switcher.get(args.filter)
    print(f"Downscaling filter: {Fore.BLUE}{filter_name}{Style.RESET_ALL}")
    print(f"Output image quality: {Fore.BLUE}{args.quality}{Style.RESET_ALL}", end='')
    if args.quality>95:
        print(f" -> {Fore.YELLOW}WARNING: values above 95 might not decrease file size with hardly any gain in image quality!")
    else:
        print('')
    print(f"Color space conversion: {Fore.BLUE}{args.colorspace}", end='')
    if args.colorspace is True:
        print(f" -> {Fore.YELLOW}WARNING: colorspace conversion from CMYK to RGB may not be accurate!")
    else:
        print('')
    print(f"Mute alert when finished: {Fore.BLUE}{args.alert}")
    print(f"Wait after end of conversion: {Fore.BLUE}{args.wait}", end='')
    if args.wait is True:
        print(f" -> {Fore.GREEN}Press enter to confirm exit when finished.")
    else:
        print('')


def wait_keypress(val):
    
    try:
        print(f"\n{Fore.YELLOW}Press {Back.BLACK}{Style.BRIGHT}Enter{Style.NORMAL}{Back.RESET} to {val}{Style.RESET_ALL}", end='')
        press = input()
    except SyntaxError:
        pass


def main(args):
    
    print_init(args)
    
    exception_files = []
    other_files = []
    if args.max_image_mpixels > 0:
        Image.MAX_IMAGE_PIXELS = args.max_image_mpixels
    MAX_SIZE = (args.size, args.size)
    filters = [Image.Resampling.NEAREST, Image.Resampling.BILINEAR, Image.Resampling.BICUBIC,  Image.Resampling.LANCZOS]
    DPI = (args.dpi, args.dpi)
    count = 0
    
    wait_keypress(f"continue or {Back.BLACK}{Style.BRIGHT}CTRL+C{Style.NORMAL}{Back.RESET} to abort")
    
    print("\nProcessing images")
    
    file_count = sum(len(files) for _, _, files in os.walk(args.path))
    
    startTime = datetime.now()
    
    with tqdm(total=file_count, unit_divisor=100, colour='green', bar_format='{desc}: {percentage:3.0f}% | {bar} | {n_fmt}/{total_fmt} Files | Elapsed: {elapsed} | Remaining: {remaining}') as pbar:
        for root, dirnames, filenames in os.walk(args.path):
            for filename in filenames:
                if filename.lower().endswith(filetype):
                    image_path = root + os.sep + filename
                    try:
                        img = Image.open(image_path)
                    except:
                        exception_files.append([root, filename])
                    else:
                        if filename.lower().endswith('.png'):
                            colour_space = 'RGBA'
                        else:
                            colour_space = 'RGB'
                        
                        img.thumbnail(MAX_SIZE, Image.Resampling(args.filter))
                        if args.colorspace is True:
                            if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')):
                                new_image_path = image_path.rsplit('.', 1)[0] + '.jpg'
                                img.convert(colour_space).save(new_image_path, dpi=DPI, quality=args.quality, optimize=args.optimize)
                                img.close()
                                os.remove(image_path)
                            else:
                                img.convert(colour_space).save(image_path, dpi=DPI, quality=args.quality, optimize=args.optimize)
                                img.close()
                        else:
                            if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')):
                                new_image_path = image_path.rsplit('.', 1)[0] + '.jpg'
                                img.save(new_image_path, dpi=DPI, quality=args.quality, optimize=args.optimize)
                                img.close()
                                os.remove(image_path)
                            else:
                                img.save(image_path, dpi=DPI, quality=args.quality, optimize=args.optimize)
                                img.close()
                        count+=1
                
                else:
                    other_files.append([root, filename])
                
                pbar.update(1)
    
    time_exec = (datetime.now() - startTime)
    
    str_time = re.match(r'(.+)\.(.+)', str(time_exec), re.M|re.I).group(1).replace(":", "h ", 1).replace(":", "m ", 1)+'s'
    print(f"\nTime to complete: {Fore.GREEN}{str_time}")
    
    print(f"Total number of converted images: {Fore.GREEN}{count}")
    
    if len(exception_files)>0:
        plural_s = ''
        if len(exception_files)>1:
            plural_s = 's'
        print(f"\n{Fore.RED}{len(exception_files)}{Style.RESET_ALL} Corrupted image{plural_s}:")
        for excpt in exception_files:
            print(f"-> {Fore.RED}{excpt[1]}{Style.RESET_ALL} found in {Fore.RED}{excpt[0]}")
    else:
        print("No corrupted images found.")
    
    if len(other_files)==1:
        print("No other files found.")
    else:
        print("\nOther files (not converted):")
        for other in other_files:
            if other[1]!=os.path.basename(__file__):
                print(f"-> {Fore.CYAN}{other[1]}{Style.RESET_ALL} found in {Fore.CYAN}{other[0]}")
    if args.alert is True:
        print('\a', end='')
    if args.wait is True:
        wait_keypress(f"exit")


if __name__ == "__main__":
    try:
        if parser.parse_args().update:
            get_update()
        main(parser.parse_args())
    except (KeyboardInterrupt):
        sys.exit()