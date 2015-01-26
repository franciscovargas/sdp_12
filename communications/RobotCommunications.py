from Communications import Communications
import time


class RobotCommunications(Communications):

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

    def __init__(self, debug=False):
        super(RobotCommunications, self).__init__(debug)

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

    def moveForwards(self, motorPower):
        self.write("LEFT_MOTOR ON FORWARDS " + str(motorPower))
        self.write("RIGHT_MOTOR ON FORWARDS " + str(motorPower))

    def moveBackwards(self, motorPower):
        self.write("LEFT_MOTOR ON BACKWARDS " + str(motorPower))
        self.write("RIGHT_MOTOR ON BACKWARDS " + str(motorPower))

    def moveSidewaysLeft(self, motorPower):
        self.write("BACK_MOTOR ON FORWARDS " + str(motorPower))

    def moveSidewaysRight(self, motorPower):
        self.write("BACK_MOTOR ON BACKWARDS " + str(motorPower))

    def rotateLeft(self, motorPower):
        self.write("RIGHT_MOTOR ON FORWARDS " + str(motorPower))
        self.write("LEFT_MOTOR ON BACKWARDS " + str(motorPower))
        self.write("BACK_MOTOR ON FORWARDS " + str(motorPower))

    def rotateRight(self, motorPower):
        self.write("RIGHT_MOTOR ON BACKWARDS " + str(motorPower))
        self.write("LEFT_MOTOR ON FORWARDS " + str(motorPower))
        self.write("BACK_MOTOR ON BACKWARDS" + str(motorPower))

    def turnLeft(self, motorPower, ratio):
        self.write("LEFT_MOTOR ON FORWARDS " + str(motorPower))
        self.write("RIGHT_MOTOR ON FORWARDS " + str(motorPower))
        self.write("BACK_MOTOR ON FORWARDS " + str(motorPower))

    def turnRight(self, motorPower, ratio):
        self.write("RIGHT_MOTOR ON FORWARDS " + str(motorPower))
        self.write("LEFT_MOTOR ON FORWARDS " + str(motorPower))
        self.write("BACK_MOTOR ON BACKWARDS" + str(motorPower))

    def stop(self):
        self.write("LEFT_MOTOR ON FORWARDS 0")
        self.write("RIGHT_MOTOR ON FORWARDS 0")
        self.write("BACK_MOTOR ON FORWARDS 0")
        self.write("KICK_MOTOR ON FORWARDS 0")

    def catch(self):
        self.write("KICK_MOTOR ON BACKWARDS 60") # update
        time.sleep(0.3)
        self.write("KICK_MOTOR ON BACKWARDS 0")

    def kick(self, motorPower):
        self.write("KICK_MOTOR ON FORWARDS " + str(motorPower))
        time.sleep(0.25)
        self.write("KICK_MOTOR ON FORWARDS 0")

    def shoot(self):
        self.kick(100)

    def passBall(self):
        self.kick(60) # update
