"""Argument validation and process class for the Batch Image Converter."""

import os
import sys

from main import main
from constants import FILTER_NAMES


def get_current_path() -> str:
    """Get the current directory path"""
    try:
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    except (IndexError, AttributeError):
        return os.getcwd()


def validate_value(value, default, expected_type):
    """Helper to safely validate and convert values to expected types."""
    try:
        if value is None or (isinstance(value, str) and not value.strip()):
            return default

        if expected_type == int:
            return int(float(value))
        if expected_type == float:
            return float(value)
        if expected_type == bool:
            return str(value).lower().strip() in ("true", "1", "yes", "on", "enabled")
        if expected_type == str:
            return str(value)

    except (ValueError, TypeError, AttributeError):
        pass

    return default


class Process:
    """Enhanced Process class with better validation and error handling"""

    def __init__(
        self,
        path=None,
        dpi=None,
        size=None,
        resample_filter=None,
        quality=None,
        max_image_mpixels=None,
        colorspace=None,
        optimize=None,
        alert=None,
        wait=None,
    ):
        """Initialize Process with validated parameters"""
        # Get default path
        default_path = get_current_path()

        # Validate and set all parameters with proper defaults
        self.path = validate_value(path, default_path, str)
        self.dpi = validate_value(dpi, 72, int)
        self.size = validate_value(size, 1000, int)  # Fixed default from 100 to 1000
        self.filter = validate_value(resample_filter, 0, int)
        self.quality = validate_value(quality, 80, int)
        self.max_image_mpixels = validate_value(max_image_mpixels, 0, int)
        self.colorspace = validate_value(colorspace, False, bool)
        self.optimize = validate_value(optimize, True, bool)  # Changed default to True
        self.alert = validate_value(alert, False, bool)
        self.wait = validate_value(wait, False, bool)

        # Validate ranges after conversion
        self._validate_ranges()

    def _validate_ranges(self):
        """Validate that all numeric values are within acceptable ranges"""
        # Clamp values to valid ranges
        self.dpi = max(1, min(1000, self.dpi))
        self.size = max(1, min(10000, self.size))
        self.filter = max(0, min(5, self.filter))
        self.quality = max(1, min(100, self.quality))
        self.max_image_mpixels = max(0, min(10000, self.max_image_mpixels))

        # Validate path exists
        if not os.path.isdir(self.path):
            print(
                f"Warning: Path '{self.path}' does not exist. Using current directory."
            )
            self.path = get_current_path()

    def get_summary(self) -> dict:
        """Get a summary of all settings"""

        return {
            "path": self.path,
            "dpi": self.dpi,
            "size": self.size,
            "filter": f"{self.filter} ({FILTER_NAMES.get(self.filter, 'Unknown')})",
            "quality": self.quality,
            "max_image_mpixels": (
                self.max_image_mpixels if self.max_image_mpixels > 0 else "No limit"
            ),
            "colorspace": "Yes" if self.colorspace else "No",
            "optimize": "Yes" if self.optimize else "No",
            "alert": "Yes" if self.alert else "No",
            "wait": "Yes" if self.wait else "No",
        }

    def run(self):
        """Execute the image processing with error handling"""
        try:
            # Validate path one more time before processing
            if not os.path.isdir(self.path):
                raise FileNotFoundError(f"Directory not found: {self.path}")

            # Check if directory is readable
            if not os.access(self.path, os.R_OK):
                raise PermissionError(f"Cannot read directory: {self.path}")

            # Call the main processing function
            main(self)

        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise
        except PermissionError as e:
            print(f"Error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error during processing: {e}")
            raise
