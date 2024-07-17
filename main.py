import threading
import tkinter as tk
import wave
from tkinter import filedialog, messagebox

import numpy as np
import pyaudio
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Global variables
is_recording = False
is_paused = False
frames = []
audio = pyaudio.PyAudio()
stream = None
recorded_data = []

# Create main window
root = tk.Tk()
root.title("Voice Recorder")
root.geometry("1270x685")
root.configure(bg="papaya whip")
root.iconbitmap("voice.ico")

# Font settings
font_settings = ("Times New Roman", 15, "bold")

# Entry box for search
search_label = tk.Label(root, text="Search File:", font=font_settings, fg="black", bg="papaya whip")
search_label.pack(pady=10)
search_entry = tk.Entry(root, font=font_settings, fg="black")
search_entry.pack(pady=5)

# Visualization area
fig = Figure(figsize=(10, 4), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=20)

# Timer
timer_label = tk.Label(root, text="00:00:00", font=font_settings, fg="black", bg="papaya whip")
timer_label.pack(pady=10)

# Control buttons
button_frame = tk.Frame(root, bg="papaya whip")
button_frame.pack(pady=20)

record_button = tk.Button(button_frame, text="Record", font=font_settings, command=lambda: start_recording())
pause_button = tk.Button(button_frame, text="Pause", font=font_settings, command=lambda: pause_recording())
stop_button = tk.Button(button_frame, text="Stop", font=font_settings, command=lambda: stop_recording())
play_button = tk.Button(button_frame, text="Play", font=font_settings, command=lambda: play_audio())
save_button = tk.Button(button_frame, text="Save", font=font_settings, command=lambda: save_audio())
delete_button = tk.Button(button_frame, text="Delete", font=font_settings, command=lambda: delete_audio())
exit_button = tk.Button(button_frame, text="Exit", font=font_settings, command=lambda: exit_app())

record_button.grid(row=0, column=0, padx=10)
pause_button.grid(row=0, column=1, padx=10)
stop_button.grid(row=0, column=2, padx=10)
play_button.grid(row=0, column=3, padx=10)
save_button.grid(row=0, column=4, padx=10)
delete_button.grid(row=0, column=5, padx=10)
exit_button.grid(row=0, column=6, padx=10)

# Functions for recording, playback, file handling, and visualization
def start_recording():
    global is_recording, is_paused, frames, stream
    if not is_recording:
        is_recording = True
        is_paused = False
        frames = []
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        threading.Thread(target=record).start()
        update_timer()
        ani.event_source.start()

def pause_recording():
    global is_paused
    if is_recording:
        is_paused = not is_paused

def stop_recording():
    global is_recording, stream
    if is_recording:
        is_recording = False
        stream.stop_stream()
        stream.close()
        ani.event_source.stop()

def record():
    global is_recording, is_paused, frames
    while is_recording:
        if not is_paused:
            data = stream.read(1024)
            frames.append(data)
            audio_data = np.frombuffer(data, dtype=np.int16)
            recorded_data.extend(audio_data)

def play_audio():
    global frames
    if frames:
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
        for frame in frames:
            stream.write(frame)
        stream.stop_stream()
        stream.close()

def save_audio():
    global frames
    if frames:
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Audio files", "*.wav")])
        if file_path:
            wf = wave.open(file_path, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
            wf.close()

def delete_audio():
    global frames, recorded_data
    if frames:
        if messagebox.askyesno("Delete", "Are you sure you want to delete the current recording?"):
            frames = []
            recorded_data = []

def exit_app():
    global is_recording
    if is_recording:
        stop_recording()
    root.quit()

# Visualization function
def update_plot(frame):
    global recorded_data
    ax.clear()
    ax.plot(recorded_data[-44100:])  # Plot the last second of data
    ax.set_ylim([-32768, 32767])

ani = FuncAnimation(fig, update_plot, interval=100)

# Timer function
start_time = 0
def update_timer():
    if is_recording and not is_paused:
        global start_time
        elapsed_time = int((root.after_info()['when'] - start_time) / 1000)
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
    root.after(1000, update_timer)

# Run the application
root.mainloop()