from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=False)
r.kick(100)
r.stop()
