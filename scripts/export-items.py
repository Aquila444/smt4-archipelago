import json
from dataclasses import asdict

from BaseClasses import ItemClassification
from ..config import DATA_DIR
from ..game.items.item_table import item_table, ItemType
from ..game.treasure.treasure import loot_table, LootDrop
from ..locations import locations
from ..smt_types import SmtItem, SmtItemReward, SmtItemSource

classification_map = {
    ItemType.KEY_ITEMS: ItemClassification.progression,
    ItemType.GEAR: ItemClassification.useful,
    ItemType.CONSUMABLES: ItemClassification.filler,
    ItemType.STARS: ItemClassification.filler
}


def main():
    unused_items = {"予備枠", "？？？", "削除", "これは未使用"}

    counter = 0
    smt_items = []
    for category in item_table.item_categories:
        item_type = category.item_type
        if item_type in [ItemType.RELICS, ItemType.CUT_CONTENT]:
            continue

        items = category.items
        for item in items:
            if item.name in unused_items:
                continue
            counter += 1

            classification = classification_map[item_type]
            smt_item = SmtItem(item.name, counter, item.item_id, item_type.name, classification.name)
            smt_items.append(smt_item)

    item_output_path = DATA_DIR / "ap-items.json"
    with open(item_output_path, 'w+') as f:
        item_data = [asdict(item) for item in smt_items]
        json.dump(item_data, f)

    item_id_to_item = {item.game_id: item for item in smt_items}

    smt_item_sources = []
    for location in locations:
        if location.type == "treasure":
            treasure = loot_table.get_treasure(location.game_id)
            item_rewards = [convert_drop(drop, item_id_to_item) for drop in treasure.drops]

            item_source = SmtItemSource(location.name, item_rewards)
            smt_item_sources.append(item_source)

    item_sources_output_path = DATA_DIR / "ap-item-sources.json"
    with open(item_sources_output_path, 'w+') as f:
        item_source_data = [asdict(item_source) for item_source in smt_item_sources]
        json.dump(item_source_data, f)


def convert_drop(drop: LootDrop, item_id_to_item: dict[int, SmtItem]) -> SmtItemReward:
    item = item_id_to_item[drop.item_id]

    return SmtItemReward(item, drop.drop_weight, 1)


if __name__ == "__main__":
    main()
