import asyncio

from . import treasure_watcher, inventory_watcher
from ..location_tracker import LocationTracker


def watch(location_tracker: LocationTracker) -> None:
    asyncio.create_task(treasure_watcher.watch(location_tracker))
    asyncio.create_task(inventory_watcher.watch())
