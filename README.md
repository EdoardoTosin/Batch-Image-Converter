<h1 align="center">
  <sub>
    <img src="https://raw.githubusercontent.com/EdoardoTosin/Batch-Image-Converter/main/doc/logo.png" height="38" width="38">
  </sub>
  Batch Image Converter
</h1>

## Summary

Simple script written in Python that converts all images found within the folder where the script is located (and all sub-folders); if the images are not in png or jpg (and jpeg) type, then it converts them to the latter one.  
Among the options there is the possibility of setting the quality, the maximum resolution in pixels of the long side of the image while maintaining the aspect ratio (without upscaling if smaller) and changing the dpi.  
There is the possibility to convert all images to the RGB colour space (Important: ICC colour profiles are not used for this conversion so switching between different formats may result in incorrect colours).  
It also prints out a list of all corrupted images and any other files found.  
The following formats are recognised: jpg, jpeg, png, tif, tiff, bmp, psd, psb.  

> **Warning**: psd and psb file types have not been tested.

![Output](https://raw.githubusercontent.com/EdoardoTosin/Batch-Image-Converter/main/doc/output.jpg)

## How it works

Batch Image Converter search recursively for all recognized images inside the path (included subfolders) and converts them. If there are no arguments given to the script, the following is the normal behaviour:
- Convert images that are not in jpg, jpeg and png filetype into the former.
- Path: the folder where the script is located.
- DPI: 72 dpi.
- Size: downscaling if bigger than 1000x1000 while mantaining the same aspect ratio.
- Filter: Downscale filter used is `Nearest`.
- Color space: No color space conversion to RGB.
- Quality for saving images: 80.
- Maximum images resolution allowed in Megapixel: 0 (None).
- Optimization: Enabled.
- Alert: Enabled.
- Wait before exit: Enabled.
By default the script try to open the images, check the dimension are downscale them to fit into 1000x1000 pixel box if bigger (no upscaling) using the `Nearest` filter. If the images are in other filetypes except png and jpeg (jpg) then it converts them to the latter and delete the original ones (otherwise it overwrites the file in jpg or png). During the saving phase, the script sets the dpi to 72.

Default: `main.py --dpi 72 --size 1000 --filter 0 --no-colorspace --quality 80 --optimize --alert --wait`

## Requirements

Python version equal or greater than 3.9 must be installed before following the instructions paragraph.

To run the script two modules are required (listed inside [`requirements.txt`](https://raw.githubusercontent.com/EdoardoTosin/Batch-Image-Converter/main/requirements.txt)):
```
Pillow>=9.4.0

tqdm>=4.65.0
```

## Instructions

### Linux

- `git clone https://github.com/EdoardoTosin/Batch-Image-Converter.git`
- `cd Batch-Image-Converter && python3 -m pip install -r requirements.txt`
- Copy `main.py` into the folder you want to convert all images.
- `python3 main.py`
- Help screen: `python3 main.py -h`

### Windows

- `git clone https://github.com/EdoardoTosin/Batch-Image-Converter.git`
- `cd Batch-Image-Converter; python -m pip install -r requirements.txt`
- Copy `main.py` into the folder you want to convert all images.
- Double click `main.py` to start it with default parameters or launch via terminal with `python main.py`.
- Help screen: `python main.py -h`

### Portable version

Portable version can be built with the [`Windows script`](https://raw.githubusercontent.com/EdoardoTosin/Batch-Image-Converter/main/tools/buildWin.ps1) and [`Linux script`](https://raw.githubusercontent.com/EdoardoTosin/Batch-Image-Converter/main/tools/buildLinux.sh), or downloaded directly from the [Release page](https://github.com/EdoardoTosin/Batch-Image-Converter/releases/latest).

#### How to build

- Windows: `.\tools\buildWin.ps1`
- Linux: `./tools/buildLinux.sh`

## Usage

```console
usage: main.py [-h] [-v] [-p PATH] [-d [1-1000]] [-s [1-10000]] [-f [0 = Nearest, 4 = Box, 2 = Bilinear, 5 = Hamming, 3 = Bicubic, 1 = Lanczos]]
                 [--colorspace | --no-colorspace | --cs | --no-cs] [-q [1-100]] [-m [0-10000]] [--optimize | --no-optimize] [--alert | --no-alert]
                 [--wait | --no-wait]

Python script that convert images to a certain dpi, max long side resolution and rgb color space. Filetype: jpg, jpeg, png, tif, tiff, bmp, psd, psb.

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

commands:
  Image conversion properties

  -p PATH, --path PATH  path where images are located (default: ".")
  -d [1-1000], --dpi [1-1000]
                        pixel density in pixels per inch (dpi), must be in range 1-1000 (default: 72)
  -s [1-10000], --size [1-10000]
                        max resolution of image (long side) in pixel (downscaling only), must be in range 1-10000 (default: 1000)
  -f [0 = Nearest, 4 = Box, 2 = Bilinear, 5 = Hamming, 3 = Bicubic, 1 = Lanczos], --filter [0 = Nearest, 4 = Box, 2 = Bilinear, 5 = Hamming, 3 = Bicubic, 1 = Lanczos]
                        type of filter used for downscaling, must be an integer in range 0-5 (default: 0 = Nearest)
  --colorspace, --no-colorspace, --cs, --no-cs
                        convert all images to RGB color space (default: False)
  -q [1-100], --quality [1-100]
                        quality of output images, must be in range 1-100 (values above 95 should be avoided) (default: 80)
  -m [0-10000], --max-image-mpixels [0-10000]
                        maximum images resolution allowed in Megapixel, (default: 0 [None])
  --optimize, --no-optimize
                        attempt to compress the palette by eliminating unused colors (default: True)

other options:
  Customize script behaviour (alert and wait)

  --alert, --no-alert   play alert sound when finished the conversion (default: True)
  --wait, --no-wait     wait user keypress (Enter) when finished the conversion (default: True)
```

## Help 🆘 [-h, --help]

Show help message and exit.

Usage: `main.py -h`

## Version [-v, --version]

Show program's version number and exit.

Usage: `main.py -v`

## Image conversion properties

### Path [-p, --path]

Set path where images are located (default: Folder where this script is located).

Usage:

- Windows: `main.py -p "C:\Windows\Log"`
- Linux: `main.py -p "/var/log"`

### Dpi [-d, --dpi]

Set pixel density in pixels per inch (dpi), must be in range 1-1000 (default: 72).

Usage: `main.py -d 72`

### Max Resolution [-s, --size]

Set max resolution of image (long side) in pixel (downscaling only), must be in range 1-10000 (default: 1000).

Usage: `main.py -s 1000`

### Resize Filter [-f, --filter]

Set type of filter used for downscaling, must be an integer in range 0-3 (default: 0 = Nearest).

[Filters comparison table](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters-comparison-table)

| 0       | 4   | 2        | 5       | 3       | 5       |
| ------- | --- | -------- | ------- | ------- | ------- |
| Nearest | Box | Bilinear | Hamming | Bicubic | Lanczos |

Usage: `main.py -f 0`

### Color space [--colorspace, --no-colorspace, --cs, --no-cs]

Set color space to RGB (default: False).

> **Warning**: converting CYMK to RGB might not be accurate because the script doesn't use the icc profiles.

| True         | False           |
| ------------ | --------------- |
| --colorspace | --no-colorspace |
| --cs         | --no-cs         |

Usage: `main.py --colorspace` or `main.py --no-colorspace`

### Quality [-q, --quality]

Set quality of output images, must be in range 1-100 (values above 95 should be avoided) (default: 80).

Usage: `main.py -q 80`

### Maximum Image MPixels [-m, --max-image-mpixels]

Set maximum images resolution allowed in Megapixel, (default: 0 [None]).

Usage `main.py -m 0`

### Optimize [--optimize, --no-optimize]

Attempt to compress the palette by eliminating unused colors (default: True).

| True       | False         |
| ---------- | ------------- |
| --optimize | --no-optimize |

Usage: `main.py --optimize` or `main.py --no-optimize`

## Customize script behaviour

### Alert 🔔 [--alert, --no-alert]

Play alert sound when finished the conversion (default: True).

| True   | False     |
| ------ | --------- |
| --mute | --no-mute |

Usage: `main.py --mute`

### Wait ✋ [--wait, --no-wait]

Wait user keypress (`Enter`) when finished the conversion (default: True).

| True   | False     |
| ------ | --------- |
| --wait | --no-wait |

Usage: `main.py --wait` or `main.py --no-wait`

## Security Policy

For more details see the [SECURITY](https://github.com/EdoardoTosin/ZooMeeting-Redirector/blob/main/SECURITY.md) file.

## Developing

See [CONTRIBUTING.md](https://github.com/EdoardoTosin/Batch-Image-Converter/tree/main/CONTRIBUTING.md)

## License

This software is released under the terms of the GNU General Public License v3.0. See the [LICENSE](https://github.com/EdoardoTosin/Batch-Image-Converter/tree/main/LICENSE) file for further information.
