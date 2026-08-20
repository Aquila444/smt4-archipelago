import asyncio
import struct

from ..emulator.memory import memory_handler
from ..config import DATA_DIR

item_count_size = 2

inventory_base_address = 0x829b474
inventory_end_address = 0x829c124
inventory_byte_length = inventory_end_address - inventory_base_address


async def main():
    inventory_ids_path = DATA_DIR / "inventory-ids.txt"
    with open(inventory_ids_path, "r", encoding="shift_jis") as inventory_file:
        inventory_id_lines = inventory_file.readlines()
        inventory_ids = {int(line.split(": ")[0]): line.split(": ")[1].strip() for line in inventory_id_lines}

    handler = lambda x, y: inventory_handler(x, y, inventory_ids)
    await memory_handler(inventory_base_address, inventory_byte_length, handler)


def inventory_handler(previous_bytes: bytes, current_bytes: bytes, inventory_ids: dict[int, str]):
    previous_item_counts = parse_inventory_entries(previous_bytes)
    current_inventory_counts = parse_inventory_entries(current_bytes)

    diff_indexes = [(i, v1, v2) for i, (v1, v2) in enumerate(zip(previous_item_counts, current_inventory_counts)) if
                    v1 != v2]
    diff_items = [map_inventory_item(diff[0], diff[1], diff[2], inventory_ids) for diff in diff_indexes]

    for item in diff_items:
        print(item)


def parse_inventory_entries(inventory_bytes: bytes) -> tuple[int]:
    num_items = int(len(inventory_bytes) / item_count_size)
    struct_format_string = f"<{num_items}H"

    item_counts = struct.unpack(struct_format_string, inventory_bytes)

    return item_counts


def map_inventory_item(index, old_item_count, new_item_count, inventory_ids):
    item_name = inventory_ids[index]

    return f"Item at index {index} ({item_name}) changed from {old_item_count} to {new_item_count}"


if __name__ == '__main__':
    asyncio.run(main())
