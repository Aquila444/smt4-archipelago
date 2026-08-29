import asyncio
import time
from datetime import datetime
from pathlib import Path

from NetUtils import NetworkItem
from settings import get_settings
from . import treasure_watcher, inventory_watcher
from .. import item_handler
from ..item_tracker import ReceivedSmtItem, ItemTracker
from ..location_tracker import LocationTracker
from ...emulator.memory import memory_handler

game_time_address = 0x82b10e0
save_file_signature = bytes.fromhex("44 44 53 34 47 41 4D 45")
save_file_address = 0x873ff28


class GameWatcher:

    def __init__(self):
        self.player_in_game = False
        self.save_loaded = False
        self.stable_iterations = 0
        self.loaded_save_time = 0
        self.tentative_load_time = 0
        self.active_save = 0

        self.location_tracker = LocationTracker()
        self.item_tracker = ItemTracker()

    async def start(self) -> None:
        asyncio.create_task(memory_handler(game_time_address, 4, self.game_load_check, interval=1))
        asyncio.create_task(memory_handler(save_file_address, len(save_file_signature), self.check_in_game))

        asyncio.create_task(treasure_watcher.watch(self.location_tracker))
        asyncio.create_task(inventory_watcher.watch())

    async def check_in_game(self, previous_bytes: bytes, current_bytes: bytes):
        if previous_bytes == save_file_signature and current_bytes != save_file_signature:
            print("Player entered the game.")
            self.player_in_game = True

    async def game_load_check(self, previous_bytes: bytes, current_bytes: bytes):
        previous_time = int.from_bytes(previous_bytes, "little")
        current_time = int.from_bytes(current_bytes, "little")
        time_difference = abs(current_time - previous_time)

        likely_loaded = time_difference > 5
        if likely_loaded:
            print("Player likely loaded game.")
            self.save_loaded = True
            self.stable_iterations = 0
            self.tentative_load_time = current_time
            return
        else:
            self.stable_iterations += 1
            print(f"Stable for {self.stable_iterations} iterations.")

        if self.save_loaded and self.stable_iterations == 3:
            self.save_loaded = False
            self.loaded_save_time = self.tentative_load_time
            print(f"Save load detected, recording loaded time as {self.loaded_save_time}")

            self.set_active_save()
            save_timestamp = self.get_previous_saved_timestamp()

            date = datetime.fromtimestamp(save_timestamp)
            date_string = date.strftime("%Y-%m-%d %H:%M:%S")
            print(f"Recovering items since {date_string}")

            missing_items = self.item_tracker.get_items_after_time(save_timestamp)
            for item in missing_items:
                print(f"Gave missing item from server: {item.ap_item_id}")
                await item_handler.receive_item(item.ap_item_id)

    def set_active_save(self):
        save_file_1 = self.get_save_file(1)
        save_file_2 = self.get_save_file(2)

        with open(save_file_1, "rb") as save_1, open(save_file_2, "rb") as save_2:
            game_time_1 = self.get_game_time_from_save(save_1)
            game_time_2 = self.get_game_time_from_save(save_2)

        time_difference_1 = abs(self.loaded_save_time - game_time_1)
        time_difference_2 = abs(self.loaded_save_time - game_time_2)

        if time_difference_1 < time_difference_2:
            self.active_save = 1
        else:
            self.active_save = 2

        print(f"Active save was set to {self.active_save}")

    @classmethod
    def get_game_time_from_save(cls, save_file):
        save_file.seek(0x000000D0)
        game_time_bytes = save_file.read(4)

        return int.from_bytes(game_time_bytes, "little")

    def get_previous_saved_timestamp(self) -> int:
        save_file = self.get_save_file(self.active_save)

        return int(save_file.stat().st_mtime)

    @classmethod
    def get_save_file(cls, save_id: int):
        azahar_path = get_settings().smt4.azahar_path
        azahar_folder = Path(azahar_path).parent

        sdmc_folder = azahar_folder / "user" / "sdmc"
        save_folder = sdmc_folder / "Nintendo 3DS/00000000000000000000000000000000/00000000000000000000000000000000/title/00040000/000e5c00/data/00000001"

        return save_folder / f"sdds4game{save_id}.sav"

    async def get_location(self) -> int:
        return await self.location_tracker.get_location()

    async def give_item(self, index: int, item: NetworkItem) -> None:
        timestamp = int(time.time())

        received_smt_item = ReceivedSmtItem(index, timestamp, item.item)
        self.item_tracker.register_item(received_smt_item)

        if self.player_in_game:
            print(f"Gave item from server: {item.item}")
            await item_handler.receive_item(item.item)
