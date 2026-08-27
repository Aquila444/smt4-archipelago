from __future__ import annotations

import asyncio
from argparse import Namespace
from typing import Any

from CommonClient import ClientCommandProcessor, CommonContext, server_loop
from .watchers import game_watcher
from .location_tracker import LocationTracker
from ..config import GAME_NAME


class SMT4ClientCommandProcessor(ClientCommandProcessor):
    ctx: SMT4Context


class SMT4Context(CommonContext):
    game = GAME_NAME

    client_loop: asyncio.Task[None]
    command_processor = SMT4ClientCommandProcessor

    # Get items from other worlds only
    items_handling = 0b001

    def __init__(self, server_address: str | None = None, password: str | None = None) -> None:
        super().__init__(server_address, password)

        self.location_tracker = LocationTracker()

    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect(game=self.game)

    async def smt_loop(self) -> None:
        game_watcher.watch(self.location_tracker)

        while not self.exit_event.is_set():
            try:
                async with asyncio.timeout(1):
                    checked_location = await self.location_tracker.get_location()
            except asyncio.TimeoutError:
                checked_location = None

            if checked_location:
                await self.check_locations({checked_location})
                print(f"Sent location to server: {checked_location}")

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
