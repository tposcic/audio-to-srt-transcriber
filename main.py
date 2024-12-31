from datetime import timedelta

import whisper
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os

def transcribe_audio(path):
    model = whisper.load_model("base")
    transcribe = model.transcribe(audio=path)
    segments = transcribe['segments']

    if not os.path.exists("output"):
        os.makedirs("output")

    srt_filename = os.path.join("output", f"{os.path.basename(path)}.srt")

    for segment in segments:
        start_time = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'
        end_time = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'
        text = segment['text']
        segment_id = segment['id']+1
        segment = f"{segment_id}\n{start_time} --> {end_time}\n{text[1:] if text[0] == ' ' else text}\n\n"

        with open(srt_filename, 'a', encoding='utf-8') as srt_file:
            srt_file.write(segment)

    return srt_filename

def process_files(file_paths):
    srt_files = [transcribe_audio(path) for path in file_paths]
    return srt_files

def select_files():
    file_paths = filedialog.askopenfilenames(
        title="Select WAV or MP3 Files",
        filetypes=(("Audio Files", "*.wav;*.mp3"), ("All Files", "*.*"))
    )
    if file_paths:
        file_list_var.set("\n".join(file_paths))


def start_processing():
    file_paths = file_list_var.get().split("\n")

    if not file_paths or file_paths == [""]:
        messagebox.showerror("Error", "No files selected!")
        return

    try:
        srt_files = process_files(file_paths)
        for srt_file in srt_files:
            output_listbox.insert(tk.END, srt_file)
        messagebox.showinfo("Success", "Processing complete!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def open_file(event):
    selected_index = output_listbox.curselection()
    if selected_index:
        selected_file = output_listbox.get(selected_index)

        try:
            if os.name == 'nt':  # Windows
                os.startfile(selected_file)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', selected_file])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Audio to SRT Transcriber")

    file_frame = tk.Frame(root)
    file_frame.pack(pady=10)

    tk.Label(file_frame, text="Input Files:").grid(row=0, column=0, sticky="w")
    file_list_var = tk.StringVar()
    tk.Entry(file_frame, textvariable=file_list_var, width=50, state="disabled").grid(row=1, column=0, padx=5, pady=5)
    tk.Button(file_frame, text="Browse", command=select_files).grid(row=1, column=1, padx=5)

    tk.Button(root, text="Transcribe", command=start_processing).pack(pady=10)

    output_frame = tk.Frame(root)
    output_frame.pack(pady=10)

    tk.Label(output_frame, text="Generated SRT Files:").grid(row=0, column=0, sticky="w")
    output_listbox = tk.Listbox(output_frame, width=100, height=10)
    output_listbox.grid(row=1, column=0, padx=5, pady=5)
    output_listbox.bind("<Double-1>", open_file)

    root.mainloop()
