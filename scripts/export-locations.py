import json
import re
from dataclasses import asdict

from ..config import DATA_DIR
from ..locations import SmtLocation

pattern = re.compile(r"(\d+): ([^;]+); ([^;]+);(.*)")


def main():
    drop_locations_path = DATA_DIR / "drop-locations.txt"

    with open(drop_locations_path, "r") as f:
        lines = f.readlines()

    locations = [asdict(map_location(index + 1, line)) for index, line in enumerate(lines)]

    output_path = DATA_DIR / "ap-locations.json"
    with open(output_path, "w+") as f:
        json.dump(locations, f)


def map_location(archipelago_id, line):
    match = re.match(pattern, line)

    game_id = int(match.group(1))
    region = match.group(2)

    name = match.group(3)
    location_name = f"{region}: {name}"

    flag = match.group(4)

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
