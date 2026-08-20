import asyncio

from ..emulator.memory import memory_handler

game_state_address = 0x8291b4c

file_header_size = 128
treasure_state_offset = 0x0000B080 + 52
treasure_state_address = game_state_address + treasure_state_offset
treasure_section_length = 160


async def main():
    await memory_handler(treasure_state_address, treasure_section_length, treasure_handler)


def treasure_handler(previous_bytes: bytes, current_bytes: bytes):
    previous_state = [byte_value for byte_value in previous_bytes]
    current_state = [byte_value for byte_value in current_bytes]

    diff_indexes = [(i, v1, v2) for i, (v1, v2) in enumerate(zip(previous_state, current_state)) if
                    v1 != v2]

    for index, previous_value, current_value in diff_indexes:
        diff_value = (~previous_value) & current_value
        differing_indices = [i for i in range(8) if (diff_value >> i) & 1]

        for sub_index in differing_indices:
            print(f"Chest {index}-{sub_index} was opened")


if __name__ == "__main__":
    asyncio.run(main())
