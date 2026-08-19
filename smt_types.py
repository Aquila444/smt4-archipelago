from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SmtItemSource:
    location: str
    item_rewards: list[SmtItemReward]

    @classmethod
    def from_dict(cls, data: dict) -> SmtItemSource:
        location = data["location"]

        item_rewards_data = data["item_rewards"]
        item_rewards = [SmtItemReward.from_dict(item) for item in item_rewards_data]

        return SmtItemSource(location, item_rewards)


@dataclass
class SmtItemReward:
    item: SmtItem
    drop_weight: int
    count: int

    @classmethod
    def from_dict(cls, data: dict) -> SmtItemReward:
        drop_weight = data["drop_weight"]
        count = data["count"]

        item_data = data["item"]
        item = SmtItem.from_dict(item_data)

        return SmtItemReward(item, drop_weight, count)


@dataclass
class SmtItem:
    name: str
    archipelago_id: int
    game_id: int
    type: str
    classification: str

    @classmethod
    def from_dict(cls, data: dict) -> SmtItem:
        name = data["name"]
        archipelago_id = data["archipelago_id"]
        game_id = data["game_id"]
        type = data["type"]
        classification = data["classification"]

        return SmtItem(name, archipelago_id, game_id, type, classification)


@dataclass
class SmtRegion:
    name: str
    entrances: list[SmtEntrance]

    @classmethod
    def from_dict(cls, data: dict) -> SmtRegion:
        name = data["name"]
        entrances = [SmtEntrance.from_dict(entry) for entry in data["entrances"]]

        return SmtRegion(name, entrances)


@dataclass
class SmtEntrance:
    region: str
    requirements: list[str]

    @classmethod
    def from_dict(cls, data: dict) -> SmtEntrance:
        region = data["region"]
        requirements = data["requirements"]

        return SmtEntrance(region, requirements)


@dataclass
class SmtLocation:
    name: str
    archipelago_id: int
    game_id: int
    region: str
    type: str
    subtype: str
    flag: str

    @classmethod
    def from_dict(cls, data: dict) -> SmtLocation:
        name = data["name"]
        archipelago_id = data["archipelago_id"]
        game_id = data["game_id"]
        region = data["region"]
        type = data["type"]
        subtype = data["subtype"]
        flag = data["flag"]

        return SmtLocation(name, archipelago_id, game_id, region, type, subtype, flag)
