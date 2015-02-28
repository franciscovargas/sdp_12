from utilities import align_robot, align_robot_to_pitch, predict_y_intersection, moveStraight, moveSideways, has_matched, \
    stop, do_nothing, BALL_MOVING, kick, grab, openGrabber, ROBOT_ALIGN_THRESHOLD
from math import pi, sin, cos
from random import randint
# Up until here are the imports that we're using

# Imports from their code that are needed to compile (and maybe later)
from utilities import calculate_motor_speed, kick_ball, turn_shoot, is_shot_blocked


class Strategy(object):

    PRECISE_BALL_ANGLE_THRESHOLD = pi/8
    UP, DOWN = 'UP', 'DOWN'

    def __init__(self, world, states):
        self.world = world
        self.states = states
        self._current_state = states[0]

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        assert new_state in self.states
        self._current_state = new_state

    def reset_current_state(self):
        self.current_state = self.states[0]

    def is_last_state(self):
        return self._current_state == self.states[-1]

    def next_action(self):
        return self.NEXT_ACTION_MAP[self.current_state]()


# Defend against incoming ball
class Defending(Strategy):

    STATES = ['UNALIGNED', 'DEFEND_GOAL']

    def __init__(self, world, robotCom):
        super(Defending, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            'UNALIGNED': self.align,
            'DEFEND_GOAL': self.defend_goal
        }

        self.our_defender = self.world.our_defender
        self.ball = self.world.ball
        self.our_goal = self.world.our_goal

        # Used to communicate with the robot
        self.robotCom = robotCom

    # Align robot so that he is 90 degrees from facing to goal
    def align(self):
        if align_robot_to_pitch(self.robotCom, self.our_defender.angle, pi/2):
            self.current_state = 'DEFEND_GOAL'

    # Calculate ideal defending position and move there.
    def defend_goal(self):
        # Specifies the type of defending. Can be 'straight' or 'sideways'
        type_of_movement = 'straight'

        # If the robot somehew unaligned himself.
        if (abs(self.our_defender.angle - pi/2) > ROBOT_ALIGN_THRESHOLD):
            self.current_state = 'UNALIGNED'

        # Predict where they are aiming.
        predicted_y = None
        if self.ball.velocity > BALL_MOVING:
            predicted_y = predict_y_intersection(self.world, self.our_defender.x, self.ball, bounce=False)
        if predicted_y is not None:
            y = predicted_y - 7*sin(self.our_defender.angle)
            y = max([y, 70])
            y = min([y, self.world._pitch.height - 70])
            displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x, y)
            if(self.our_defender.y > y):
                displacement = -displacement
        else:
            # Try to be in same vertical position as the ball
            y = self.ball.y
            y = max([y, 70])
            y = min([y, self.world._pitch.height - 70])
            displacement, angle = self.our_defender.get_direction_to_point(self.our_defender.x, y)
            if(self.our_defender.y > y):
                displacement = -displacement

        if type_of_movement == 'straight':
            moveStraight(self.robotCom, displacement)
        elif type_of_movement == 'sideways':
            moveSideways(self.robotCom, displacement)


# Defender robot - Go to the ball and grab it. Assumes the ball is not moving or moving very slowly.
class DefendingGrab(Strategy):

    STATES = ['OPEN_CATCHER', 'ROTATE_TO_BALL', 'MOVE_TO_BALL', 'GRAB_BALL', 'GRABBED']

    def __init__(self, world, robotCom):
        super(DefendingGrab, self).__init__(world, self.STATES)

        self.NEXT_ACTION_MAP = {
            'OPEN_CATCHER': self.openCatcher,
            'ROTATE_TO_BALL': self.rotate,
            'MOVE_TO_BALL': self.position,
            'GRAB_BALL': self.grab,
            'GRABBED': do_nothing
        }

        self.our_defender = self.world.our_defender
        self.ball = self.world.ball

        # Used to communicate with the robot
        self.robotCom = robotCom

    def openCatcher(self):
        openGrabber(self.robotCom)
        self.our_defender.catcher == 'OPEN'

        self.current_state = 'ROTATE_TO_BALL'

    def rotate(self):
        angle = self.our_defender.get_rotation_to_point(self.ball.x, self.ball.y)

        if angle > pi:
            angle = 2*pi - angle

        if align_robot(self.robotCom,
                       angle,
                       self.PRECISE_BALL_ANGLE_THRESHOLD):
            self.current_state = 'MOVE_TO_BALL'

    def position(self):
        displacement, angle = self.our_defender.get_direction_to_point(self.ball.x, self.ball.y)

        if angle > pi:
            angle = 2*pi - angle

        if self.our_defender.can_catch_ball(self.ball):
            self.current_state = 'GRAB_BALL'
        elif (abs(angle) > self.PRECISE_BALL_ANGLE_THRESHOLD):
            self.current_state = 'ROTATE_TO_BALL'
        else:
            moveStraight(self.robotCom, displacement)

    def grab(self):
        # if self.our_defender.has_ball(self.ball):
        #     self.current_state = 'GRABBED'
        # else:
        #     self.our_defender.catcher = 'CLOSED'
        #     self.robotCom.grabCont(100)

        grab(self.robotCom)
        self.current_state = 'GRABBED'
        self.our_defender.catcher = 'CLOSED'


# Defender robot - Move to center and pass the ball.
class DefendingPass(Strategy):

    STATES = ['ROTATE_TO_MIDDLE',
              # 'GO_TO_MIDDLE', 'ROTATE_TO_GOAL',
              'SHOOT', 'FINISHED']

    def __init__(self, world, robotCom):
        super(DefendingPass, self).__init__(world, self.STATES)

        # Map states into functions
        self.NEXT_ACTION_MAP = {
            'ROTATE_TO_MIDDLE': self.rotate,
            # 'GO_TO_MIDDLE': self.position,
            # 'ROTATE_TO_GOAL': self.rotate,
            'SHOOT': self.shoot,
            'FINISHED': do_nothing
        }

        self.our_defender = self.world.our_defender
        self.ball = self.world.ball

        # # Find the position to shoot from and cache it
        # self.shooting_pos = self._get_shooting_coordinates(self.our_defender)

        # Used to communicate with the robot
        self.robotCom = robotCom

    # # Rotate robot towards the middle of our defending zone.
    # def rotatePosition(self):
    #     ideal_x, ideal_y = self.shooting_pos
    #     angle = self.our_defender.get_rotation_to_point(ideal_x, ideal_y)

    #     if align_robot(self.robotCom,
    #                    angle,
    #                    self.PRECISE_BALL_ANGLE_THRESHOLD):
    #         stop(self.robotCom)
    #         self.current_state = 'GO_TO_MIDDLE'

    # def position(self):
    #     """
    #     Position the robot in the middle close to the goal. Angle does not matter.
    #     Executed initially when we've grabbed the ball and want to move.
    #     """
    #     ideal_x, ideal_y = self.shooting_pos
    #     distance, angle = self.our_defender.get_direction_to_point(ideal_x, ideal_y)

    #     if has_matched(self.our_defender, x=ideal_x, y=ideal_y):
    #         self.current_state = 'ROTATE_TO_GOAL'
    #         stop(self.robotCom)
    #     else:
    #         moveStraight(self.robotCom, distance)

    # Rotate robot towards their goal.
    def rotate(self):
        # angle = self.our_defender.get_rotation_to_point(self.world.their_goal.x, self.world.their_goal.y)

        if align_robot_to_pitch(self.robotCom,
                                self.our_defender.angle,
                                0,
                                grab=True):
            self.current_state = 'SHOOT'

    def shoot(self):
        """
        Kick.
        """
        if (abs(self.our_defender.angle - 0) > self.PRECISE_BALL_ANGLE_THRESHOLD):
            self.current_state = 'ROTATE_TO_MIDDLE'
        self.current_state = 'FINISHED'

        kick(self.robotCom)
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
        y = self.world.pitch.height / 2

        return (x, y)


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

    STATES = ['ROTATE_TO_POINT',
              'SHOOT', 'FINISHED']

    def __init__(self, world, robotCom):
        super(PassToAttacker, self).__init__(world, self.STATES)

        # Map states into functions
        self.NEXT_ACTION_MAP = {
	    #'DETECT_AND_EVADE': self.
            'ROTATE_TO_POINT': self.rotate,
            'SHOOT': self.shoot,
            'FINISHED': do_nothing
        }

        self.our_defender = self.world.our_defender
	self.our_attacker = self.world.our_attacker
        self.ball = self.world.ball

        # Used to communicate with the robot
        self.robotCom = robotCom
	
	#if is_shot_blocked(



    # Rotate robot towards the point
    def rotate(self):
	# our_defender rotates to our_attacker

        angle = self.our_defender.get_rotation_to_point(self.our_attacker.x, self.our_attacker.y)

        if angle > pi:
            angle = 2*pi - angle

        if align_robot(self.robotCom,
                       angle,
                       self.PRECISE_BALL_ANGLE_THRESHOLD):
            self.current_state = 'SHOOT'

    # Shoot
    def shoot(self):
        """
        Kick.
        """
        if (abs(self.our_defender.angle - 0) > self.PRECISE_BALL_ANGLE_THRESHOLD):
            self.current_state = 'ROTATE_TO_POINT'
        self.current_state = 'FINISHED'

        kick(self.robotCom)
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
        y = self.world.pitch.height / 2

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
