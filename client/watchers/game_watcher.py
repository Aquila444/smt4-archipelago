import asyncio

from . import treasure_watcher, inventory_watcher
from .in_game_checker import InGameChecker
from ..location_tracker import LocationTracker


async def watch(location_tracker: LocationTracker) -> None:
    in_game_checker = InGameChecker()
    asyncio.create_task(in_game_checker.start())

    asyncio.create_task(treasure_watcher.watch(location_tracker))
    asyncio.create_task(inventory_watcher.watch())
