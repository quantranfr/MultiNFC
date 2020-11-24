# This script work with serial devices emitting one line of text at a time (Serial.println), at 9600 baud rate,
# and send messages to a websocket server. There is a mockup websocket server in the same repository.
#
# Input (from serial ports, per line):
#   <readerID>:<cardID>
# Output (to websocket server, if no card on it, the reader will not be included in the message):
#   <reader1>:<card1>;<reader2>:<card2>;…
#
# Properties:
#
#   * send maximum 2 messages every second
#   * no subsequent same messages
#   * robust:
#
#     * filter faulty messages where 1 same card can be on 2 different readers
#     * have to receive 3 times nothing from the reader to consider that there's no card. Actually, this is one of the most important HYPERPARAMETER of this script. Should it be change if:
#
#       * add or substract overhead (time to process each loop, or add/remove readers).
#       * modify the loop's delay in the corresponding Arduino sketch

from serial import Serial
import serial.tools.list_ports
import glob, time, sys
import asyncio
import websockets
from collections import defaultdict

current_reader = defaultdict(str) # get the readerID from port name
last_content = defaultdict(str) # last received (or not) content
nb_empty = defaultdict(int) # if receive over, say, 4 times raw empty content, then consider the card to have been removed, then reset the counter
current_card = defaultdict(str) # current card (inferred)
ws_sendtime = 0 # last time a message was sent via websocket, keep track of how frequently a message should be sent
last_message = "" # last message sent over websocket, get rid of sending the same message

async def send(message):
    uri = "ws://localhost:9080"
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        print(f"ws> {message}")

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
            
            if s == "": # decide whether to consider a card has been removed from a reader
                if last_content[device.name] != "":
                    nb_empty[device.name] = 0
                else:
                    if current_card[device.name] != "":
                        nb_empty[device.name] += 1 # increment only if before there was a card

                        if nb_empty[device.name] > 2: # the card should be not there any more
                            current_card[device.name] = "" # remove the card
                            nb_empty[device.name] = 0 # reinit the counter
            else:
                current_reader[device.name] = s.split(':')[0]
                current_card[device.name] = s.split(':')[1]

            last_content[device.name] = s

        if time.time() - ws_sendtime > 0.5: # consider to send a message only after some time
            ws_sendtime = time.time()
            
            # send only if there is no same card on 2 different readers (user moves too fast)
            current_cards = [current_card[device.name] for device in devices if current_card[device.name] != ""]
            if len(current_cards) == len(set(current_cards)):
                message = ";".join([current_reader[device.name]+":"+current_card[device.name] for device in devices if current_card[device.name] != ""])
                if  message != last_message:
                    asyncio.get_event_loop().run_until_complete(send(message))
                    last_message = message

        time.sleep(0.01)
