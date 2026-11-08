def main():
    ce_macca_address = 0x20EDB592CCC
    target_ce_address = 0x20EDB9F0D18

    ce_offset = target_ce_address - ce_macca_address

    macca_address = 0x8291c8c

    target_address = macca_address + ce_offset

    print(f"Target address: 0x{target_address:x}")


if __name__ == "__main__":
    main()
