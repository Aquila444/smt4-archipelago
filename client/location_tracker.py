import asyncio


class LocationTracker:

    def __init__(self):
        self.check_queue = asyncio.Queue()
        self.checked_locations = set()

    def check_location(self, location_id: int) -> bool:
        if location_id not in self.checked_locations:
            self.check_queue.put_nowait(location_id)
            self.checked_locations.add(location_id)

            return True

        return False

    async def get_location(self) -> int:
        return await self.check_queue.get()
