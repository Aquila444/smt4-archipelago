from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from settings import get_settings


@dataclass
class ReceivedSmtItem:
    index: int
    timestamp: int
    ap_item_id: int

    def to_csv(self) -> str:
        return ",".join(asdict(self).values())

    @classmethod
    def from_csv(cls, data: str) -> ReceivedSmtItem:
        values = data.split(",")

        index = int(values[0])
        timestamp = int(values[1])
        ap_item_id = int(values[2])

        return ReceivedSmtItem(index, timestamp, ap_item_id)


class ItemTracker:

    def __init__(self):
        self.items = ItemTracker.get_items_from_file()
        self.seen_indices = {item.index for item in self.items}

    def register_item(self, item: ReceivedSmtItem) -> None:
        if item.index not in self.seen_indices:
            self.items.append(item)
            ItemTracker.write_to_file(item)
            self.seen_indices.add(item.index)

    def get_items_after_time(self, timestamp: int) -> list[ReceivedSmtItem]:
        return [item for item in self.items if item.timestamp >= timestamp]

    @classmethod
    def write_to_file(cls, item: ReceivedSmtItem) -> None:
        item_string = item.to_csv()
        file_path = cls.get_data_file_path()

        with open(file_path, "w+") as file:
            file.write(item_string + "\n")
            file.flush()

    @classmethod
    def get_data_file_path(cls) -> Path:
        azahar_path = get_settings().smt4.azahar_path
        azahar_folder = Path(azahar_path).parent

        return azahar_folder / "client-data.csv"

    @classmethod
    def get_items_from_file(cls) -> list[ReceivedSmtItem]:
        file_path = ItemTracker.get_data_file_path()

        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
                return [ReceivedSmtItem.from_csv(line) for line in lines]
        except FileNotFoundError:
            return []
