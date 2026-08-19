from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .tbcr import TBCR
from .tbl import TBL


@dataclass
class Table:

    def __init__(self, tbcr: TBCR, tables: list[TBL]):
        self.tbcr = tbcr
        self.tables = tables

    @classmethod
    def from_file(cls, file_path) -> Table:
        with open(file_path, mode="rb") as tbb_file:
            file_bytes = tbb_file.read()

            return Table.from_bytes(file_bytes)

    @classmethod
    def from_bytes(cls, file_bytes: bytes) -> Table:
        tbcr = TBCR.from_bytes(file_bytes)

        pointers = tbcr.pointers.pointers
        tables = []
        for pointer in pointers:
            table_bytes = file_bytes[pointer:]

            table = TBL.from_bytes(table_bytes)
            tables.append(table)

        return Table(tbcr, tables)

    @classmethod
    def from_dict(cls, data: dict) -> Table:
        tbcr = TBCR.from_dict(data["tbcr"])
        tables = [TBL.from_dict(table_data) for table_data in data["tables"]]

        return Table(tbcr, tables)

    def to_file(self, file_path: str) -> None:
        output_file = Path(file_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        output_bytes = self.to_bytes()

        with open(file_path, mode="wb+") as tbb_file:
            tbb_file.write(output_bytes)

    def to_bytes(self) -> bytes:
        tbcr_bytes = self.tbcr.to_bytes(self.tables)
        table_bytes = b"".join([table.to_bytes() for table in self.tables])

        return tbcr_bytes + table_bytes

    def to_empty_table(self) -> Table:
        for table in self.tables:
            table.empty_table()

        self.tbcr.sync(self.tables)

        return self
