from __future__ import annotations

import struct
from dataclasses import dataclass

from .item import Item
from ...utils.utils import extract_string_from_bytes


@dataclass
class KeyItem(Item):

    _NAME_LENGTH = 80

    _STRUCT_FORMAT = f"<{_NAME_LENGTH}s2HI"
    _STRUCT_LENGTH = struct.calcsize(_STRUCT_FORMAT)

    unknown_1: int
    unknown_2: int

    @classmethod
    def from_bytes(cls, value_bytes: bytes) -> KeyItem:
        struct_bytes = value_bytes[:cls._STRUCT_LENGTH]

        name_bytes, item_id, unknown_1, unknown_2 = struct.unpack(cls._STRUCT_FORMAT, struct_bytes)

        original_name = name_bytes.decode(encoding="shift-jis")
        name = extract_string_from_bytes(name_bytes)

        return KeyItem(item_id, name, original_name, unknown_1, unknown_2)

    def to_bytes(self) -> bytes:
        name_bytes = self.get_name_bytes(self._NAME_LENGTH)

        values = name_bytes, self.item_id, self.unknown_1, self.unknown_2

        return struct.pack(self._STRUCT_FORMAT, *values)

    @classmethod
    def from_dict(cls, data: dict) -> Item:
        return KeyItem(**data)