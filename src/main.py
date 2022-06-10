#!/usr/bin/env python3.10

import argparse
from io import open
import os
from tqdm import tqdm
from PIL import Image, ImageCms
from datetime import datetime
import re
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

filetype = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.psd', '.psb')

def str_filetypes(list_types):
	text = ''
	spacing = ', '
	for single_type in list_types:
		text = text + single_type.strip('.') + spacing
	return text[0:len(text)-len(spacing)]

parser = argparse.ArgumentParser(description=f'Batch image conversion. Filetype: {str_filetypes(filetype)}.')
group = parser.add_argument_group('commands', 'use these commands to customize script behaviour and image conversion')

group.add_argument(
	"--dpi",
	"-d",
	type=int,
	choices=range(1, 1000),
	metavar="[1-1000]",
	default=72,
	help="pixel density in pixels per inch (dpi), must be in range 1-1000 (default: 72)",
)

group.add_argument(
	"--size",
	"-s",
	type=int,
	choices=range(1, 10000),
	metavar="[1-10000]",
	default=1000,
	help="max resolution of image (long side) in pixel, must be in range 1-10000 (default: 1000)",
)

group.add_argument(
	"--colorspace",
	"-c",
	type=bool,
	default=False,
	action=argparse.BooleanOptionalAction,
	help="convert all images to RGB color space",
)

group.add_argument(
	"--mute",
	"-m",
	type=bool,
	default=False,
	action=argparse.BooleanOptionalAction,
	help="play alert sound when finished",
)

group.add_argument(
	"--wait",
	"-w",
	type=bool,
	default=True,
	action=argparse.BooleanOptionalAction,
	help="wait user keypress (Enter) at the end",
)

def print_init(args, folder):
	print(f"\nRoot folder: {Fore.BLUE}{str(folder)}\n")
	print(f"Dpi value: {Fore.BLUE}{args.dpi}")
	print(f"Max pixel long side: {Fore.BLUE}{args.size}{Style.RESET_ALL}")
	print(f"Color space conversion: {Fore.BLUE}{args.colorspace}", end='')
	if (args.colorspace) is True:
		print(f" -> {Fore.YELLOW}WARNING: colorspace conversion from CMYK to RGB may not be accurate!")
	else:
		print('')
	print(f"Mute alert when finished: {Fore.BLUE}{args.mute}")
	print(f"Wait after end of conversion: {Fore.BLUE}{args.wait}", end='')
	if (args.wait) is True:
		print(f" -> {Fore.GREEN}Press enter to confirm exit when finished.")
	else:
		print('')

def wait_keypress():
	try:
		input(f"\n{Fore.YELLOW}Press enter to continue")
	except SyntaxError:
		pass

def main(args):
	
	folder = os.path.realpath(__file__).rsplit(os.sep, 1)[0]
	
	print_init(args, folder)
	
	exception_files = []
	other_files = []
	MAX_SIZE = (args.size, args.size)
	DPI = args.dpi
	count = 0
	
	wait_keypress()
	
	print("\nProcessing images")
	
	startTime = datetime.now()
	
	for root, dirnames, filenames in tqdm(list(os.walk(folder)), unit_divisor=100, colour='green', bar_format='{desc}: {percentage:3.0f}% | {bar} | {n_fmt}/{total_fmt} Folders | Elapsed: {elapsed} | Remaining: {remaining}'):
		for filename in filenames:
			if filename.endswith(filetype):
				image_path = root + os.sep + filename
				try:
					im = Image.open(image_path)
				except:
					exception_files.append([root, filename])
				else:
					if (filename.lower().endswith('.png')):
						colour_space = 'RGBA'
					else:
						colour_space = 'RGB'
					if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')):
						if (args.colorspace) is True:
							im = im.convert(colour_space)
						new_image_path = image_path.rsplit('.', 1)[0] + '.jpg'
						im.save(new_image_path, dpi=(DPI,DPI), quality=90, optimize=True)
						os.remove(image_path)
					else:
						if (args.colorspace):
							im = im.convert(colour_space)
						im.save(image_path, dpi=(DPI,DPI), quality=90, optimize=True)
						new_image_path = image_path
					img = Image.open(new_image_path)
					img.thumbnail(MAX_SIZE, Image.ANTIALIAS)
					img.save(new_image_path)
					count+=1
				
			else:
				other_files.append([root, filename])
	
	time_exec = (datetime.now() - startTime)
	
	str_time = re.match(r'(.+)\.(.+)', str(time_exec), re.M|re.I).group(1).replace(":", "h ", 1).replace(":", "m ", 1)+'s'
	print(f"\nTime to complete: {Fore.GREEN}{str_time}")
	
	print(f"Total number of converted images: {Fore.GREEN}{count}")
	
	if (len(exception_files)>0):
		print(f"\n{Fore.RED}{len(exception_files)}{Style.RESET_ALL} Corrupted images:")
		for excpt in exception_files:
			print(f"-> {Fore.RED}{excpt[1]}{Style.RESET_ALL} found in {Fore.RED}{excpt[0]}")
	else:
		print("No corrupted images found.")
	
	if (len(other_files)==1):
		print("No other files found.")
	else:
		print("\nOther files (not converted):")
		for other in other_files:
			if(other[1]!=os.path.basename(__file__)):
				print(f"-> {Fore.CYAN}{other[1]}{Style.RESET_ALL} found in {Fore.CYAN}{other[0]}")
	if (args.mute) is False:
		print('\a', end='')
	if (args.wait) is True:
		wait_keypress()

if __name__ == "__main__":

	main(parser.parse_args())
