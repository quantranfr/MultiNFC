import asyncio
import websockets

async def hello(websocket, path):
    mes = await websocket.recv()
    print(f"< {mes}")

start_server = websockets.serve(hello, "localhost", 9080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
