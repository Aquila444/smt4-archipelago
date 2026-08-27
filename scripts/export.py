import re

from ..config import DATA_DIR, INPUT_ROMFS_DIR
from ..game.demons.demons import DemonTable
from ..game.items.item_table import ItemTable
from ..game.quests.quests import QuestTable
from ..game.treasure.treasure import LootTable
from ..tbb.tbb import Table

category_regex = re.compile(r"^root->([^->]+)->")
address_regex = re.compile(r".*?(0x[0-9a-f]+)")
name_regex = re.compile(r".*->([^=]+)\s=")


def main():
    export_demons()
    export_items()
    export_inventory_ids()
    export_item_ids()
    export_loot()
    export_quests()


def export_inventory_ids():
    item_tbb_file_path = INPUT_ROMFS_DIR / "item/ItemTable.tbb"
    item_table = Table.from_file(item_tbb_file_path)
    unpacked_item_tables = [entry for subtable in item_table.tables for entry in subtable.table_data.data]
    decoded_item_table_data = [entry.decode("shift_jis", errors='ignore') for entry in unpacked_item_tables]
    prettified_item_data = [strip_item_data(entry) for entry in decoded_item_table_data]

    output_path = DATA_DIR / "inventory-ids.txt"
    with open(output_path, "w", encoding="shift_jis") as item_file:
        for index, entry in enumerate(prettified_item_data):
            item_file.write(f"{index}: {entry}\n")


def export_item_ids():
    item_tbb_file_path = INPUT_ROMFS_DIR / "item/ItemTable.tbb"
    item_table = Table.from_file(item_tbb_file_path)

    key_items = item_table.tables[0].table_data.data
    consumables = item_table.tables[1].table_data.data
    gear = item_table.tables[2].table_data.data
    stars = item_table.tables[3].table_data.data
    relics = item_table.tables[4].table_data.data
    cut_content_items = item_table.tables[5].table_data.data

    reordered_item_tables = [consumables, gear, key_items, stars, relics, cut_content_items]

    unpacked_item_tables = [entry for subtable in reordered_item_tables for entry in subtable]
    decoded_item_table_data = [entry.decode("shift_jis", errors='ignore') for entry in unpacked_item_tables]
    prettified_item_data = [strip_item_data(entry) for entry in decoded_item_table_data]

    output_path = DATA_DIR / "item-ids.txt"
    with open(output_path, "w", encoding="shift_jis") as item_file:
        for index, entry in enumerate(prettified_item_data):
            item_file.write(f"{index + 1}: {entry}\n")


def strip_item_data(item_data):
    return item_data.split("\x00")[0]


def export_demons():
    demon_table = DemonTable.load_from_rom()
    demon_table.export()


def export_quests():
    quest_table = QuestTable.load_from_rom()
    quest_table.export()


def export_loot():
    loot_table = LootTable.load_from_rom()
    loot_table.export()


def export_items():
    item_table = ItemTable.load_from_rom()
    item_table.export()


if __name__ == '__main__':
    main()
