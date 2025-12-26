from config import WATCH_DIRECTORIES, TEMP_BASE_DIR, TEMP_CATEGORIES
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileFlowHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: 
            return  # skip paths and out of method
        
        print(f"FFA detected new file: {event.src_path}")
