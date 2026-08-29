import struct

from emulator.azahar import azahar
from ..emulator.memory import read_memory
from ..items import items

base_inventory_address = 0x829b474
item_cap = 255

ap_id_to_inventory_id = {item.archipelago_id: item.inventory_index for item in items}


async def receive_item(ap_item_id: int) -> None:
    inventory_index = ap_id_to_inventory_id[ap_item_id]

    address = get_address_for_item_id(inventory_index)
    current_item_count_bytes = await read_memory(address, 1)
    current_item_count = int.from_bytes(current_item_count_bytes, byteorder="little")

    new_item_count = min(current_item_count + 1, item_cap)
    new_item_count_bytes = struct.pack("<H", new_item_count)
    await azahar.write(address, new_item_count_bytes)


def get_address_for_item_id(inventory_index: int) -> int:
    offset = 2 * inventory_index

    return base_inventory_address + offset
