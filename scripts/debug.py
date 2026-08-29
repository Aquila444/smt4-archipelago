def main():
    ce_macca_address = 0x20E9AE7ACCC

    macca_address = 0x8291c8c
    target_address = 0x8291d06

    offset = target_address - macca_address

    target_ce_address = ce_macca_address + offset

    print(f"{target_ce_address:x}")


if __name__ == "__main__":
    main()
