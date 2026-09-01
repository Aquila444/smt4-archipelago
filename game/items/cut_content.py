from __future__ import annotations

import struct
from dataclasses import dataclass

from .item import Item
from ...utils.utils import extract_name_from_bytes


@dataclass
class CutContentItem(Item):

    _NAME_LENGTH = 32

    _STRUCT_FORMAT = f"<{_NAME_LENGTH}s6H"
    _STRUCT_LENGTH = struct.calcsize(_STRUCT_FORMAT)

    unknown: list[int]

    @classmethod
    def from_bytes(cls, value_bytes: bytes) -> CutContentItem:
        struct_bytes = value_bytes[:cls._STRUCT_LENGTH]

        name_bytes, item_id, *unknown = struct.unpack(cls._STRUCT_FORMAT, struct_bytes)

        original_name = name_bytes.decode(encoding="shift-jis")
        name = extract_name_from_bytes(name_bytes)

        return CutContentItem(item_id, name, original_name, unknown)

    def to_bytes(self) -> bytes:
        name_bytes = self.get_name_bytes(self._NAME_LENGTH)

        values = name_bytes, self.item_id, *self.unknown

        return struct.pack(self._STRUCT_FORMAT, *values)

    @classmethod
    def from_dict(cls, data: dict) -> CutContentItem:
        return CutContentItem(**data)