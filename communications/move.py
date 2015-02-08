from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=True)
r.moveStraight(60)
time.sleep(1)
r.stop()