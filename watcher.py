import time
from watchdog.observers import Observer  # следит за папкой IN
from watchdog.events import FileSystemEventHandler  # «создан новый файл» - что делать


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:  # созданный объект — папка?
            return

        print("Нашел:", event.src_path)


# Observer - класс из watchdog
def watch_folder(folder):
    observer = Observer()  # созданный объект
    handler = NewFileHandler()  # создание объекта класса  
    observer.schedule(handler, str(folder), recursive=False)  # Следит за folder, события передает в handler
    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()  # Если Ctrl+C - остановить Observer

    observer.join()
