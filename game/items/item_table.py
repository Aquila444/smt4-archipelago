from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

import orjson

from .consumables import Consumable
from .cut_content import CutContentItem
from .gear import Gear
from .item import Item
from .key_items import KeyItem
from .relics import Relic
from .stars import StarItem
from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table, TBL
from ...utils.utils import load_data_file_as_json

TBB_FILE_PATH = "item/ItemTable.tbb"
ROM_FILE_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
DATA_FILE_NAME = "items.json"
DATA_FILE_LOCATION = DATA_DIR / DATA_FILE_NAME


class ItemType(IntEnum):
    KEY_ITEMS = 0
    CONSUMABLES = 1
    GEAR = 2
    STARS = 3
    RELICS = 4
    CUT_CONTENT = 5


@dataclass
class ItemTable:
    item_categories: list[ItemCategory]

    def __init__(self, item_categories: list[ItemCategory], tbb_table: Table):
        self.item_categories = item_categories
        self.tbb_table = tbb_table.to_empty_table()
        self._id_to_item = {item.item_id: item for category in self.item_categories for item in category.items}

    @staticmethod
    def load_from_rom() -> ItemTable:
        table = Table.from_file(ROM_FILE_LOCATION)

        key_items = table.tables[ItemType.KEY_ITEMS.value]
        consumables = table.tables[ItemType.CONSUMABLES.value]
        gear = table.tables[ItemType.GEAR.value]
        stars = table.tables[ItemType.STARS.value]
        relics = table.tables[ItemType.RELICS.value]
        cut_content_items = table.tables[ItemType.CUT_CONTENT.value]

        key_item_category = ItemCategory.from_table(key_items, ItemType.KEY_ITEMS, KeyItem)
        consumable_category = ItemCategory.from_table(consumables, ItemType.CONSUMABLES, Consumable)
        gear_category = ItemCategory.from_table(gear, ItemType.GEAR, Gear)
        star_category = ItemCategory.from_table(stars, ItemType.STARS, StarItem)
        relic_category = ItemCategory.from_table(relics, ItemType.RELICS, Relic)
        cut_items = ItemCategory.from_table(cut_content_items, ItemType.CUT_CONTENT, CutContentItem)

        categories = [key_item_category, consumable_category, gear_category, star_category, relic_category, cut_items]

        return ItemTable(categories, table)

    def to_file(self, romfs_path: Path) -> None:
        self._sync_state_to_tbb_table()

        tbb_file_path = romfs_path / TBB_FILE_PATH
        self.tbb_table.to_file(tbb_file_path)

    def _sync_state_to_tbb_table(self) -> None:
        for table_index, category in enumerate(self.item_categories):
            subtable = self.tbb_table.tables[table_index]

            for item in category.items:
                item_bytes = item.to_bytes()
                subtable.add_entry(item_bytes)

    @classmethod
    def load_from_json(cls) -> ItemTable:
        data = load_data_file_as_json(DATA_FILE_NAME, encoding="shift_jis")

        categories = data["item_categories"]
        mapped_categories = [ItemCategory.from_dict(entry) for entry in categories]

        table = Table.from_dict(data["tbb_table"])

        return ItemTable(mapped_categories, table)

    def export(self):
        with open(DATA_FILE_LOCATION, "wb+") as json_file:
            encoded_json = orjson.dumps(self)
            json_file.write(encoded_json)

    def get_item_by_id(self, item_id: int) -> Item:
        return self._id_to_item[item_id]


@dataclass
class ItemCategory[T: Item]:
    class_map = {
        ItemType.KEY_ITEMS: KeyItem,
        ItemType.CONSUMABLES: Consumable,
        ItemType.GEAR: Gear,
        ItemType.STARS: StarItem,
        ItemType.RELICS: Relic,
        ItemType.CUT_CONTENT: CutContentItem
    }

    item_type: ItemType
    items: list[T]

    @classmethod
    def from_table[S](cls, table: TBL, item_type: ItemType, item_class: S) -> ItemCategory[S]:
        items = [item_class.from_bytes(value) for value in table.table_data.data]

        return ItemCategory(item_type, items)

    @classmethod
    def from_dict(cls, data: dict):
        item_type = ItemType(data["item_type"])
        item_class = cls.class_map[item_type]
        items = [item_class.from_dict(entry) for entry in data["items"]]

        return ItemCategory(item_type, items)


try:
    item_table = ItemTable.load_from_json()
except Exception as e:
    print(e)


def main():
    print()


if __name__ == "__main__":
    main()
