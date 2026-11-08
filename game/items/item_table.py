from __future__ import annotations

import pickle
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

from .consumables import Consumable
from .cut_content import CutContentItem
from .gear import Gear
from .item import Item
from .key_items import KeyItem
from .relics import Relic
from .stars import StarItem
from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...mbm.mbm import MBM
from ...tbb.tbb import Table, TBL

TBB_FILE_PATH = "item/ItemTable.tbb"
MBM_FILE_PATH = "item/ItemHelpMess.mbm"
ROM_FILE_TBB_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
ROM_FILE_MBM_LOCATION = INPUT_ROMFS_DIR / MBM_FILE_PATH
DATA_FILE_NAME = "items.pickle"
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

    def __init__(self, item_categories: list[ItemCategory], tbb_table: Table, mbm: MBM):
        self.item_categories = item_categories
        self.tbb_table = tbb_table.to_empty_table()
        self.mbm = mbm
        self._id_to_item = {item.item_id: item for category in self.item_categories for item in category.items}

    @staticmethod
    def load_from_rom() -> ItemTable:
        mbm = MBM.from_file(ROM_FILE_MBM_LOCATION)
        description_map = {item_id: description_bytes.decode(encoding="shift_jis", errors="surrogateescape")
                           for item_id, description_bytes in mbm.data.items() if description_bytes is not None}

        table = Table.from_file(ROM_FILE_TBB_LOCATION)

        key_items = table.tables[ItemType.KEY_ITEMS.value]
        consumables = table.tables[ItemType.CONSUMABLES.value]
        gear = table.tables[ItemType.GEAR.value]
        stars = table.tables[ItemType.STARS.value]
        relics = table.tables[ItemType.RELICS.value]
        cut_content_items = table.tables[ItemType.CUT_CONTENT.value]

        key_item_category = ItemCategory.from_table(key_items, ItemType.KEY_ITEMS, KeyItem, description_map)
        consumable_category = ItemCategory.from_table(consumables, ItemType.CONSUMABLES, Consumable, description_map)
        gear_category = ItemCategory.from_table(gear, ItemType.GEAR, Gear, description_map)
        star_category = ItemCategory.from_table(stars, ItemType.STARS, StarItem, description_map)
        relic_category = ItemCategory.from_table(relics, ItemType.RELICS, Relic, description_map)
        cut_items = ItemCategory.from_table(cut_content_items, ItemType.CUT_CONTENT, CutContentItem, description_map)

        categories = [key_item_category, consumable_category, gear_category, star_category, relic_category, cut_items]

        return ItemTable(categories, table, mbm)

    def to_file(self, romfs_path: Path) -> None:
        self._sync_state_to_tbb_table()
        tbb_file_path = romfs_path / TBB_FILE_PATH
        self.tbb_table.to_file(tbb_file_path)

        self._update_mbm_table()
        mbm_file_path = romfs_path / MBM_FILE_PATH
        self.mbm.to_file(mbm_file_path)

    def _sync_state_to_tbb_table(self) -> None:
        self.tbb_table.to_empty_table()

        for table_index, category in enumerate(self.item_categories):
            subtable = self.tbb_table.tables[table_index]

            for item in category.items:
                item_bytes = item.to_bytes()
                subtable.add_entry(item_bytes)

    def _update_mbm_table(self):
        items = [item for category in self.item_categories for item in category.items]
        description_map = {item.item_id: item.get_description_bytes() for item in items}

        self.mbm.data = self.mbm.data | description_map

    @classmethod
    def load_from_data(cls) -> ItemTable:
        with open(DATA_FILE_LOCATION, "rb+") as pickle_file:
            return pickle.load(pickle_file)

    def export(self):
        with open(DATA_FILE_LOCATION, "wb+") as pickle_file:
            pickle.dump(self, pickle_file)

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
    def from_table[S](cls, table: TBL, item_type: ItemType, item_class: S, description_map: dict[int, str]) -> \
            ItemCategory[S]:
        items = [item_class.from_bytes(value, description_map) for value in table.table_data.data]

        return ItemCategory(item_type, items)


try:
    item_table = ItemTable.load_from_data()
except Exception as e:
    item_table = None
    print(e)
