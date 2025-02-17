# ArkadeBlaster
This is my implementation of the Arkade blaster model A2 bluetooth communication protocol in Python.  

I made this, because the company that makes the device has stopped supporting it and hasn't published the SDK. 
  
Most of the games that were compatible with it are no longer usable, some of them have dropped the support for the blaster, some of them have shut down their servers.  

This is very WIP project, but I hope that I could implement some sort of a driver so that I can play any PC game with it

All the logic is done in the `handle_rx` method, I have not yet discovered the commands that I can send to the blaster to change the LED colors
