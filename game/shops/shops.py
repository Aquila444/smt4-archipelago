from __future__ import annotations

import struct
from dataclasses import dataclass

import orjson

from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table, TBL
from ...utils.utils import extract_string_from_bytes, load_data_file_as_json

TBB_FILE_PATH = "shop/ShopTable.tbb"
ROM_FILE_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
DATA_FILE_NAME = "shops.json"
DATA_FILE_LOCATION = DATA_DIR / DATA_FILE_NAME


@dataclass
class ShopTable:
    shop_actions: list[str]
    shop_names: list[str]
    shops: list[Shop]

    @classmethod
    def load_from_rom(cls):
        shop_table = Table.from_file(ROM_FILE_LOCATION)

        shop_actions = [extract_string_from_bytes(shop_action_bytes) for shop_action_bytes in
                        shop_table.tables[0].get_data()]
        shop_names = [extract_string_from_bytes(shop_name_bytes) for shop_name_bytes in shop_table.tables[1].get_data()]
        shop_tables = shop_table.tables[2:]

        item_ids_path = DATA_DIR / "item-ids.txt"
        with open(item_ids_path, mode="r", encoding="shift_jis") as item_data_file:
            item_data = item_data_file.readlines()

            item_map = {int(entry.split(": ")[0]): entry.split(": ")[1].strip() for entry in item_data}

        shops = [Shop.from_table(shop_name, shop_tables[index], item_map) for index, shop_name in enumerate(shop_names)]

        return ShopTable(shop_actions, shop_names, shops)

    @classmethod
    def load_from_json(cls) -> ShopTable:
        data = load_data_file_as_json(DATA_FILE_NAME, encoding="shift_jis")

        shop_actions = data["shop_actions"]
        shop_names = data["shop_names"]

        shops = [Shop.from_dict(entry) for entry in data["shops"]]

        return ShopTable(shop_actions, shop_names, shops)

    def export(self):
        with open(DATA_FILE_LOCATION, "wb+") as json_file:
            encoded_json = orjson.dumps(self)
            json_file.write(encoded_json)


@dataclass
class Shop:
    name: str
    shop_items: list[ShopItem]

    @classmethod
    def from_table(cls, name: str, shop_table: TBL, item_map: dict[int, str]) -> Shop:
        table_data = shop_table.get_data()
        shop_items = [ShopItem.from_bytes(entry, item_map) for entry in table_data]

        return Shop(name, shop_items)

    @classmethod
    def from_dict(cls, data: dict) -> Shop:
        name = data["name"]

        shop_items = [ShopItem.from_dict(entry) for entry in data["shop_items"]]

        return Shop(name, shop_items)


@dataclass
class ShopItem:
    _STRUCT_FORMAT = "<4h"

    item_id: int
    item_name: str
    unlock_requirement: int
    remove_requirement: int
    quest_requirement: int

    @classmethod
    def from_bytes(cls, shop_item_bytes: bytes, item_map: dict[int, str]) -> ShopItem:
        (
            item_id, unlock_requirement, remove_requirement, quest_requirement
        ) = struct.unpack(ShopItem._STRUCT_FORMAT, shop_item_bytes)

        item_name = item_map[item_id]

        return ShopItem(item_id, item_name, unlock_requirement, remove_requirement, quest_requirement)

    @classmethod
    def from_dict(cls, data: dict) -> ShopItem:
        return ShopItem(**data)
