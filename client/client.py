from __future__ import annotations

import asyncio
from argparse import Namespace

from CommonClient import ClientCommandProcessor, CommonContext, server_loop
from ..config import GAME_NAME
from ..emulator.azahar import azahar

class SMT4ClientCommandProcessor(ClientCommandProcessor):
    ctx: SMT4Context


class SMT4Context(CommonContext):
    game = GAME_NAME

    client_loop: asyncio.Task[None]

    command_processor = SMT4ClientCommandProcessor


async def main(args: Namespace) -> None:
    ctx = SMT4Context(args.connect, args.password)
    ctx.auth = args.name

    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

    ctx.run_gui()
    ctx.run_cli()
