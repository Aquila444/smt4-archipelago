from __future__ import annotations

from BaseClasses import Location
from .config import GAME_NAME
from .smt_types import SmtLocation
from .utils.utils import load_data_file_as_json

blacklisted_locations = {
    "Usetan / Harajuku Police Station / Kabuto Shrine: Dead hunter",
    "Yoroi shrine / Cameron Building / Bikkuri Camera: Dead hunter",
    "Yodogawa Camera / Jujo Base / Kiou Shrine / Camp Meguro: Dead hunter",
    "Kiba Storage: Dead hunter"
}


def create_all_locations(world) -> None:
    create_regular_locations(world)


def create_regular_locations(world) -> None:
    filtered_locations = [location for location in locations if
                          location.subtype != "relic" and location.name not in blacklisted_locations]

    for smt_location in filtered_locations:
        region = world.get_region(smt_location.region)

        location = Location(world.player, smt_location.name, smt_location.archipelago_id, region)
        location.game = GAME_NAME

        region.locations.append(location)


def load_locations() -> list[SmtLocation]:
    try:
        location_file_name = "ap-locations.json"
        data = load_data_file_as_json(location_file_name)

        return [SmtLocation.from_dict(entry) for entry in data]
    except Exception:
        return []


locations = load_locations()
location_name_to_id = {location.name: location.archipelago_id for location in locations}
