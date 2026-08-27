import asyncio
import time
from typing import Callable

from .azahar import azahar


async def monitor_address(address, size_bytes: int, conversion_func):
    while True:
        byte_value = await azahar.read(address, size_bytes)
        converted_value = conversion_func(byte_value)
        message = f"{address:x}: {converted_value}"

        print(f"\r{message}\033[K", end="", flush=True)

        time.sleep(0.1)


async def search_for_value(target_value, value_size_bytes: int, conversion_func):
    print(f"Searching for value: {target_value}")

    start_address = 0x08000000
    end_address = 0x10000000
    current_address = start_address
    distance = end_address - start_address
    print(f"{distance} bytes to scan")
    found_addresses = []

    interval = 5
    next_run = time.monotonic()

    while current_address + azahar.MAX_READ_SIZE <= end_address:
        progress_bytes = current_address - start_address
        progress_ratio_percent = (progress_bytes / distance) * 100

        if time.monotonic() >= next_run:
            print(f"Progress: {progress_ratio_percent}%")
            next_run += interval

        value_bytes = await azahar.read(current_address, azahar.MAX_READ_SIZE)

        max_offset = azahar.MAX_READ_SIZE - value_size_bytes + 1
        for offset in range(max_offset):
            byte_slice = value_bytes[offset:offset + value_size_bytes]
            value = conversion_func(byte_slice)

            slice_address = current_address + offset
            if value == target_value:
                found_addresses.append(current_address)
                print(f"offset: {slice_address:x}, value: {value}")

        current_address += azahar.MAX_READ_SIZE

    return found_addresses


async def memory_handler(address: int, size_bytes: int, handler: Callable[[bytes, bytes], None]):
    previous_value = await read_memory(address, size_bytes)
    while True:
        await asyncio.sleep(1)

        current_value = await read_memory(address, size_bytes)
        handler(previous_value, current_value)

        previous_value = current_value


async def read_memory(address: int, size_bytes: int) -> bytes:
    chunks, leftover = divmod(size_bytes, azahar.MAX_READ_SIZE)

    current_address = address
    value_bytes = b""
    for _ in range(chunks):
        value_bytes_chunk = await azahar.read(current_address, azahar.MAX_READ_SIZE)
        value_bytes += value_bytes_chunk

        current_address = current_address + azahar.MAX_READ_SIZE

    if leftover > 0:
        value_bytes_leftover = await azahar.read(current_address, leftover)
        value_bytes += value_bytes_leftover

    return value_bytes
