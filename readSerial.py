# This script work with serial devices emitting one line of text at a time (Serial.println), at 9600 baud rate.

from serial import Serial
import glob, time, sys

def get_port():
    """
    This function let the user choose one or more ports to hear from
    """

    # detect serial devices
    ports = glob.glob('/dev/tty.usb*')
    if not len(ports):
        raise IOError("no device detected")

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
    except (IOError, ValueError) as e:
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