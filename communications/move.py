from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=True)
r.moveStraight(100)
time.sleep(0.2)
r.stop()
