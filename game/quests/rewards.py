from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum
from itertools import batched

from ...utils.utils import extract_name_from_bytes


class RewardType(IntEnum):
    ITEM = 1
    MACCA = 3
    ITEM_SET = 4


@dataclass
class ItemReward:
    item_id: int
    count: int

    @classmethod
    def from_dict(cls, data: dict) -> ItemReward:
        return ItemReward(**data)


@dataclass
class MaccaReward:
    amount: int

    @classmethod
    def from_dict(cls, data: dict) -> MaccaReward:
        return MaccaReward(**data)


@dataclass
class ItemSetDrop:
    _STRUCT_FORMAT = f"2H"
    _STRUCT_SIZE = struct.calcsize(_STRUCT_FORMAT)

    item_id: int
    drop_weight: int

    @classmethod
    def from_bytes(cls, reward_bytes: bytes) -> ItemSetDrop:
        item_id, drop_weight = struct.unpack(cls._STRUCT_FORMAT, reward_bytes)

        return ItemSetDrop(item_id, drop_weight)

    @classmethod
    def from_dict(cls, data: dict) -> ItemSetDrop:
        return ItemSetDrop(**data)


@dataclass
class ItemSetReward:
    _NAME_LENGTH = 48
    _REWARD_SECTION_LENGTH = 32
    _STRUCT_FORMAT = f"{_NAME_LENGTH}s{_REWARD_SECTION_LENGTH}s"
    _STRUCT_SIZE = struct.calcsize(_STRUCT_FORMAT)

    name: str
    rewards: list[ItemSetDrop]

    @classmethod
    def from_bytes(cls, item_set_bytes: bytes):
        struct_bytes = item_set_bytes[:cls._STRUCT_SIZE]

        name_bytes, reward_bytes = struct.unpack(cls._STRUCT_FORMAT, struct_bytes)

        name = extract_name_from_bytes(name_bytes)

        rewards = [ItemSetDrop.from_bytes(bytes(chunk)) for chunk in batched(reward_bytes, ItemSetDrop._STRUCT_SIZE)]
        non_empty_rewards = [reward for reward in rewards if reward.item_id > 0]

        return ItemSetReward(name, non_empty_rewards)

    @classmethod
    def from_dict(cls, data: dict) -> ItemSetReward:
        name = data["name"]
        rewards = [ItemSetDrop.from_dict(entry) for entry in data["rewards"]]

        return ItemSetReward(name, rewards)
