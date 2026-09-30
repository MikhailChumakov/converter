from pathlib import Path # для работы с структурой папок
import subprocess # модуль для запуска внешних программ
import json
import platform
from tkinter import filedialog


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
