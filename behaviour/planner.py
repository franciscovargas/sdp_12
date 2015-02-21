from world import World
from strategies import AttackerDefend, AttackerGrab, AttackerGrabCareful, AttackerDriveByTurn, AttackerDriveBy, \
    AttackerTurnScore, AttackerScoreDynamic, AttackerPositionCatch, AttackerCatch, Milestone2Def, Milestone2DefPass, \
    Milestone2DefGrab, Milestone2AttGrab, Milestone2AttKick, DefenderDefence, DefenderGrab, DefenderBouncePass, \
    Milestone2Standby
from utilities import calculate_motor_speed, BALL_MOVING


class Planner:

    def __init__(self, our_side, pitch_num, robotCom, robotType):
        self._world = World(our_side, pitch_num)
        self._world.our_defender._receiving_area = {'width': 30, 'height': 30, 'front_offset': 12} # 10
        self._world.our_attacker._receiving_area = {'width': 30, 'height': 30, 'front_offset': 14}

        # To be assigned to strategy. Used to communicate with the robot
        self.robotCom = robotCom
        self.robotType = robotType

        self._attacker_strategies = {'defending': [Milestone2Standby, AttackerDefend],
                                     'fetching': [Milestone2AttGrab, AttackerGrab, AttackerGrabCareful],
                                     'shooting': [Milestone2AttKick, AttackerDriveBy, AttackerTurnScore, AttackerScoreDynamic],
                                     'receiving': [AttackerPositionCatch, AttackerCatch]}

        self._defender_strategies = {'defending': [Milestone2Def, DefenderDefence],
                                     'fetching': [Milestone2DefGrab, DefenderGrab],
                                     'passing': [Milestone2DefPass, DefenderBouncePass],
                                     'waiting': [Milestone2Standby]}

        if robotType == 'defender':
            # for milestone 2, we need to wait for the ball to start moving before defending
            self._state = 'waiting'
            next_strategy = self._defender_strategies[self._state][0]
        else:
            self._state = 'defend'
            next_strategy = self._attacker_strategies[self._state][0]

        self._current_strategy = next_strategy(self._world, self.robotCom)


    # Provisional. Choose the first strategy in the applicable list.
    def get_next_strategy(self):
        if self.robotType == 'defender':
            next_strategy = self._defender_strategies[self._state][0]

        elif self.robotType == 'attacker':
            next_strategy = self._attacker_strategies[self._state][0]

        self._current_strategy = next_strategy(self._world, self.robotCom)
        print 'Choosing strategy: ', next_strategy

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

    def in_zone(self, ball, zone):
        return self._world.pitch.zones[zone].isInside(ball.x, ball.y)

    def plan(self):
        print self.strat_state

        assert self.robotType in ['attacker', 'defender']
        our_defender = self._world.our_defender
        our_attacker = self._world.our_attacker
        their_defender = self._world.their_defender
        their_attacker = self._world.their_attacker
        ball = self._world.ball

        if self.robotType == 'defender':
            # If the ball is in not in our defender zone:

            if self._state == 'waiting':
                # (milestone 2) once the ball starts moving, we can start moving the defender
                # (there is a bug in the vision (?) code that sets the ball velocity to 304 for the first two frames or so)
                if ball.velocity > BALL_MOVING and ball.velocity < 300:
                    self._state = 'defending'
                    self.get_next_strategy()
                    print "Ball has started moving, enabling movement for defender"

            elif not self.in_zone(ball, our_defender.zone):
                    # If the ball is not in the defender's zone, the state should always be 'defend'.
                    if self._state != 'defending':
                        self._state = 'defending'
                        self.get_next_strategy()
                    print "Defending, ball moving and not in our zone"

            # once we have the ball, pass it to our teammate
            elif self._state == 'fetching' and self.strat_state == 'GRABBED':
                self._state = 'passing'
                self.get_next_strategy()
                print "We've grabbed the ball, now switching to passing"

            # We have the ball in our zone, so we fetching and passing:
            else:
                # # If the ball is still moving, keep defending
                # if ball.velocity >= BALL_MOVING:
                #     if self._state != 'defending':
                #         self._state = 'defending'
                #         self.get_next_strategy()
                #     print "Defending, ball in our zone but moving"

                # If we've grabbed the ball, switch to a passing strategy.

                # If we're defending or waiting with the ball in our zone, switch to a fetching strategy.
                if self._state == 'defending' or self._state == 'waiting':
                    self._state = 'fetching'
                    self.get_next_strategy()
                    print "Defending, fetching the ball"

                # If we've finished passing but the ball's still in our zone, fetch it
                elif self._state == 'passing' and self.strat_state == 'FINISHED':
                    self._state = 'fetching'
                    self.get_next_strategy()
                    print "Passing the ball"
                else:
                    print "Keeping same strategy"

        elif self.robotType == 'attacker':

            if self.in_zone(ball, our_attacker.zone):

                # Check if we should switch from a fetching to a scoring strategy.
                if self._state == 'fetching' and self.strat_state == 'GRABBED':
                    self._state = 'shooting'
                    self.get_next_strategy()
                    print "Ball grabbed, shooting"

                # Check if we managed to shoot the ball..
                elif self._state == 'shooting' and self.strat_state == 'FINISHED':
                    # Robot stops now and waits until the ball goes outside his zone.
                        #self._state = 'fetching'
                        #self.get_next_strategy()
                    print "Finished shooting, switching to fetching"

                elif self._state == 'defending':
                    self._state = 'fetching'
                    self.get_next_strategy()
                    print "Ball in our zone, switching from defending/receiving to fetching"

            elif self._state != 'defending':
                self._state = 'defending'
                self.get_next_strategy()

            else:
                self._state = 'defending'

        return self._current_strategy.next_action()
