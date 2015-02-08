from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=True)
r.rotate(100)
time.sleep(1)
r.rotate(-30)
time.sleep(0.5)
r.stop()
