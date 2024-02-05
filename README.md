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
        <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/edoardotosin/Batch-Image-Converter/build.yml?style=for-the-badge"></a>
    <a href="https://github.com/EdoardoTosin/Batch-Image-Converter/releases/latest">
        <img alt="GitHub release (latest SemVer)" src="https://img.shields.io/github/v/release/EdoardoTosin/Batch-Image-Converter?label=Latest%20Release&style=for-the-badge"></a>
    <img alt="GitHub all releases" src="https://img.shields.io/github/downloads/edoardotosin/Batch-Image-Converter/total?style=for-the-badge">
    <a href="https://edoardotosin.github.io/Batch-Image-Converter">
        <img alt="GitHub deployments" src="https://img.shields.io/github/deployments/edoardotosin/Batch-Image-Converter/github-pages?label=DEPLOYMENT&style=for-the-badge"></a>
	<a href="https://github.com/EdoardoTosin/Batch-Image-Converter/blob/main/LICENSE">
		<img alt="GitHub" src="https://img.shields.io/github/license/edoardotosin/Batch-Image-Converter?style=for-the-badge"></a>
</p>

## Summary

Python script that enables users to convert images to a specific dpi, maximum long side resolution, and RGB color space. It supports various file types and provides a user-friendly CLI for easy usage. Additionally, it offers precompiled binaries for Linux, Windows, and Mac platforms, allowing users to run the script without installing Python or any dependencies.

![Output](https://raw.githubusercontent.com/EdoardoTosin/Batch-Image-Converter/main/assets/output.jpg)

## Features

- Convert images to a specific dpi and maximum long side resolution (Default: 72dpi, 1000px).
- Convert images to RGB color space (Important: ICC colour profiles are not used for this conversion so switching between different formats may result in incorrect colours).
- Downscale images using different filters.
- Compress the palette by eliminating unused colors.
- Alert user upon completion of conversion.
- Wait for user keypress upon completion of conversion.

## Method 1: Download release binary

There are precompiled binaries for Linux, Windows, and Mac. These binary files allow you to run the script without installing Python or any dependencies. You can download these binaries from the [Releases](https://github.com/EdoardoTosin/Batch-Image-Converter/releases/latest) page. After downloading, simply run the binary file to start using the script.

## Method 2: Build release binary

If you wish to manually build the binaries, the repository contains scripts to do so for both Windows and Linux platforms. 

For Windows, from the `Batch-Image-Converter` directory run `buildWin.ps1` PowerShell script as followed:

```powershell
git clone https://github.com/EdoardoTosin/Batch-Image-Converter.git
cd Batch-Image-Converter
.\tools\buildWin.ps1
```

For Linux, from the `Batch-Image-Converter` directory run `buildLinux.ps1` bash script as followed:

```bash
git clone https://github.com/EdoardoTosin/Batch-Image-Converter.git
cd Batch-Image-Converter
./tools/buildLinux.sh
```

These scripts will automatically build the binaries for the corresponding platform.

## Method 3: Run with Python3

First, clone the repository:

```bash
git clone https://github.com/EdoardoTosin/Batch-Image-Converter.git
```

Next, navigate into the cloned repository:

```bash
cd Batch-Image-Converter
```

Afterwards, install the required Python packages using the `requirements.txt` file:

```bash
pip3 install -r requirements.txt
```

Once you have installed the required packages and are ready to run the script, you need to move the `main.py` file from the `src` directory into the folder where you want to convert images.

On Linux, use the `mv` command:

```bash
mv src/main.py /path/to/your/folder
```

On Windows, use the `move` command:

```powershell
Move-Item -Path "src\main.py" -Destination "\path\to\your\folder"
```

After moving the `main.py` file, navigate to the folder where you moved the file and run the script:

On Linux:

```bash
cd /path/to/your/folder
python3 main.py --help
```

On Windows:

```powershell
cd \path\to\your\folder
python main.py --help
```

## Usage

The script takes several command line arguments:

- `-p` or `--path`: Specify the directory where the images are located. Defaults to the current directory.
- `-d` or `--dpi`: Specify the pixel density in pixels per inch (dpi). Must be in the range 1-1000. Defaults to 72.
- `-s` or `--size`: Specify the maximum resolution of the image (long side) in pixels. For downscaling only. Must be in the range 1-10000. Defaults to 1000.
- `-f` or `--filter`: Specify the type of filter used for downscaling. Must be an integer in the range 0-5. Defaults to 0 (Nearest). ([Filters comparison table](https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters-comparison-table))
- `--colorspace` or `--cs`: Convert all images to RGB color space.
- `-q` or `--quality`: Specify the quality of output images. Must be in the range 1-100. Values above 95 should be avoided. Defaults to 80.
- `-m` or `--max-image-mpixels`: Specify the maximum images resolution allowed in Megapixel. Defaults to 0 (None).
- `--optimize`: Attempt to compress the palette by eliminating unused colors.
- `--alert`: Play alert sound when finished the conversion.
- `--wait`: Wait for user keypress (Enter) when finished the conversion.

## Security Policy

For more details see the [SECURITY](https://github.com/EdoardoTosin/Batch-Image-Converter/blob/main/SECURITY.md) file.

## Contributing

See [CONTRIBUTING.md](https://github.com/EdoardoTosin/Batch-Image-Converter/tree/main/CONTRIBUTING.md).

## License

This software is released under the terms of the GNU General Public License v3.0. See the [LICENSE](https://github.com/EdoardoTosin/Batch-Image-Converter/tree/main/LICENSE) file for further information.
