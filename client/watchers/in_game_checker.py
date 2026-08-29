import asyncio

from ...emulator.memory import memory_handler

game_time_address = 0x82b10e0
save_file_signature = bytes.fromhex("44 44 53 34 47 41 4D 45")
save_file_address = 0x873ff28


class InGameChecker:

    def __init__(self):
        self.player_is_in_game = False
        self.player_loaded_save = False
        self.loaded_save_time = -100
        self.passed_iterations = 0
        self.iterations_since_save = 0

    async def start(self) -> None:
        # await memory_handler(game_time_address, 4, self.time_check, interval=1)
        await memory_handler(save_file_address, len(save_file_signature), self.check_in_game)

    async def check_in_game(self, previous_bytes: bytes, current_bytes: bytes):
        print(f"Player is in game: {self.player_is_in_game}")

        if previous_bytes == save_file_signature and current_bytes != save_file_signature:
            self.player_is_in_game = True

    async def time_check(self, previous_bytes: bytes, current_bytes: bytes):
        previous_time = int.from_bytes(previous_bytes, "little")
        current_time = int.from_bytes(current_bytes, "little")
        time_difference = abs(current_time - previous_time)

        self.player_loaded_save = time_difference > 3

        if self.player_loaded_save:
            self.loaded_save_time = current_time
            print(f"Save load detected, recording loaded time as {self.loaded_save_time}")

    def is_player_in_game(self):
        return self.player_is_in_game


async def main():
    checker = InGameChecker()
    await checker.start()


if __name__ == '__main__':
    asyncio.run(main())
