import numpy as np

def dynamics(t, x, u):
    A, a1, a2, a3, g = 1.0, 0.1, 0.1, 0.1, 9.81
    h1, h2, h3 = x[0], x[1], x[2]
    xdot = [u/A - a1/A * np.sqrt(2*g*h1),
            a1/A * np.sqrt(2*g*h1) - a2/A * np.sqrt(2*g*h2),
            a2/A * np.sqrt(2*g*h2) - a3/A * np.sqrt(2*g*h3)]
    return np.array(xdot)