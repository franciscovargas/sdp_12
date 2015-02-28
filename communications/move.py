from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=True)
r.kick(100)
time.sleep(0.5)
r.stop()
