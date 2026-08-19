from ..config import BASE_DIR


def main():
    item_id = 142

    # Macca value 32139021
    # macca_address = 0x1E8BE084CCC
    # item_relative_offset = 0x28108

    # item_base_address = macca_address + item_relative_offset

    item_base_address = 0x2F2486774B4

    item_address = item_base_address + (2 * item_id)

    output_path = BASE_DIR / "notes/ce_addresses.txt"
    with open(output_path, "w+") as outputfile:
        # outputfile.write(f"Macca address: {macca_address:x}\n")
        outputfile.write(f"base address: {item_base_address:x}\n")
        outputfile.write(f"Item address: {item_address:x}\n")


if __name__ == "__main__":
    main()
