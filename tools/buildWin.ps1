python -m pip install --user pyinstaller_versionfile
python -m pip install --user PyInstaller
python tools\versionfile_generator.py
python -m PyInstaller .\src\main.py --onefile --distpath ./ --icon=.\doc\logo.png -n="Batch-Image-Converter-Win64" --version-file versionfile.txt