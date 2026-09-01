from __future__ import annotations

from dataclasses import dataclass

import orjson

from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table
from ...utils.utils import extract_name_from_bytes, load_data_file_as_json

TBB_FILE_PATH = "battle/NKMSortIndex.tbb"
ROM_FILE_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
DATA_FILE_NAME = "demons.json"
DATA_FILE_LOCATION = DATA_DIR / DATA_FILE_NAME


@dataclass
class DemonRace:
    race_id: int
    name: str

    @classmethod
    def from_bytes(cls, race_bytes: bytes, index: int):
        name = extract_name_from_bytes(race_bytes)

        return DemonRace(index, name)


@dataclass
class Demon:
    demon_id: int
    name: str

    @classmethod
    def from_bytes(cls, demon_bytes: bytes, index: int) -> Demon:
        name = extract_name_from_bytes(demon_bytes)

        return Demon(index, name)

    @classmethod
    def from_dict(cls, data: dict) -> Demon:
        return Demon(**data)


@dataclass
class DemonTable:
    demons: dict[str, Demon]

    @classmethod
    def load_from_rom(cls) -> DemonTable:
        table = Table.from_file(ROM_FILE_LOCATION)

        races_data = table.tables[0].get_data()
        demon_data = table.tables[1].get_data()

        races = {index: DemonRace.from_bytes(race_bytes, index) for index, race_bytes in enumerate(races_data)}
        demons = {str(index): Demon.from_bytes(entry, index) for index, entry in enumerate(demon_data)}

        return DemonTable(demons)

    @classmethod
    def load_from_json(cls) -> DemonTable:
        data = load_data_file_as_json(DATA_FILE_NAME, encoding="shift_jis")

        demons = data["demons"]
        mapped_demons = {key: Demon.from_dict(value) for key, value in demons.items()}

        return DemonTable(mapped_demons)

    def export(self):
        with open(DATA_FILE_LOCATION, "wb+") as json_file:
            encoded_json = orjson.dumps(self)
            json_file.write(encoded_json)

    def get_demon(self, demon_id: int) -> Demon:
        return self.demons[str(demon_id)]


demon_table = None
try:
    demon_table = DemonTable.load_from_json()
except Exception as e:
    print(e)


def main():
    print()


if __name__ == '__main__':
    main()
