from Communications import Communications
import time


class RobotCommunications(Communications):

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

    def __init__(self, debug=False):
        super(RobotCommunications, self).__init__(debug)

    def stop(self):
        self.write("STOP")

    def moveStraight(self, motorPower):
        self.write("MOVE STRAIGHT " + str(motorPower))

    def moveSidewaysLeft(self, motorPower):
        self.write("MOVE SIDEWAYS L " + str(motorPower))

    def moveSidewaysRight(self, motorPower):
        self.write("MOVE SIDEWAYS R " + str(motorPower))

    def moveDiagonalLeft(self, motorPower):
        self.write("MOVE DIAGONAL L " + str(motorPower))

    def moveDiagonalRight(self, motorPower):
        self.write("MOVE DIAGONAL R " + str(motorPower))

    def rotateLeft(self, motorPower, time):
        self.write("ROTATE L " + str(motorPower) + " " + str(time))

    def rotateRight(self, motorPower, time):
        self.write("ROTATE R " + str(motorPower) + " " + str(time))

    def grab(self, motorPower):
        self.write("ACTION GRAB " + str(motorPower))

    def kick(self, motorPower):
        self.write("ACTION KICK " + str(motorPower))