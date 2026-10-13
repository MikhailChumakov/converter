import sys
from pathlib import Path


def get_binary_path(name: str) -> Path:
    if getattr(sys, "frozen", False):
        # Программа запущена из приложения PyInstaller
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(__file__).resolve().parent

    return base_dir / "bin" / name


FFMPEG = get_binary_path("ffmpeg")
FFPROBE = get_binary_path("ffprobe")
