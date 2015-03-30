from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=False)
r.rotate(60)
time.sleep(1)
r.stopRotate(-30)