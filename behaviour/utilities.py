from math import tan, pi, hypot, log, copysign
from world import Robot

BALL_ALIGN_THRESHOLD = 10
ROBOT_ALIGN_THRESHOLD = pi/4

POWER_SIDEWAYS = 80
POWER_STRAIGHT = 70
POWER_STOP_STRAIGHT = 70
POWER_ROTATE = 40
POWER_STOP_ROTATION = 30
POWER_GRAB = 60
POWER_KICK = 100

# Stop everything
def stop(robotCom):
    robotCom.stop()

# Moving sideways
def moveSideways(robotCom, displacement):
    if abs(displacement) > BALL_ALIGN_THRESHOLD:
        power = copysign(POWER_SIDEWAYS, displacement)
        robotCom.moveSideways(power)
    else:
        robotCom.stop()

# Move straight indefinitely trying to defend
def moveStraight(robotCom, displacement):
    if abs(displacement) > BALL_ALIGN_THRESHOLD:
        power = copysign(POWER_STRAIGHT, displacement)
        robotCom.moveStraight(power)
    else:
        robotCom.stopStraight(-POWER_STOP_STRAIGHT)

# Move straight, with speed relative to the distance left to cover
def moveStraight(robotCom, displacement):
    if abs(displacement) > BALL_ALIGN_THRESHOLD:
        power = (POWER_STRAIGHT * 0.005 * displacement) + copysign(40, displacement)
        robotCom.moveStraight(power)
    else:
        robotCom.stop()

# Move from A to B
def moveFromTo(robotCom, displacement, angle):
    if abs(angle) > ROBOT_ALIGN_THRESHOLD:
        align_robot(robotCom, angle, 0, ROBOT_ALIGN_THRESHOLD)
    elif not (displacement is None):
        moveStraight(robotCom, displacement)
    else:
        stop(robotCom)

# Grab the ball
def grab(robotCom):
    robotCom.grab(POWER_GRAB)

# Kick the ball, full power
def kick(robotCom):
    robotCom.kick(POWER_KICK)

# rotate the robot until it is at the target alignment, with speed relative to
# the difference between the robot and target alignments
def align_robot(robotCom, robot_alignment, target_alignment, angle_threshold):
    difference = normalize_angle(robot_alignment, target_alignment)
    print "Difference: " + str(difference)

    if (difference > pi):
        direction = 1
        difference = 2*pi - difference
    else:
        direction = -1

    if(difference > angle_threshold and difference < 2*pi - angle_threshold):
        print "Aligning..."
        power = (POWER_ROTATE * 0.15 * difference) + 30
        print "Power: " + str(power)
        robotCom.rotate(direction * power)
        return False
    else:
        robotCom.stopRotate(direction * -POWER_STOP_ROTATION)
        return True

# to find the angle between the robot's alignment and our target alignment,
# makes the target angle 0/the origin, and returns the robot's alignment in terms of that
def normalize_angle(robot_alignment, target_alignment):
    robot_alignment -= target_alignment

    if(robot_alignment >= 2*pi):
        robot_alignment -= 2*pi
    elif(robot_alignment < 0):
        robot_alignment += 2*pi

    return robot_alignment



# not using the below






# Variables used by old code.
DISTANCE_MATCH_THRESHOLD = 20
ANGLE_MATCH_THRESHOLD = pi/10
BALL_ANGLE_THRESHOLD = pi/20
MAX_DISPLACEMENT_SPEED = 690
MAX_ANGLE_SPEED = 50
BALL_MOVING = 3

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


def is_attacker_shot_blocked(world, our_attacker, their_defender):
    '''
    Checks if our attacker would score if it would immediately turn and shoot.
    '''

    # Acceptable distance that the opponent defender can be relative to our
    # shooting position in order for us to have a clear shot.
    distance_threshold = 40

    # Return True if attacker and defender ar close to each other on
    # the y dimension
    return abs(our_attacker.y - their_defender.y) < distance_threshold


def can_score(world, our_robot, their_goal, turn=0):
    # Offset the robot angle if need be
    robot_angle = our_robot.angle + turn
    goal_zone_poly = world.pitch.zones[their_goal.zone][0]

    reverse = True if their_goal.zone == 3 else False
    goal_posts = sorted(goal_zone_poly, key=lambda x: x[0], reverse=reverse)[:2]
    # Makes goal be sorted from smaller to bigger
    goal_posts = sorted(goal_posts, key=lambda x: x[1])

    goal_x = goal_posts[0][0]

    robot = Robot(
        our_robot.zone, our_robot.x, our_robot.y, robot_angle % (pi * 2), our_robot.velocity)

    predicted_y = predict_y_intersection(world, goal_x, robot, full_width=True)

    return goal_posts[0][1] < predicted_y < goal_posts[1][1]

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


def open_catcher():
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
