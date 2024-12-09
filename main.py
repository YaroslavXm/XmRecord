import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
import numpy as np
import pyautogui
import mss
import threading
import time
import webbrowser

class ScreenRecorder:
    def __init__(self, fps=20):
        self.recording = False
        self.fps = fps
        self.resolution = (1920, 1080)
        self.update_resolution()
        self.output_filename = "output.mp4"

    def update_resolution(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            self.resolution = (monitor['width'], monitor['height'])

    def start_recording(self):
        self.recording = True
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(self.output_filename, fourcc, self.fps, self.resolution)

        with mss.mss() as sct:
            while self.recording:
                img = sct.grab(sct.monitors[1])
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                cursor_x, cursor_y = pyautogui.position()
                cv2.circle(frame, (cursor_x, cursor_y), 5, (0, 0, 255), -1)

                out.write(frame)
                time.sleep(1 / self.fps)

        out.release()

    def stop_recording(self):
        self.recording = False

    def donateOpen(url):
        webbrowser.open_new(url)

class SettingsWindow:
    def __init__(self, master, recorder, language_callback):
        self.recorder = recorder
        self.language_callback = language_callback
        self.settings_window = tk.Toplevel(master)
        self.settings_window.title(self.get_text("Settings"))

        self.fps_label = tk.Label(self.settings_window, text=self.get_text("FPS:"))
        self.fps_label.grid(row=0, column=0, padx=5, pady=5)

        self.fps_entry = tk.Entry(self.settings_window)
        self.fps_entry.insert(0, str(recorder.fps))
        self.fps_entry.grid(row=0, column=1, padx=5, pady=5)

        self.path_label = tk.Label(self.settings_window, text=self.get_text("Save Path:"))
        self.path_label.grid(row=1, column=0, padx=5, pady=5)

        self.path_entry = tk.Entry(self.settings_window)
        self.path_entry.insert(0, recorder.output_filename)
        self.path_entry.grid(row=1, column=1, padx=5, pady=5)

        self.browse_button = tk.Button(self.settings_window, text=self.get_text("Browse"), command=self.browse)
        self.browse_button.grid(row=1, column=2, padx=5, pady=5)

        self.save_button = tk.Button(self.settings_window, text=self.get_text("Save"), command=self.save_settings)
        self.save_button.grid(row=2, columnspan=3, pady=10)

        # Выбор языка / Select language

    def get_text(self, text_key):
        translations = {
            "FPS:": ["Кадров в секунду:", "FPS:"],
            "Save Path:": ["Путь сохранения видео:", "Save Path:"],
            "Browse": ["Обзор", "Browse"],
            "Save": ["Сохранить", "Save"],
            "Settings": ["Настройки", "Settings"],
            "Select Language:": ["Выберите язык:", "Select Language:"],
            "Donate": ["Донат","Donate"]
        }
        return translations[text_key][self.language_callback()]

    def browse(self):
        filename = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if filename:
            self.path_entry.delete(0, tk.END)
            
            self.path_entry.insert(0, filename)

    def save_settings(self):
        fps = int(self.fps_entry.get())
        self.recorder.fps = fps

        path = self.path_entry.get()
        if path:
            self.recorder.output_filename = path

        self.settings_window.destroy()

    def update_language(self):
        language = 0 if self.language_var.get() == "Russian" else 1
        self.language_callback(language)
        self.fps_label.config(text=self.get_text("FPS:"))
        self.path_label.config(text=self.get_text("Save Path:"))
        self.browse_button.config(text=self.get_text("Browse"))
        self.save_button.config(text=self.get_text("Save"))
        self.language_label.config(text=self.get_text("Select Language:"))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("XmRecord")
        self.language = 0  # 0 - Русский / Russian, 1 - Английский / English
        self.recorder = ScreenRecorder()
        
        self.create_control_frame()
        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        language_menu = tk.Menu(menubar, tearoff=0)
        language_menu.add_command(label="Русский", command=lambda: self.set_language(0))
        language_menu.add_command(label="English", command=lambda: self.set_language(1))
        menubar.add_cascade(label="Язык", menu=language_menu)
        self.root.config(menu=menubar)

    def set_language(self, lang):
        self.language = lang
        self.update_ui_lang()

    def update_ui_lang(self):
        self.start_button.config(text=self.get_text("Start Recording"))
        self.stop_button.config(text=self.get_text("Stop Recording"))
        self.settings_button.config(text=self.get_text("Settings"))
        self.status_label.config(text=self.get_text("Status: Waiting..."))
        self.donate_button.config(text=self.get_text("Donate"))

    def get_text(self, text_key):
        translations = {
            "Start Recording": ["Начать запись", "Start Recording"],
            "Stop Recording": ["Остановить запись", "Stop Recording"],
            "Settings": ["Настройки", "Settings"],
            "Status: Waiting...": ["Статус: Ожидание...", "Status: Waiting..."],
            "Status: Recording...": ["Статус: Запись...", "Status: Recording..."],
            "Status: Recording stopped!": ["Статус: Запись остановлена!", "Status: Recording stopped!"],
            "Donate": ["Донат","Donate"]
        }
        return translations[text_key][self.language]

    def create_control_frame(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20)

        self.start_button = tk.Button(control_frame, text=self.get_text("Start Recording"), command=self.start_recording)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(control_frame, text=self.get_text("Stop Recording"), command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.settings_button = tk.Button(control_frame, text=self.get_text("Settings"), command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.root, text=self.get_text("Status: Waiting..."))
        self.status_label.pack(pady=20)

        self.donate_button = tk.Button(control_frame, text=self.get_text("Donate"), command=webbrowser.open("https://www.donationalerts.com/r/xmgam3s"))
        self.donate_button.pack(side=tk.LEFT, padx=5)

    def open_settings(self):
        SettingsWindow(self.root, self.recorder, lambda: self.language)

    def start_recording(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text=self.get_text("Status: Recording..."))
        
        threading.Thread(target=self.recorder.start_recording).start()

    def stop_recording(self):
        self.recorder.stop_recording()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text=self.get_text("Status: Recording stopped!"))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
