from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table

TBB_FILE_PATH = "item/ItemHelpMess.tbb"
ROM_FILE_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
DATA_FILE_NAME = "items.json"
DATA_FILE_LOCATION = DATA_DIR / DATA_FILE_NAME


@dataclass
class ItemDescriptionTable:
    items: list[bytes]

    def __init__(self, data: list[bytes], tbb_table: Table) -> None:
        self.items = data
        self.tbb_table = tbb_table

    @classmethod
    def from_file(cls, romfs_path) -> ItemDescriptionTable:
        tbb_file_path = romfs_path / TBB_FILE_PATH
        table = Table.from_file(tbb_file_path)

        data = table.tables[0].get_data()

        return ItemDescriptionTable(data, table)

    def to_file(self, romfs_path: Path) -> None:
        self._sync_state_to_tbb_table()

        tbb_file_path = romfs_path / TBB_FILE_PATH
        self.tbb_table.to_file(tbb_file_path)

    def _sync_state_to_tbb_table(self) -> None:
        table = self.tbb_table.tables[0]

        for index, item in enumerate(self.items):
            table.table_data.set_entry(index, item)
