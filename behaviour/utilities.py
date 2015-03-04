from math import tan, pi, hypot, log, copysign
from world import Robot
import time

BALL_APPROACH_THRESHOLD = 55

BACK_OFF_THRESHOLD = 25

BALL_ALIGN_THRESHOLD = 20

ROBOT_ALIGN_THRESHOLD = pi/12

PRECISE_BALL_ANGLE_THRESHOLD = pi/8

POWER_SIDEWAYS_MODIFIER = 0.5
POWER_SIDEWAYS_BASE = 45

POWER_STRAIGHT_MODIFIER = 0.3
POWER_STRAIGHT_BASE = 30

# POWER_ROTATE_MODIFIER = 1.5
# POWER_ROTATE_BASE = 25
POWER_ROTATE_MODIFIER = 1.2
POWER_ROTATE_BASE = 23

POWER_GRAB = 30
POWER_KICK = 100

BALL_MOVING = 3

LEFT_DEFENDER_ZONE_THRESHOLD = 115
RIGHT_DEFENDER_ZONE_THRESHOLD = 500


# Stop everything
def stop(robotCom):
    robotCom.stop()


# Moving sideways
def moveSideways(robotCom, displacement, side):
    # print "Absolute displacement to destination: %d" % displacement
    side_modifier = -1 if side == 'right' else 1
    if abs(displacement) > BALL_ALIGN_THRESHOLD:
        power = side_modifier * \
            ((POWER_SIDEWAYS_MODIFIER * displacement) +
             copysign(POWER_SIDEWAYS_BASE, displacement))
        robotCom.moveSideways(power)
    else:
        robotCom.stop()


# Move straight, with speed relative to the distance left to cover
def moveStraight(robotCom, displacement, threshold=BALL_APPROACH_THRESHOLD):
    print "Absolute displacement to destination: %d" % displacement
    if abs(displacement) > threshold:
        power = (POWER_STRAIGHT_MODIFIER * displacement) \
            + copysign(POWER_STRAIGHT_BASE, displacement)
        robotCom.moveStraight(power)
    else:
        robotCom.stop()


# Grab the ball
def grab(robotCom):
    robotCom.grab(POWER_GRAB)
    # time.sleep(0.5)


# Open the grabber without kickingROBOT_ALIGN_THRESHOLD
def openGrabber(robotCom):
    robotCom.grab(-POWER_GRAB)
    #time.sleep(0.5)


# Kick the ball, full power
def kick(robotCom):
    robotCom.kick(POWER_KICK)
    # time.sleep(1)


# rotate the robot until it is at the target angle, with speed relative to
# the difference between the robot and target angles
def align_robot(robotCom, angle, grab=False):
    if(abs(angle) > ROBOT_ALIGN_THRESHOLD):
        power = (POWER_ROTATE_MODIFIER * angle) + copysign(POWER_ROTATE_BASE, angle)
        if grab:
            # power = power * 1.2
            robotCom.rotateAndGrab(power, POWER_GRAB)
        else:
            robotCom.rotate(power)
        return False
    else:
        # robotCom.stop()
        return True


def align_robot_to_pitch(robotCom, robot_angle, pitch_alignment_angle, grab=False):
    absolute_angle = normalize_angle(robot_angle, pitch_alignment_angle)
    return align_robot(robotCom, absolute_angle, grab)


# to find the angle between the robot's angle and our target angle,
# makes the target angle 0/the origin, and returns the robot's angle in terms of that
def normalize_angle(robot_angle, target_angle):
    normalized_angle = target_angle - robot_angle

    if(normalized_angle > pi):
        normalized_angle -= 2*pi
    elif(normalized_angle < -pi):
        normalized_angle += 2*pi

    return normalized_angle


def back_off(robotCom, side, robot_angle, robot_x):
    if side == 'left':
        print 'on left side'
        if robot_x > LEFT_DEFENDER_ZONE_THRESHOLD:
            print 'over left threshold, aligning'
            if align_robot_to_pitch(robotCom, robot_angle, 0):
                print 'aligned'
                moveStraight(robotCom, -30, BACK_OFF_THRESHOLD)
                return False
        else:
            stop(robotCom)
            return True
    if side == 'right':
        print 'on right side'
        if robot_x < RIGHT_DEFENDER_ZONE_THRESHOLD:
            print 'over right threshold, aligning'
            if align_robot_to_pitch(robotCom, robot_angle, pi):
                print 'aligned'
                moveStraight(robotCom, -30, BACK_OFF_THRESHOLD)
                return False
        else:
            stop(robotCom)
            return True

            # re-align robot towards goal
            # move backwards until 20 (?) from threshold


def is_shot_blocked(world, our_robot, their_robot):
    '''
    Checks if our robot could shoot past their robot
    returns true if robot is facing the wrong direction
    '''
    # predicted_y = predict_y_intersection(
    #     world, their_robot.x, our_robot, full_width=True, bounce=False)
    # if predicted_y is None:
    #     return True
    # print "Predicted y: " + str(predicted_y) + " Their robot's y: " + str(their_robot.y) + "Their robot's length: " + str(their_robot.length)
    # print "Shot blocked: ", abs(predicted_y - their_robot.y) < their_robot.length
    # return abs(predicted_y - their_robot.y) < their_robot.length
    return abs(their_robot.y - our_robot.y) < 40


def predict_y_intersection(world,
                           predict_for_x,
                           robot,
                           full_width=False,
                           bounce=False):
        '''
        Predicts the y coordinate  for the x coordinate provided returns
        None if robot is facing the wrong direction
        '''
        x = robot.x
        y = robot.y

        if full_width:
            top_y = world._pitch.height - 60
            bottom_y = 60
        else:
            top_y = world.our_goal.y + (world.our_goal.width/2) - 70
            bottom_y = world.our_goal.y - (world.our_goal.width/2) + 70

        angle = robot.angle

        # Checks if robot is facing the correct direction
        if (robot.x < predict_for_x and not (pi/2 < angle < 3*pi/2)) or \
           (robot.x > predict_for_x and (3*pi/2 > angle > pi/2)):

            predicted_y = (y + tan(angle) * (predict_for_x - x))

            # Correcting the y coordinate to the closest y coordinate on the goal line:
            if predicted_y > top_y:
                return top_y
            elif predicted_y < bottom_y:
                return bottom_y
            else:
                return predicted_y

        else:
            return None

# not using the below






# Variables used by old code.
DISTANCE_MATCH_THRESHOLD = 20
ANGLE_MATCH_THRESHOLD = pi/10
BALL_ANGLE_THRESHOLD = pi/20
MAX_DISPLACEMENT_SPEED = 690
MAX_ANGLE_SPEED = 50




def has_matched(robot, x=None, y=None, angle=None,
                angle_threshold=ANGLE_MATCH_THRESHOLD,
                distance_threshold=DISTANCE_MATCH_THRESHOLD):
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
            return {'left_motor': 0,
                    'right_motor': 0,
                    'kicker': 0,
                    'catcher': 0,
                    'speed': general_speed}

        elif abs(angle) > angle_thresh:
            speed = (angle/pi) * MAX_ANGLE_SPEED
            return {'left_motor': -speed,
                    'right_motor': speed,
                    'kicker': 0,
                    'catcher': 0,
                    'speed': general_speed}

        else:
            speed = log(displacement, 10) * MAX_DISPLACEMENT_SPEED
            speed = -speed if moving_backwards else speed
            # print 'DISP:', displacement
            if careful:
                return {'left_motor': speed,
                        'right_motor': speed,
                        'kicker': 0, 'catcher': 0,
                        'speed': 1000/(1+10**(-0.1*(displacement-85)))}
            return {'left_motor': speed,
                    'right_motor': speed,
                    'kicker': 0,
                    'catcher': 0,
                    'speed': 1000/(1+10**(-0.1*(displacement-30)))}

    else:

        if abs(angle) > angle_thresh:
            speed = (angle/pi) * MAX_ANGLE_SPEED
            return {'left_motor': -speed,
                    'right_motor': speed,
                    'kicker': 0,
                    'catcher': 0,
                    'speed': general_speed}

        else:
            return {'left_motor': 0,
                    'right_motor': 0,
                    'kicker': 0,
                    'catcher': 0,
                    'speed': general_speed}


def do_nothing():
    pass
