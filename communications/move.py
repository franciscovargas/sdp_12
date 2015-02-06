from RobotCommunications import RobotCommunications
import time

r = RobotCommunications(debug=True)
r.rotate(50)
time.sleep(1)
r.stop()