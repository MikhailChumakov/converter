import time
from pathlib import Path
from queue import PriorityQueue
from threading import Thread
from watchdog.observers import Observer  # следит за папкой IN
from watchdog.events import FileSystemEventHandler  # «создан новый файл» - что делать
from converter import get_priority


file_queue = PriorityQueue()  # объект очереди


# пока отложил - сделаю другу проверку готовности файла
def wait_until_ready(file: Path):
    previous_size = -1
    count = 0

    while True:
        current_size = file.stat().st_size

        if current_size == previous_size:
            count += 1
        else:
            count = 0

        if count >= 7:
            return

        previous_size = current_size
        time.sleep(1)


def process_queue():
    while True:
        priority, file = file_queue.get()  # распаковка кортежа.

        print("Взял из очереди: ", file.name)

        file_queue.task_done()


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file = Path(event.src_path)  # путь в объект
        priority = get_priority(file)

        file_queue.put((priority, file))
        # отправляем кортеж в очередь. Пример (1, Path("audio.ogg"))

        print("Добавлен в очередь: ", file.name)


# Observer - класс из watchdog
def watch_folder(folder):
    observer = Observer()  # созданный объект
    handler = NewFileHandler()  # создание объекта класса  
    observer.schedule(handler, str(folder), recursive=False)  # Следит за folder, события передает в handler
    worker = Thread(target=process_queue, daemon=True)  # запуск функции в новом потоке, а не моментально.
    # daemon=True - не будет удерживать программу запущенной, когда процесс закончен
    worker.start()
    observer.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()  # Если Ctrl+C - остановить Observer

    observer.join()
