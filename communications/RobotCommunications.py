from Communications import Communications
import time


class RobotCommunications(Communications):

    LEFT_WHEEL_MOTOR = 1
    RIGHT_WHEEL_MOTOR = 2
    BACK_WHEEL_MOTOR = 3
    KICK_MOTOR = 4

    def __init__(self, debug=False):
        super(RobotCommunications, self).__init__(debug)

    # Stops all motors
    def stop(self):
        self.write("STOP")

    # Straight movement
    def moveStraight(self, motorPower):
        self.write("MOVE STRAIGHT " + str(motorPower))

    # Sideways LEFT  = -motorPower
    # Sideways RIGHT = +motorPower
    def moveSideways(self, motorPower):
        self.write("MOVE SIDEWAYS L " + str(motorPower))

    # Same as Sideways, it's just diagonal
    def moveDiagonalLeft(self, motorPower):
        self.write("MOVE DIAGONAL L " + str(motorPower))

    def moveDiagonalRight(self, motorPower):
        self.write("MOVE DIAGONAL R " + str(motorPower))

    # Rotate LEFT  = -motorPower
    # Rotate RIGHT = +motorPower
    def rotate(self, motorPower):
        self.write("ROTATE R " + str(motorPower))

    # Grab and Kick take motorPower. The values should be predefined depending
    # on how far we need to kick or grab (it will probably be a constant)
    def grab(self, motorPower):
        self.write("ACTION GRAB " + str(motorPower))

    def kick(self, motorPower):
        self.write("ACTION KICK " + str(motorPower))

    def test(self, argument):
        print 'I got your message: ' + str(argument)