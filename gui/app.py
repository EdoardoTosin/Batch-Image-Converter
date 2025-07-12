from customtkinter import *
from gui_args import Proccess

root = CTk()

root.title("Batch image converter GUI")
root.geometry("800x600")
root.maxsize(800 , 600)
root_bg_color = root.cget("fg_color")


def start_proccess(path, dpi, size , filter , quality , max_image_mpixles , colorspace, optimize, alert , wait):

    try:
        dpi_data = int(dpi.get())
    except:
        dpi_data = dpi.get()
    
    try:
        size_data = int(size.get())
    except:
        size_data = size.get()

    try:
        filter_data = int(filter.get())
    except:
        filter_data = filter.get()

    try:
        quality_data = int(quality.get())
    except:
        quality_data = quality.get()

    try:
        max_image_mpixles_data = int(max_image_mpixles.get())
    except:
        max_image_mpixles_data = max_image_mpixles.get()

    run = Proccess(path=path.get() , dpi=dpi_data , size=size_data , filter=filter_data , quality=quality_data , max_image_mpixles=max_image_mpixles_data , colorspace=colorspace.get() , optimize=optimize.get() , alert=alert.get() , wait=wait.get())

    print(wait.get())

    run.run()

current_path = sys.argv[0].rsplit(os.sep, 1)[0]

title = CTkLabel(root , text="Convert your images , Quickly" , font=("Arial" , 30)).pack(pady=30)

inputs_title = CTkLabel(root , text="Data fields : " , font=("Arial" , 17) , text_color="green").pack()

inputs = CTkFrame(root, fg_color=root_bg_color, bg_color=root_bg_color)
inputs.pack(fill="x", padx=20, pady=10)

inputs.grid_columnconfigure(0, weight=1)
inputs.grid_columnconfigure(1, weight=1)

path = CTkEntry(inputs, placeholder_text=f"path where images are located (default: {current_path})", width=1100, height=35)
path.grid(row=0, column=0, columnspan=2, pady=10)

dpi = CTkEntry(inputs, placeholder_text="DPI (default: 72)", width=420, height=30)
dpi.grid(row=1, column=0, pady=10, padx=10)

size = CTkEntry(inputs, placeholder_text="Max resolution (default: 1000)", width=420, height=30)
size.grid(row=1, column=1, pady=10, padx=10)

filter = CTkEntry(inputs, placeholder_text="type of filter used for downscaling (default: 0 = Nearest)", width=1100, height=30)
filter.grid(row=2 , column=0 , pady=5 , columnspan=2)

quality = CTkEntry(inputs, placeholder_text="quality of output images (default: 80)", width=420, height=30)
quality.grid(row=3 , column=0 , pady=15)

max_image_mpixles = CTkEntry(inputs, placeholder_text="maximum image resolution allowed in Megapixels (default: 0 [None])", width=420, height=30)
max_image_mpixles.grid(row=3 , column=1 , pady=15)


colorspace = CTkCheckBox(inputs , text="convert all images to RGB color space" , onvalue=True , offvalue=False)
colorspace.grid(row = 4 , column=0 , pady=5)

optimize = CTkCheckBox(inputs , text="attempt to compress the palette by eliminating unused colors" , onvalue=True , offvalue=False)
optimize.grid(row=4 , column=1 , pady=10)

alert = CTkCheckBox(inputs , text="play alert sound when finished the conversion" , onvalue=True , offvalue=False)
alert.grid(row=5 , column=0 , pady=10)

wait = CTkCheckBox(inputs , text="wait for user keypress (Enter) when finished the conversion" , onvalue=True , offvalue=False)
wait.grid(row=5 , column=1 , pady=10)

start_btn = CTkButton(root , fg_color="green" , text_color="white" , width=250 , height=33 , font=("Arial" , 15) , text="Start conveting" , corner_radius=10 , hover=False , command=lambda: start_proccess(path=path, dpi=dpi, size=size , filter=filter , quality=quality , max_image_mpixles=quality , colorspace=colorspace, optimize=optimize, alert=alert , wait=wait))
start_btn.pack(pady=30)

root.mainloop()