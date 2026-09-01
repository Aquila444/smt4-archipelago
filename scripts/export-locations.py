import json
import re

from ..config import DATA_DIR
from ..locations import SmtLocation
from ..utils.ids import IdGenerator

pattern = re.compile(r"(\d+): ([^;]+); ([^;]+);(.*)")
id_generator = IdGenerator()


def main():
    treasure_locations = create_treasure_locations()

    locations = treasure_locations

    output_path = DATA_DIR / "ap-locations.json"
    with open(output_path, "w+") as f:
        json.dump(locations, f)


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

    game_id = int(match.group(1))
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


if __name__ == '__main__':
    main()
