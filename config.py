from pathlib import Path

from .. import smt4 as parent_package

SOURCE_DIR = Path(__file__).resolve().parent
BASE_DIR = SOURCE_DIR.parent.parent.parent
DATA_DIR = SOURCE_DIR / "data"
INPUT_ROM_DIR = BASE_DIR / "clean_rom"
INPUT_ROMFS_DIR = INPUT_ROM_DIR / "ExtractedRomFS"
OUTPUT_ROM_DIR = BASE_DIR / "rom"

GAME_NAME = "Shin Megami Tensei 4"