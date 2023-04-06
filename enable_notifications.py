# -*- coding: utf-8 -*-
"""
Notifications
-------------

Example showing how to add notifications to a characteristic and handle the responses.

Updated on 2019-07-03 by hbldh <henrik.blidh@gmail.com>

"""

import sys
import asyncio
import platform

from bleak import BleakClient


# you can change these to match your device or override them from the command line
CHARACTERISTIC_UUID = "00001800-0000-1000-8000-00805f9b34fb"
ADDRESS = "E3:2C:A4:2E:71:7D"


def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print("{0}: {1}".format(sender, data))


async def main(address, char_uuid):
    try:
        async with BleakClient(address) as client:
            print(f"Connected: {client.is_connected}")

            await client.start_notify(char_uuid, notification_handler)
            await client.write_gatt_char(char_uuid, bytearray([2,1,3]))
            await asyncio.sleep(8.0)
            print(f"Connected: {client.is_connected}")
            #await client.stop_notify(char_uuid)
    except KeyboardInterrupt:
        print("Exiting...")
        await client.stop_notify(char_uuid)
        print(f"Connected: {client.is_connected}")


if __name__ == "__main__":
    asyncio.run(
        main(
            sys.argv[1] if len(sys.argv) > 1 else ADDRESS,
            sys.argv[2] if len(sys.argv) > 2 else CHARACTERISTIC_UUID,
        )
    )
