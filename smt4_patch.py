from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import orjson

from settings import get_settings
from worlds.Files import APProcedurePatch, AutoPatchExtensionRegister
from .config import GAME_NAME
from .patch.patch import patch

patch_data_file_name = "patch_info.json"


@dataclass
class SMT4PatchInfo:
    seed: str
    check_map: dict[str, str]

    def to_json(self) -> bytes:
        return orjson.dumps(self)

    @classmethod
    def from_json(cls, json_data: bytes) -> SMT4PatchInfo:
        data = orjson.loads(json_data)

        check_map = data["check_map"]
        seed = data["seed"]

        return SMT4PatchInfo(seed, check_map)


class SMT4Patch(APProcedurePatch):
    game = GAME_NAME
    hash = None
    patch_file_ending = ".apsmt4"
    result_file_ending = ".3ds"

    procedure = [
        ("patch_smt4", [])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        cls.rom_file = get_settings().smt4_settings.rom_file

        return b""


class Smt4PatchExtension(metaclass=AutoPatchExtensionRegister):
    game = GAME_NAME

    @staticmethod
    def patch_smt4(caller: SMT4Patch, rom: bytes) -> bytes:
        try:
            return patch_smt4_inner(caller)
        except Exception as e:
            from tkinter.messagebox import showerror
            showerror(message=str(e))
            raise e


def patch_smt4_inner(caller: SMT4Patch) -> bytes:
    rom_file_path = Path(caller.rom_file)
    patch_data = caller.get_file(patch_data_file_name)
    patch_info = SMT4PatchInfo.from_json(patch_data)

    patched_rom = patch(rom_file_path, patch_info)

    with open(patched_rom, "rb") as output_file:
        return output_file.read()
