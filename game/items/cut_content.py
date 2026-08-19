from __future__ import annotations

import struct
from dataclasses import dataclass

from .item import Item
from ...utils.utils import extract_string_from_bytes


@dataclass
class CutContentItem(Item):
    _NAME_LENGTH = 32

    _STRUCT_FORMAT = f"<{_NAME_LENGTH}sH10s"
    _STRUCT_LENGTH = struct.calcsize(_STRUCT_FORMAT)

    unknown_1: bytes

    @classmethod
    def from_bytes(cls, value_bytes: bytes) -> CutContentItem:
        struct_bytes = value_bytes[:cls._STRUCT_LENGTH]

        name_bytes, item_id, unknown_1 = struct.unpack(cls._STRUCT_FORMAT, struct_bytes)

        name = extract_string_from_bytes(name_bytes)

        return CutContentItem(item_id, name, name_bytes, unknown_1)

    def to_bytes(self) -> bytes:
        name_bytes = self.get_name_bytes(self._NAME_LENGTH)

        values = name_bytes, self.item_id, self.unknown_1

        return struct.pack(self._STRUCT_FORMAT, *values)
