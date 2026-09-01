from __future__ import annotations

import struct
from dataclasses import dataclass
from itertools import batched

from .item import Item
from ...utils.utils import extract_name_from_bytes


@dataclass
class RelicDrop:
    _STRUCT_FORMAT = f"2H"
    _STRUCT_SIZE = struct.calcsize(_STRUCT_FORMAT)

    item_id: int
    drop_weight: int

    @classmethod
    def from_bytes(cls, reward_bytes: bytes) -> RelicDrop:
        item_id, drop_weight = struct.unpack(cls._STRUCT_FORMAT, reward_bytes)

        return RelicDrop(item_id, drop_weight)

    def to_bytes(self) -> bytes:
        return struct.pack(self._STRUCT_FORMAT, self.item_id, self.drop_weight)

    @classmethod
    def from_dict(cls, data: dict) -> RelicDrop:
        return RelicDrop(**data)

@dataclass
class StarItem(Item):
    _NAME_LENGTH = 32

    _STRUCT_FORMAT = f"<{_NAME_LENGTH}s2HI20s"
    _STRUCT_LENGTH = struct.calcsize(_STRUCT_FORMAT)

    items: list[RelicDrop]
    unknown_1: int
    unknown_2: int

    @classmethod
    def from_bytes(cls, value_bytes: bytes) -> StarItem:
        struct_bytes = value_bytes[:cls._STRUCT_LENGTH]

        name_bytes, item_id, unknown_1, unknown_2, items_bytes = struct.unpack(cls._STRUCT_FORMAT, struct_bytes)

        original_name = name_bytes.decode(encoding="shift-jis")
        name = extract_name_from_bytes(name_bytes)
        items = cls.parse_items_bytes(items_bytes)

        return StarItem(item_id, name, original_name, items, unknown_1, unknown_2)

    def to_bytes(self) -> bytes:
        name_bytes = self.get_name_bytes(self._NAME_LENGTH)
        items_bytes = self.item_bytes()

        values = name_bytes, self.item_id, self.unknown_1, self.unknown_2, items_bytes

        return struct.pack(self._STRUCT_FORMAT, *values)

    @classmethod
    def parse_items_bytes(cls, items_bytes) -> list[RelicDrop]:
        relic_drops = [RelicDrop.from_bytes(bytes(chunk)) for chunk in batched(items_bytes, RelicDrop._STRUCT_SIZE)]

        return [drop for drop in relic_drops if drop.item_id > 0]

    def item_bytes(self) -> bytes:
        items = self.items.copy()
        items_to_pad = 5 - len(self.items)

        for i in range(items_to_pad):
            empty_item = RelicDrop(0, 0)
            items.append(empty_item)

        item_bytes = [item.to_bytes() for item in items]

        return b"".join(item_bytes)

    @classmethod
    def from_dict(cls, data: dict) -> StarItem:
        item_id = data["item_id"]
        name = data["name"]
        original_name = data["original_name"]

        relic_drops = [RelicDrop.from_dict(item) for item in data["items"]]
        unknown_1 = data["unknown_1"]
        unknown_2 = data["unknown_2"]

        return StarItem(item_id, name, original_name, relic_drops, unknown_1, unknown_2)