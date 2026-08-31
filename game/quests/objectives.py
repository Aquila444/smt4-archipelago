from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum


class QuestType(IntEnum):
    DELIVERY = 0
    SLAY = 1
    FIND = 2
    FUSION = 3
    BRING = 4
    ESCORT = 5
    TRAINING = 6
    UNUSED_1 = 7
    DLC = 8
    DLC_2 = 9
    UNUSED_2 = 10
    UNUSED_3 = 11


class ObjectiveType(IntEnum):
    NONE = 0
    ITEM = 1
    SLAY = 2
    UNUSED = 7


@dataclass
class Objective:
    STRUCT_FORMAT = "<2HI"
    STRUCT_SIZE = struct.calcsize(STRUCT_FORMAT)

    objective_type: ObjectiveType

    @classmethod
    def from_bytes(cls, data: bytes) -> Objective | None:
        objective_type_value, objective_id, count = struct.unpack(cls.STRUCT_FORMAT, data)

        objective_type = ObjectiveType(objective_type_value)

        if objective_type == ObjectiveType.ITEM:
            return ItemObjective(objective_type, objective_id, count)
        elif objective_type == ObjectiveType.SLAY:
            return EnemyObjective(objective_type, objective_id, count)
        return None


@dataclass
class ItemObjective(Objective):
    item_id: int
    count: int

    @classmethod
    def from_dict(cls, data: dict) -> ItemObjective:
        return ItemObjective(**data)


@dataclass
class EnemyObjective(Objective):
    enemy_id: int
    count: int

    @classmethod
    def from_dict(cls, data: dict) -> EnemyObjective:
        return EnemyObjective(**data)
