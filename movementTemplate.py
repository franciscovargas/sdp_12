"""
This file contains movement functions that need to be implemented.
The functions will be called from strategy.py and should communicate with the arduino directly.

Feel free to comment/add/delete as appropriate.
"""

# Move forwards/backwards with supplied power for given distance.
# (if power is negative, moves backwards)
# Maybe we can use time instead of distance and do the necessary calulations on the DICE.
def moveStraight(self, motorPower, distance)

# Moves forward/backwards for one step.
# The size of the step is questionable:
#   Either it can be the 1/200 seconds as Iuilia mentioned we will send this command to the robot once per every frame.
#   Or the size of the step can be one coordinate. For example, it will move the robot from (x,y) to (x+1,y).
def moveStraightOneStep(self, motorPower)

# Turns the robot by a given angle.
# Normally turn clock-wise. If motorPower is negative then turn anti clock-wise.
# Same as in moveForwards, it might be more efficient to use time instead of angle here.
def turnAngle(self, motorPower, angle)

# Turns the robot by one step in given direction.
# The step can either be a small number of degrees or just turn for a short time period(1/200 seconds).
def turnOneStep(self, direction)

# Moves the robot sideways.
# The direction depends on the motorPower.
# It should move a certain distance but we can use time instead of distance for reasons mentioned before.
def moveSideways(self, motorPower, distance)

# Moves the robot sideways by one step.
# The direction depends on the motorPower.
# Same size of step issue as in moveStraighOneStep.
# Since defending(blocking the other team's attacker) will be based on sideways movement,
#   I would prefer moving by one step instead of moveSideways(distance).
# This function makes the robot more reactive, faster to change the direction of movement.
# However, it might end up being to slow, we need to test it.(or brainstorm it)
def moveSidewaysOneStep(self, motorPower)

# Kicks the ball.
# Since our kicker is not super-strong, we should always use full power for kicking??????
def kick(self)

# Grabs the ball.
# Assumes the ball is stationary and positioned in front of the robot.
def grab(self)

# Moves the robot from current position to new postion.
# This should do the necessary calculations and then call some of the functions above.
# If we are using moveOneStep and turnOneStep, we probably do not need this function.
def moveFromTo(self, from_X, from_Y, from_Angle, to_X, to_Y, to_Angle)

# Stops the robot from doing whatever he is doing.
# Might be useful to avoid collisions or penalties.
def stop(self)
