import re

import orjson

from ..config import DATA_DIR
from ..game.shops.shop_table import shop_table
from ..locations import SmtLocation
from ..utils.ids import IdGenerator

pattern = re.compile(r"(\d+): ([^;]+); ([^;]+);(.*)")
id_generator = IdGenerator()


def main():
    treasure_locations = create_treasure_locations()
    shop_locations = create_shop_locations()

    locations = treasure_locations + shop_locations

    output_path = DATA_DIR / "ap-locations.json"
    with open(output_path, "wb+") as f:
        encoded_json = orjson.dumps(locations)
        f.write(encoded_json)


def create_treasure_locations() -> list[SmtLocation]:
    drop_locations_path = DATA_DIR / "drop-locations.txt"

    with open(drop_locations_path, "r") as f:
        lines = f.readlines()

    locations = []
    for line in lines:
        ap_id = id_generator.get_new_id()
        treasure_location = map_treasure_location(ap_id, line)
        locations.append(treasure_location)

    return locations


def map_treasure_location(archipelago_id, line) -> SmtLocation:
    match = re.match(pattern, line)

    game_id = match.group(1)
    region = match.group(2)

    name = match.group(3)
    location_name = f"{region}: {name}"

    flag = match.group(4).strip()

    if "chest" in name.lower():
        subtype = "chest"
    elif "dead hunter" in name.lower():
        subtype = "corpse"
    elif "relic" in name.lower():
        subtype = "relic"
    else:
        subtype = ""

    type = "treasure"

    return SmtLocation(location_name, archipelago_id, game_id, region, type, subtype, flag)


def create_shop_locations() -> list[SmtLocation]:
    with open(DATA_DIR / "shop-regions.txt", "r") as f:
        lines = f.readlines()
        shop_to_region = {int(line.split(": ")[0]): line.split(": ")[1].strip() for line in lines}

    type = "shop"
    subtype = ""
    flag = ""

    locations = []
    for shop in shop_table.shops:
        shop_id = shop.shop_id
        region = shop_to_region.get(shop_id)

        if region is None:
            continue

        for index, item in enumerate(shop.shop_items):
            location_name = f"{region} - Item {index + 1}"
            archipelago_id = id_generator.get_new_id()
            game_id = f"{shop_id}-{index}"

            location = SmtLocation(location_name, archipelago_id, game_id, region, type, subtype, flag)
            locations.append(location)

    return locations


if __name__ == '__main__':
    main()
