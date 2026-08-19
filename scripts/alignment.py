import asyncio
from time import sleep

from ..citra.citra import CitraInterface

alignment_address = 0x8291d04
alignment_length = 2
target_value = 0


async def main():
    citra = CitraInterface()
    await citra.connect()

    alignment_bytes = target_value.to_bytes(alignment_length, signed=True)

    while True:
        await citra.write(alignment_address, alignment_bytes)

        sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
