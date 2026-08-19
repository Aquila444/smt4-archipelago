from __future__ import annotations

import struct
from dataclasses import dataclass
from itertools import batched

import orjson

from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table
from ...utils.utils import pad_bytes, load_data_file, load_data_file_as_json

ROM_FILE_LOCATION = INPUT_ROMFS_DIR / "map/all/TakaraTable.tbb"
DATA_FILE_NAME = "loot-drops.json"
DATA_FILE_LOCATION = DATA_DIR / DATA_FILE_NAME


@dataclass
class LootTable:
    loot_indices: list[int]
    locations: dict[str, LootLocation]

    def __init__(self, loot_indices: list[int], locations: dict[str, LootLocation], tbb_table: Table):
        self.loot_indices = loot_indices
        self.locations = locations
        self.tbb_table = tbb_table.to_empty_table()

    @classmethod
    def load_from_rom(cls) -> LootTable:
        takara_table = Table.from_file(ROM_FILE_LOCATION)

        item_ids_file_name = "item-ids.txt"
        item_ids_data = load_data_file(item_ids_file_name, encoding="shift_jis")

        lines = item_ids_data.split("\n")[:-1]
        item_map = {int(entry.split(": ")[0]): entry.split(": ")[1].strip() for entry in lines}

        index_data = takara_table.tables[0].get_data()
        loot_indices = [int.from_bytes(entry, "little") for entry in index_data]

        location_data = takara_table.tables[1].get_data()
        loot_locations = [LootLocation.from_bytes(index, entry, item_map) for index, entry in enumerate(location_data)]
        loot_locations_map = {str(location.drop_id): location for location in loot_locations}

        return LootTable(loot_indices, loot_locations_map, takara_table)

    def to_file(self, takara_table_path: str) -> None:
        self._sync_state_to_tbb_table()

        self.tbb_table.to_file(takara_table_path)

    def _sync_state_to_tbb_table(self) -> None:
        index_table = self.tbb_table.tables[0]
        for value in self.loot_indices:
            byte_value = struct.pack("<I", value)
            index_table.add_entry(byte_value)

        location_table = self.tbb_table.tables[1]
        for index, location in self.locations.items():
            location_bytes = location.to_bytes()
            location_table.set_entry(int(index), location_bytes)

    @classmethod
    def load_from_json(cls) -> LootTable:
        data = load_data_file_as_json(DATA_FILE_NAME, encoding="shift_jis")

        loot_indices = data["loot_indices"]
        locations = data["locations"]
        table = Table.from_dict(data["tbb_table"])
        mapped_locations = {key: LootLocation.from_dict(value) for key, value in locations.items()}

        return LootTable(loot_indices, mapped_locations, table)

    def export(self):
        with open(DATA_FILE_LOCATION, "wb+") as json_file:
            encoded_json = orjson.dumps(self)
            json_file.write(encoded_json)

    def get_treasure(self, drop_id: int) -> LootLocation:
        return self.locations[str(drop_id)]


@dataclass
class LootLocation:
    MAX_ENTRIES = 4

    drop_id: int
    drops: list[LootDrop]

    @classmethod
    def from_bytes(cls, drop_id: int, location_bytes: bytes, item_map: dict[int, str]) -> LootLocation:
        drops = [LootDrop.from_bytes(bytes(chunk), item_map) for chunk in
                 batched(location_bytes, LootDrop._STRUCT_SIZE)]
        non_empty_drops = [drop for drop in drops if drop.item_id > 0]

        return LootLocation(drop_id, non_empty_drops)

    def to_bytes(self) -> bytes:
        bytes_per_entry = struct.calcsize(LootDrop._STRUCT_FORMAT)
        byte_length = self.MAX_ENTRIES * bytes_per_entry

        entry_bytes = b"".join([drop.to_bytes() for drop in self.drops])

        return pad_bytes(entry_bytes, byte_length)

    @classmethod
    def from_dict(cls, data: dict) -> LootLocation:
        drop_id = data["drop_id"]

        drops = data["drops"]
        mapped_drops = [LootDrop.from_dict(drop) for drop in drops]

        return LootLocation(drop_id, mapped_drops)


@dataclass
class LootDrop:
    _STRUCT_FORMAT = "<HB5x"
    _STRUCT_SIZE = struct.calcsize(_STRUCT_FORMAT)

    item_id: int
    drop_weight: int
    item_name: str

    @classmethod
    def from_bytes(cls, drop_bytes: bytes, item_map: dict[int, str]) -> LootDrop:
        item_id, drop_weight = struct.unpack(cls._STRUCT_FORMAT, drop_bytes)

        item_name = item_map.get(item_id)
        item_name = item_name if item_name else ""

        return LootDrop(item_id, drop_weight, item_name)

    def to_bytes(self) -> bytes:
        return struct.pack(self._STRUCT_FORMAT, self.item_id, self.drop_weight)

    @classmethod
    def from_dict(cls, data: dict) -> LootDrop:
        item_id = data["item_id"]
        drop_weight = data["drop_weight"]
        item_name = data["item_name"]

        return LootDrop(item_id, drop_weight, item_name)


try:
    loot_table = LootTable.load_from_json()
except Exception as e:
    print(e)


def main():
    print()


if __name__ == "__main__":
    main()
