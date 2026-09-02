from __future__ import annotations

import asyncio
from pathlib import Path

from .rom import unpack_rom, build_rom
from .. import items
from .. import locations
from .. import smt4_patch
from ..game.items.item_table import item_table
from ..game.shops.shop_table import shop_table
from ..game.treasure.treasure import loot_table, LootLocation, LootDrop

ap_item_id = 1951
ap_item_name = "AP Item"


def patch(rom_file_path: Path, patch_info: smt4_patch.SMT4PatchInfo, target_path: Path):
    return asyncio.run(patch_inner(rom_file_path, patch_info, target_path))


async def patch_inner(rom_file_path: Path, patch_info: smt4_patch.SMT4PatchInfo, target_path: Path):
    print("Unpacking rom.")
    await unpack_rom(rom_file_path)

    print("Applying patches.")

    romfs_path = rom_file_path.parent / "ExtractedRomFS"

    patch_items(romfs_path)
    patch_loot(romfs_path, patch_info)
    patch_shops(romfs_path, patch_info)

    print("Finished applying patches.")

    print("Rebuilding rom.")
    await build_rom(rom_file_path, target_path)


def patch_loot(romfs_path: Path, patch_info: smt4_patch.SMT4PatchInfo):
    game_locations_to_items = get_game_id_map(patch_info, "treasure")
    new_game_locations = {
        location_id: map_loot_entry(int(location_id), item_id)
        for location_id, item_id in game_locations_to_items.items()
    }

    loot_table.locations = loot_table.locations | new_game_locations
    loot_table.to_file(romfs_path)


def map_loot_entry(location_id: int, item_id: int) -> LootLocation:
    drop = LootDrop(item_id, 100, "")

    return LootLocation(location_id, [drop])


def patch_items(romfs_path: Path):
    ap_item = item_table.get_item_by_id(ap_item_id)
    ap_item.name = ap_item_name

    item_table.to_file(romfs_path)


def patch_shops(romfs_path: Path, patch_info: smt4_patch.SMT4PatchInfo):
    game_locations_to_items = get_game_id_map(patch_info, "shop")

    for location_id, item_id in game_locations_to_items.items():
        shop_index, item_index = [int(value) for value in location_id.split("-")]
        shop_item = shop_table.get_shop_item(shop_index, item_index)
        shop_item.item_id = item_id

    shop_table.to_file(romfs_path)


def get_game_id_map(patch_info: smt4_patch.SMT4PatchInfo, location_type: str) -> dict[str, int]:
    checks_map = patch_info.check_map

    ap_locations_to_game_id = {location.name: location.game_id for location in locations.locations if
                               location.type == location_type}
    ap_items_to_game_id = {item.name: item.game_id for item in items.items} | {ap_item_name: ap_item_id}

    game_locations_to_items = {
        ap_locations_to_game_id[location_name]: ap_items_to_game_id[item_name]
        for (location_name, item_name) in checks_map.items() if ap_locations_to_game_id.get(location_name) is not None
    }

    return game_locations_to_items


if __name__ == '__main__':
    patch()
