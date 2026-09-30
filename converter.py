from pathlib import Path # для работы с структурой папок
import subprocess # модуль для запуска внешних программ
import json
import platform
from tkinter import filedialog


VIDEO_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.mxf'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'}
LIMIT_25_GB = 25 * 1024 * 1024 * 1024

def get_config_dir() -> Path:
    if platform.system() == 'Darwin':
        return Path.home() / 'Library' / 'Application Support' / 'Converter'

    if platform.system() == 'Windows':
        return Path.home() / 'AppData' / 'Roaming' / 'Converter'

    return Path.home() / '.config' / 'Converter'

CONFIG_DIR = get_config_dir()
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / 'config.json'

def save_config(input_dir: Path, output_dir: Path):
    config = {
        'input_dir': str(input_dir.resolve()),  # откуда брать
        'output_dir': str(output_dir.resolve())  # куда положить
    }

    with CONFIG_FILE.open('w') as file:
        json.dump(config, file, indent=4)


def load_config():

    if not CONFIG_FILE.exists():

        return None

    with CONFIG_FILE.open('r') as file:

        config = json.load(file)

    input_dir = Path(config['input_dir'])

    output_dir = Path(config['output_dir'])

    return input_dir, output_dir


def select_folder() -> Path | None:
    folder = filedialog.askdirectory()

    if not folder:
        return None

    return Path(folder)


def get_priority(file: Path) -> int:
    extension = file.suffix.lower()

    file_size = file.stat().st_size

    if extension in AUDIO_EXTENSIONS:
        return 1

    if extension in VIDEO_EXTENSIONS and file_size <= LIMIT_25_GB:
        return 2

    if extension in VIDEO_EXTENSIONS and file_size > LIMIT_25_GB:
        return 3

    return 4


def execute_conversion (command: list[str], file: Path):
    subprocess.run(command, check=True)

    file.unlink()

    print(f'Конвертация прошла успешно, {file.name} удален')


# проверяем название - добавляем номер
def get_unique_name(source_name: str, output_format: str, output_dir: Path) -> Path:
    output_file = output_dir / f'{source_name}_convert{output_format}'

    if not output_file.exists():
        return output_file

    counter = 2

    while True:
        output_file = output_dir / f'{source_name}_{counter:03}_convert{output_format}'

        if not output_file.exists():
            return output_file

        counter += 1


def process_files(input_dir: Path, output_dir: Path):
    files = sorted(input_dir.iterdir(), key=get_priority)

    for file in files:
        extension = file.suffix.lower()

        if extension in AUDIO_EXTENSIONS:
            output_file = get_unique_name(file.stem, '.wav', output_dir) # путь и имя сконвертируемого файла

            command = [
                'ffmpeg',
                '-i', str(file),
                '-af', 'loudnorm=I=-23:TP=-2:LRA=7', # -23 LUFS
                '-c:a', 'pcm_s16le', # указываем явно кодек
                str(output_file),
            ]

            print('Конвертирую аудио:', file.name)
            execute_conversion(command, file)

        elif extension in VIDEO_EXTENSIONS:
            output_file = get_unique_name(file.stem, '.mp4', output_dir)

            command = [
                'ffmpeg',
                '-i', str(file),
                str(output_file)
            ]

            print('Конвертирую видео:', file.name)

            execute_conversion(command, file)


        else:
            print('Пропускаю:', file.name)


config = load_config()

if config is not None:
    input_dir, output_dir = config

    print('IN:', input_dir)
    print('OUT:', output_dir)

    folders_exist = input_dir.exists() and output_dir.exists()

    if not input_dir.exists():
        print('Папка IN не найдена')

        input_base_dir = select_folder()

        if input_base_dir is not None:
            input_dir = input_base_dir / 'in'
            input_dir.mkdir(exist_ok=True)

            print('Новая IN:', input_dir)

            save_config(input_dir, output_dir)

    if not output_dir.exists():
        print('Папка OUT не найдена')

        output_base_dir = select_folder()

        if output_base_dir is not None:
            output_dir = output_base_dir / 'out'
            output_dir.mkdir(exist_ok=True)

            print('Новая OUT:', output_dir)

            save_config(input_dir, output_dir)

    if folders_exist:
        print('Папки найдены')

else:
    input_base_dir = select_folder()

    # назначаем и создаем папки IN/OUT
    if input_base_dir is not None:
        input_dir = input_base_dir / 'in'  # создаем папку in
        input_dir.mkdir(exist_ok=True)

        print('IN:', input_dir)

        output_base_dir = select_folder()

        if output_base_dir is not None:
            output_dir = output_base_dir / 'out'
            output_dir.mkdir(exist_ok=True)

            print('OUT:', output_dir)

            save_config(input_dir, output_dir)
        else:
            print('Место для OUT не выбрано')

    else:
        print('Место для IN не выбрано')
