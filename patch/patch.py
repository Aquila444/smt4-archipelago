from __future__ import annotations

import asyncio
from pathlib import Path

from .rom import unpack_rom, build_rom
from .. import items
from .. import locations
from .. import smt4_patch
from ..game.treasure import treasure


def patch(rom_file_path: Path, patch_info: smt4_patch.SMT4PatchInfo) -> Path:
    return asyncio.run(patch_inner(rom_file_path, patch_info))


async def patch_inner(rom_file_path: Path, patch_info: smt4_patch.SMT4PatchInfo) -> Path:
    print("Unpacking rom.")
    await unpack_rom(rom_file_path)

    print("Applying patches.")

    romfs_path = rom_file_path.parent / "ExtractedRomFS"

    patch_loot(romfs_path, patch_info)

    print("Finished applying patches.")

    print("Rebuilding rom.")
    return await build_rom(rom_file_path)


def patch_loot(romfs_path: Path, patch_info: smt4_patch.SMT4PatchInfo):
    checks_map = patch_info.check_map

    ap_locations_to_game_id = {location.name: location.game_id for location in locations.locations}
    ap_items_to_game_id = {item.name: item.game_id for item in items.items}

    game_locations_to_items = {
        ap_locations_to_game_id[location_name]: ap_items_to_game_id[item_name]
        for (location_name, item_name) in checks_map.items()
    }

    new_game_locations = {
        str(location_id): map_loot_entry(location_id, item_id)
        for index, (location_id, item_id) in game_locations_to_items.items()
    }

    treasure.loot_table.locations = new_game_locations
    treasure.loot_table.to_file(romfs_path)


def map_loot_entry(location_id: int, item_id: int) -> treasure.LootLocation:
    drop = treasure.LootDrop(item_id, 100, "")

    return treasure.LootLocation(location_id, [drop])


if __name__ == '__main__':
    patch()
