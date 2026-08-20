from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import orjson

from settings import get_settings
from worlds.Files import APProcedurePatch
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

    def patch(self, target: str) -> None:
        target_path = Path(target)
        if target_path.exists():
            return

        rom_file_path_str = get_settings().smt4.rom_file.resolve()
        rom_file_path = Path(rom_file_path_str)
        patch_data = self.get_file(patch_data_file_name)
        patch_info = SMT4PatchInfo.from_json(patch_data)

        patch(rom_file_path, patch_info, target_path)
