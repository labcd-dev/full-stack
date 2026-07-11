import numpy as np

def dynamics(t, x, u):
    J1, J2, k, d, b1, b2 = 0.01, 0.01, 1.0, 0.1, 0.05, 0.05
    theta1, omega1, theta2, omega2 = x[0], x[1], x[2], x[3]
    xdot = [omega1,
            (u - k*(theta1 - theta2) - d*(omega1 - omega2) - b1*omega1) / J1,
            omega2,
            (k*(theta1 - theta2) + d*(omega1 - omega2) - b2*omega2) / J2]
    return np.array(xdot)