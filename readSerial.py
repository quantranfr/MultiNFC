# This script work with serial devices emitting one line of text at a time (Serial.println), at 9600 baud rate.

from serial import Serial
import serial.tools.list_ports
import glob, time, sys
import asyncio
import websockets

async def hello():
    uri = "ws://localhost:9080"
    async with websockets.connect(uri) as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

def get_port():
    """
    This function let the user choose one or more ports to hear from
    """

    # detect serial devices
    if sys.platform.startswith('linux'):
        # a more precise way is to extract info from `dmesg | grep -E "tty.*USB|USB.*tty"`
        ports = [port.device for port in serial.tools.list_ports.comports()]
    elif sys.platform.startswith('darwin'): # MacOS
        ports = glob.glob('/dev/tty.usb*')
    else:
        raise OSError("Not a Linux or MacOS machine. Abort.")

    if not len(ports):
        raise IOError("No device detected. Abort.")

    # choice(s) of serial devices
    print('Available serial ports are:')
    for i, port in enumerate(ports):
        print(f'{i+1}. {port}')
    iports = map(int, input('Which port(s) do you want to hear from (space separated): ').split()) # 1 base

    try:
        return [ports[iport-1] for iport in iports]
    except IndexError:
        raise ValueError("wrong choice")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(hello())
    try:
        ports=get_port()
    except (IOError, ValueError, OSError) as e:
        print(e)
        sys.exit(1)

    if not len(ports):
        sys.exit(0)

    devices = [Serial(port, 9600, timeout=0.1) for port in ports]
    while True:
        for device in devices:
            s = device.readline()[:-2].decode('ascii') #gets rid of the new-line chars
            if s:
                print(s)

        time.sleep(0.1)
