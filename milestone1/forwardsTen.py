from RobotCommunications import RobotCommunications
import time


r = RobotCommunications(debug=True)
r.moveForwards(100)
time.sleep(1)
r.stop()
