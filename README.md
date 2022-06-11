# Batch-Image-Converter

## Summary

Python script that converts images to a certain dpi, max long side resolution and rgb color space. If images are not in jpg or png then they are all converted to jpg.

Accepted file types: jpg, jpeg, png, tif, tiff, bmp, psd, psb.

> **Warning**: psd and psb file types have not been tested.

![Output](./doc/output.jpg)

## Instructions

### Linux

- `git clone https://github.com/EdoardoTosin/Batch-Image-Converter.git`
- `cd Batch-Image-Converter/src && python3 -m pip install -r requirements.txt`
- Copy `main.py` into the folder you want to convert all images.
- `python3 main.py`
- Help screen: `python3 main.py -h`

### Windows

- `git clone https://github.com/EdoardoTosin/Batch-Image-Converter.git`
- `cd Batch-Image-Converter\src; python -m pip install -r requirements.txt`
- Copy `main.py` into the folder you want to convert all images.
- Double click `main.py` to start it with default parameters or launch via terminal with `python main.py`.
- Help screen: `python main.py -h`

## Commands

![Help](./doc/help.jpg)

> **Note**: append the following string before calling main.py script based on your operating system.
> 
> - Linux: `python3`
> - Windows: `python`

### Help :sos: [-h, --help]

Show help message and exit

Usage: `main.py -h`

### Dpi [--dpi, -d]

Set pixel density in pixels per inch (dpi), must be in range 1-1000 (Default: 72).

Usage: `main.py -d 72`

### Max Resolution [--size, -s]

Set max resolution of image (long side) in pixel (downscaling only), must be in range 1-10000 (default: 1000)".

Usage: `main.py -s 1000`

### Color space [--colorspace, --no-colorspace, --cs, --no-cs]

Set color space to RGB (default: False).

> **Warning**: converting CYMK to RGB might not be accurate due to PIL Python module not using icc profiles.

| True         | False           |
| ------------ | --------------- |
| --colorspace | --no-colorspace |
| --cs         | --no-cs         |

Usage: `main.py --colorspace`

### Quality [--quality, --no-quality]

Set quality of output images, must be in range 1-100 (values above 95 should be avoided) (default: 80).

Usage: `main.py --quality 80`

### Optimize [--optimize, --no-optimize]

Attempt to compress the palette by eliminating unused colors (default: True).

| True       | False         |
| ---------- | ------------- |
| --optimize | --no-optimize |

Usage: `main.py --optimize`

### Alert :bell: [--alert, --no-alert]

Play alert sound when finished the conversion (default: True).

| True   | False     |
| ------ | --------- |
| --mute | --no-mute |

Usage: `main.py --mute`

### Wait :raised_hand: [--wait, --no-wait]

Wait user keypress (`Enter`) when finished the conversion (default: True).

| True   | False     |
| ------ | --------- |
| --wait | --no-wait |

Usage: `main.py --wait`

## License

This software is released under the terms of the GNU General Public License v3.0. See the [LICENSE](https://github.com/EdoardoTosin/Batch-Image-Converter/tree/main/LICENSE) file for further information.
