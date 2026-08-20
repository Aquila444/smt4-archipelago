import asyncio
import os
import signal
from pathlib import Path

hacking_tool_kit_path = "./HackingToolkit3DS.exe"
patch_name = "ap-patch"


async def unpack_rom(rom_file_path: Path) -> None:
    rom_dir_path = rom_file_path.parent
    rom_name = sanitize_rom_file(rom_file_path)
    rom_process = None

    try:
        print(f"Unpacking ROM...")
        print(f"Switching to {rom_dir_path} folder.")
        os.chdir(rom_dir_path)

        print("Running ROM builder.")
        rom_process = await asyncio.create_subprocess_exec(
            hacking_tool_kit_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE)

        stdout = rom_process.stdout
        stdin = rom_process.stdin

        target_string = "Enter your choice"
        await wait_for_string(stdout, target_string)
        await send_data(stdin, "D")

        rom_name_without_extension = rom_name.replace(".3ds", "")
        target_string = "Enter the name of your decrypted .3DS file (Without extension)"
        await wait_for_string(stdout, target_string)
        await send_data(stdin, rom_name_without_extension)

        target_string = "Decompress the code.bin file (n/y)?"
        await wait_for_string(stdout, target_string)
        await send_data(stdin, "n")

        target_string = "Extraction done!"
        await wait_for_string(stdout, target_string)

        print("Finished unpacking ROM!")
    finally:
        if rom_process is not None:
            kill_process(rom_process)

        print("Returning to original folder.")
        os.chdir(os.path.dirname(os.path.abspath(__file__)))


async def build_rom(rom_file_path: Path, target_path: Path):
    rom_dir_path = rom_file_path.parent
    rom_process = None

    try:
        print(f"Building ROM...")
        print(f"Switching to {rom_dir_path} folder.")
        os.chdir(rom_dir_path)

        print("Running ROM builder.")
        rom_process = await asyncio.create_subprocess_exec(
            hacking_tool_kit_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE)

        stdout = rom_process.stdout
        stdin = rom_process.stdin

        target_string = "Enter your choice"
        await wait_for_string(stdout, target_string)
        await send_data(stdin, "R")

        target_string = "Enter the output filename for your custom .3DS file"
        await wait_for_string(stdout, target_string)
        await send_data(stdin, patch_name)

        target_string = "Creation done!"
        await wait_for_string(stdout, target_string)

        print("Finished building ROM!")

        patched_file_name = f"{patch_name}_Edited.3ds"
        patched_file = rom_dir_path / patched_file_name

        patched_file.rename(target_path)
    finally:
        if rom_process is not None:
            kill_process(rom_process)

        print("Returning to original folder.")
        os.chdir(os.path.dirname(os.path.abspath(__file__)))


def sanitize_rom_file(rom_file_path: Path) -> str:
    new_name = rom_file_path.name.replace(" ", "_")
    new_path = rom_file_path.with_name(new_name)

    rom_file_path.rename(new_path)

    return new_path.name


def kill_process(process):
    pid = process.pid
    os.kill(pid, signal.SIGTERM)


async def wait_for_string(stdout, target_string: str):
    while True:
        line = await asyncio.wait_for(stdout.read(1000), timeout=60)
        if not line:
            break

        line_content = line.decode()

        if target_string in line_content:
            break


async def send_data(stdin, data: str):
    input_string = data.encode()

    stdin.write(input_string)
    await stdin.drain()
