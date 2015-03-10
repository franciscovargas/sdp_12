import numpy as np
from numpy import dot


class Kalman:
    # Timestep in between frames
    dt = 0.0416

    # Matrices:

    # Produces transition to next state
    TransitionMatrix = np.array([[1, 0, 1, 0],
                                 [0, 1, 0, 1],
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

    #  Estimated coovariance for Kalman gain
    P = np.zeros((4, 4))

    # Identity Matrix
    I = np.identity(4)

    # Vectors:
    control_vector = np.array([0, 0, 0, 0])
    prediction = np.array([0, 0, 0, 0])

    def __init__(self,
                 TransitionMatrix=TransitionMatrix,
                 InputControl=InputControl,
                 MeasurementMatrix=MeasurementMatrix,
                 ActionUncertainty=ActionUncertainty,
                 SensorUncertainty=SensorUncertainty,
                 control_vector=control_vector):
        """
        Constructor for Kalman filter object sets up Matrices for
        state changes and evaluations before hand yet allows them
        to be passed as parameters
        """
        self.InputControl = InputControl
        self.MeasurementMatrix = MeasurementMatrix
        self.ActionUncertainty = ActionUncertainty
        self.SensorUncertainty = SensorUncertainty

    def prediction_step(self, measurement_vec):
        measurement_vec = np.array(measurement_vec)
        # Transitioning to the next state
        self.prediction = dot(self.TransitionMatrix, measurement_vec) + \
            dot(self.InputControl, self.control_vector)
        # Evaluating a priori estimate error covariance
        self.P = dot(self.TransitionMatrix, dot(self.P, self.TransitionMatrix.T)) + \
            self.ActionUncertainty
        return self.prediction

    def correction_step(self, measurement_vec):
        self.prediction_step(measurement_vec)
        S = dot(self.MeasurementMatrix,
                dot(self.P,
                    self.MeasurementMatrix.T)) + \
            self.SensorUncertainty
        S_inv = np.linalg.inv(S)
        K = dot(self.P,
                dot(self.MeasurementMatrix.T,
                    S_inv))
        y = measurement_vec - dot(self.MeasurementMatrix,
                                  self.prediction)
        self.prediction = self.prediction + dot(K, y)
        self.P = dot((self.I - dot(K,
                                   self.MeasurementMatrix)),
                     self.P)
        return self.prediction

    def n_frames(self, n, measurement_vec):
        mes1 = self.correction_step(measurement_vec)
        for i in range(n - 1):
            mes1 = self.correction_step(mes1)
        return mes1


if __name__ == '__main__':
    a = Kalman()
    # print a.P
    print a.n_frames(1,[1, 1, 20, 20])
    # print a.P
