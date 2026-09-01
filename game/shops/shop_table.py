from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import orjson

from .shops import Shop, ShopAction, ShopEntry
from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table
from ...utils.utils import load_data_file_as_json

TBB_FILE_PATH = "shop/ShopTable.tbb"
ROM_FILE_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
DATA_FILE_NAME = "shops.json"
DATA_FILE_LOCATION = DATA_DIR / DATA_FILE_NAME


@dataclass
class ShopTable:
    shop_actions: list[ShopAction]
    shop_names: list[ShopEntry]
    shops: list[Shop]

    def __init__(self, shop_actions: list[ShopAction], shop_names: list[ShopEntry], shops: list[Shop], tbb_table: Table):
        self.shop_actions = shop_actions
        self.shop_names = shop_names
        self.shops = shops
        self.tbb_table = tbb_table.to_empty_table()

    @classmethod
    def load_from_rom(cls):
        shop_table = Table.from_file(ROM_FILE_LOCATION)

        shop_actions = [ShopAction.from_bytes(shop_action_bytes) for shop_action_bytes in
                        shop_table.tables[0].get_data()]
        shop_names = [ShopEntry.from_bytes(shop_name_bytes) for shop_name_bytes in shop_table.tables[1].get_data()]
        shop_tables = shop_table.tables[2:]

        item_ids_path = DATA_DIR / "item-ids.txt"
        with open(item_ids_path, mode="r", encoding="shift_jis") as item_data_file:
            item_data = item_data_file.readlines()

            item_map = {int(entry.split(": ")[0]): entry.split(": ")[1].strip() for entry in item_data}

        shops = [Shop.from_table(index, shop_name, shop_tables[index], item_map) for index, shop_name in
                 enumerate(shop_names)]

        return ShopTable(shop_actions, shop_names, shops, shop_table)

    def to_file(self, romfs_path: Path) -> None:
        self._sync_state_to_tbb_table()

        tbb_file_path = romfs_path / TBB_FILE_PATH
        self.tbb_table.to_file(tbb_file_path)

    def _sync_state_to_tbb_table(self) -> None:
        self.tbb_table.to_empty_table()

        shop_action_table = self.tbb_table.tables[0]
        for shop_action in self.shop_actions:
            shop_action_bytes = shop_action.to_bytes()
            shop_action_table.add_entry(shop_action_bytes)

        shop_names_table = self.tbb_table.tables[1]
        for shop_name in self.shop_names:
            shop_name_bytes = shop_name.to_bytes()
            shop_names_table.add_entry(shop_name_bytes)

        for index, shop in enumerate(self.shops):
            subtable = self.tbb_table.tables[index + 2]

            for shop_item in shop.shop_items:
                shop_item_bytes = shop_item.to_bytes()
                subtable.add_entry(shop_item_bytes)

    @classmethod
    def load_from_json(cls) -> ShopTable:
        data = load_data_file_as_json(DATA_FILE_NAME, encoding="shift_jis")

        shop_actions = [ShopAction.from_dict(entry) for entry in data["shop_actions"]]
        shop_names = [ShopEntry.from_dict(entry) for entry in data["shop_names"]]
        shops = [Shop.from_dict(entry) for entry in data["shops"]]

        table = Table.from_dict(data["tbb_table"])

        return ShopTable(shop_actions, shop_names, shops, table)

    def export(self):
        with open(DATA_FILE_LOCATION, "wb+") as json_file:
            encoded_json = orjson.dumps(self)
            json_file.write(encoded_json)
