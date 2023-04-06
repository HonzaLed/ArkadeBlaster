"""
UART Service
-------------

An example showing how to write a simple program using the Nordic Semiconductor
(nRF) UART service.

"""

import asyncio
import sys
import os

from time import sleep

import keyboard

from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from math import pi, sin, cos
import _thread

Xrot = 0
Yrot = 0
Zrot = 0


UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
#CHARACTERISTIC_UUID = "00001800-0000-1000-8000-00805f9b34fb"


DATAS = []

# All BLE devices have MTU of at least 23. Subtracting 3 bytes overhead, we can
# safely send 20 bytes at a time to any device supporting this service.
UART_SAFE_SIZE = 20

loopCount = 1

def printIndex(index):
    print("Current:\n")
    try:
        for i in DATAS:
            print(i[index])
    except BaseException as err:
        print(err)
    print("Old:\n")
    try:
        for i in OLD_DATAS:
            print(i[index])
    except BaseException as err:
        print(err)


async def uart_terminal():
    ### Find ARKADE blaster and connect to it
    devices = await BleakScanner.discover()
    device = None
    for d in devices:
        if d.name[0:6] == "ARKADE":
            print(d)
            device = d
    if device == None:
        print("No device was found, exiting...")
        sys.exit(1)
    ### CONNECTION END

    def handle_disconnect(_: BleakClient):
        print("\nDevice was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()
        exit()

    def handle_rx(_: int, data: bytearray):
        global loopCount, Xrot, Yrot, Zrot
        #NAKLON: data[7]
        #SMER (otoceni): data[8]?
        #if data[0]!=124 and data[0]!=130:
        if True:
            print("\rreceived data  ", end="")
            for i in data:
                print(str(i)+(" "*(4-len(str(i)))), end=" ")
        if data[0]==124:
            #Xrot = round(data[7]/20)
            Yrot = round(data[7]/3)
            #Zrot = round(data[8]/20)
        #os.system("cls")
        #if data[0]==124:
            #pistole=round(data[7]/17)
            #print( ("\n"*(pistole-1))+"*"+("\n"*(15-pistole)))
            #plt.scatter(loopCount,data[7])
            #plt.pause(0.05)
            #loopCount = loopCount+1
            #pass


    
    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)
        print("\nConnected!")
        loop = asyncio.get_running_loop()
        code = 200
        while True:
            #await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray(bytes([2,1,3])))
            #CodeList = list(str(code))
            CodeList = input("What to send?: ").split(",")
            IntList = [int(x) for x in CodeList]
            SendData = bytes(IntList)
            await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray(SendData))
            code=code+1
            print("sent:",IntList)
            await asyncio.sleep(0.25)
            #await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray(bytes([2,1,4])))
            """keyboard.wait('c')
            if keyboard.is_pressed('c'):
                await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray(bytes([2,1,4])))
            elif keyboard.is_pressed('k'):
                await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray(bytes([2,1,3])))
            print("sent:", data)"""
        

def Receiver():
    try:
        asyncio.run(uart_terminal())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass

def PandaApp():
    app = MyPandaApp()
    app.run()

if __name__ == "__main__":
    useThread = False
    if useThread:
        RecThread = _thread.start_new_thread(Receiver, ())
        PandaApp()
    else:
        Receiver()
