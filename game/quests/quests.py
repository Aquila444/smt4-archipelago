from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum
from itertools import batched

import orjson

from .objectives import QuestType, ItemObjective, EnemyObjective, Objective
from .rewards import ItemSetReward, RewardType, ItemReward, MaccaReward
from ...config import DATA_DIR, INPUT_ROMFS_DIR
from ...tbb.tbb import Table
from ...utils.utils import extract_string_from_bytes, load_data_file_as_json

TBB_FILE_PATH = "event/quest"
ROM_FILE_LOCATION = INPUT_ROMFS_DIR / TBB_FILE_PATH
DATA_FILE_NAME = "quests.json"
DATA_FILE_LOCATION = DATA_DIR / "quests.json"


class QuestCategory(IntEnum):
    MAIN = 1
    SUB = 2


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
    def load_from_json(cls) -> QuestTable:
        data = load_data_file_as_json(DATA_FILE_NAME, encoding="shift_jis")

        quests = [Quest.from_dict(entry) for entry in data]

        return QuestTable(quests)

    def export(self):
        with open(DATA_FILE_LOCATION, "wb+") as json_file:
            encoded_json = orjson.dumps(self)
            json_file.write(encoded_json)


@dataclass
class Quest:
    _NAME_LENGTH = 176
    _QUEST_GIVER_LENGTH = 48
    _DESCRIPTION_LENGTH = 64

    _STRUCT_FORMAT = f"3HBB{_NAME_LENGTH}s{_QUEST_GIVER_LENGTH}s{_DESCRIPTION_LENGTH}s16s16sH6xI5H2x6H48s6H6x3H"
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
    objectives: list[Objective]
    quest_requirements: list[int]
    unknown_1: int
    unknown_2: int
    unknown_3: int
    unknown_4: int
    unknown_5: int
    unknown_6: int
    unknown_7: int
    unknown_8: int
    unknown_9: int
    unknown_10: int
    unknown_11: int
    unknown_12: int
    unknown_13: int
    unknown_14: int
    unknown_15: int
    unknown_16: int

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
            unknown_7, unknown_8, unknown_9, unknown_10, objectives_bytes,
            unknown_11, unknown_12,
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

        objectives = [Objective.from_bytes(bytes(entry)) for entry in batched(objectives_bytes, Objective.STRUCT_SIZE)]
        non_empty_objectives = [objective for objective in objectives if objective is not None]

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
            reward, non_empty_objectives, quest_requirements_filtered,
            unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8,
            unknown_9, unknown_10, unknown_11, unknown_12, unknown_13, unknown_14, unknown_15, unknown_16
        )

    @classmethod
    def from_dict(cls, data: dict) -> Quest:
        quest_id = data["quest_id"]
        quest_category = QuestCategory(data["quest_category"])
        quest_type = QuestType(data["quest_type"])
        name = data["name"]
        quest_giver = data["quest_giver"]
        description = data["description"]
        sort_order = data["sort_order"]
        start_event = data["start_event"]
        end_event = data["end_event"]
        star_rating = data["star_rating"]

        reward_type = RewardType(data["reward_type"])
        reward_data = data["reward"]
        if reward_type == RewardType.ITEM:
            reward = ItemReward.from_dict(reward_data)
        elif reward_type == RewardType.MACCA:
            reward = MaccaReward.from_dict(reward_data)
        else:
            reward = ItemSetReward.from_dict(reward_data)

        objective_data = data["objective"]
        if quest_type == QuestType.DELIVERY:
            objective = ItemObjective.from_dict(objective_data)
        elif quest_type == QuestType.SLAY:
            objective = EnemyObjective.from_dict(objective_data)
        else:
            objective = None

        quest_requirements = data["quest_requirements"]

        unknown_1 = data["unknown_1"]
        unknown_2 = data["unknown_2"]
        unknown_3 = data["unknown_3"]
        unknown_4 = data["unknown_4"]
        unknown_5 = data["unknown_5"]
        unknown_6 = data["unknown_6"]
        unknown_7 = data["unknown_7"]
        unknown_8 = data["unknown_8"]
        unknown_9 = data["unknown_9"]
        unknown_10 = data["unknown_10"]
        unknown_11 = data["unknown_11"]
        unknown_12 = data["unknown_12"]
        unknown_13 = data["unknown_13"]
        unknown_14 = data["unknown_14"]
        unknown_15 = data["unknown_15"]

        return Quest(
            quest_id, quest_category, quest_type, name, quest_giver, description, sort_order, start_event, end_event,
            star_rating, reward_type, reward, objective, quest_requirements,
            unknown_1, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, unknown_9,
            unknown_10, unknown_11, unknown_12, unknown_13, unknown_14, unknown_15
        )


try:
    quest_table = QuestTable.load_from_json()
except Exception as e:
    print(e)


def main():
    print()


if __name__ == "__main__":
    main()
