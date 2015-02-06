from world import *
from collisions import *
from strategies import *
from utilities import *


class Planner:

    def __init__(self, our_side, pitch_num, robotCom):
        self._world = World(our_side, pitch_num)
        self._world.our_defender.receivinger_area = {'width': 30, 'height': 30, 'front_offset': 12} # 10
        self._world.our_attacker.receivinger_area = {'width': 30, 'height': 30, 'front_offset': 14}

        # To be passinged to strategy. Used to communicate with the robot
        # BEING USED
        self.robotCom = robotCom

        self._attacker_strategies = {'defending': [AttackerDefend],
                                     'fetching': [AttackerGrab, AttackerGrabCareful],
                                     'shooting': [AttackerDriveByTurn, AttackerDriveBy, AttackerTurnScore, AttackerScoreDynamic],
                                     'receiving': [AttackerPositionCatch, AttackerCatch]}

        # BEING USED
        self._defender_strategies = {'defending': [Milestone2Def, DefenderDefence],
                                     'fetching': [DefenderGrab],
                                     'passing': [Milestone2Pass, DefenderBouncePass]}

        self._defender_state = 'defending'
        self._defender_current_strategy = self.choose_defender_strategy(self._world, self.robotCom)

        self._attacker_state = 'defending'
        self._attacker_current_strategy = self.choose_attacker_strategy(self._world)

    # Provisional. Choose the first strategy in the applicable list.
    def choose_next_strategy(robot_type):
        if robot_type == 'defender':
            next_strategy = self._defender_strategies[self._defender_state][0]
            self._defender_current_strategy = next_strategy(self._world, self.robotCom)
        elif robot_type == 'attacker':
            next_strategy = self._attacker_strategies[self._attacker_state][0]
            self._attacker_current_strategy = next_strategy(self._world)

        print 'Choosing strategy: ', next_strategy

    # def choose_attacker_strategy(self, world):
    #     next_strategy = self._attacker_strategies[self._attacker_state][0]
    #     return next_strategy(world)

    # Provisional. Choose the first strategy in the applicable list.
    # def choose_defender_strategy(self, world, robotCom):
    #     next_strategy = self._defender_strategies[self._defender_state][0]
    #     print 'Choosing strategy: ', next_strategy
    #     return next_strategy(world, robotCom)

    @property
    def attacker_strat_state(self):
        return self._attacker_current_strategy.current_state

    @property
    def defender_strat_state(self):
        return self._defender_current_strategy.current_state

    @property
    def attacker_state(self):
        return self._attacker_state

    @attacker_state.setter
    def attacker_state(self, new_state):
        assert new_state in ['defending', 'attack']
        self._attacker_state = new_state

    @property
    def defender_state(self):
        return self._defender_state

    @defender_state.setter
    def defender_state(self, new_state):
        assert new_state in ['defending', 'attack']
        self._defender_state = new_state

    def update_world(self, position_dictionary):
        self._world.update_positions(position_dictionary)

    # refactoring functions
    def in_zone(ball, zone):
        self._world.pitch.zones[zone].isInside(ball.x, ball.y)


    def plan(self, robot='defender'):
        assert robot in ['attacker', 'defender']
        our_defender = self._world.our_defender
        our_attacker = self._world.our_attacker
        their_defender = self._world.their_defender
        their_attacker = self._world.their_attacker
        ball = self._world.ball
        # BEING USED
        if robot == 'defender':
            # If the ball is in not in our defender zone:
            if not in_zone(ball, our_defender.zone) and self._defender_state != 'defending':
                # If the ball is not in the defender's zone, the state should always be 'defend'.
                    self._defender_state = 'defending'
                    choose_next_strategy('defender')

            # We have the ball in our zone, so we fetching and passing:
            else:
                # If the ball is still moving, keep defending
                if ball.velocity >= 3 and self._defender_state != 'defending':
                    self._defender_state = 'defending'
                    self.choose_next_strategy('defender')

                # If we've grabbed the ball, switch to a passing strategy.
                elif self._defender_state == 'fetching' and self._defender_current_strategy.current_state == 'GRABBED':
                    self._defender_state = 'passing'
                    self.choose_next_strategy('defender')

                # If we're defending (and the ball isn't moving), switch to a fetching strategy.
                elif self._defender_state == 'defending':
                    self._defender_state = 'fetching'
                    self.choose_next_strategy('defender')

                elif self._defender_state == 'passing' and self._defender_current_strategy.current_state == 'FINISHED':
                    self._defender_state = 'fetching'
                    self.choose_next_strategy('defender')
                else:
                    return do_nothing()

            return self._defender_current_strategy.next_action()

        elif robot == 'attacker':
            # If the ball is in their defender zone we defend:
            if in_zone(ball, their_defender.zone) and self._attacker_state != 'defending':
                self._attacker_state = 'defending'
                choose_next_strategy('attacker')

                return self._attacker_current_strategy.next_action()
            # If ball is in our attacker zone, then fetch the ball and shoot:
            elif in_zone(ball, our_attacker.zone):

                # Check if we should switch from a fetching to a scoring strategy.
                if self._attacker_state == 'fetching' and self._attacker_current_strategy.current_state == 'GRABBED':
                    self._attacker_state = 'shooting'
                    choose_next_strategy('attacker')

                elif self._attacker_state == 'fetching':
                    # Switch to careful mode if the ball is too close to the wall.
                    # if abs(self._world.ball.y - self._world.pitch.height) < 0 or abs(self._world.ball.y) < 0:
                    #     if isinstance(self._attacker_current_strategy, AttackerGrab):
                    #         self._attacker_current_strategy = AttackerGrabCareful(self._world)
                    # else:
                        # if isinstance(self._attacker_current_strategy, AttackerGrabCareful):
                    self._attacker_current_strategy = AttackerGrab(self._world)

                # Check if we should switch from a defending to a fetching strategy.
                elif self._attacker_state in ['defending', 'receiving']:
                    self._attacker_state = 'fetching'
                    self._attacker_current_strategy = self.choose_attacker_strategy(self._world)

                elif self._attacker_state == 'shooting' and self._attacker_current_strategy.current_state == 'FINISHED':
                    self._attacker_state = 'fetching'
                    self._attacker_current_strategy = self.choose_attacker_strategy(self._world)

                return self._attacker_current_strategy.next_action()
            # If the ball is in our defender zone, prepare to receiving the passinged ball:
            elif in_zone(ball, our_defender.zone) or self._attacker_state == 'receiving':
                self._attacker_state = 'receiving'
                choose_next_strategy('attacker')
                return self._attacker_current_strategy.next_action()
            else:
                return calculate_motor_speed(0, 0)
