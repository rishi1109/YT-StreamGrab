import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk  
from pytube import YouTube

# Function to modify pytube's inner workings to prevent 404 errors
from pytube import cipher
from pytube.innertube import _default_clients
import re

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def get_throttling_function_name(js: str) -> str:
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise Exception("Regex match error: get_throttling_function_name")

cipher.get_throttling_function_name = get_throttling_function_name

# GUI functions
def download_video():
    url = url_entry.get()
    try:
        yt = YouTube(url)
        title_label.config(text=f"Title: {yt.title}")
        streams = get_streams_with_audio(yt)
        if streams:
            selected_stream = select_stream(streams)
            if selected_stream:
                status_label.config(text=f"Downloading '{yt.title}' in {selected_stream.resolution} with audio...")
                download_path = filedialog.askdirectory(title="Select Download Directory")
                if download_path:
                    selected_stream.download(output_path=download_path)
                    messagebox.showinfo("Success", f"Video '{yt.title}' has been downloaded successfully!")
                    status_label.config(text="Download completed.")
                else:
                    messagebox.showwarning("Warning", "Download path not selected.")
            else:
                messagebox.showerror("Error", "No stream selected.")
        else:
            messagebox.showerror("Error", "No stream with audio found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def get_streams_with_audio(yt):
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    return streams

def select_stream(streams):
    stream_options = [f"{i+1}. Resolution: {stream.resolution}, FPS: {stream.fps}, Type: {stream.mime_type}" for i, stream in enumerate(streams)]
    choice = simpledialog.askinteger("Select Stream", "Choose a stream to download:\n\n" + "\n".join(stream_options), parent=root, minvalue=1, maxvalue=len(streams))
    if choice is not None:
        return streams[choice - 1]
    return None

# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("600x500")
root.configure(bg="#f0f0f0")

# Load and place the logo
logo_image = Image.open("DownloaderIcon.png")  # Ensure the image file is in the same directory or provide the full path
logo_image = logo_image.resize((150, 150), Image.LANCZOS)  # Use Image.LANCZOS for high-quality downsampling
logo_photo = ImageTk.PhotoImage(logo_image)

logo_label = tk.Label(root, image=logo_photo, bg="#f0f0f0")
logo_label.pack(pady=20)

# Create and pack widgets
title_font = ('Helvetica', 16, 'bold')
label_font = ('Helvetica', 12)
button_font = ('Helvetica', 12, 'bold')

url_label = tk.Label(root, text="Enter YouTube URL:", font=label_font, bg="#f0f0f0")
url_label.pack(pady=10)

url_entry = tk.Entry(root, width=60, font=label_font)
url_entry.pack(pady=5)

download_button = tk.Button(root, text="Download Video", command=download_video, font=button_font, bg="#4CAF50", fg="white")
download_button.pack(pady=20)

title_label = tk.Label(root, text="", font=label_font, bg="#f0f0f0")
title_label.pack(pady=5)

status_label = tk.Label(root, text="", font=label_font, bg="#f0f0f0")
status_label.pack(pady=10)

# Run the main loop
root.mainloop()
