from math import tan, pi, hypot, log, copysign
from world import Robot
import time

BALL_APPROACH_THRESHOLD = 30
ROBOT_ALIGN_THRESHOLD = pi/10

POWER_SIDEWAYS = 80
POWER_STRAIGHT_MODIFIER = 60
POWER_STRAIGHT_BASE = 40
POWER_STOP_STRAIGHT = 70
POWER_ROTATE_MODIFIER = 3.5
POWER_ROTATE_BASE = 25
POWER_STOP_ROTATION = 25
POWER_GRAB = 100
POWER_KICK = 100

BALL_MOVING = 3

# Stop everything
def stop(robotCom):
    robotCom.stop()

# Moving sideways
def moveSideways(robotCom, displacement):
    if abs(displacement) > BALL_APPROACH_THRESHOLD:
        power = copysign(POWER_SIDEWAYS, displacement)
        robotCom.moveSideways(power)
    else:
        robotCom.stop()

# # Move straight indefinitely trying to defend
# def moveStraight(robotCom, displacement):
#     if abs(displacement) > BALL_APPROACH_THRESHOLD:
#         power = copysign(POWER_STRAIGHT, displacement)
#         robotCom.moveStraight(power)
#     else:
#         robotCom.stopStraight(-POWER_STOP_STRAIGHT)

# Move straight, with speed relative to the distance left to cover
def moveStraight(robotCom, displacement):
    print "Absolute displacement to destination: %d" % displacement
    if abs(displacement) > BALL_APPROACH_THRESHOLD:
        power = (POWER_STRAIGHT_MODIFIER * 0.005 * displacement) + copysign(POWER_STRAIGHT_BASE, displacement)
        robotCom.moveStraight(power)
    else:
        robotCom.stop()

# Grab the ball
def grab(robotCom):
    robotCom.grab(POWER_GRAB)
    time.sleep(0.5)

# Kick the ball, full power
def kick(robotCom):
    robotCom.kick(POWER_KICK)
    time.sleep(0.5)

# rotate the robot until it is at the target angle, with speed relative to
# the difference between the robot and target angles
def align_robot(robotCom, angle, angle_threshold, grab=False):
    #angle = normalize_angle(angle)
    #print "Normalized angle: %f" % angle

    if(abs(angle) > angle_threshold):
        print "Aligning..."
        power = (POWER_ROTATE_MODIFIER * angle) + copysign(POWER_ROTATE_BASE, angle)
        print "Power: " + str(power)
        if grab:
            print "Rotating and grabbing"
            robotCom.rotateAndGrab(power, 100)
        else:
            print "Rotating without grabbing"
            robotCom.rotate(power)
        return False
    else:
        robotCom.stop()
        return True

def align_robot_to_pitch(robotCom, robot_angle, pitch_alignment_angle, grab=False):
    absolute_angle = pitch_alignment_angle - robot_angle
    return align_robot(robotCom, absolute_angle, ROBOT_ALIGN_THRESHOLD, grab)


# to find the angle between the robot's angle and our target angle,
# makes the target angle 0/the origin, and returns the robot's angle in terms of that
def normalize_angle(angle):

    if(angle >= 2*pi):
        angle -= 2*pi
    elif(angle < 0):
        angle += 2*pi

    return angle
# not using the below






# Variables used by old code.
DISTANCE_MATCH_THRESHOLD = 20
ANGLE_MATCH_THRESHOLD = pi/10
BALL_ANGLE_THRESHOLD = pi/20
MAX_DISPLACEMENT_SPEED = 690
MAX_ANGLE_SPEED = 50

def is_shot_blocked(world, our_robot, their_robot):
    '''
    Checks if our robot could shoot past their robot
    '''
    predicted_y = predict_y_intersection(
        world, their_robot.x, our_robot, full_width=True, bounce=True)
    if predicted_y is None:
        return True
    print '##########', predicted_y, their_robot.y, their_robot.length
    print abs(predicted_y - their_robot.y) < their_robot.length
    return abs(predicted_y - their_robot.y) < their_robot.length

def predict_y_intersection(world, predict_for_x, robot, full_width=False, bounce=False):
        '''
        Predicts the (x, y) coordinates of the ball shot by the robot
        Corrects them if it's out of the bottom_y - top_y range.
        If bounce is set to True, predicts for a bounced shot
        Returns None if the robot is facing the wrong direction.
        '''
        x = robot.x
        y = robot.y
        top_y = world._pitch.height - 60 if full_width else world.our_goal.y + (world.our_goal.width/2) - 30
        bottom_y = 60 if full_width else world.our_goal.y - (world.our_goal.width/2) + 30
        angle = robot.angle
        if (robot.x < predict_for_x and not (pi/2 < angle < 3*pi/2)) or (robot.x > predict_for_x and (3*pi/2 > angle > pi/2)):
            if bounce:
                if not (0 <= (y + tan(angle) * (predict_for_x - x)) <= world._pitch.height):
                    bounce_pos = 'top' if (y + tan(angle) * (predict_for_x - x)) > world._pitch.height else 'bottom'
                    x += (world._pitch.height - y) / tan(angle) if bounce_pos == 'top' else (0 - y) / tan(angle)
                    y = world._pitch.height if bounce_pos == 'top' else 0
                    angle = (-angle) % (2*pi)
            predicted_y = (y + tan(angle) * (predict_for_x - x))
            # Correcting the y coordinate to the closest y coordinate on the goal line:
            if predicted_y > top_y:
                return top_y
            elif predicted_y < bottom_y:
                return bottom_y
            return predicted_y
        else:
            return None

def grab_ball():
    return {'left_motor': 0, 'right_motor': 0, 'kicker': 0, 'catcher': 1, 'speed': 1000}


def kick_ball():
    return {'left_motor': 0, 'right_motor': 0, 'kicker': 1, 'catcher': 0, 'speed': 1000}

def turn_shoot(orientation):
    return {'turn_90': orientation, 'left_motor': 0, 'right_motor': 0, 'kicker': 1, 'catcher': 0, 'speed': 1000}


def has_matched(robot, x=None, y=None, angle=None,
                angle_threshold=ANGLE_MATCH_THRESHOLD, distance_threshold=DISTANCE_MATCH_THRESHOLD):
    dist_matched = True
    angle_matched = True
    if not(x is None and y is None):
        dist_matched = hypot(robot.x - x, robot.y - y) < distance_threshold
    if not(angle is None):
        angle_matched = abs(angle) < angle_threshold
    return dist_matched and angle_matched


def calculate_motor_speed(displacement, angle, backwards_ok=False, careful=False):
    '''
    Simplistic view of calculating the speed: no modes or trying to be careful
    '''
    moving_backwards = False
    general_speed = 95 if careful else 300
    angle_thresh = BALL_ANGLE_THRESHOLD if careful else ANGLE_MATCH_THRESHOLD

    if backwards_ok and abs(angle) > pi/2:
        angle = (-pi + angle) if angle > 0 else (pi + angle)
        moving_backwards = True

    if not (displacement is None):

        if displacement < DISTANCE_MATCH_THRESHOLD:
            return {'left_motor': 0, 'right_motor': 0, 'kicker': 0, 'catcher': 0, 'speed': general_speed}

        elif abs(angle) > angle_thresh:
            speed = (angle/pi) * MAX_ANGLE_SPEED
            return {'left_motor': -speed, 'right_motor': speed, 'kicker': 0, 'catcher': 0, 'speed': general_speed}

        else:
            speed = log(displacement, 10) * MAX_DISPLACEMENT_SPEED
            speed = -speed if moving_backwards else speed
            # print 'DISP:', displacement
            if careful:
                return {'left_motor': speed, 'right_motor': speed, 'kicker': 0, 'catcher': 0, 'speed': 1000/(1+10**(-0.1*(displacement-85)))}
            return {'left_motor': speed, 'right_motor': speed, 'kicker': 0, 'catcher': 0, 'speed': 1000/(1+10**(-0.1*(displacement-30)))}

    else:

        if abs(angle) > angle_thresh:
            speed = (angle/pi) * MAX_ANGLE_SPEED
            return {'left_motor': -speed, 'right_motor': speed, 'kicker': 0, 'catcher': 0, 'speed': general_speed}

        else:
            return {'left_motor': 0, 'right_motor': 0, 'kicker': 0, 'catcher': 0, 'speed': general_speed}



def do_nothing():
    pass
