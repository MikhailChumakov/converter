from pathlib import Path # для работы с структурой папок
import subprocess # модуль для запуска внешних программ
# from watchdog.observers import Observer  # следит за папкой IN
# from watchdog.events import FileSystemEventHandler  # «создан новый файл»


VIDEO_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.mxf'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'}
LIMIT_25_GB = 25 * 1024 * 1024 * 1024


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
