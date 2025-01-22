import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
import json


class ScriptRunnerApp:
    CONFIG_FILE = "script_runner_config.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Script Runner GUI")
        self.root.geometry("600x400")

        # Folder Selection Button
        self.select_btn = tk.Button(root, text="Select Project Folder", command=self.select_folder)
        self.select_btn.pack(pady=10)

        # Script Buttons Frame
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Output Display
        self.output_display = scrolledtext.ScrolledText(root, height=10)
        self.output_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Dictionary to track loaded folders
        self.loaded_folders = {}
        self.load_config()

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.load_scripts(folder_path)

    def load_scripts(self, folder_path):
        if folder_path in self.loaded_folders:
            return

        scripts = [f for f in os.listdir(folder_path) if f.endswith(".py")]
        folder_name = os.path.basename(folder_path)

        for script in scripts:
            script_key = os.path.join(folder_path, script)
            button_text = f"{folder_name}: {script}"

            btn = tk.Button(
                self.button_frame,
                text=button_text,
                command=lambda f=folder_path, s=script: self.run_script_thread(f, s)
            )
            btn.pack(pady=5)

        self.loaded_folders[folder_path] = scripts
        self.save_config()

    def run_script_thread(self, folder, script):
        thread = threading.Thread(target=self.run_script, args=(folder, script), daemon=True)
        thread.start()

    def run_script(self, folder, script):
        self.output_display.delete('1.0', tk.END)
        try:
            venv_activate = os.path.join(folder, 'venv', 'Scripts', 'python.exe')
            script_path = os.path.join(folder, script)

            current_dir = os.getcwd()
            os.chdir(folder)

            if os.path.exists(venv_activate):
                command = [venv_activate, script_path]
            else:
                command = ["python", script_path]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False
            )

            for line in process.stdout:
                self.output_display.insert(tk.END, line)
                self.output_display.see(tk.END)

            for line in process.stderr:
                self.output_display.insert(tk.END, line)
                self.output_display.see(tk.END)

            process.wait()
        except Exception as e:
            self.output_display.insert(tk.END, f"Error: {e}")
        finally:
            os.chdir(current_dir)

    def save_config(self):
        with open(self.CONFIG_FILE, "w") as file:
            json.dump(self.loaded_folders, file)

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as file:
                self.loaded_folders = json.load(file)
                for folder, scripts in self.loaded_folders.items():
                    if os.path.exists(folder):
                        self.load_scripts(folder)


# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptRunnerApp(root)
    root.mainloop()
