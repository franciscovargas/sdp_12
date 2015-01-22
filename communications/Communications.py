import serial
import time

class Communications(object):

    def __init__(self,
                 debug=False,
                 setConnectionOff=False,
                 port='/dev/ttyACM0',
                 baudrate=9600,
                 timeout=2):
        if setConnectionOff is False:

            try:
                self.port = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
                self.debug = debug
                time.sleep(0.5)
            except:
                raise BaseException("Radio not connected or wrong port supplied.")

    def write(self, command):
        self.port.write(command + '\r\n')
        if self.debug:
            print self.port.readline()

'''if __name__ == '__main__':
    c = Communications(debug=True)'''

class RobotCommunication(Communications):
	def __init__(self, debug=False):
		super(RobotCommunication, self).__init__(debug)

	def turn_on(self):			
		self.write("ON")

	def turn_off(self):
		self.write("OFF")

	def blink(self, arg):
		self.write("BLINK " + str(arg))

	def say_hello(self):
		self.write("HELLO")
	
	def add(self, arg1, arg2):
		self.write("ADD " + str(arg1) + " " + str(arg2))




