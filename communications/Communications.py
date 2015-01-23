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

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

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

    def moveForward(self, motorPower):
        self.write("LEFT_MOTOR ON FORWARD " + str(motorPower))
        self.write("RIGHT_MOTOR ON FORWARD " + str(motorPower))

    def moveBackward(self, motorPower):
        self.write("LEFT_MOTOR ON BACKWARD " + str(motorPower))
        self.write("RIGHT_MOTOR ON BACKWARD " + str(motorPower))

    def moveSideWaysLeft(self, motorPower):
        self.write("BACK_MOTOR ON BACKWARD " + str(motorPower))

    def moveSideWaysRight(self, motorPower):
        self.write("BACK_MOTOR ON FORWARD " + str(motorPower))

    def rotateLeft(self, motorPower):
        self.write("RIGHT_MOTOR ON FORWARD " + str(motorPower))
        self.write("LEFT_MOTOR ON BACKWARD " + str(motorPower))
        self.write("BACK_MOTOR ON FORWARD " + str(motorPower))

    def rotateRight(self, motorPower):
        self.write("RIGHT_MOTOR ON BACKWARD " + str(motorPower))
        self.write("LEFT_MOTOR ON FORWARD " + str(motorPower))
        self.write("BACK_MOTOR ON BACKWARD" + str(motorPower))

    def turnLeft(self, motorPower, ratio):
        self.write("LEFT_MOTOR ON FORWARD " + str(motorPower))
        self.write("RIGHT_MOTOR ON FORWARD " + str(motorPower))
        self.write("BACK_MOTOR ON FORWARD " + str(motorPower))

    def turnRight(self, motorPower, ratio):
        self.write("RIGHT_MOTOR ON FORWARD " + str(motorPower))
        self.write("LEFT_MOTOR ON FORWARD " + str(motorPower))
        self.write("BACK_MOTOR ON BACKWARD" + str(motorPower))

    def stop(self):
        self.write("LEFT_MOTOR ON FORWARD 0")
        self.write("RIGHT_MOTOR ON FORWARD 0")
        self.write("BACK_MOTOR ON FORWARD 0")
        self.write("KICK_MOTOR ON FORWARD 0")

    def catch(self):
        self.write("KICK_MOTOR ON BACKWARD 10") # update

    def kick(self, motorPower):
        self.write("KICK_MOTOR ON FORWARD " + str(motorPower))

    def shoot(self):
        self.kick(100)

    def passBall(self):
        self.kick(50) # update
