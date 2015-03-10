import numpy as np


class Kalman:
    # Timestep in between frames
    t = 0.0416

    # Matrices:

    # Produces transition to next state
    TransitionMatrix = np.array([[1, 0, t, 0],
                                 [0, 1, 0, t],
                                 [0, 0, 1, 0],
                                 [0, 0, 0, 1]])

    # Will not be used but it accounts for the
    # control vector things such as acceleration etc
    InputControl = np.array([[1, 0, 0, 0],
                             [0, 1, 0, 0],
                             [0, 0, 1, 0],
                             [0, 0, 0, 1]])

    # Converts state transitions back to measurements
    # A pointless computation in this case
    MeasurementMatrix = np.array([[1, 0, 0, 0],
                                  [0, 1, 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])

    # Covariance Matrix for the measurements
    # quantifies the error in the state transition
    ActionUncertainty = np.array([[1, 0, 0,   0],
                                  [0, 1, 0,   0],
                                  [0, 0, 0.1, 0],
                                  [0, 0, 0, 0.1]])

    # Covariance matrix for uncertainty in measurements
    SensorUncertainty = np.array([[0.1, 0, 0, 0],
                                  [0, 0.1, 0, 0],
                                  [0, 0, 0.1, 0],
                                  [0, 0, 0, 0.1]])

    # Vectors:
    control_vector = np.array([0, 0, 0, 0])

    def __init__(self,
                 measurement_vector,
                 TransitionMatrix=TransitionMatrix,
                 InputControl=InputControl,
                 MeasurementMatrix=MeasurementMatrix,
                 ActionUncertainty=ActionUncertainty,
                 SensorUncertainty=SensorUncertainty,
                 control_vector=control_vector):
        self.InputControl = InputControl
        self.MeasurementMatrix = MeasurementMatrix
        self.ActionUncertainty = ActionUncertainty
        self.SensorUncertainty = SensorUncertainty

if __name__ == '__main__':
    a = Kalman(1)
    print Kalman.TransitionMatrix
