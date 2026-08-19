from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum

from .item import Item
from ...utils.utils import extract_string_from_bytes


class RelicCategory(IntEnum):
    NONE = 0
    GADGET = 1
    LEISURE = 2
    FOOD = 3
    FURNITURE = 4
    COSMETICS = 5
    COMMODITY = 6
    MINERALS = 7
    DOCUMENT = 8
    MEDICINE = 9
    CLOTHING = 10


@dataclass
class Relic(Item):

    _NAME_LENGTH = 32

    _STRUCT_FORMAT = f"<{_NAME_LENGTH}s2HxB2x2I"
    _STRUCT_LENGTH = struct.calcsize(_STRUCT_FORMAT)

    sell_value: int
    category: RelicCategory
    sort_value: int
    unknown_1: int

    @classmethod
    def from_bytes(cls, value_bytes: bytes) -> Relic:
        struct_bytes = value_bytes[:cls._STRUCT_LENGTH]

        (
            name_bytes, item_id, unknown_1, category_value, sort_value, sell_value
        ) = struct.unpack(cls._STRUCT_FORMAT, struct_bytes)

        original_name = name_bytes.decode(encoding="shift-jis")
        name = extract_string_from_bytes(name_bytes)

        category = RelicCategory(category_value)

        return Relic(item_id, name, original_name, sell_value, category, sort_value, unknown_1)

    def to_bytes(self) -> bytes:
        name_bytes = self.get_name_bytes(self._NAME_LENGTH)

        values = name_bytes, self.item_id, self.unknown_1, self.category.value, self.sort_value, self.sell_value

        return struct.pack(self._STRUCT_FORMAT, *values)

    @classmethod
    def from_dict(cls, data: dict) -> Relic:
        item_id = data["item_id"]
        name = data["name"]
        original_name = data["original_name"]

        sell_value = data["sell_value"]
        category = RelicCategory(data["category"])
        sort_value = data["sort_value"]
        unknown_1 = data["unknown_1"]

        return Relic(item_id, name, original_name, sell_value, category, sort_value, unknown_1)