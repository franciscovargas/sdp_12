class Strategy:
    'strategic reasoning using inputs from world.py'
    import world

    def attack:
        if i have the ball:
            manouver to shoot
            if clear shot(goal):
                shoot
            else move to clear shot (goal)
        else catch

    def defend:
        if i have the ball:
            if clear shot(team_mate):
                shoot
            else move to clear shot (team_mate)
       else catch

    def clear_shot(robot, target):
        a straight line can be drawn between the robot kicker and the targete and the goa


    def catch:
        track ball
        if ball coming:
            move into path
            grabber open
            detect ball
            grabber close

movement

is_moving_forwards
is_moving_backwards
is_moving_left
is_moving_right
is_rotating_clockwise
is_rotating_anticlockwise

ball 

grabber_open
grabber_closed
ball_posession_us
ball_possession_them
ready_to_shoot

strategies

defender
attacker
