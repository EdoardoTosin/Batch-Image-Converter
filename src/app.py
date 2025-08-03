"""GUI interface for the Batch Image Converter using customtkinter."""

import os
import sys
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from gui_args import Process

# Set appearance mode and color theme
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class BatchImageConverterApp:
    """Main GUI application class for batch image conversion."""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Batch Image Converter")
        self.root.geometry("900x850")
        self.root.minsize(800, 800)

        # Center the window
        self.center_window()

        # Initialize variables
        self.current_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.is_processing = False

        # Declare attributes used in other methods
        self.path_var = None
        self.path_entry = None
        self.dpi_var = None
        self.dpi_entry = None
        self.size_var = None
        self.size_entry = None
        self.quality_var = None
        self.quality_entry = None
        self.filter_var = None
        self.filter_combo = None
        self.max_mpixels_var = None
        self.max_mpixels_entry = None
        self.colorspace_var = None
        self.colorspace_cb = None
        self.optimize_var = None
        self.optimize_cb = None
        self.alert_var = None
        self.alert_cb = None
        self.wait_var = None
        self.wait_cb = None
        self.start_btn = None
        self.reset_btn = None
        self.conversion_thread = None

        # Create GUI elements
        self.create_widgets()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container with padding
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🖼️ Batch Image Converter",
            font=ctk.CTkFont(size=32, weight="bold"),
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Convert your images quickly and efficiently",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40"),
        )
        subtitle_label.pack(pady=(0, 30))

        # Create scrollable frame for inputs
        self.scrollable_frame = ctk.CTkScrollableFrame(main_frame, height=400)
        self.scrollable_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Path selection section
        self.create_path_section()

        # Image settings section
        self.create_image_settings_section()

        # Advanced options section
        self.create_advanced_options_section()

        # Control buttons
        self.create_control_buttons(main_frame)

        # Progress bar (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_label = ctk.CTkLabel(main_frame, text="")

    def create_path_section(self):
        """Create path selection section"""
        path_frame = ctk.CTkFrame(self.scrollable_frame)
        path_frame.pack(fill="x", pady=(0, 20))

        path_title = ctk.CTkLabel(
            path_frame,
            text="📁 Source Directory",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        path_title.pack(pady=(15, 10))

        path_input_frame = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_input_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.path_var = ctk.StringVar(value=self.current_path)
        self.path_entry = ctk.CTkEntry(
            path_input_frame,
            textvariable=self.path_var,
            placeholder_text="Select directory containing images...",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(
            path_input_frame,
            text="Browse",
            command=self.browse_directory,
            width=100,
            height=40,
        )
        browse_btn.pack(side="right")

    def create_image_settings_section(self):
        """Create image settings section"""
        settings_frame = ctk.CTkFrame(self.scrollable_frame)
        settings_frame.pack(fill="x", pady=(0, 20))

        settings_title = ctk.CTkLabel(
            settings_frame,
            text="⚙️ Image Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        settings_title.pack(pady=(15, 10))

        # Create grid for inputs
        grid_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=15, pady=(0, 15))
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)

        # DPI setting
        ctk.CTkLabel(grid_frame, text="DPI:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        self.dpi_var = ctk.StringVar(value="72")
        self.dpi_entry = ctk.CTkEntry(grid_frame, textvariable=self.dpi_var, width=200)
        self.dpi_entry.grid(row=0, column=1, sticky="ew", pady=5)

        # Max resolution setting
        ctk.CTkLabel(
            grid_frame, text="Max Resolution (px):", font=ctk.CTkFont(size=14)
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        self.size_var = ctk.StringVar(value="1000")
        self.size_entry = ctk.CTkEntry(
            grid_frame, textvariable=self.size_var, width=200
        )
        self.size_entry.grid(row=1, column=1, sticky="ew", pady=5)

        # Quality setting
        ctk.CTkLabel(
            grid_frame, text="Quality (1-100):", font=ctk.CTkFont(size=14)
        ).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        self.quality_var = ctk.StringVar(value="80")
        self.quality_entry = ctk.CTkEntry(
            grid_frame, textvariable=self.quality_var, width=200
        )
        self.quality_entry.grid(row=2, column=1, sticky="ew", pady=5)

        # Filter setting
        ctk.CTkLabel(
            grid_frame, text="Downscaling Filter:", font=ctk.CTkFont(size=14)
        ).grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
        self.filter_var = ctk.StringVar(value="0")
        filter_options = [
            "0 - Nearest",
            "1 - Lanczos",
            "2 - Bilinear",
            "3 - Bicubic",
            "4 - Box",
            "5 - Hamming",
        ]
        self.filter_combo = ctk.CTkOptionMenu(
            grid_frame, variable=self.filter_var, values=filter_options, width=200
        )
        self.filter_combo.grid(row=3, column=1, sticky="ew", pady=5)

        # Max image megapixels
        ctk.CTkLabel(
            grid_frame, text="Max Image Megapixels (0=None):", font=ctk.CTkFont(size=14)
        ).grid(row=4, column=0, sticky="w", padx=(0, 10), pady=5)
        self.max_mpixels_var = ctk.StringVar(value="0")
        self.max_mpixels_entry = ctk.CTkEntry(
            grid_frame, textvariable=self.max_mpixels_var, width=200
        )
        self.max_mpixels_entry.grid(row=4, column=1, sticky="ew", pady=5)

    def create_advanced_options_section(self):
        """Create advanced options section"""
        options_frame = ctk.CTkFrame(self.scrollable_frame)
        options_frame.pack(fill="x", pady=(0, 20))

        options_title = ctk.CTkLabel(
            options_frame,
            text="🔧 Advanced Options",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        options_title.pack(pady=(15, 10))

        # Checkboxes frame
        checkboxes_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        checkboxes_frame.pack(fill="x", padx=15, pady=(0, 15))
        checkboxes_frame.grid_columnconfigure(0, weight=1)
        checkboxes_frame.grid_columnconfigure(1, weight=1)

        # RGB colorspace conversion
        self.colorspace_var = ctk.BooleanVar(value=False)
        self.colorspace_cb = ctk.CTkCheckBox(
            checkboxes_frame,
            text="Convert to RGB colorspace",
            variable=self.colorspace_var,
            font=ctk.CTkFont(size=14),
        )
        self.colorspace_cb.grid(row=0, column=0, sticky="w", pady=5)

        # Optimize
        self.optimize_var = ctk.BooleanVar(value=True)
        self.optimize_cb = ctk.CTkCheckBox(
            checkboxes_frame,
            text="Optimize file size",
            variable=self.optimize_var,
            font=ctk.CTkFont(size=14),
        )
        self.optimize_cb.grid(row=0, column=1, sticky="w", pady=5)

        # Alert sound
        self.alert_var = ctk.BooleanVar(value=False)
        self.alert_cb = ctk.CTkCheckBox(
            checkboxes_frame,
            text="Play alert when finished",
            variable=self.alert_var,
            font=ctk.CTkFont(size=14),
        )
        self.alert_cb.grid(row=1, column=0, sticky="w", pady=5)

        # Wait for keypress
        self.wait_var = ctk.BooleanVar(value=False)
        self.wait_cb = ctk.CTkCheckBox(
            checkboxes_frame,
            text="Wait for keypress when done",
            variable=self.wait_var,
            font=ctk.CTkFont(size=14),
        )
        self.wait_cb.grid(row=1, column=1, sticky="w", pady=5)

    def create_control_buttons(self, parent):
        """Create control buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))

        self.start_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Start Conversion",
            command=self.start_conversion_threaded,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#1f538d", "#14375e"),
            hover_color=("#14375e", "#1f538d"),
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.reset_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Reset",
            command=self.reset_form,
            height=50,
            font=ctk.CTkFont(size=16),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            width=120,
        )
        self.reset_btn.pack(side="right", padx=(5, 0))

    def browse_directory(self):
        """Open file dialog to select directory"""
        directory = filedialog.askdirectory(
            title="Select Directory Containing Images", initialdir=self.current_path
        )
        if directory:
            self.path_var.set(directory)

    def reset_form(self):
        """Reset all form fields to default values"""
        if self.is_processing:
            messagebox.showwarning("Warning", "Cannot reset while processing images.")
            return

        self.path_var.set(self.current_path)
        self.dpi_var.set("72")
        self.size_var.set("1000")
        self.quality_var.set("80")
        self.filter_var.set("0")
        self.max_mpixels_var.set("0")
        self.colorspace_var.set(False)
        self.optimize_var.set(True)
        self.alert_var.set(False)
        self.wait_var.set(False)

    def validate_inputs(self):
        """Validate all input fields"""
        errors = []

        # Validate path
        if not os.path.isdir(self.path_var.get()):
            errors.append("Invalid directory path")

        # Validate numeric inputs
        try:
            dpi = int(self.dpi_var.get())
            if not 1 <= dpi <= 1000:
                errors.append("DPI must be between 1 and 1000")
        except ValueError:
            errors.append("DPI must be a valid number")

        try:
            size = int(self.size_var.get())
            if not 1 <= size <= 10000:
                errors.append("Size must be between 1 and 10000")
        except ValueError:
            errors.append("Size must be a valid number")

        try:
            quality = int(self.quality_var.get())
            if not 1 <= quality <= 100:
                errors.append("Quality must be between 1 and 100")
        except ValueError:
            errors.append("Quality must be a valid number")

        try:
            filter_val = int(self.filter_var.get().split(" ")[0])
            if not 0 <= filter_val <= 5:
                errors.append("Filter must be between 0 and 5")
        except (ValueError, IndexError):
            errors.append("Invalid filter selection")

        try:
            max_mpixels = int(self.max_mpixels_var.get())
            if max_mpixels < 0:
                errors.append("Max megapixels cannot be negative")
        except ValueError:
            errors.append("Max megapixels must be a valid number")

        return errors

    def start_conversion_threaded(self):
        """Start conversion in a separate thread"""
        if self.is_processing:
            messagebox.showwarning("Warning", "Conversion is already in progress.")
            return

        # Validate inputs
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Check if directory has images
        supported_formats = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp")
        image_count = 0
        for _, _, files in os.walk(self.path_var.get()):
            for file in files:
                if file.lower().endswith(supported_formats):
                    image_count += 1

        if image_count == 0:
            messagebox.showwarning(
                "No Images", "No supported images found in the selected directory."
            )
            return

        # Confirm conversion
        if not messagebox.askyesno(
            "Confirm Conversion",
            f"Found {image_count} images to convert.\n"
            "This will modify the original files.\n\nDo you want to continue?",
        ):
            return

        # Start conversion in thread
        self.conversion_thread = threading.Thread(
            target=self.start_conversion, daemon=True
        )
        self.conversion_thread.start()

    def start_conversion(self):
        """Start the conversion process"""
        self.is_processing = True

        if not self.root.winfo_exists():
            return

        # Update UI
        if self.root.winfo_exists():
            self.root.after(0, self.show_progress)

        try:
            # Extract filter number
            filter_val = int(self.filter_var.get().split(" ")[0])

            # Create process object
            process = Process(
                path=self.path_var.get(),
                dpi=int(self.dpi_var.get()),
                size=int(self.size_var.get()),
                resample_filter=filter_val,
                quality=int(self.quality_var.get()),
                max_image_mpixels=int(self.max_mpixels_var.get()),
                colorspace=self.colorspace_var.get(),
                optimize=self.optimize_var.get(),
                alert=self.alert_var.get(),
                wait=self.wait_var.get(),
            )

            # Run conversion
            process.run()

            # Show success message
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Success", "Image conversion completed successfully!"
                ),
            )

        except (ValueError, OSError, RuntimeError) as e:
            # Show error message
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Error", f"An error occurred during conversion:\n{str(e)}"
                ),
            )

        finally:
            self.is_processing = False
            if self.root.winfo_exists():
                self.root.after(0, self.hide_progress)

    def show_progress(self):
        """Show progress bar and update UI"""
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_label.pack(pady=(0, 10))
        self.progress_bar.set(0.5)  # Indeterminate progress
        self.progress_label.configure(text="Converting images...")
        self.start_btn.configure(state="disabled", text="Converting...")

    def hide_progress(self):
        """Hide progress bar and reset UI"""
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
        self.start_btn.configure(state="normal", text="🚀 Start Conversion")

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            self.root.quit()


def main():
    """Entry point for launching the GUI application."""
    app = BatchImageConverterApp()
    app.run()


if __name__ == "__main__":
    main()
