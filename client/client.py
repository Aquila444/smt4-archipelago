from __future__ import annotations

import asyncio
from argparse import Namespace
from typing import Any

from CommonClient import ClientCommandProcessor, CommonContext, server_loop
from .watchers.game_watcher import GameWatcher
from ..config import GAME_NAME


class SMT4ClientCommandProcessor(ClientCommandProcessor):
    ctx: SMT4Context


class SMT4Context(CommonContext):
    game = GAME_NAME

    client_loop: asyncio.Task[None]
    command_processor = SMT4ClientCommandProcessor

    # Get items from other worlds only
    items_handling = 0b001

    highest_processed_item_index: int = 0

    def __init__(self, server_address: str | None = None, password: str | None = None) -> None:
        super().__init__(server_address, password)
        self.game_watcher = GameWatcher()

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect(game=self.game)

    async def smt_loop(self) -> None:
        await self.game_watcher.start()

        while not self.exit_event.is_set():
            try:
                async with asyncio.timeout(1):
                    checked_location = await self.game_watcher.get_location()
                    print(f"Got location from game {checked_location}")
            except asyncio.TimeoutError:
                checked_location = None

            if checked_location:
                await self.check_locations({checked_location})
                print(f"Sent location to server: {checked_location}")

            new_items = self.items_received[self.highest_processed_item_index:]
            for item in new_items:
                print(f"Got item {item.item} from server with index {self.highest_processed_item_index}")
                await self.game_watcher.give_item(self.highest_processed_item_index, item)
                self.highest_processed_item_index += 1

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        pass


async def main(args: Namespace) -> None:
    ctx = SMT4Context(args.connect, args.password)
    ctx.auth = args.name

    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

    ctx.run_gui()
    ctx.run_cli()

    ctx.client_loop = asyncio.create_task(ctx.smt_loop(), name="client loop")

    await ctx.exit_event.wait()
    await ctx.shutdown()
