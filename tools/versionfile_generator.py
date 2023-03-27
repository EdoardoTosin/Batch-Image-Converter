import pyinstaller_versionfile
import re
from os.path import basename, join, dirname, abspath
from os import sep

directory = dirname(abspath(__file__)).rsplit(sep)[0]

def get_metadata(name):
    pythonsrc_path = join(directory, "src", "main.py")
    with open(pythonsrc_path, 'r') as f:
        for line in f:
            if line.startswith(f'__{name}__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        return ""

def get_original_filename():
    buildwin_path = join(directory, "tools", "buildWin.ps1")
    with open(buildwin_path, 'r') as f:
        matches = []
        for line in f:
            matches.extend(re.findall(r'-n=(.*?)\"(.+?)\"',line))
        if len(matches)>0:
            for match in matches:
                for substr in match:
                    if len(substr)>0:
                        return substr+".exe"
        else:
            return ""

pyinstaller_versionfile.create_versionfile(
    output_file="versionfile.txt",
    version=get_metadata("version"),
    company_name=get_metadata("author"),
    file_description=get_metadata("description"),
    internal_name=get_metadata("name"),
    legal_copyright=get_metadata("copyright"),
    original_filename=get_original_filename(),
    product_name=get_metadata("name").replace("-"," ")
)