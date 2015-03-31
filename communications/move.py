from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=False)
r.speed_kick(100, 100, -25)