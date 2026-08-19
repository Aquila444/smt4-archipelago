from __future__ import annotations

import io
import struct
from dataclasses import dataclass
from itertools import batched

from ..utils.utils import pad_bytes


@dataclass
class TBLHeader:
    MAGIC_STRING = b"TBL1"
    STRUCT_FORMAT = "<4sIII"
    HEADER_LENGTH = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, table_size: int, entry_size: int, entry_target_padding: int):
        self.table_size = table_size
        self.entry_size = entry_size
        self.entry_target_padding = entry_target_padding

    @classmethod
    def from_bytes(cls, header_bytes: bytes) -> TBLHeader:
        _, table_size, entry_size, entry_target_padding = struct.unpack(TBLHeader.STRUCT_FORMAT, header_bytes)

        return TBLHeader(table_size, entry_size, entry_target_padding)

    def to_bytes(self) -> bytes:
        return struct.pack(TBLHeader.STRUCT_FORMAT, TBLHeader.MAGIC_STRING, self.table_size, self.entry_size,
                           self.entry_target_padding)

    def _update_table_size(self, table_data: TBLData):
        num_entries = len(table_data)

        total_size = num_entries * self.entry_size

        self.table_size = total_size

    @classmethod
    def from_dict(cls, data: dict) -> TBLHeader:
        table_size = data["table_size"]
        entry_size = data["entry_size"]
        entry_target_padding = data["entry_target_padding"]

        return TBLHeader(table_size, entry_size, entry_target_padding)


@dataclass
class TBLData:

    def __init__(self, data: list[bytes], entry_size: int):
        self.data = data
        self.entry_size = entry_size

    @classmethod
    def from_bytes(cls, data_bytes: bytes, entry_size: int) -> TBLData:
        chunks = [bytes(chunk) for chunk in batched(data_bytes, entry_size)]

        return TBLData(chunks, entry_size)

    def to_bytes(self) -> bytes:
        return b"".join(self.data)

    def __len__(self):
        return len(self.data)

    def add_entry(self, entry: bytes) -> None:
        entry_size = self.entry_size
        padded_entry = pad_bytes(entry, entry_size)

        self.data.append(padded_entry)

    def set_entry(self, index: int, entry: bytes) -> None:
        entry_size = self.entry_size

        missing_indices = (index - len(self.data)) + 1
        if missing_indices > 0:
            for i in range(missing_indices):
                dud_entry = pad_bytes(b"", entry_size)
                self.data.append(dud_entry)

        padded_entry = pad_bytes(entry, entry_size)

        self.data[index] = padded_entry

    def clear(self):
        self.data = []

    @classmethod
    def from_dict(cls, data_dict: dict) -> TBLData:
        data = data_dict["data"]
        entry_size = data_dict["entry_size"]

        return TBLData(data, entry_size)


@dataclass
class TBL:

    def __init__(self, header: TBLHeader, table_data: TBLData):
        self.header = header
        self.table_data = table_data

    @classmethod
    def from_bytes(cls, table_bytes: bytes) -> TBL:
        reader = io.BytesIO(table_bytes)

        header_bytes = reader.read(TBLHeader.HEADER_LENGTH)
        header = TBLHeader.from_bytes(header_bytes)

        data_bytes = reader.read(header.table_size)
        table_data = TBLData.from_bytes(data_bytes, header.entry_size)

        return TBL(header, table_data)

    def to_bytes(self) -> bytes:
        self.sync()

        table_data_bytes = self.table_data.to_bytes()
        table_header_bytes = self.header.to_bytes()

        table_bytes = table_header_bytes + table_data_bytes

        table_byte_length = len(table_bytes)
        table_boundary_offset = table_byte_length % 16
        missing_bytes = 0 if table_boundary_offset == 0 else 16 - table_boundary_offset
        desired_byte_length = table_byte_length + missing_bytes

        return pad_bytes(table_bytes, desired_byte_length)

    def get_data(self) -> list[bytes]:
        return self.table_data.data

    def add_entry(self, entry: bytes) -> None:
        self.table_data.add_entry(entry)
        self.sync()

    def set_entry(self, index: int, entry: bytes) -> None:
        self.table_data.set_entry(index, entry)
        self.sync()

    def empty_table(self):
        self.table_data.clear()
        self.sync()

    def sync(self):
        self.header._update_table_size(self.table_data)

    @classmethod
    def from_dict(cls, data: dict) -> TBL:
        header = TBLHeader.from_dict(data["header"])
        table_data = TBLData.from_dict(data["table_data"])

        return TBL(header, table_data)
