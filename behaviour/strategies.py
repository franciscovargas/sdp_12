from utilities import rotate_robot, align_robot, align_robot_to_y_axis, predict_y_intersection, moveStraight, moveSideways, has_matched, \
    stop, do_nothing, BALL_MOVING, kick, grab, openGrabber, ROBOT_ALIGN_THRESHOLD, back_off, PRECISE_BALL_ANGLE_THRESHOLD, \
    ball_moving_to_us, BALL_ALIGN_THRESHOLD, DEFENDING_PITCH_EDGE, robot_is_aligned, robot_is_aligned_to_y_axis, robot_within_goal, \
    robot_within_zone, back_off_from_goal, speed_kick
from math import pi, sin, cos
from random import randint
# Up until here are the imports that we're using

# Imports from their code that are needed to compile (and maybe later)
from utilities import calculate_motor_speed, is_shot_blocked
import time


class Strategy(object):

    UP, DOWN = 'UP', 'DOWN'

    def __init__(self, world, states):
        self.world = world
        self.states = states
        self._current_state = states[0]
        self.our_side = self.world._our_side
        self.pitch_centre = pi if self.our_side == 'right' else 0

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        assert new_state in self.states
        self._current_state = new_state

    def reset_current_state(self):
        self._current_state = self.states[0]

    def is_last_state(self):
        return self._current_state == self.states[-1]

    def next_action(self):
        return self.NEXT_ACTION_MAP[self.current_state]()


# Defend against incoming ball
class Defending(Strategy):

    STATES = ['UNALIGNED',
              'CLOSE_GRABBER',
              'MOVE_BACK',
              'MOVE_FORWARD',
              'DEFEND_GOAL']

    def __init__(self, world, robotCom):
        super(Defending, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            'UNALIGNED': self.align,
            'CLOSE_GRABBER': self.close_grabber,
            'MOVE_BACK': self.move_back,
            'MOVE_FORWARD': self.move_forward,
            'DEFEND_GOAL': self.defend_goal
        }

        self.our_defender = self.world.our_defender
        self.ball = self.world.ball
        self.our_goal = self.world.our_goal

        # Used to communicate with the robot
        self.robotCom = robotCom

    # Align robot so that he is 180 degrees from facing to goal
    def align(self):
        if robot_is_aligned_to_y_axis(self.our_defender.angle):
            stop(self.robotCom)
            self.current_state = 'MOVE_BACK'
        else:
            align_robot_to_y_axis(self.robotCom, self.our_defender.angle)

    def close_grabber(self):
        if self.our_defender.catcher == 'OPEN':
            grab(self.robotCom)
            self.our_defender.catcher = 'CLOSED'
        self.current_state = 'UNALIGNED'

    def move_back(self):
        if robot_within_zone(self.our_side, self.our_defender.x, self.world.pitch.zone_boundaries()):
            stop(self.robotCom)
            self.current_state = 'DEFEND_GOAL'
        else:
            back_off(self.robotCom, self.our_side, self.our_defender.angle,
                     self.our_defender.x, self.world.pitch.zone_boundaries())

    def move_forward(self):
        if robot_within_goal(self.our_side, self.our_defender.x, self.world.pitch.zone_boundaries()):
            back_off_from_goal(self.robotCom, self.our_side, self.our_defender.angle,
                               self.our_defender.x, self.world.pitch.zone_boundaries())
        else:
            stop(self.robotCom)
            self.current_state = 'DEFEND_GOAL'

    # Calculate ideal defending position and move there.
    def defend_goal(self):
        # Specifies the type of defending. Can be 'straight' or 'sideways'
        type_of_movement = 'straight'

        # If the robot somehow unaligned himself.
        if not robot_is_aligned_to_y_axis(self.our_defender.angle):
            self.current_state = 'UNALIGNED'
        elif not robot_within_zone(self.our_side, self.our_defender.x, self.world.pitch.zone_boundaries()):
            self.current_state = 'MOVE_BACK'
        elif robot_within_goal(self.our_side, self.our_defender.x, self.world.pitch.zone_boundaries()):
            self.current_state = 'MOVE_FORWARD'
        else:

            # Predict where they are aiming.
            # predicted_y = None
            # if self.ball.velocity > BALL_MOVING:
            #     predicted_y = predict_y_intersection(self.world, self.our_defender.x, self.ball, bounce=False)

            # if predicted_y is not None:
            #     y = predicted_y - 7*sin(self.our_defender.angle)
            #     y = max([y, 100])
            #     y = min([y, self.world._pitch.height - 100])
            #     displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x, y)
            #     if(self.our_defender.y > y):
            #         displacement = -displacement
            # else:
                # Try to be in same vertical position as the ball
            y = self.ball.y
            y = max([y, DEFENDING_PITCH_EDGE])
            y = min([y, self.world._pitch.height - DEFENDING_PITCH_EDGE])
            # displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x, y)
            displacement = self.our_defender.y - y
            # if(self.our_defender.y > self.ball.y):
            #     displacement = -displacement

            # if ball_moving_to_us(self.ball, self.our_side):

            #     if self.our_defender.catcher == 'CLOSED':
            #         print "Opening grabber"
            #         openGrabber(self.robotCom)
            #         self.our_defender.catcher = 'OPEN'
            # else:
            #     if self.our_defender.catcher == 'OPEN':
            #         print "Closing grabber"
            #         grab(self.robotCom)
            #         self.our_defender.catcher = 'CLOSED'
            if abs(self.our_defender.angle - 3*pi/2) > (self.our_defender.angle - pi/2):
                rotation_modifier = -1
            else:
                rotation_modifier = 1

            if type_of_movement == 'straight':
                moveStraight(self.robotCom, displacement * rotation_modifier, threshold=BALL_ALIGN_THRESHOLD)
            elif type_of_movement == 'sideways':
                moveSideways(self.robotCom, -displacement, self.world._our_side)


# Defend against incoming ball
class PenaltyDefend(Strategy):

    STATES = ['UNALIGNED',
              # 'CLOSE_GRABBER',
              'DEFEND_GOAL']

    def __init__(self, world, robotCom):
        super(Defending, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            'UNALIGNED': self.align,
            # 'CLOSE_GRABBER': self.close_grabber,
            'DEFEND_GOAL': self.defend_goal
        }

        self.our_defender = self.world.our_defender
        self.ball = self.world.ball
        self.our_goal = self.world.our_goal

        # Used to communicate with the robot
        self.robotCom = robotCom

    # Align robot so that he is 180 degrees from facing to goal
    def align(self):
        if robot_is_aligned_to_y_axis(self.our_defender.angle):
            stop(self.robotCom)
            # self.current_state = 'CLOSE_GRABBER'
            self.current_state = 'DEFEND_GOAL'
        else:
            align_robot_to_y_axis(self.robotCom, self.our_defender.angle)

    # def close_grabber(self):
    #     if robot_is_aligned_to_y_axis(self.our_defender.angle):
    #         if self.our_defender.catcher == 'OPEN':
    #             grab(self.robotCom)
    #             self.our_defender.catcher = 'CLOSED'
    #         self.current_state = 'MOVE_BACK'
    #     else:
    #         self.current_state = 'UNALIGNED'

    # Calculate ideal defending position and move there.
    def defend_goal(self):
        # Specifies the type of defending. Can be 'straight' or 'sideways'
        type_of_movement = 'straight'

        # If the robot somehow unaligned himself.
        if not robot_is_aligned_to_y_axis(self.our_defender.angle):
            self.current_state = 'UNALIGNED'
        else:

            y = self.ball.y
            y = max([y, DEFENDING_PITCH_EDGE])
            y = min([y, self.world._pitch.height - DEFENDING_PITCH_EDGE])
            # displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x, y)
            displacement = self.our_defender.y - y
            # if(self.our_defender.y > self.ball.y):
            #     displacement = -displacement

            # if ball_moving_to_us(self.ball, self.our_side):

            #     if self.our_defender.catcher == 'CLOSED':
            #         print "Opening grabber"
            #         openGrabber(self.robotCom)
            #         self.our_defender.catcher = 'OPEN'
            # else:
            #     if self.our_defender.catcher == 'OPEN':
            #         print "Closing grabber"
            #         grab(self.robotCom)
            #         self.our_defender.catcher = 'CLOSED'
            if abs(self.our_defender.angle - 3*pi/2) > (self.our_defender.angle - pi/2):
                rotation_modifier = -1
            else:
                rotation_modifier = 1

            if type_of_movement == 'straight':
                moveStraight(self.robotCom, displacement * rotation_modifier, threshold=BALL_ALIGN_THRESHOLD)
            elif type_of_movement == 'sideways':
                moveSideways(self.robotCom, -displacement, self.world._our_side)



# Defender robot - Go to the ball and grab it. Assumes the ball is not moving or moving very slowly.
class DefendingGrab(Strategy):

    STATES = ['ROTATE_TO_BALL', 'OPEN_CATCHER', 'MOVE_TO_BALL', 'GRAB_BALL', 'GRABBED']

    def __init__(self, world, robotCom):
        super(DefendingGrab, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            'ROTATE_TO_BALL': self.rotate,
            'OPEN_CATCHER': self.openCatcher,
            'MOVE_TO_BALL': self.position,
            'GRAB_BALL': self.grab,
            'GRABBED': do_nothing
        }

        self.our_defender = self.world.our_defender
        self.ball = self.world.ball

        # Used to communicate with the robot
        self.robotCom = robotCom

    def openCatcher(self):
        if self.our_defender.catcher == 'CLOSED':
            openGrabber(self.robotCom)
            self.our_defender.catcher = 'OPEN'

        self.current_state = 'ROTATE_TO_BALL'

    def rotate(self):
        angle = self.our_defender.get_rotation_to_point(self.ball.x, self.ball.y)

        if angle > pi:
            angle = 2*pi - angle

        # If we are already aligned, this function will call stopRotate.
        rotate_robot(self.robotCom, angle)

        if abs(angle) <= ROBOT_ALIGN_THRESHOLD:
            self.current_state = 'MOVE_TO_BALL'

    def position(self):
        displacement, angle = self.our_defender.get_direction_to_point(self.ball.x, self.ball.y)

        if angle > pi:
            angle = 2*pi - angle

        if self.our_defender.can_catch_ball(self.ball):
            stop(self.robotCom)
            self.current_state = 'GRAB_BALL'
        elif (abs(angle) > PRECISE_BALL_ANGLE_THRESHOLD):
            self.current_state = 'ROTATE_TO_BALL'
        else:
            moveStraight(self.robotCom, displacement, state='fetching')

    def grab(self):
        grab(self.robotCom)
        self.current_state = 'GRABBED'
        self.our_defender.catcher = 'CLOSED'


# When the ball is not in our zone, do nothing.
class Standby(Strategy):

    STATES = ['STOP', 'DO_NOTHING']

    def __init__(self, world, robotCom):
        super(Standby, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            'STOP': self.stopRobot,
            'DO_NOTHING': self.doNothing
        }

        # Used to communicate with the robot
        self.robotCom = robotCom

    # Stop the robot if he was moving before.
    def stopRobot(self):
        stop(self.robotCom)
        self.current_state = 'DO_NOTHING'

    def doNothing(self):
        do_nothing()


# Pass ball to attacker
class PassToAttacker(Strategy):

    STATES = ['ALIGN', 'EVADE',
              'SHOOT', 'FINISHED']

    def __init__(self, world, robotCom):
        super(PassToAttacker, self).__init__(world, self.STATES)

        # Map states into functions
        self.NEXT_ACTION_MAP = {
            'ALIGN': self.align,
            'EVADE': self.evade,
            'SHOOT': self.shoot,
            'FINISHED': do_nothing
        }

        self.our_defender = self.world.our_defender
        self.our_attacker = self.world.our_attacker
        self.their_attacker = self.world.their_attacker
        self.ball = self.world.ball
        self.pitch = self.world.pitch

        # Used to communicate with the robot
        self.robotCom = robotCom

    def align(self):
        # align Kevin to 180 deg from goal
        if robot_is_aligned(self.our_defender.angle, self.pitch_centre):
            stop(self.robotCom)
            # if shot is possible, change to shooting
            if is_shot_blocked(self.world, self.our_defender, self.their_attacker):
                print "SHOT IS BLOCKED"
                print "######### Evading align ############"
                # raise BaseException
                self.current_state = 'EVADE'
            else:
                self.current_state = 'SHOOT'
        else:
            align_robot(self.robotCom, self.our_defender.angle, self.pitch_centre, grab=True)

    def evade(self):
        if is_shot_blocked(self.world, self.our_defender, self.their_attacker):
            # find the mid-point of the pitch
            mid_y = self.pitch.height / 2.0
            print mid_y

            if self.their_attacker.y >= mid_y:
                # if the robot is in the upper half of the pitch, move down
                y = self.our_defender.y - 50
            else:
                # otherwise, move up
                y = self.our_defender.y + 50

            # stop the robot from going to the extremities of the pitch
            y = max([y, 30])
            y = min([y, self.world._pitch.height - 30])

            displacement = self.our_defender.get_displacement_to_point(self.our_defender.x, y)
            if(self.our_defender.y > y):
                displacement = -displacement
                print "-displacement"
            print "displacement"
            # raise BaseException
            # send correct movement type to comms
            moveSideways(self.robotCom, displacement, self.world._our_side)
        else:
            # raise BaseException("DRAMA kick after evade")
            stop(self.robotCom)
            self.current_state = 'SHOOT'

    def shoot(self):
        """
        Kick.
        """
        # angle = self.our_defender.get_rotation_to_point(self.our_attacker.x, self.our_defender.y)
        # if (abs(angle) > self.PRECISE_BALL_ANGLE_THRESHOLD):
        # if robot_is_aligned(self.our_defender.angle, self.pitch_centre):
        stop(self.robotCom)
        kick(self.robotCom)
        self.current_state = 'FINISHED'
        self.our_defender.catcher = 'OPEN'
        # else:
        #     self.current_state = 'ALIGN'


'''

    # Evade the other team's attacker
    def evade(self):
        # if the shot is blocked, evade
        if is_shot_blocked(self.world, self.our_defender, self.their_attacker):
            # Specifies the type of defending. Can be 'straight' or 'sideways'
            type_of_movement = 'sideways'

            # If the robot somehew unaligned himself.
            if (abs(self.our_defender.angle - pi) > ROBOT_ALIGN_THRESHOLD):
                self.current_state = 'UNALIGNED'

            # Try to be in same vertical position +- their_attacker.length as their_attacker
            y = self.their_attacker.y + self.their_attacker.length
            y = max([y, 50])
            y = min([y, self.world._pitch.height - 50])

            displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x, y)
            if(self.our_defender.y > y):
                displacement = -displacement

            if type_of_movement == 'straight':
                    moveStraight(self.robotCom, displacement)
            elif type_of_movement == 'sideways':
                    moveSideways(self.robotCom, displacement, self.world._our_side)
        else:
            self.current_state = 'ROTATE_TO_POINT'

'''
# A way to easily test individual functions
# class TestStrategy(Strategy):

#     STATES = ['TEST']

#     def __init__(self, world, robotCom):
#         super(TestStrategy, self).__init__(world, self.STATES)

#         self.NEXT_ACTION_MAP = {
#             'TEST': self.test
#         }

#         self.robotCom = robotCom
#         self.our_defender = self.world.our_defender

#     def test(self):
#         back_off(self.robotCom, self.world._our_side, self.our_defender.angle, self.our_defender.x)


# Pass ball to attacker using speed_shoot
# 1 - Position yourself to the middle of your zone.
# 2 - Align towards enemies goal
# 3 - If we have a clear shot, shoot. Else evade and shoot rapidly.
# The speed boost is gained but performing the evasion and kicking on the arduino level, getting rid of vision delay.
class SpeedPass(Strategy):

    STATES = ['ROTATE_TO_MIDDLE', 'POSITION', 'ALIGN', 'SHOOT',
              'SPEEDSHOOT', 'FINISHED']

    def __init__(self, world, robotCom):
        super(SpeedPass, self).__init__(world, self.STATES)

        # Map states into functions
        self.NEXT_ACTION_MAP = {
            'ROTATE_TO_MIDDLE': self.rotate_to_middle,
            'POSITION': self.position,
            'ALIGN': self.align,
            'SHOOT': self.shoot,
            'SPEEDSHOOT': self.speed_shoot,
            'FINISHED': do_nothing
        }

        self.our_defender = self.world.our_defender
        self.our_attacker = self.world.our_attacker
        self.their_attacker = self.world.their_attacker
        self.ball = self.world.ball
        self.pitch = self.world.pitch

        # Counter used to stop sending commands to arduino while the robot is kicking
        self.max_counter = 50
        self.counter = self.max_counter

        # Used to communicate with the robot
        self.robotCom = robotCom

    # Rotate yourself to the middle of your zone.
    def rotate_to_middle(self):
        ideal_x, ideal_y = self._get_shooting_coordinates(self.our_defender)
        displacement, angle = self.our_defender.get_direction_to_point(ideal_x, ideal_y)

        if angle > pi:
            angle = 2*pi - angle

        if has_matched(self.our_defender, x=ideal_x, y=ideal_y): # if robot is in the middle of his zone, align and shoot.
            stop(self.robotCom)
            self.current_state = 'ALIGN'
        else:
            if abs(angle) <= ROBOT_ALIGN_THRESHOLD: # move towards middle of the zone
                stop(self.robotCom)
                self.current_state = 'POSITION'
            else:# align towards middle of the zone
                rotate_robot(self.robotCom, angle, grab=True)

    # Position yourself to the middle of your zone.
    def position(self):
        ideal_x, ideal_y = self._get_shooting_coordinates(self.our_defender)
        displacement, angle = self.our_defender.get_direction_to_point(ideal_x, ideal_y)

        if angle > pi:
            angle = 2*pi - angle

        if has_matched(self.our_defender, x=ideal_x, y=ideal_y): # if robot is in the middle of his zone, align and shoot.
            stop(self.robotCom)
            self.current_state = 'ALIGN'
        else:
            if abs(angle) <= ROBOT_ALIGN_THRESHOLD: # move towards middle of the zone
                moveStraight(self.robotCom, displacement, state='fetching', threshold=20)
            else:# align towards middle of the zone
                stop(self.robotCom)
                self.current_state = 'ROTATE_TO_MIDDLE'

    def align(self):
        # align Kevin to 180 deg from goal
        if robot_is_aligned(self.our_defender.angle, self.pitch_centre):
            stop(self.robotCom)
            time.sleep(0.2) # wait until the robot stops rotating.

            # if shot is blocked, speedshoot. else just shoot straght.
            if is_shot_blocked(self.world, self.our_defender, self.their_attacker):
                self.current_state = 'SPEEDSHOOT'
            else:
                self.current_state = 'SHOOT'
        else:
            align_robot(self.robotCom, self.our_defender.angle, self.pitch_centre, grab=True)

    # Taking advantage of the vision delay, we tell Kevin to evade and shoot rapidly, without interaction with the vision.
    # This should be impossible for the opponents to catch.
    def speed_shoot(self):
        if(self.counter == self.max_counter):

            speed_kick(self.robotCom, self.our_defender.angle)

            self.counter -= 1
        elif(self.counter > 0):
            self.counter -= 1
        else:
            stop(self.robotCom)
            self.current_state = 'FINISHED'
            self.our_defender.catcher = 'OPEN'

    # Just shoot straight.
    def shoot(self):
        if(self.counter == self.max_counter):
            kick(self.robotCom)
            self.counter -= 1
        elif(self.counter > 0):
            self.counter -= 1
        else:
            stop(self.robotCom)
            self.current_state = 'FINISHED'
            self.our_defender.catcher = 'OPEN'

    def _get_shooting_coordinates(self, robot):
        """
        Retrieve the coordinates to which we need to move before we set up the pass.
        """
        zone_index = robot.zone
        zone_poly = self.world.pitch.zones[zone_index][0]

        min_x = int(min(zone_poly, key=lambda z: z[0])[0])
        max_x = int(max(zone_poly, key=lambda z: z[0])[0])

        x = min_x + (max_x - min_x) / 2
        y =  self.world.pitch.height / 2

        return (x, y)


# This might be a good strategy for later.
class DefenderBouncePass(Strategy):
    '''
    Once the defender grabs the ball, move to the center of the zone and shoot towards
    the wall of the center of the opposite attacker zone, in order to reach our_attacker
    attacker zone.
    '''

    POSITION, ROTATE, SHOOT, FINISHED = 'POSITION', 'ROTATE', 'SHOOT', 'FINISHED'
    STATES = [POSITION, ROTATE, SHOOT, FINISHED]

    UP, DOWN = 'UP', 'DOWN'

    def __init__(self, world, robotCom):
        super(DefenderBouncePass, self).__init__(world, self.STATES)

        # Map states into functions
        self.NEXT_ACTION_MAP = {
            self.POSITION: self.position,
            self.ROTATE: self.rotate,
            self.SHOOT: self.shoot,
            self.FINISHED: do_nothing
        }

        self.our_defender = self.world.our_defender
        self.their_attacker = self.world.their_attacker
        self.ball = self.world.ball

        # Choose a random side to bounce off
        self.point = randint(0,1)

        # Find the position to shoot from and cache it
        self.shooting_pos = self._get_shooting_coordinates(self.our_defender)

        # Maximum number of turns
        self.laps_left = 4

    def position(self):
        """
        Position the robot in the middle close to the goal. Angle does not matter.
        Executed initially when we've grabbed the ball and want to move.
        """
        ideal_x, ideal_y = self.shooting_pos
        distance, angle = self.our_defender.get_direction_to_point(ideal_x, ideal_y)

        if has_matched(self.our_defender, x=ideal_x, y=ideal_y):
            self.current_state = self.ROTATE
            return do_nothing()
        else:
            return calculate_motor_speed(distance, angle, careful=True)

    def rotate(self):
        """
        Once the robot is in position, rotate to one side or the other in order
        to bounce the ball into the attacker zone. If one side is blocked by their
        attacker, turn 90 degrees and shoot to the other side.
        """
        bounce_points = self._get_bounce_points(self.our_defender)
        x, y = bounce_points[self.point][0], bounce_points[self.point][1]
        angle = self.our_defender.get_rotation_to_point(x, y)

        if has_matched(self.our_defender, angle=angle, angle_threshold=pi/20):
            # if not is_shot_blocked(self.world, self.our_defender, self.world.their_attacker) or \
            their_attacker_side = self._get_robot_side(self.their_attacker)
            if (self.point == 0 and their_attacker_side == self.UP) or \
               (self.point == 1 and their_attacker_side == self.DOWN):
                self.current_state = self.SHOOT
                return do_nothing()
            else:
                # self.point = 1 - self.point
                # self.laps_left -= 1
                # x, y = bounce_points[self.point][0], bounce_points[self.point][1]
                # angle = self.our_defender.get_rotation_to_point(x, y)
                if self.world._our_side == 'right':
                    orientation = 1 if self.point == 1 else -1
                else:
                    orientation = 1 if self.point == 0 else -1
                self.current_state = self.FINISHED
                print 'orientation', orientation
                return turn_shoot(orientation)
        else:
            return calculate_motor_speed(None, angle, careful=True)

    def shoot(self):
        """
        Kick.
        """
        self.current_state = self.FINISHED
        self.our_defender.catcher = 'open'
        return kick_ball()

    def _get_shooting_coordinates(self, robot):
        """
        Retrive the coordinates to which we need to move before we set up the pass.
        """
        zone_index = robot.zone
        zone_poly = self.world.pitch.zones[zone_index][0]

        min_x = int(min(zone_poly, key=lambda z: z[0])[0])
        max_x = int(max(zone_poly, key=lambda z: z[0])[0])

        x = min_x + (max_x - min_x) / 2
        y =  self.world.pitch.height / 2

        return (x, y)

    def _get_robot_side(self, robot):
        height = self.world.pitch.height
        print '###########', height, robot.y
        if robot.y > height/2:
            return self.UP
        else:
            return self.DOWN

    def _get_bounce_points(self, robot):
        """
        Get the points in the opponent's attacker zone where our defender needs to shoot
        in order to bounce the ball to our attacker zone.
        """
        attacker_zone = {0:1, 3:2}
        zone_index = attacker_zone[robot.zone]
        zone_poly = self.world.pitch.zones[zone_index][0]

        min_x = int(min(zone_poly, key=lambda z: z[0])[0])
        max_x = int(max(zone_poly, key=lambda z: z[0])[0])
        bounce_x = min_x + (max_x - min_x) / 2

        min_y = int(min(zone_poly, key=lambda z: z[1])[1])
        max_y = int(max(zone_poly, key=lambda z: z[1])[1])

        return [(bounce_x, min_y), (bounce_x, max_y)]
