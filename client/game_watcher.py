import asyncio

from . import treasure_monitor
from .location_tracker import LocationTracker


def watch(location_tracker: LocationTracker) -> None:
    asyncio.create_task(treasure_monitor.monitor(location_tracker))
