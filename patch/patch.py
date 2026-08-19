from __future__ import annotations

import asyncio
from pathlib import Path

from .rom import unpack_rom, build_rom
from .. import items
from .. import locations
from .. import smt4_patch
from ..game.items import item_table
from ..game.treasure import treasure

ap_item_id = 1951


def patch(rom_file_path: Path, patch_info: smt4_patch.SMT4PatchInfo, target_file_name: str) -> Path:
    return asyncio.run(patch_inner(rom_file_path, patch_info, target_file_name))


async def patch_inner(rom_file_path: Path, patch_info: smt4_patch.SMT4PatchInfo, target_file_name: str) -> Path:
    print("Unpacking rom.")
    await unpack_rom(rom_file_path)

    print("Applying patches.")

    romfs_path = rom_file_path.parent / "ExtractedRomFS"

    patch_loot(romfs_path, patch_info)
    patch_items(romfs_path)

    print("Finished applying patches.")

    print("Rebuilding rom.")
    return await build_rom(rom_file_path, target_file_name)


def patch_loot(romfs_path: Path, patch_info: smt4_patch.SMT4PatchInfo):
    checks_map = patch_info.check_map

    ap_locations_to_game_id = {location.name: location.game_id for location in locations.locations}
    ap_items_to_game_id = {item.name: item.game_id for item in items.items} | {"AP Item": ap_item_id}

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


def patch_items(romfs_path: Path):
    table = item_table.item_table

    ap_item = table.get_item_by_id(ap_item_id)
    ap_item.name = "AP Item"

    table.to_file(romfs_path)


if __name__ == '__main__':
    patch()
