import numpy as np

def dynamics(t, x, u):
    m, c, ki, g = 1, 0.5, 0.001, 9.81
    x1, v1, x2, v2 = x[0], x[1], x[2], x[3]
    F1 = ki * u / ((x1+1)**2)
    F2 = ki * u / ((x2+1)**2)
    xdot = [v1, F1/m - c*v1/m - g, v2, F2/m - c*v2/m]
    return np.array(xdot)