from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum
from itertools import batched

import jsonpickle

from ..demons.demons import demon_table
from ..items.item_table import ItemTable
from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table
from ...utils.utils import extract_string_from_bytes

TBB_FILE_PATH = "event/quest"
ROM_FILE_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
DATA_FILE_LOCATION = DATA_DIR / "quests.json"


class RewardType(IntEnum):
    ITEM = 1
    MACCA = 3
    ITEM_SET = 4


class QuestCategory(IntEnum):
    MAIN = 1
    SUB = 2


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


@dataclass
class ItemObjective:
    item_id: int
    count: int


@dataclass
class EnemyObjective:
    enemy_id: int
    enemy_name: str
    count: int


@dataclass
class ItemReward:
    item_id: int
    count: int


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


@dataclass
class MaccaReward:
    amount: int


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

        name = extract_string_from_bytes(name_bytes)

        rewards = [ItemSetDrop.from_bytes(bytes(chunk)) for chunk in batched(reward_bytes, ItemSetDrop._STRUCT_SIZE)]
        non_empty_rewards = [reward for reward in rewards if reward.item_id > 0]

        return ItemSetReward(name, non_empty_rewards)


@dataclass
class QuestTable:
    quests: list[Quest]

    @classmethod
    def load_from_rom(cls) -> QuestTable:
        main_quest_file = ROM_FILE_LOCATION / "QuestData.tbb"
        sub_quest_file = ROM_FILE_LOCATION / "SubQuestData.tbb"

        main_quest_table = Table.from_file(main_quest_file)
        sub_quest_table = Table.from_file(sub_quest_file)

        main_quest_data = main_quest_table.tables[0].get_data()
        sub_quest_data = sub_quest_table.tables[0].get_data()

        item_set_data = sub_quest_table.tables[1].get_data()
        item_sets = {index: ItemSetReward.from_bytes(entry) for index, entry in enumerate(item_set_data)}

        main_quests = [Quest.from_bytes(quest_bytes, QuestCategory.MAIN, item_sets) for quest_bytes in main_quest_data]
        sub_quests = [Quest.from_bytes(quest_bytes, QuestCategory.SUB, item_sets) for quest_bytes in sub_quest_data]

        quests = main_quests + sub_quests

        return QuestTable(quests)

    @classmethod
    def load_from_json(cls) -> ItemTable | None:
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


@dataclass
class Quest:
    _NAME_LENGTH = 176
    _QUEST_GIVER_LENGTH = 48
    _DESCRIPTION_LENGTH = 64

    _STRUCT_FORMAT = f"3HBB{_NAME_LENGTH}s{_QUEST_GIVER_LENGTH}s{_DESCRIPTION_LENGTH}s16s16sH6xI5H2x9H46s4H6x3H"
    _STRUCT_SIZE = struct.calcsize(_STRUCT_FORMAT)

    quest_id: int
    quest_category: QuestCategory
    quest_type: QuestType
    name: str
    quest_giver: str
    description: str
    sort_order: int
    start_event: str
    end_event: str
    star_rating: int
    reward_type: RewardType
    reward: ItemReward | MaccaReward | ItemSetReward | None
    objective: ItemObjective | EnemyObjective | None
    quest_requirements: list[int]
    unknown_1: bytes
    unknown_2: bytes
    unknown_3: bytes
    unknown_4: bytes
    unknown_5: bytes
    unknown_6: bytes
    unknown_7: bytes
    unknown_8: bytes
    unknown_9: bytes
    unknown_10: bytes
    unknown_11: bytes
    unknown_12: bytes
    unknown_13: bytes
    unknown_14: bytes
    unknown_15: bytes
    unknown_16: bytes

    @classmethod
    def from_bytes(cls, quest_bytes: bytes, quest_category: QuestCategory,
                   item_sets: dict[int, ItemSetReward]) -> Quest:
        struct_bytes = quest_bytes[:cls._STRUCT_SIZE]

        (
            quest_id, unknown_1, sort_order, quest_type_value, unknown_2, name_bytes, quest_giver_bytes,
            description_bytes,
            start_event_bytes, end_event_bytes,
            unknown_3, star_rating, reward_type_value, item_reward_id, reward_amount,
            unknown_4, unknown_5, unknown_6, item_set_reward_value,
            unknown_7, unknown_8, unknown_9, unknown_10, unknown_11, objective_id, objective_amount,
            unknown_12,
            quest_requirement_1, quest_requirement_2, quest_requirement_3,
            unknown_13, unknown_14, unknown_15, unknown_16
        ) = struct.unpack(cls._STRUCT_FORMAT, struct_bytes)

        name = extract_string_from_bytes(name_bytes)
        quest_giver = extract_string_from_bytes(quest_giver_bytes)
        description = extract_string_from_bytes(description_bytes)

        start_event = extract_string_from_bytes(start_event_bytes)
        end_event = extract_string_from_bytes(end_event_bytes)

        quest_type = QuestType(quest_type_value)
        reward_type = RewardType(reward_type_value)

        objective = None
        if objective_id == 0 or objective_amount == 0:
            objective = None
        elif quest_type == quest_type.DELIVERY:
            objective = ItemObjective(objective_id, objective_amount)
        elif quest_type == quest_type.SLAY:
            target_demon = demon_table.get_demon(objective_id)
            objective = EnemyObjective(target_demon.demon_id, target_demon.name, objective_amount)

        if reward_type == RewardType.ITEM:
            reward = ItemReward(item_reward_id, reward_amount)
        elif reward_type == RewardType.MACCA:
            reward = MaccaReward(reward_amount)
        else:
            reward = item_sets.get(item_reward_id)

        quest_requirements = [quest_requirement_1, quest_requirement_2, quest_requirement_3]
        quest_requirements_filtered = [requirement for requirement in quest_requirements if requirement != 0]

        return Quest(
            quest_id, quest_category, quest_type, name, quest_giver, description,
            sort_order, start_event, end_event, star_rating, reward_type,
            reward, objective, quest_requirements_filtered,
            unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8,
            unknown_9, unknown_10, unknown_11, unknown_12, unknown_13, unknown_14, unknown_15, unknown_16
        )


try:
    quest_table = QuestTable.load_from_json()
except Exception as e:
    print(e)


def main():
    print()


if __name__ == "__main__":
    main()
