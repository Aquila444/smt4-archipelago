from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ...utils.utils import create_name_entry


@dataclass
class Item(ABC):
    item_id: int
    name: str
    _name_bytes: bytes | None

    @classmethod
    @abstractmethod
    def from_bytes(cls, value_bytes: bytes) -> Item:
        pass

    @abstractmethod
    def to_bytes(self) -> bytes:
        pass

    def get_name_bytes(self, length: int) -> bytes:
        encoded_name = self.name.encode(encoding="shift_jis")

        if self._name_bytes is not None and self._name_bytes.startswith(encoded_name):
            return self._name_bytes
        else:
            return create_name_entry(self.name, length)
