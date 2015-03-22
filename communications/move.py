from RobotCommunications import RobotCommunications
import time
import random

r = RobotCommunications(debug=True)
r.moveSideways(100)
time.sleep(0.8)
r.rotate(80)
time.sleep(0.4)
r.stop()
r.kick(20)
time.sleep(0.3)
r.stop()
