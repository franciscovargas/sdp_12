class World:
    'class that uses the vision module to build a model of the world, updates throughout game' 
'''
/-------|-------|-------|-------\
|our	|their	|our 	|our	|
|defence|attack	|attack	|defence|
|	|	|	|	|
\-------|-------|-------|-------/

or

/-------|-------|-------|-------\
|their	|our	|their 	|their	|
|defence|attack	|attack	|defence|
|	|	|	|	|
\-------|-------|-------|-------/
'''


    def pitch_attributes:
        robot_role = attack or defense
        pitch_coordinates/dimensions.... from vision?
        zone_confinements = if attack... if defense
        goal_coords = if left_side ... if right_side... 

    def robot_position:
        x = get x from vision
        y = get y from vision

    def team_mate_position:
        x = get x from vision
        y = get y from vision

    def ball_position:
        x = get x from vision or unknown
        y = get y from vision or unknown
        posession = me, team_mate, opposion_attack, opposition_defense

    def current_goal: 
        get current goal

