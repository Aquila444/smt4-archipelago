import json
from dataclasses import asdict

from BaseClasses import ItemClassification
from ..config import DATA_DIR
from ..game.items.item_table import item_table, ItemType
from ..game.shops.shop_table import shop_table
from ..game.treasure.treasure import loot_table, LootDrop
from ..locations import locations
from ..smt_types import SmtItem, SmtItemReward, SmtItemSource
from ..utils.ids import IdGenerator

classification_map = {
    ItemType.KEY_ITEMS: ItemClassification.progression,
    ItemType.GEAR: ItemClassification.useful,
    ItemType.CONSUMABLES: ItemClassification.filler,
    ItemType.STARS: ItemClassification.filler,
    ItemType.RELICS: ItemClassification.filler,
    ItemType.CUT_CONTENT: ItemClassification.filler
}

id_generator = IdGenerator()


def sanitize_item_name(name: str) -> str:
    return name.replace("＃", "#")


def export_items() -> list[SmtItem]:
    unused_items = {"予備枠", "？？？", "削除", "これは未使用", "×魔導書（大）", "真サムライ制服", "未使用"}
    blacklisted_item_types = {ItemType.RELICS, ItemType.CUT_CONTENT}

    filtered_categories = [category for category in item_table.item_categories if
                           category.item_type not in blacklisted_item_types]

    inventory_index = 0
    smt_items = []
    for category in filtered_categories:
        item_type = category.item_type

        items = category.items
        for item in items:
            inventory_index += 1

            if item.name in unused_items:
                continue

            ap_id = id_generator.get_new_id()

            classification = classification_map[item_type]

            item_name = sanitize_item_name(item.name)
            smt_item = SmtItem(item_name, ap_id, item.item_id, inventory_index, item_type.name, classification.name,
                               count=1)
            smt_items.append(smt_item)

    item_output_path = DATA_DIR / "ap-items.json"
    with open(item_output_path, 'w+') as f:
        item_data = [asdict(item) for item in smt_items]
        json.dump(item_data, f)

    return smt_items


def get_treasure_item_sources(item_id_to_item: dict[int, SmtItem]) -> list[SmtItemSource]:
    item_sources = []

    for location in locations:
        if location.type == "treasure":
            treasure = loot_table.get_treasure(location.game_id)
            item_rewards = [map_drop(drop, item_id_to_item) for drop in treasure.drops]

            item_source = SmtItemSource(location.name, item_rewards)
            item_sources.append(item_source)

    return item_sources


def map_drop(drop: LootDrop, item_id_to_item: dict[int, SmtItem]) -> SmtItemReward:
    smt_item = item_id_to_item[drop.item_id]

    return SmtItemReward(smt_item, drop.drop_weight)


def export_item_sources(smt_items: list[SmtItem]):
    item_id_to_item = {item.game_id: item for item in smt_items}

    smt_item_sources = []

    for location in locations:
        item_rewards = []
        if location.type == "treasure":
            treasure = loot_table.get_treasure(location.game_id)
            item_rewards = [map_drop(drop, item_id_to_item) for drop in treasure.drops]
        elif location.type == "shop":
            shop_index, item_index = [int(value) for value in location.game_id.split("-")]
            shop_item = shop_table.get_shop_item(shop_index, item_index)
            smt_item = item_id_to_item[shop_item.item_id]
            smt_item_reward = SmtItemReward(smt_item, drop_weight=100)
            item_rewards = [smt_item_reward]

        if len(item_rewards) > 0:
            item_source = SmtItemSource(location.name, item_rewards)
            smt_item_sources.append(item_source)

    item_sources_output_path = DATA_DIR / "ap-item-sources.json"
    with open(item_sources_output_path, 'w+') as f:
        item_source_data = [asdict(item_source) for item_source in smt_item_sources]
        json.dump(item_source_data, f)


def main():
    smt_items = export_items()
    export_item_sources(smt_items)


if __name__ == "__main__":
    main()
