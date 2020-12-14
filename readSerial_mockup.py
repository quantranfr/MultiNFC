#!/usr/bin/env python

# This script simulates serial devices reading, then send data over websocket to a client.
# Type
#     python -m websockets ws://127.0.0.1:9080
# in a terminal to simulate a websocket client
#
# Input from keyboard:
#   <reader1>:<card1>;<reader2>:<card2>;…
# Output to websocket server: the same. If no card on it, the reader will not be included in the message.

import asyncio
import websockets

async def handler(websocket, path):
    while True:
        message = input("Type the message to be sent: ")
        await websocket.send(message)

start_server = websockets.serve(handler, "localhost", 9080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
