from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=True)
r.moveSideways(100)
time.sleep(2)
r.stop()
time.sleep(1)
r.moveSideways(-100)
time.sleep(2)
r.stop()