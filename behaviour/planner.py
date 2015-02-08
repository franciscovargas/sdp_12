from world import World
from strategies import AttackerDefend, AttackerGrab, AttackerGrabCareful, AttackerDriveByTurn, AttackerDriveBy, \
    AttackerTurnScore, AttackerScoreDynamic, AttackerPositionCatch, AttackerCatch, Milestone2Def, Milestone2Pass, \
    DefenderDefence, DefenderGrab, DefenderBouncePass, DoNothing
from utilities import calculate_motor_speed, BALL_MOVING


class Planner:

    def __init__(self, our_side, pitch_num, robotCom, robotType):
        self._world = World(our_side, pitch_num)
        self._world.our_defender.receiving_area = {'width': 30, 'height': 30, 'front_offset': 12} # 10
        self._world.our_attacker.receiving_area = {'width': 30, 'height': 30, 'front_offset': 14}

        # To be assigned to strategy. Used to communicate with the robot
        # BEING USED
        self.robotCom = robotCom

        self._attacker_strategies = {'defending': [AttackerDefend],
                                     'fetching': [AttackerGrab, AttackerGrabCareful],
                                     'shooting': [AttackerDriveByTurn, AttackerDriveBy, AttackerTurnScore, AttackerScoreDynamic],
                                     'receiving': [AttackerPositionCatch, AttackerCatch]}

        # BEING USED
        self._defender_strategies = {'defending': [Milestone2Def, DefenderDefence],
                                     'fetching': [DefenderGrab],
                                     'passing': [Milestone2Pass, DefenderBouncePass],
                                     'doing_nothing': [DoNothing]}

        self._state = 'defending'
        # assume we are the defender for now
        self.current_strategy = self.get_next_strategy()

    # Provisional. Choose the first strategy in the applicable list.
    def get_next_strategy(self):
        if self.robotType == 'defender':
            next_strategy = self._defender_strategies[self._state][0]
            self._current_strategy = next_strategy(self._world, self.robotCom)

        elif self.robotType == 'attacker':
            next_strategy = self._attacker_strategies[self._state][0]
            self._current_strategy = next_strategy(self._world)

        print 'Choosing strategy: ', next_strategy

    # def choose_attacker_strategy(self, world):
    #     next_strategy = self._attacker_strategies[self._state][0]
    #     return next_strategy(world)

    # Provisional. Choose the first strategy in the applicable list.
    # def choose_defender_strategy(self, world, robotCom):
    #     next_strategy = self._defender_strategies[self._state][0]
    #     print 'Choosing strategy: ', next_strategy
    #     return next_strategy(world, robotCom)

    @property
    def strat_state(self):
        return self._current_strategy.current_state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        assert new_state in ['defending', 'attack']
        self._state = new_state

    def update_world(self, position_dictionary):
        self._world.update_positions(position_dictionary)

    # refactoring functions
    def in_zone(self, ball, zone):
        self._world.pitch.zones[zone].isInside(ball.x, ball.y)


    def plan(self):
        assert self.robotType in ['attacker', 'defender']
        our_defender = self._world.our_defender
        our_attacker = self._world.our_attacker
        their_defender = self._world.their_defender
        their_attacker = self._world.their_attacker
        ball = self._world.ball
        # BEING USED
        if self.robotType == 'defender':
            # If the ball is in not in our defender zone:
            if not self.in_zone(ball, our_defender.zone):  #and self._state != 'defending':
                # If the ball is not in the defender's zone, the state should always be 'defend'.
                    self._state = 'defending'
                    print "Defending, ball not in our zone"

            # We have the ball in our zone, so we fetching and passing:
            else:
                # If the ball is still moving, keep defending
                if ball.velocity >= BALL_MOVING and self._state != 'defending':
                    self._state = 'defending'
                    print "Defending, ball in our zone but moving"

                # If we've grabbed the ball, switch to a passing strategy.
                elif self._state == 'fetching' and self.strat_state == 'GRABBED':
                    self._state = 'passing'
                    print "We've grabbed the ball"

                # If we're defending (and the ball isn't moving), switch to a fetching strategy.
                elif self._state == 'defending':
                    self._state = 'fetching'
                    print "Defending, fetching the ball"

                elif self._state == 'passing' and self.strat_state == 'FINISHED':
                    self._state = 'fetching'
                    print "Passing the ball"
                else:
                    self._state = 'doing_nothing'
                    # return do_nothing()
                    print "Doing nothing"

        elif self.robotType == 'attacker':
            # If the ball is in their defender zone we defend:
            if self.in_zone(ball, their_defender.zone) and self._state != 'defending':
                self._state = 'defending'
                print "Ball in their defender zone, defending"

            # If ball is in our attacker zone, then fetch the ball and shoot:
            elif self.in_zone(ball, our_attacker.zone):

                # Check if we should switch from a fetching to a scoring strategy.
                if self._state == 'fetching' and self.strat_state == 'GRABBED':
                    self._state = 'shooting'
                    print "Ball grabbed, shooting"

                # elif self._state == 'fetching':
                    # Switch to careful mode if the ball is too close to the wall.
                    # if abs(self._world.ball.y - self._world.pitch.height) < 0 or abs(self._world.ball.y) < 0:
                    #     if isinstance(self._current_strategy, AttackerGrab):
                    #         self._current_strategy = AttackerGrabCareful(self._world)
                    # else:
                    # if isinstance(self._current_strategy, AttackerGrabCareful):
                    # self._current_strategy = AttackerGrab(self._world)

                # Check if we should switch from a defending to a fetching strategy.
                elif self._state in ['defending', 'receiving']:
                    self._state = 'fetching'
                    print ""

                elif self._state == 'shooting' and self._current_strategy.current_state == 'FINISHED':
                    self._state = 'fetching'

            # If the ball is in our defender zone, prepare to receiving the passinged ball:
            elif self.in_zone(ball, our_defender.zone) or self._state == 'receiving':
                self._state = 'receiving'
            else:
                self._state = 'do_nothing'

        self.get_next_strategy()
        return self._current_strategy.next_action()
