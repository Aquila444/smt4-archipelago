import json
from dataclasses import asdict

from ..config import DATA_DIR
from ..game.treasure.treasure import loot_table


def main():
    drop_locations_path = DATA_DIR / "drop-locations.txt"
    missing_loot_path = DATA_DIR / "missing-loot.json"

    with open(drop_locations_path) as f, open(missing_loot_path, "w+") as g:
        drops = f.readlines()

        found_ids = {int(drop.split(":")[0]) for drop in drops}

        missing_loot = [asdict(location) for location in loot_table.locations.values() if
                        len(location.drops) > 0 and location.drop_id not in found_ids]

        json.dump(missing_loot, g)


if __name__ == "__main__":
    main()
