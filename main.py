import asyncio
import sys
import os

from time import sleep

from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

import mouse
import keyboard
import screeninfo

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
#CHARACTERISTIC_UUID = "00001800-0000-1000-8000-00805f9b34fb"

# All BLE devices have MTU of at least 23. Subtracting 3 bytes overhead, we can
# safely send 20 bytes at a time to any device supporting this service.
UART_SAFE_SIZE = 20

terminal_size = os.get_terminal_size()
monitor = screeninfo.get_monitors()[0]

previous_buttons = dict(zip(["A","B","C","D","E","F","X","Y"], [False, False, False, False, False, False, False, False]))
prev_yaw, prev_pitch = 0, 0
dyaw, dpitch = None, None


mouse_mode = True
game_mode = not mouse_mode

def convert_range(OldMin, OldMax, NewMin, NewMax, OldValue):
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)  
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    return NewValue

async def arkade_connect():
    ### Find ARKADE blaster and connect to it
    devices = await BleakScanner.discover()
    device = None
    try:
        for d in devices:
            if d.name[0:6] == "ARKADE":
                print(d)
                device = d
    except:
        pass
    if device == None: # if nothing was found, try to connect with hard-coded UUID
        print("No device was found, trying device UUID...")
        device = "E3:2C:A4:2E:71:7D"
    ### CONNECTION END

    # Handle when device disconnects
    def handle_disconnect(_: BleakClient):
        print("\nDevice disconnected, shutting down!")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()
        exit()

    # Handle incoming data
    def handle_rx(_: int, data: bytearray):
        global previous_buttons, prev_pitch, prev_yaw
        # reset text variable, will print it at the end of the loop
        text = "\rreceived data  "

        # pretty print all incoming data
        for i in data:
            text += str(i) + (" " * ( 4 - len( str( i ) ) ) )
        
        if data[0]==124: # move packet? has data about gyro and buttons
            # parse yaw, roll and pitch data
            roll = data[5]
            pitch = data[7]
            yaw = data[9]
            
            # pretty print it
            text += " ("
            for i in [roll, pitch, yaw]:
                text += str(i) + (" " * ( 4 - len( str( i ) ) ) )
            text += ")"

            # butons are represented by one byte, each button corresponds to one bit, if the bit is 1, the corresponding button is pressed
            buttons = bin( data[2] + 256 ) #YXFEDCBA is the binary mapping. add 256 to the number because of python bin method
            buttons = dict( zip( ['Y', 'X', 'F', 'E', 'D', 'C', 'B', 'A'], [1 if i=="1" else 0 for i in buttons[3:]] ) ) # combine with the mapping, so we can do buttons["A"] and get True if the button "A" is pressed

            # pretty print pressed buttons
            text += " ("
            for key, value in zip(buttons.keys(), buttons.values()):
                if value=="1":
                    text += f" {key}"
            text += ")"

            # same as buttons, just different mapping
            movement = bin( data[3] )
            movement = dict( zip( ["run", "walk", "backwalk", "fire", "left", "right"], [1 if i=="1" else 0 for i in movement[3:]] ) )

            # same as pretty print buttons, just for the movement buttons
            text += " ("
            for key, value in zip(movement.keys(), movement.values()):
                if value=="1":
                    text += f" {key}"
            text += ")"

            # print the text and fill the rest with spaces
            print(text + " " * ( terminal_size.columns - len(text) ), end="" )

            
            # fire is mouseclick
            if movement["fire"]:
                mouse.press(button='left')
            else:
                mouse.release(button='left')

            if game_mode: # try to implement this as a game controller, so you can play virtually any game with it,
                          # you could also write custom mappings to some keys or even macros if you need it for some specific game
                          # the gyro mouse doesnt work
                multiplier = 8
                x = yaw - prev_yaw
                if x >= 253:
                    x = 1
                elif x <= -253:
                    x = -1
                x *= -multiplier
                
                y = pitch - prev_pitch
                if y >= 253:
                    y = 1
                elif y <= -253:
                    y = -1
                y *= multiplier

                prev_pitch, prev_yaw = pitch, yaw
                #x = convert_range(20,70, 0,monitor.height, yaw)
                #y = convert_range(0,255, 0,monitor.width, pitch+128)
                
                #mouse.move(x,y, absolute=False)
                
                # WSAD movement
                if movement["left"]:
                    keyboard.press("a")
                else:
                    keyboard.release("a")
                if movement["right"]:
                    keyboard.press("d")
                else:
                    keyboard.release("d")
                if movement["walk"] or movement["run"]:
                    keyboard.press("w")
                else:
                    keyboard.release("w")
                if movement["backwalk"]:
                    keyboard.press("s")
                else:
                    keyboard.release("s")

                # jump, sneak, other buttons
                if buttons["E"]:
                    mouse.press(button="right")
                else:
                    mouse.release(button="right")
                if buttons["Y"]:
                    keyboard.press("shift")
                else:
                    keyboard.release("shift")
                if buttons["X"]:
                    keyboard.press("space")
                else:
                    keyboard.release("space")

            # MOUSE
            if mouse_mode: # mouse using some keys to move the mouse verticaly and horizontaly
                mouse_speed = 2
                velX, velY = 0, 0 # velocity X and Y
                if movement["left"]:
                    velX = -mouse_speed # change velocity X by -2, move mouse left
                if movement["right"]:
                    velX = mouse_speed # change velocity X by 2, move mouse right
                if movement["walk"]:
                    velY = -mouse_speed # change velocity Y by -2, move mouse up
                if movement["backwalk"]:
                    velY = mouse_speed # change velocity Y by 2, move mouse down
                mouse.move(velX, velY, absolute=False) # move mouse relative to current position

                # media controls
                if buttons["A"] and not previous_buttons["A"]:
                    keyboard.press_and_release("play/pause media")
                if buttons["B"] and not previous_buttons["B"]:
                    keyboard.press_and_release("volume mute")
                if buttons["C"] and not previous_buttons["C"]:
                    keyboard.press_and_release("volume up")
                if buttons["D"] and not previous_buttons["D"]:
                    keyboard.press_and_release("volume down")
                previous_buttons = buttons # save so we can detect rising and falling edges

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client: # connect
        print("\nConnected!")
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx) # register rx handler
        while True:
            await asyncio.sleep(0.25) # sleep so other tasks can be processed
            await client.write_gatt_char(UART_RX_CHAR_UUID, bytearray([2,1,4])) # we need to send this
            # i guess its somewhat of a keep alive packet, you donw need to send 214, i think anything would work

if __name__ == "__main__":
    try:
        asyncio.run(arkade_connect())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass
