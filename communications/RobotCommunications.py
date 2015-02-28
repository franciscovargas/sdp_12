from Communications import Communications


class RobotCommunications(Communications):
    """
    STOP                A
    MOVE STRAIGHT       B
    STOP STRAIGHT       C
    MOVE SIDEWAYS       D
    MOVE DIAGONAL       E
    ROTATE              F
    ROTATE GRAB         G
    STOP ROTATE         H
    ACTION GRAB         I
    ACTION GRAB_CONT    J
    ACTION KICK         K
    """




    def __init__(self, debug=False):
        super(RobotCommunications, self).__init__(debug)

    # Stops all motors
    def stop(self):
        self.write("A")

    # Straight movement
    def moveStraight(self, motorPower):
        self.write("B " + str(motorPower))

    def stopStraight(self, motorPower):
        self.write("C " + str(motorPower))

    # Sideways LEFT  = -motorPower
    # Sideways RIGHT = +motorPower
    def moveSideways(self, motorPower):
        self.write("D " + str(motorPower))

    # Same as Sideways, it's just diagonal
    def moveDiagonalLeft(self, motorPower):
        self.write("E " + str(motorPower))

    def moveDiagonalRight(self, motorPower):
        self.write("E " + str(motorPower))

    # Rotate LEFT  = -motorPower
    # Rotate RIGHT = +motorPower
    def rotate(self, motorPower):
        self.write("F " + str(motorPower))

    # Rotate and Grab - 2 args: power_rotate, power_grab
    def rotateAndGrab(self, motorPower_r, motorPower_g):
        self.write("G " + str(motorPower_r) + " " + str(motorPower_g))

    def stopRotate(self, motorPower):
        self.write("H " + str(motorPower))

    # Grab and Kick take motorPower. The values should be predefined depending
    # on how far we need to kick or grab (it will probably be a constant)
    def grab(self, motorPower):
        self.write("I " + str(motorPower))

    def grab_cont(self, motorPower):
        self.write("J " + str(motorPower))

    def kick(self, motorPower):
        self.write("K " + str(motorPower))

    def test(self, argument):
        print 'I got your message: ' + str(argument)
