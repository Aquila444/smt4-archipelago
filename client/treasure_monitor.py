from .location_tracker import LocationTracker
from ..emulator.memory import memory_handler
from ..locations import locations
from ..smt_types import SmtLocation

game_state_address = 0x8291b4c

file_header_size = 128
treasure_state_offset = 0x0000B080 + 52
treasure_state_address = game_state_address + treasure_state_offset
treasure_section_length = 160


async def monitor(location_tracker: LocationTracker):
    handler = lambda x, y: treasure_handler(x, y, location_tracker)

    await memory_handler(treasure_state_address, treasure_section_length, handler)


def treasure_handler(previous_bytes: bytes, current_bytes: bytes, location_tracker: LocationTracker):
    previous_state = [byte_value for byte_value in previous_bytes]
    current_state = [byte_value for byte_value in current_bytes]

    diff_indexes = [(i, v1, v2) for i, (v1, v2) in enumerate(zip(previous_state, current_state)) if
                    v1 != v2]

    for index, previous_value, current_value in diff_indexes:
        diff_value = (~previous_value) & current_value
        differing_indices = [i for i in range(8) if (diff_value >> i) & 1]

        for sub_index in differing_indices:
            flag = f"{index}-{sub_index}"

            print(f"Chest with flag {flag} opened")

            location = get_location_from_flag(locations, flag)

            if location is not None:
                location_tracker.check_location(location)


def get_location_from_flag(location_list: list[SmtLocation], flag: str) -> int | None:
    location = next((location for location in location_list if location.flag == flag), None)

    if location is not None:
        return location.archipelago_id
    else:
        return None
