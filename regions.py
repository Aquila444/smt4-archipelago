from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region
from .smt_types import SmtRegion
from .utils.utils import load_data_file_as_json

if TYPE_CHECKING:
    from .world import SMT4World


def create_and_connect_regions(world: SMT4World) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: SMT4World) -> None:
    for smt_region in regions:
        region = Region(smt_region.name, world.player, world.multiworld)
        world.multiworld.regions.append(region)


def connect_regions(world: SMT4World) -> None:
    for smt_region in regions:
        source_region = world.get_region(smt_region.name)

        for entrance in smt_region.entrances:
            destination_region = world.get_region(entrance.region)
            source_region.connect(destination_region)


def load_regions():
    region_file_name = "ap-regions.json"
    data = load_data_file_as_json(region_file_name)

    return [SmtRegion.from_dict(entry) for entry in data]


regions = load_regions()
