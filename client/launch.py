import asyncio
from collections.abc import Sequence

import colorama

import Patch
from CommonClient import get_base_parser, handle_url_arg
from settings import get_settings


def launch_smt4_client(*args: Sequence[str]) -> None:
    return asyncio.run(launch_smt4_client_inner(*args))


async def launch_smt4_client_inner(*args: Sequence[str]) -> None:
    from .client import main

    parser = get_base_parser()
    parser.add_argument("patch_file", default="", type=str, nargs="?", help="Path to an Archipelago patch file")
    parser.add_argument("--name", default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")

    launch_args = handle_url_arg(parser.parse_args(args))

    patch_file = launch_args.patch_file
    if patch_file != "":
        metadata, output_file = Patch.create_rom_file(patch_file)

    azahar_path = get_settings().smt4.azahar_path
    command = f"{azahar_path} {output_file}"
    azahar_process = await asyncio.create_subprocess_exec(
        command,
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL, stdin=asyncio.subprocess.DEVNULL
    )

    colorama.just_fix_windows_console()

    asyncio.run(main(launch_args))
    colorama.deinit()
