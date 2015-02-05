from vision.vision import Vision, Camera, GUI
from postprocessing.postprocessing import Postprocessing
from preprocessing.preprocessing import Preprocessing
import vision.tools as tools
from cv2 import waitKey
import cv2
import serial
import warnings
import time
from behaviour.planner import Planner
from communications.RobotCommunications import RobotCommunications


warnings.filterwarnings("ignore", category=DeprecationWarning)


class Controller:
    """
    This class aims to be the bridge in between vision and strategy/logic
    """
    robotCom = None

    def __init__(self, pitch, color, our_side, video_port=0, comm_port='/dev/ttyACM0', comms=1):
        """
        Entry point for the SDP system.

        Params:
            [int] video_port                port number for the camera
            [string] comm_port              port number for the arduino
            [int] pitch                     0 - main pitch, 1 - secondary pitch
            [string] our_side               the side we're on - 'left' or 'right'
            *[int] port                     The camera port to take the feed from
            *[Robot_Controller] attacker    Robot controller object - Attacker Robot has a RED
                                            power wire
            *[Robot_Controller] defender    Robot controller object - Defender Robot has a YELLOW
                                            power wire
        """
        assert pitch in [0, 1]
        assert color in ['yellow', 'blue']
        assert our_side in ['left', 'right']

        self.pitch = pitch

        # Set up robot communications to bet sent to planner.
        try:
            self.robotCom = RobotCommunications(debug=True)
        except:
            print 'not connected to the radio'
            pass

        # Set up main planner
        if(self.robotCom is not None):
            self.planner = Planner(our_side=our_side, pitch_num=self.pitch, robotCom=self.robotCom)

        # Set up camera for frames
        self.camera = Camera(port=video_port, pitch=self.pitch)
        frame = self.camera.get_frame()
        center_point = self.camera.get_adjusted_center(frame)

        # Set up vision
        self.calibration = tools.get_colors(pitch)
        self.vision = Vision(
            pitch=pitch, color=color, our_side=our_side,
            frame_shape=frame.shape, frame_center=center_point,
            calibration=self.calibration)

        # Set up postprocessing for vision
        self.postprocessing = Postprocessing()

        # Set up GUI
        self.GUI = GUI(calibration=self.calibration, pitch=self.pitch)

        self.color = color
        self.side = our_side

        self.preprocessing = Preprocessing()


    def main(self):
        """
        This main method  brings in to action the controller class which so far
        does nothing but set up the vision and its ouput
        """
        counter = 1L
        timer = time.clock()
        try:
            c = True
            while c != 27:  # the ESC key

                frame = self.camera.get_frame()
                pre_options = self.preprocessing.options
                # Apply preprocessing methods toggled in the UI
                preprocessed = self.preprocessing.run(frame, pre_options)
                frame = preprocessed['frame']
                if 'background_sub' in preprocessed:
                    cv2.imshow('bg sub', preprocessed['background_sub'])
                # Find object positions
                # model_positions have their y coordinate inverted

                #  IMPORTANT
                model_positions, regular_positions = self.vision.locate(frame)
                model_positions = self.postprocessing.analyze(model_positions)
                #print model_positions

                # Update planner world beliefs
                if(self.robotCom is not None):
                    self.planner.update_world(model_positions)
                    
                    # This activates the defending strategy for our robot. I did not work on attacking strategy.
                    self.planner.plan('defender')

                # Use 'y', 'b', 'r' to change color.
                c = waitKey(2) & 0xFF
                actions = []
                fps = float(counter) / (time.clock() - timer)
                # Draw vision content and actions

                self.GUI.draw(
                    frame, model_positions, actions, regular_positions, fps, None,
                    None, None, None, False,
                    our_color=self.color, our_side=self.side, key=c, preprocess=pre_options)
                counter += 1

        except:
            print("TODO SOMETHING CLEVER HERE")
            raise
        finally:
            tools.save_colors(self.pitch, self.calibration)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pitch", help="[0] Main pitch, [1] Secondary pitch")
    parser.add_argument("side", help="The side of our defender ['left', 'right'] allowed.")
    parser.add_argument("color", help="The color of our team - ['yellow', 'blue'] allowed.")
    parser.add_argument(
        "-n", "--nocomms", help="Disables sending commands to the robot.", action="store_true")

    args = parser.parse_args()
    if args.nocomms:
        c = Controller(
            pitch=int(args.pitch), color=args.color, our_side=args.side, comms=0).main()
    else:
        c = Controller(
            pitch=int(args.pitch), color=args.color, our_side=args.side).main()
