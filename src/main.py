from config import WATCH_DIRECTORIES
from watcher import FileFlowHandler
from watchdog.observers import Observer
import time


if __name__ == "__main__":
    print("File Flow Assistant started!")
    print(f"Monitoring: {WATCH_DIRECTORIES}")

    handler = FileFlowHandler()
    observer = Observer()

    # Agenda pra todas as pastas do config (ou comece com uma só pra testar)
    for pasta in WATCH_DIRECTORIES:
        observer.schedule(handler, pasta, recursive=False)
        print(f" - Watching: {pasta}")

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Stoping the File Flow Assistant...")
        observer.stop()
    observer.join()
    print("Stop with success!")