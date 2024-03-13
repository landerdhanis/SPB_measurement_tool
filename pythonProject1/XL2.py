import time
import serial
import serial.tools.list_ports
from datetime import datetime
global COM_port
global xl2

def read_xl2():
    global xl2
    xl2.write(b'MEAS:INIT\n')  # Triggers a measurement
    xl2.write(b'MEAS:SLM:123? LAFMAX\n')  # Query LAFMAX
    result = xl2.readline()
    print(result)
    xl2.write(b'INIT STOP\n')  # Stop the measurement (optional)
    return result


def measure_RTA():
    global xl2
    xl2.write(b'MEAS:INIT\n')
    xl2.write(b'MEAS:SLM:RTA? Live\n')
    result = xl2.readline()
    print(result)
    return result

def measure_Laf():
    global xl2
    xl2.write(b'MEAS:INIT\n')  # Triggers a measurement
    xl2.write(b'MEAS:SLM:123? LAF\n')  # Query LAFMAX
    result = xl2.readline()
    return result


def start_measurement():
    global xl2
    xl2 = serial.Serial(COM_port, timeout=1)
    xl2.write(b'INIT START\n')  # Start the measurement
    time.sleep(3)  # Allow the XL2 to start the measurement


def stop_measurement():
    global xl2
    xl2.write(b'INIT STOP\n')
    xl2.close()


def reset_xl2():
    global xl2
    xl2.write(b'*RST\n')  # Reset the XL2 to default state (SLMeter, ...)


def init():
    # Query the Device Manager of your Windows PC to find out which COM port the
    # system assigned to the XL2 and adapt the following line:
    global COM_port
    global xl2
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        if "1A2B:0004" in hwid:
            COM_port = port
            print(COM_port)
