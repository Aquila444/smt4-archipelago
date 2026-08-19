import argparse
from itertools import batched
from pathlib import Path

from ..tbb.tbb import Table


def format_hex(line_bytes: bytes):
    return line_bytes.hex(" ")


def format_string(line_bytes: bytes):
    string = line_bytes.decode("shift_jis", errors='ignore')

    return string.split("\x00")[0]


def format_integer(line_bytes: bytes):
    parsed_integers = [str(int.from_bytes(chunk, "little")) for chunk in batched(line_bytes, 4)]

    return " ".join(parsed_integers)


def format_short(line_bytes: bytes):
    parsed_integers = [str(int.from_bytes(chunk, "little")) for chunk in batched(line_bytes, 2)]

    return " ".join(parsed_integers)


def format_byte(line_bytes: bytes):
    parsed_integers = [str(int.from_bytes(chunk, "little")) for chunk in batched(line_bytes, 1)]

    return " ".join(parsed_integers)


type_conversion_map = {
    "string": format_string,
    "hex": format_hex,
    "int": format_integer,
    "short": format_short,
    "byte": format_byte,
}


def main(args):
    filepath = args.path
    data_type = args.type

    type_conversion_func = type_conversion_map.get(data_type)

    table = Table.from_file(filepath)
    mapped_tables = [[type_conversion_func(entry) for entry in subtable.table_data.data] for subtable in
                     table.tables]

    output_path = filepath.replace("clean_rom/ExtractedRomFS", "tbb").replace(".tbb", ".txt")
    dir_path = Path(output_path)
    dir_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w+", encoding="shift_jis") as output_file:
        for index, table in enumerate(mapped_tables):
            output_file.write(f"Table {index}\n\n")

            for entry in table:
                output_file.write(entry + "\n")

            output_file.write("\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='tbb',
        description="Parse tbb files")

    parser.add_argument("path")
    parser.add_argument("type")

    args = parser.parse_args()

    main(args)
