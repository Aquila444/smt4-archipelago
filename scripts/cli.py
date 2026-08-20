import argparse
import asyncio

from ..emulator import memory
from ..emulator.azahar import azahar

read_type_conversion_map = {
    "string": lambda x: x.decode("shift_jis", errors='ignore'),
    "int": lambda x: int.from_bytes(x, "little"),
    "byte": lambda x: bytes(x)
}
write_type_conversion_map = {
    "string": lambda x: str(x).encode(),
    "hex": lambda x: int(x, 16).to_bytes(len(x), "little"),
    "int": lambda x: int(x).to_bytes(4, "little"),
    "short": lambda x: int(x).to_bytes(2, "little"),
    "byte": lambda x: int(x).to_bytes(1, "little")
}


async def main(args):
    if args.command == "scan_memory":
        conversion_func = read_type_conversion_map.get(args.type)
        size_bytes = int(args.size_bytes)
        target_value = args.value

        matching_addresses = await memory.search_for_value(target_value, size_bytes, conversion_func)

        if len(matching_addresses) > 0:
            output_string = ", ".join(f"0x{address:02x}" for address in matching_addresses)
            print(f"Found matching addresses: {output_string}")
        else:
            print(f"No address found for value {target_value}")
    elif args.command == "read_memory":
        address = int(args.address, 16)
        size_bytes = int(args.size_bytes)

        byte_value = await azahar.read(address, size_bytes)
        conversion_func = read_type_conversion_map.get(args.type)
        converted_value = conversion_func(byte_value)
        print(f"Value at address 0x{address:x}: {converted_value}")
    elif args.command == "monitor_memory":
        address = int(args.address, 16)
        size_bytes = int(args.size_bytes)

        conversion_func = read_type_conversion_map.get(args.type)

        await memory.monitor_address(address, size_bytes, conversion_func)
    elif args.command == "write_memory":
        address = int(args.address, 16)

        conversion_func = write_type_conversion_map.get(args.type)
        converted_value = conversion_func(args.value)

        await azahar.write(address, converted_value)
        print(f"Wrote value {args.value} to address 0x{address:x}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='smt4',
        description="Smt 4 archipelago")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available subcommands")

    scan_parser = subparsers.add_parser("scan_memory")
    scan_parser.add_argument("type")
    scan_parser.add_argument("size_bytes")
    scan_parser.add_argument("value")

    read_memory_parser = subparsers.add_parser("read_memory")
    read_memory_parser.add_argument("address")
    read_memory_parser.add_argument("type")
    read_memory_parser.add_argument("size_bytes")

    read_memory_parser = subparsers.add_parser("monitor_memory")
    read_memory_parser.add_argument("address")
    read_memory_parser.add_argument("type")
    read_memory_parser.add_argument("size_bytes")

    read_memory_parser = subparsers.add_parser("write_memory")
    read_memory_parser.add_argument("address")
    read_memory_parser.add_argument("type")
    read_memory_parser.add_argument("value")

    args = parser.parse_args()

    asyncio.run(main(args))
