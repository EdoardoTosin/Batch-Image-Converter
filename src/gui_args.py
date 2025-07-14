import os
import sys
from main import main

current_path = sys.argv[0].rsplit(os.sep, 1)[0]


def validate(value, default, type):
    if value == "" or value is None or not isinstance(value, type):
        return default
    else:
        return value


class Proccess:
    def __init__(
        self,
        path,
        dpi,
        size,
        filter,
        quality,
        max_image_mpixles,
        colorspace,
        optimize,
        alert,
        wait,
    ):
        self.path = validate(path, current_path, str)
        self.dpi = validate(dpi, 72, int)
        self.size = validate(size, 100, int)
        self.filter = validate(filter, 0, int)
        self.quality = validate(quality, 80, int)
        self.max_image_mpixles = validate(max_image_mpixles, 0, int)
        self.colorspace = validate(colorspace, False, bool)
        self.optimize = validate(optimize, False, bool)
        self.alert = validate(alert, False, bool)
        self.wait = validate(wait, False, bool)

    def run(self):
        main(args=self)
