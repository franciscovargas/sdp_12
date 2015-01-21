import serial

class Communications:
    def __init__(self, debug):
        self.port = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=2)
        self.debug = debug

    def write(self, command):
        self.port.write(command + '\n')
        if self.debug:
            print self.port.readline()
