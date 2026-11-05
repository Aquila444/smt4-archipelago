import struct

from ...emulator.azahar import azahar
from ...emulator.memory import memory_handler

ap_item_address = 0x829b580


async def watch() -> None:
    await memory_handler(ap_item_address, 1, ap_item_handler)


async def ap_item_handler(previous_bytes: bytes, current_bytes: bytes):
    count = int.from_bytes(current_bytes, "little")

    data = struct.pack("<H", 0)

    if count > 0:
        await azahar.write(ap_item_address, data)
