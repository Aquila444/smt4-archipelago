import asyncio
import subprocess
from collections.abc import Sequence

import colorama

import Patch
from CommonClient import get_base_parser, handle_url_arg
from settings import get_settings


def launch_smt4_client(*args: Sequence[str]) -> None:
    parser = get_base_parser()
    parser.add_argument("patch_file", default="", type=str, nargs="?", help="Path to an Archipelago patch file")
    parser.add_argument("--name", default=None, help="Slot Name to connect as.")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")

    launch_args = handle_url_arg(parser.parse_args(args))

    patch_file = launch_args.patch_file
    if patch_file != "":
        metadata, output_file = Patch.create_rom_file(patch_file)

    azahar_process = None
    try:
        azahar_path = get_settings().smt4.azahar_path
        azahar_process = subprocess.Popen([azahar_path, output_file])

        colorama.just_fix_windows_console()

        from .client import main
        asyncio.run(main(launch_args))
    finally:
        if azahar_process is not None:
            azahar_process.kill()
        colorama.deinit()
