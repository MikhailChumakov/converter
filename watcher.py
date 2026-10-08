import time
from pathlib import Path
from queue import PriorityQueue
from threading import Thread
from watchdog.observers import Observer  # следит за папкой IN
from watchdog.events import FileSystemEventHandler  # «создан новый файл» - что делать
from converter import get_priority, convert_file
import subprocess  # для запуска внешних программ. В нашем случае - ffprobe


file_queue = PriorityQueue()  # объект очереди
pending_files = set()  # Множество не хранит одинаковые значения дважды
# PriorityQueue больше не будет заниматься ожиданием копирования - будет отвечать только за очерёдность конвертации готовых файлов.
file_states = {}  # Словарь - потому что ключом будет путь
# значением позже сделаем информацию о предыдущем состоянии


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


# файл докопировался? проверка через ffprobe
# запоминает размер и время изменения файла, что бы сравнивать
def is_file_ready(file: Path) -> bool:
    if not file.exists():
        return False

    stat = file.stat()  #
    current_state = (stat.st_size, stat.st_mtime)
    # stat.st_size - размер; stat.st_mtime - время последнего изменения файла.
    # создаем кортеж
    previous_state = file_states.get(file)  # Посмотри в словаре file_states, есть ли уже сохранённое состояние этого файла.
    #  изначально там previous_state = None
    file_states[file] = current_state  # сохраняем текущие изменения

    if previous_state != current_state:

        return False

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_format",
            str(file),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode == 0


def check_pending_files():
    while True:
        for file in list(pending_files):
            if is_file_ready(file):
                priority = get_priority(file)

                pending_files.remove(file)
                file_states.pop(file, None)

                file_queue.put((priority, file))

                print("Файл готов и добавлен в очередь:", file.name)

        time.sleep(2)


def process_queue(output_dir):
    while True:
        priority, file = file_queue.get()  # распаковка кортежа.

        try:
            print("Взял файл из очереди:", file.name)
            convert_file(file, output_dir)

        except subprocess.CalledProcessError:
            print("Ошибка конвертации:", file.name)

        finally:
            file_queue.task_done()


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file = Path(event.src_path)  # путь в объект

        # проверка существования до get_priority()
        if not file.exists():
            return

        if get_priority(file) == 4:
            print("Пропускаю:", file.name)
            return

        pending_files.add(file)

        print("Добавлен в очередь: ", file.name)


def add_existing_files(folder: Path):
    for file in folder.iterdir():
        if not file.is_file():
            continue

        if get_priority(file) == 4:
            print("Пропускаю:", file.name)
            continue

        pending_files.add(file)

        print("Добавлен в очередь при запуске:", file.name)


# Observer - класс из watchdog
def watch_folder(folder, output_dir):
    observer = Observer()  # созданный объект
    handler = NewFileHandler()  # создание объекта класса  
    observer.schedule(handler, str(folder), recursive=False)  # Следит за folder, события передает в handler
    checker = Thread(target=check_pending_files, daemon=True)
    worker = Thread(
        target=process_queue,
        args=(output_dir,),
        daemon=True
    )  # запуск функции в новом потоке, а не моментально.
    # daemon=True - не будет удерживать программу запущенной, когда процесс закончен
    checker.start()
    worker.start()
    observer.start()

    add_existing_files(folder)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()  # Если Ctrl+C - остановить Observer

    observer.join()
