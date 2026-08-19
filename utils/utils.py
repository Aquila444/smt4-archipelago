import os
import re
from pkgutil import get_data
from typing import Any

import orjson

from ..config import parent_package

_NAME_PADDING = 32
_NAME_PATTERN = re.compile(rb"[^\x00]+")


def extract_string_from_bytes(string_bytes: bytes) -> str:
    match = re.match(_NAME_PATTERN, string_bytes)

    if match:
        name_bytes_extracted = match.group(0)

        return str(name_bytes_extracted, encoding="shift_jis")
    else:
        return ""


def create_name_entry(name: str, length: int) -> bytes:
    name_bytes = name.encode(encoding="shift_jis")

    padding_length = min(length, _NAME_PADDING)
    name_padded = pad_bytes(name_bytes, padding_length)

    occurrences = max(length // _NAME_PADDING, 1)
    name_string = name_padded * occurrences

    return pad_bytes(name_string, length)


def pad_bytes(string_bytes: bytes, length: int) -> bytes:
    return string_bytes.ljust(length, b"\x00")


def load_data_file(file_name: str, binary: bool = False, encoding: str = "utf-8") -> str | bytes:
    path = os.path.join("/data", file_name)
    data = get_data(parent_package.__name__, path)

    if not binary:
        return data.decode(encoding)
    else:
        return data


def load_data_file_as_json(file_name: str, encoding: str = "utf-8") -> Any:
    data = load_data_file(file_name, encoding=encoding, binary=True)

    return orjson.loads(data)
