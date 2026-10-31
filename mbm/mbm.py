from __future__ import annotations

import struct
from dataclasses import dataclass
from itertools import batched
from pathlib import Path


@dataclass
class MBM:
    header: MBMHeader
    data: dict[int, bytes | None]

    @classmethod
    def from_file(cls, file_path) -> MBM:
        with open(file_path, mode="rb") as mbm_file:
            file_bytes = mbm_file.read()

            return MBM.from_bytes(file_bytes)

    @classmethod
    def from_bytes(cls, data_bytes: bytes) -> MBM:
        header = MBMHeader.from_bytes(data_bytes)

        index_start = header.header_size
        index_data = data_bytes[index_start:]
        index = MBMIndex.from_bytes(index_data, header.num_entries)

        data = MBMData.from_bytes(data_bytes, index)

        return MBM(header, data.values)

    def to_bytes(self) -> bytes:
        num_items = len([value for value in self.data.values() if value is not None])

        header_bytes = self.header.to_bytes(num_items)
        data = MBMData(self.data)
        data_bytes = data.to_bytes()
        index = MBMIndex.from_data(data, self.header.header_size)
        index_bytes = index.to_bytes()

        return header_bytes + index_bytes + data_bytes

    def to_file(self, file_path: Path) -> None:
        file_path.parent.mkdir(exist_ok=True, parents=True)

        output_bytes = self.to_bytes()

        with open(file_path, mode="wb+") as tbb_file:
            tbb_file.write(output_bytes)


@dataclass
class MBMHeader:
    MAGIC_STRING = b"MSG2"
    STRUCT_FORMAT = "<4x4s4I8x"
    STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)

    unknown_1: int
    table_size: int
    num_entries: int
    header_size: int

    @classmethod
    def from_bytes(cls, data: bytes) -> MBMHeader:
        struct_data = data[:cls.STRUCT_SIZE]
        _, unknown_1, table_size, num_entries, header_size = struct.unpack(cls.STRUCT_FORMAT, struct_data)

        return MBMHeader(unknown_1, table_size, num_entries, header_size)

    def to_bytes(self, num_items: int) -> bytes:
        return struct.pack(self.STRUCT_FORMAT, MBMHeader.MAGIC_STRING, self.unknown_1, self.table_size,
                           num_items, self.header_size)


@dataclass
class MBMIndex:
    items: list[MBMIndexItem]

    @classmethod
    def from_bytes(cls, data: bytes, num_entries: int) -> MBMIndex:
        entry_size = MBMIndexItem.STRUCT_SIZE

        chunks = [bytes(chunk) for chunk in batched(data, entry_size)]
        items = []
        found_entries = 0
        true_index = 0
        while found_entries < num_entries:
            chunk = chunks[true_index]
            entry = MBMIndexItem.from_bytes(chunk, true_index)

            if entry.index > 0:
                found_entries = found_entries + 1

            items.append(entry)

            true_index = true_index + 1

        return MBMIndex(items)

    def to_bytes(self) -> bytes:
        return b"".join([item.to_bytes() for item in self.items])

    @classmethod
    def from_data(cls, data: MBMData, header_size: int) -> MBMIndex:
        index_size = len(data.values) * MBMIndexItem.STRUCT_SIZE
        index_items = []

        offset = header_size + index_size
        for key, value in data.values.items():
            if value is None:
                value_size = 0
                index_item = MBMIndexItem(0, key, value_size, 0)
            else:
                value_size = len(value)
                index_item = MBMIndexItem(key, key, value_size, offset)

            index_items.append(index_item)
            offset = offset + value_size

        return MBMIndex(index_items)


@dataclass
class MBMIndexItem:
    STRUCT_FORMAT = "<3I4x"
    STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)

    index: int
    true_index: int
    value_size: int
    pointer: int

    @classmethod
    def from_bytes(cls, data: bytes, true_index: int) -> MBMIndexItem:
        index, value_size, pointer = struct.unpack(cls.STRUCT_FORMAT, data)

        return MBMIndexItem(index, true_index, value_size, pointer)

    def to_bytes(self) -> bytes:
        return struct.pack(self.STRUCT_FORMAT, self.index, self.value_size, self.pointer)


@dataclass
class MBMData:
    values: dict[int, bytes | None]

    def __init__(self, values: dict[int, bytes | None]):
        terminated_values = {key: self.terminate_item(value) for key, value in values.items()}
        self.values = terminated_values

    @classmethod
    def from_bytes(cls, data: bytes, index_table: MBMIndex) -> MBMData:
        items = {entry.true_index: cls.parse_item(data, entry) for entry in index_table.items}

        return MBMData(items)

    @classmethod
    def parse_item(cls, data: bytes, index_item: MBMIndexItem) -> bytes | None:
        size = index_item.value_size
        if size == 0:
            return None

        start_offset = index_item.pointer
        end_offset = index_item.pointer + size

        return data[start_offset:end_offset]

    def to_bytes(self) -> bytes:
        non_empty_items = [item for item in self.values.values() if item is not None]

        return b"".join(non_empty_items)

    @classmethod
    def terminate_item(cls, item: bytes | None) -> bytes | None:
        if item is None:
            return None

        return item if item.endswith(b"\xFF\xFF") else item + b"\xFF\xFF"
