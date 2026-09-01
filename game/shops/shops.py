from __future__ import annotations

import struct
from dataclasses import dataclass

from ...tbb.tbb import TBL
from ...utils.utils import extract_name_from_bytes, encode_string_with_padding


@dataclass
class ShopAction:
    NAME_LENGTH = 64
    DESCRIPTION_LENGTH = 64
    STRUCT_FORMAT = f"<{NAME_LENGTH}s{DESCRIPTION_LENGTH}s"

    name: str
    description: str

    @classmethod
    def from_bytes(cls, shop_action_bytes: bytes) -> ShopAction:
        name_bytes, description_bytes = struct.unpack(ShopAction.STRUCT_FORMAT, shop_action_bytes)

        name = extract_name_from_bytes(name_bytes)
        description = extract_name_from_bytes(description_bytes)

        return ShopAction(name, description)

    def to_bytes(self) -> bytes:
        name = encode_string_with_padding(self.name, self.NAME_LENGTH)
        description = encode_string_with_padding(self.description, self.DESCRIPTION_LENGTH)
        values = [name, description]

        return struct.pack(ShopAction.STRUCT_FORMAT, *values)

    @classmethod
    def from_dict(cls, data: dict) -> ShopAction:
        return ShopAction(**data)


@dataclass
class ShopEntry:
    NAME_LENGTH = 32
    DESCRIPTION_LENGTH = 64
    STRUCT_FORMAT = f"<{NAME_LENGTH}sI2H{DESCRIPTION_LENGTH}s"

    name: str
    description: str
    unknown_1: int
    unknown_2: int
    unknown_3: int

    @classmethod
    def from_bytes(cls, shop_name_bytes: bytes) -> ShopEntry:
        name_bytes, unknown_1, unknown_2, unknown_3, description_bytes = struct.unpack(ShopEntry.STRUCT_FORMAT,
                                                                                       shop_name_bytes)

        name = extract_name_from_bytes(name_bytes)
        description = extract_name_from_bytes(description_bytes)

        return ShopEntry(name, description, unknown_1, unknown_2, unknown_3)

    def to_bytes(self) -> bytes:
        name = encode_string_with_padding(self.name, self.NAME_LENGTH)
        description = encode_string_with_padding(self.description, self.DESCRIPTION_LENGTH)
        values = [name, self.unknown_1, self.unknown_2, self.unknown_3, description]

        return struct.pack(ShopEntry.STRUCT_FORMAT, *values)

    @classmethod
    def from_dict(cls, data: dict) -> ShopEntry:
        return ShopEntry(**data)


@dataclass
class Shop:
    shop_id: int
    name: str
    description: str
    shop_items: list[ShopItem]

    @classmethod
    def from_table(cls, index: int, shop_name: ShopEntry, shop_table: TBL, item_map: dict[int, str]) -> Shop:
        table_data = shop_table.get_data()
        shop_items = [ShopItem.from_bytes(entry, item_map) for entry in table_data]

        return Shop(index, shop_name.name, shop_name.description, shop_items)

    @classmethod
    def from_dict(cls, data: dict) -> Shop:
        name = data["name"]
        description = data["description"]
        shop_id = int(data["shop_id"])

        shop_items = [ShopItem.from_dict(entry) for entry in data["shop_items"]]

        return Shop(shop_id, name, description, shop_items)


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

    def to_bytes(self) -> bytes:
        values = [self.item_id, self.unlock_requirement, self.remove_requirement, self.quest_requirement]

        return struct.pack(ShopItem._STRUCT_FORMAT, *values)

    @classmethod
    def from_dict(cls, data: dict) -> ShopItem:
        return ShopItem(**data)
