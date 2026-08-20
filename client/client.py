from __future__ import annotations

import asyncio
from argparse import Namespace

from CommonClient import ClientCommandProcessor, CommonContext
from ..config import GAME_NAME


class SMT4ClientCommandProcessor(ClientCommandProcessor):
    ctx: SMT4Context


class SMT4Context(CommonContext):
    game = GAME_NAME

    client_loop: asyncio.Task[None]

    command_processor = SMT4ClientCommandProcessor


async def main(args: Namespace) -> None:
    ctx = SMT4Context(args.connect, args.password)
    ctx.auth = args.name

    ctx.run_gui()
    ctx.run_cli()
