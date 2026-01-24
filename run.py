import subprocess
import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Watch these extensions for changes
WATCH_EXTENSIONS = (".py", ".kv")

class RestartOnChange(FileSystemEventHandler):
    def __init__(self, run_script):
        self.run_script = run_script
        self.process = None
        self.restart()  # start the app immediately

    def restart(self):
        if self.process:
            print("🔁 Restarting app...\n")
            self.process.terminate()  # stop old instance
            self.process.wait()       # wait for it to close
        print("▶️ Starting app...")
        self.process = subprocess.Popen([sys.executable, self.run_script])

    def on_modified(self, event):
        # Trigger restart only if the modified file is a .py or .kv
        if event.src_path.endswith(WATCH_EXTENSIONS):
            self.restart()

if __name__ == "__main__":
    run_script = "main.py"  # <- replace with your Kivy app file
    event_handler = RestartOnChange(run_script)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
