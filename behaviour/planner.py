from world import World
from strategies import Defending, DefendingGrab, DefendingPass, PassToAttacker, \
    DefenderBouncePass, Standby
from utilities import calculate_motor_speed, BALL_MOVING


class Planner:

    def __init__(self, our_side, pitch_num, robotCom):
        self._world = World(our_side, pitch_num)
        self._world.our_defender._receiving_area = {'width': 30, 'height': 30, 'front_offset': 12}

        # To be assigned to strategy. Used to communicate with the robot
        self.robotCom = robotCom

        self._defender_strategies = {'defending': [Defending],
                                     'fetching': [DefendingGrab],
                                     'passing': [PassToAttacker, DefenderBouncePass],
                                     'waiting': [Standby]}

        # for milestone 2, we need to wait for the ball to start moving before defending
        self._state = 'waiting'
        next_strategy = self._defender_strategies[self._state][0]

        self._current_strategy = next_strategy(self._world, self.robotCom)


    # Provisional. Choose the first strategy in the applicable list.
    def get_next_strategy(self):
        next_strategy = self._defender_strategies[self._state][0]
        self._current_strategy = next_strategy(self._world, self.robotCom)
        print 'Choosing strategy: ', next_strategy

    @property
    def strat_state(self):
        return self._current_strategy.current_state

    def update_world(self, position_dictionary):
        self._world.update_positions(position_dictionary)

    def in_zone(self, ball, zone):
        return self._world.pitch.zones[zone].isInside(ball.x, ball.y)

    def plan(self):

        our_defender = self._world.our_defender
        our_attacker = self._world.our_attacker
        their_defender = self._world.their_defender
        their_attacker = self._world.their_attacker
        ball = self._world.ball

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



        return self._current_strategy.next_action()
