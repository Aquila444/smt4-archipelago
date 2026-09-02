from __future__ import annotations

from random import Random
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification
from .smt_types import SmtItem, SmtItemSource, SmtItemReward
from .utils.utils import load_data_file_as_json

if TYPE_CHECKING:
    from .world import SMT4World


def load_items() -> list[SmtItem]:
    item_file_name = "ap-items.json"
    data = load_data_file_as_json(item_file_name)

    return [SmtItem.from_dict(entry) for entry in data]


def load_item_sources():
    item_source_file_name = "ap-item-sources.json"
    data = load_data_file_as_json(item_source_file_name)

    return [SmtItemSource.from_dict(entry) for entry in data]


def create_item_with_correct_classification(world: SMT4World, name: str) -> Item:
    item = item_name_to_item[name]
    classification = ItemClassification[item.classification]

    return Item(name, classification, item.archipelago_id, world.player)


def create_all_items(world: SMT4World) -> None:
    locations = world.get_locations()
    location_names = {location.name for location in locations}

    for item_source in item_sources:
        if item_source.location in location_names:
            item_reward = pick_reward(item_source, world.random)

            item = create_item_with_correct_classification(world, item_reward.item.name)
            world.multiworld.itempool.append(item)

    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    world.multiworld.itempool += [world.create_filler() for _ in range(number_of_unfilled_locations)]


def pick_reward(item_source: SmtItemSource, rng: Random) -> SmtItemReward:
    rewards = item_source.item_rewards
    weights = [reward.drop_weight for reward in rewards]

    return rng.choices(rewards, weights=weights, k=1)[0]


def get_random_filler_item_name(world: SMT4World) -> str:
    return "Medicine"


try:
    items = load_items()
    item_sources = load_item_sources()
except Exception:
    items = []
    item_sources = []

item_name_to_id = {item.name: item.archipelago_id for item in items}
item_name_to_item = {item.name: item for item in items}
