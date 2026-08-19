from __future__ import annotations

import io
import struct
from dataclasses import dataclass

from .tbl import TBL
from ..utils.utils import pad_bytes


@dataclass
class TBCRHeader:
    MAGIC_STRING = b"TBCR"
    STRUCT_FORMAT = "<4sII"
    HEADER_LENGTH = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, header_size: int, num_sections: int):
        self.header_size = header_size
        self.num_sections = num_sections

    @classmethod
    def from_bytes(cls, header_bytes: bytes) -> TBCRHeader:
        _, header_size, num_sections = struct.unpack(TBCRHeader.STRUCT_FORMAT, header_bytes)

        return TBCRHeader(header_size, num_sections)

    def to_bytes(self) -> bytes:
        return struct.pack(TBCRHeader.STRUCT_FORMAT, TBCRHeader.MAGIC_STRING, self.header_size, self.num_sections)

    @classmethod
    def from_dict(cls, data: dict) -> TBCRHeader:
        header_size = data["header_size"]
        num_sections = data["num_sections"]

        return TBCRHeader(header_size, num_sections)


@dataclass
class TBCRPointers:
    POINTER_SIZE = 4

    def __init__(self, pointers: list[int], header_size: int):
        self.pointers = pointers
        self.header_size = header_size

    @classmethod
    def from_bytes(cls, pointer_bytes: bytes, header_size: int) -> TBCRPointers:
        num_sections = int(len(pointer_bytes) / TBCRPointers.POINTER_SIZE)

        struct_format = f"<{num_sections}I"

        pointer_values = struct.unpack(struct_format, pointer_bytes)
        pointers = [int(pointer + header_size) for pointer in pointer_values]

        return TBCRPointers(pointers, header_size)

    def to_bytes(self, tables: list[TBL]) -> bytes:
        self._update_pointers(tables)
        num_sections = len(self.pointers)

        struct_format = f"<{num_sections}I"

        return struct.pack(struct_format, *self.pointers)

    def _update_pointers(self, tables: list[TBL]):
        cursor = 0

        for index, table in enumerate(tables):
            table_size = len(table.to_bytes())

            self.pointers[index] = cursor

            cursor += table_size

    @classmethod
    def from_dict(cls, data: dict) -> TBCRPointers:
        pointers = data["pointers"]
        header_size = data["header_size"]

        return TBCRPointers(pointers, header_size)


@dataclass
class TBCR:

    def __init__(self, header: TBCRHeader, pointers: TBCRPointers):
        self.header = header
        self.pointers = pointers

    @classmethod
    def from_bytes(cls, tbb_bytes: bytes) -> TBCR:
        reader = io.BytesIO(tbb_bytes)

        header_bytes = reader.read(TBCRHeader.HEADER_LENGTH)
        header = TBCRHeader.from_bytes(header_bytes)

        num_sections = header.num_sections
        pointer_section_length = num_sections * TBCRPointers.POINTER_SIZE
        pointer_bytes = reader.read(pointer_section_length)
        pointers = TBCRPointers.from_bytes(pointer_bytes, header.header_size)

        return TBCR(header, pointers)

    def to_bytes(self, tables: list[TBL]) -> bytes:
        header_bytes = self.header.to_bytes()
        pointer_bytes = self.pointers.to_bytes(tables)

        tbcr_bytes = header_bytes + pointer_bytes
        desired_header_size = self.header.header_size

        padded_header_bytes = pad_bytes(tbcr_bytes, desired_header_size)

        return padded_header_bytes

    def sync(self, tables: list[TBL]):
        self.pointers._update_pointers(tables)

    @classmethod
    def from_dict(cls, data: dict) -> TBCR:
        header = TBCRHeader.from_dict(data["header"])
        pointers = TBCRPointers.from_dict(data["pointers"])

        return TBCR(header, pointers)
