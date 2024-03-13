import time
import serial
import serial.tools.list_ports

global COM_port


def init():
    # Query the Device Manager of your Windows PC to find out which COM port the
    # system assigned to the XL2 and adapt the following line:
    global COM_port
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        if "067B:23A3" in hwid:
            COM_port = port
            print(COM_port)


def set_units():
    # change the default setting (miles/h) to (km/h)
    ser = serial.Serial(
        port=COM_port,  # replace with your serial port name
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

    # Send the hexadecimal value of the packet
    data_byte = bytes([0xEF, 0x02, 0x01, 0x00, 0x03, 0x00, 0x94, 0x00, 0x01, 0x88, 0x03])

    ser.write(data_byte)


def measure_speed():
    ser = serial.Serial(
        port=COM_port,  # replace with your serial port name
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

    response = ser.read(32)

    start_index = response.find(b'\x81')
    if start_index >= 0:
        my_slice = response[start_index:start_index + 16]  # slice the byte string from the start index to 16 bytes

    speed_ones = chr(my_slice[14])
    speed_tens = chr(my_slice[13])
    speed_hundreds = chr(my_slice[12])
    speed = speed_hundreds + speed_tens + speed_ones
    ser.close()
    return speed


def forking_mode_on():
    ser = serial.Serial(
        port=COM_port,  # replace with your serial port name
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

    # Send the hexadecimal value of the packet (see appendix E configuration
    # protocol in manual from stalker page E-1).
    data_byte = bytes([0xEF, 0x02, 0x01, 0x00, 0x03, 0x00, 0xAF, 0x00, 0x01, 0xA3, 0x03])

    ser.write(data_byte)

    # Close the serial port
    ser.close()


def forking_mode_off():
    ser = serial.Serial(
        port=COM_port,  # replace with your serial port name
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

    # Send the hexadecimal value of the packet (see appendix E configuration
    # protocol in manual from stalker page E-1).
    data_byte = bytes([0xEF, 0x02, 0x01, 0x00, 0x03, 0x00, 0xAF, 0x00, 0x00, 0xA2, 0x03])

    ser.write(data_byte)

    # Close the serial port
    ser.close()
