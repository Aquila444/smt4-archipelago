from __future__ import annotations

from dataclasses import dataclass

import jsonpickle

from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table
from ...utils.utils import extract_string_from_bytes

TBB_FILE_PATH = "battle/NKMSortIndex.tbb"
ROM_FILE_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
DATA_FILE_LOCATION = DATA_DIR / "demons.json"


@dataclass
class DemonRace:
    race_id: int
    name: str

    @classmethod
    def from_bytes(cls, race_bytes: bytes, index: int):
        name = extract_string_from_bytes(race_bytes)

        return DemonRace(index, name)


@dataclass
class Demon:
    demon_id: int
    name: str

    @classmethod
    def from_bytes(cls, demon_bytes: bytes, index: int) -> Demon:
        name = extract_string_from_bytes(demon_bytes)

        return Demon(index, name)


@dataclass
class DemonTable:
    demons: dict[int | str, Demon]

    @classmethod
    def load_from_rom(cls) -> DemonTable:
        table = Table.from_file(ROM_FILE_LOCATION)

        races_data = table.tables[0].get_data()
        demon_data = table.tables[1].get_data()

        races = {index: DemonRace.from_bytes(race_bytes, index) for index, race_bytes in enumerate(races_data)}
        demons = {index: Demon.from_bytes(entry, index) for index, entry in enumerate(demon_data)}

        return DemonTable(demons)

    @classmethod
    def load_from_json(cls) -> DemonTable | None:
        try:
            with open(DATA_FILE_LOCATION, encoding="shift_jis") as json_file:
                json_string = json_file.read()

                return jsonpickle.decode(json_string)
        except FileNotFoundError:
            return None

    def export(self):
        with open(DATA_FILE_LOCATION, "w+", encoding="shift_jis") as json_file:
            encoded_json = jsonpickle.encode(self, json_file)
            json_file.write(encoded_json)

    def get_demon(self, demon_id: int) -> Demon | None:
        demon = self.demons.get(demon_id)

        if demon is None:
            str_index = str(demon_id)
            return self.demons.get(str_index)
        else:
            return demon


try:
    demon_table = DemonTable.load_from_json()
except Exception as e:
    print(e)


def main():
    print()


if __name__ == '__main__':
    main()
