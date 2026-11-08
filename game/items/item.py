from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ...utils.utils import create_name_entry


@dataclass
class Item(ABC):
    item_id: int
    name: str
    original_name: str | None
    description: str

    @classmethod
    @abstractmethod
    def from_bytes(cls, value_bytes: bytes, description_map: dict[int, str]) -> Item:
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

    def get_description_bytes(self) -> bytes:
        return self.description.encode(encoding="shift_jis", errors="surrogateescape")

    def get_name_bytes(self, length: int) -> bytes:
        if self.original_name is not None and self.original_name.startswith(self.name):
            return self.original_name.encode(encoding="shift_jis")
        else:
            return create_name_entry(self.name, length)
